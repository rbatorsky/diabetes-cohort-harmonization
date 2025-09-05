LIB="/cluster/tufts/patralab/rbator01/R_libs/4.4.0/"
.libPaths(LIB)

library(openxlsx)
library(tidyverse)
library("corrplot")
library(pheatmap)
library(VIM)
library(naniar)
library(sas7bdat)
library(haven)
library(caret)
library(ggpubr)
library(visdat)
library(ggfortify)
library("FactoMineR")
library(ggcorrplot)
library(dplyr)
library(purrr)
library(ggpubr)
library(ggplot2)
library(tidyr)
library(data.table)

filter=dplyr::filter
rename=dplyr::rename
select=dplyr::select
setwd("/cluster/tufts/patralab/rbator01/aiml_ordovas_project/")
library(fastDummies)

# analyze class balance ----
#data = readRDS("r_pipeline/analysis/rds/harmonize_2cohort_healthsdohffq_24apr25_v1_rmmissing_50col_10row_preproc_for_eda.rds")
data = readRDS("r_pipeline/analysis/rds/harmonize_2cohort_healthsdohffq_4aug25_v1_rmmissing_50col_10row_preproc_for_eda.rds")

table(data$diabetes, useNA = "ifany")

nclass = 2
outvar = "diabetes"
filter_cohort = "none"
downsample = 0
seed=1
year='w1'
importance = "boruta"
data_string="all"

save_string = paste0(data_string, "_",outvar,"_",year,"_class", nclass,"_filter",filter_cohort,"_ds",downsample,"_", seed,"_tune_balancecohort_",importance,"_12jul25")

table(data$cohort)

# train_baked = readRDS(paste0("r_pipeline/analysis/rf/train_baked_", save_string,".rds"))
# test_baked = readRDS(paste0("r_pipeline/analysis/rf/test_baked_", save_string,".rds"))
# 
# any(is.na(train_baked))
# any(is.na(test_baked))
# any(is.infinite(train_baked))
# any(is.na(test_baked))
# dim(train_baked)
# dim(test_baked)
# 
# data = rbind(train_baked, test_baked)
# any(!is.finite(as.matrix(data)))
# which(!is.finite(as.matrix(data)), arr.ind = TRUE)
# data[,1]
# prop.table(table(data$cohort, data$diabetes))

unique(data$cohort)

# analyze the variable features
data_mod = data %>%
  mutate(cohort = ifelse(cohort == 0,"BPRHS","PROSPECT")) %>%
  mutate(cohort_db = factor(paste0(cohort, "_", diabetes), levels=c("BPRHS_0","BPRHS_1","PROSPECT_0","PROSPECT_1")))

warning_cols <- character(0)
data_numeric <- data %>%
  mutate(across(everything(), ~ {
    if (is.factor(.x) || is.character(.x)) {
      num_x <- suppressWarnings(as.numeric(as.character(.x)))

      # Check if coercion introduced NA
      if (any(is.na(num_x) & !is.na(.x))) {
        warning_cols <<- c(warning_cols, cur_column())
      }

      num_x
    } else {
      .x
    }
  }))

warning_cols
str(data_numeric$diabetes)

pca_norm.pca <- princomp(data_numeric)

nonfinite_summary <- sapply(data_numeric, function(x) any(!is.finite(x)))
nonfinite_columns <- names(nonfinite_summary[nonfinite_summary])
print(nonfinite_columns)

summary(pca_norm.pca)
library(factoextra)
fviz_eig(pca_norm.pca, addlabels = TRUE)
fviz_pca_var(pca_norm.pca, col.var = "black")

autoplot(pca_norm.pca,
         data = data,
         colour='cohort',
         loadings.label.repel=T)

# make a umap -----
library(plotly)
library(umap)

data.umap <- umap(data_numeric, random_state=123)
layout <- data.frame(data.umap$layout)
meta = data %>%
  select(cohort) %>%
  mutate(cohort = factor(cohort, labels = c("0","1")))

final <- cbind(layout, meta) %>%
  mutate(cohort = ifelse(cohort == 0,"BPRHS", "PROSPECT"))
colnames(final)
colnames(final) = c("UMAP1","UMAP2","cohort")


# https://plotly.com/r/t-sne-and-umap-projections/
p = plot_ly(final, x = ~UMAP1, y = ~UMAP2, color = ~cohort,
        type = 'scatter', mode = 'markers', alpha=0.5) %>%
  layout(
    legend=list(title=list(text='Cohort')),
    xaxis = list(
      title = "UMAP1",range = list(-10, 10)),
    yaxis = list(
      title = "UMAP2"))

show(p)
ggsave(p, "r_pipeline/analysis/plots/umap.pdf", height)

# can I add something like loading vectors 

cor_matrix <- cor(data_numeric, layout)

# Scale the correlation values to visualize as arrows
vectors <- as.data.frame(cor_matrix) * 5  # scaling factor for visual effect
vectors$feature <- rownames(vectors)

colnames(vectors)[1:2] <- c("xend", "yend")
vectors$x <- 0
vectors$y <- 0

# reduce number of vectors that I plot
vectors$magnitude <- sqrt(vectors$xend^2 + vectors$yend^2)

# direction
vectors$unit_x <- vectors$xend / vectors$magnitude
vectors$unit_y <- vectors$yend / vectors$magnitude

#3. Cluster Directions (e.g., K-means or angular bins)
set.seed(123)
direction_clusters <- kmeans(vectors[, c("unit_x", "unit_y")], centers = 10)  # pick 6–12 for coverage
vectors$dir_cluster <- direction_clusters$cluster

#select top n by magnitude within each cluster
vectors_filtered <- vectors %>%
  group_by(dir_cluster) %>%
  slice_max(order_by = magnitude, n = 1) %>%  # can change to 2 or 3 per cluster
  ungroup() %>%
  mutate(feature = gsub("hmz_","", feature))


# plot filtered
p = ggplot(final, aes(x = UMAP1, y = UMAP2, color = cohort)) +
  geom_point(alpha = 0.5) +
  geom_segment(data = vectors_filtered,
               aes(x = 0, y = 0, xend = xend, yend = yend),
               arrow = arrow(length = unit(0.2, "cm")),
               color = "black",
               inherit.aes = FALSE) +
  geom_text(data = vectors_filtered,
            aes(x = xend, y = yend, label = feature),
            size = 3, hjust = 0.5, vjust = -0.5,
            inherit.aes = FALSE) +
  theme_minimal()

show(p)
ggsave(p, filename = "r_pipeline/analysis/plots/umap_with_vectors.pdf",height=6, width=6)

# correlation analysis, find correlated variables across modalities ----

library(corrplot)

# Compute correlation matrix
cor_matrix <- cor(data_numeric, use = "complete.obs")  # Use "complete.obs" to ignore NAs
cor_matrix[lower.tri(cor_matrix, diag = TRUE)] <- NA

# Find column pairs with correlation above threshold, keep reducing the threshold until we find some cross-modality correlations
threshold=0.75
high_corr_pairs <- which(abs(cor_matrix) > threshold, arr.ind = TRUE)

# Convert matrix indices to column names

correlated_pairs <- data.frame(
  Col1 = colnames(data)[high_corr_pairs[, 1]],
  Col2 = colnames(data)[high_corr_pairs[, 2]],
  Correlation = cor_matrix[high_corr_pairs]
)

correlated_pairs

corr_diffmod = correlated_pairs %>%
  mutate(type_1 = ifelse(grepl("ffq",Col1),"ffq",
                         ifelse(grepl("health",Col1),"health",
                                ifelse(grepl("sdoh",Col1),"sdoh",NA))))%>%
  mutate(type_2 = ifelse(grepl("ffq",Col2),"ffq",
                         ifelse(grepl("health",Col2),"health",
                                ifelse(grepl("sdoh",Col2),"sdoh",NA)))) %>%
  filter(type_1 != type_2)

#none
head(corr_diffmod)

# another way of doing correlation analysis, this one gives plots ----
library(caret)

# Find and remove highly correlated features (threshold = 0.9)
high_cor <- findCorrelation(cor(data_numeric, use = "complete.obs"),
                            cutoff = 0.8,
                            verbose = TRUE)
data_reduced <- data_numeric[, -high_cor]

# are there any high cross-variable correlations?
cor_matrix <- cor(data_reduced, use = "complete.obs")  # Use "complete.obs" to ignore NAs
cor_matrix[lower.tri(cor_matrix, diag = TRUE)] <- NA

threshold=0.6
high_corr_pairs <- which(abs(cor_matrix) > threshold, arr.ind = TRUE)

# Convert matrix indices to column names
correlated_pairs <- data.frame(
  Col1 = colnames(data_reduced)[high_corr_pairs[, 1]],
  Col2 = colnames(data_reduced)[high_corr_pairs[, 2]],
  Correlation = cor_matrix[high_corr_pairs]
)

cor_matrix <- cor(data_reduced, use = "complete.obs")  # Use "complete.obs" to ignore NAs
rownames(cor_matrix) = gsub("hmz_","",rownames(cor_matrix))
colnames(cor_matrix) = gsub("hmz_","",colnames(cor_matrix))
corrplot(cor_matrix, method = "color", order = "hclust", tl.cex = 0.6)


cor_df <- as.data.frame(cor_matrix)
cor_df$Var1 <- rownames(cor_df)

cor_long <- cor_df %>%
  pivot_longer(-Var1, names_to = "Var2", values_to = "Correlation")





library(heatmaply)



p = heatmaply(cor_matrix,
          k_col = 5,
          k_row = 5,
          colors = colorRampPalette(c("blue", "white", "red"))(200),  # Balanced diverging palette
          labCol = colnames(cor_matrix),
          labRow = rownames(cor_matrix),
          margins = c(60, 100),  # space for axis labels
          plot_method = "plotly",
          main = "",
          xlab = "",
          ylab = "",
          row_text_angle = 0,
          column_text_angle = 90,
          fontsize_row = 10,
          fontsize_col = 10,
          grid_color = "grey80",
          text_matrix = round(cor_matrix, 2),
          label_names = c("Row", "Column", "Value"),
          label_color = "black")

show(p)
htmlwidgets::saveWidget(p, file = "r_pipeline/analysis/plots/heatmap_correlation.html")

data_reduced = data_reduced %>%
  as.data.frame()


threshold=0.5
high_corr_pairs <- which(abs(cor_matrix) > threshold, arr.ind = TRUE)

corr_diffmod = correlated_pairs %>%
  mutate(type_1 = ifelse(grepl("ffq",Col1),"ffq",
                       ifelse(grepl("health",Col1),"health",
                              ifelse(grepl("sdoh",Col1),"sdoh",NA))))%>%
  mutate(type_2 = ifelse(grepl("ffq",Col2),"ffq",
                         ifelse(grepl("health",Col2),"health",
                                ifelse(grepl("sdoh",Col2),"sdoh",NA)))) %>%
  filter(type_1 != type_2)


corr_diffmod

# run a loop to test for differences between cohorts, archive this -----
#   ffq_main_ro = readRDS("data/harmonize_ffq_select_main_commoncols_fulljoin_rm_kcal_outlier.rds")
# dim(ffq_main_ro)
# rm_nearzerovar = nearZeroVar(ffq_main_ro, names = TRUE)
# rm_nearzerovar
#
# ffq_main_test = ffq_main_ro %>%
#   select(-rm_nearzerovar) %>%
#   select(-c("studyid","visit"))
#
# cs = colnames(ffq_main_test)
#
# library(ggpubr)
#
# # c = "hmz_ffq_kcal"
# # c = "hmz_gramamt_f"
# # c="hmz_kj_f"
# # c="hmz_tcho_f"
# # c="hmz_fat_f"
#
# df = NULL
# for (c in cs){
#   if(c != "cohort"){
#     print(c)
#
#     f = ffq_main_test %>%
#       select(all_of(c("cohort",c)))
#
#
#     f_p = f %>%
#       filter(cohort == "prospect")
#
#     f_b = f %>%
#       filter(cohort == "bprhs")
#
#     res = t.test(get(c) ~ cohort, data = f)
#
#
#     if(res$p.value < 0.05){
#       p <- ggviolin(f, x = "cohort", y = c,
#                     add = "boxplot") + stat_compare_means(method = "t.test",
#                                                           label.x = 1.5, label.y = max(f[[c]])) +
#         ggtitle(c)
#
#       ggsave(p, filename=paste0("r_pipeline/analysis/plots/",c,"_rm_outlier.pdf"), height = 4, width = 4)
#     }
#
#
#     df_c = data.frame(feature = c,
#                       pval =res$p.value,
#                       min_p = min(f_p[[c]], na.rm = T),
#                       max_p = max(f_p[[c]], na.rm = T),
#                       min_b = min(f_b[[c]], na.rm = T),
#                       max_b = max(f_b[[c]], na.rm = T),
#                       med_b = median(f_b[[c]], na.rm = T),
#                       med_p = median(f_p[[c]], na.rm = T)
#     )
#
#     if(is.null(df)){
#       df = df_c
#     }else{
#       df = rbind(df, df_c)
#     }
#   }
# }
#
# write.xlsx(df, "r_pipeline/analysis/plots/pvals_rm_outlier.xlsx")
#
#
# There is some RAW survey data in prospect that can be combined - here some things need to be harmonized - do this later -----
to_select = unique(ffq_h_key$prospect_ffq_raw[!is.na(ffq_h_key$prospect_ffq_raw)])

# note there are some suplicates, we will pick the max redcapid for a given studyid, visit
#dup_studyid=c('842101149','866101456')
#data_p_1s_dup = read.xlsx("data/prospect/data_13may24/csv/PROSPECT5_FFQ_DATA_RAW_Spanish_VISITS1&2_2024-11-26.xlsx") %>%
#  filter(studyid %in% dup_studyid)

data_p_1s = read.xlsx("data/prospect/data_13may24/csv/PROSPECT5_FFQ_DATA_RAW_Spanish_VISITS1&2_2024-11-26.xlsx") %>%
  group_by(studyid, redcap_event_name) %>%
  mutate(max_redcapid = redcapid[which.max(redcapid)]) %>%
  ungroup() %>%
  filter(redcapid == max_redcapid)  %>%
  select(to_select)

data_p_1e = read.xlsx("data/prospect/data_13may24/csv/PROSPECT5a_FFQ_DATA_RAW_English_VISITS1&2_2024-11-26.xlsx")%>%
  select(to_select)

data_p_1 = rbind(data_p_1e, data_p_1s)
colnames(data_p_1) = tolower(colnames(data_p_1))

# rename some columns
ffq_h_key_rename = ffq_h_key %>%
  select("prospect_ffq_raw", "harmonized_name") %>%
  filter(!is.na(prospect_ffq_raw) & !is.na(harmonized_name))

data_p_1 = data_p_1 %>%
  rename_at(vars(ffq_h_key_rename$prospect_ffq_raw), ~ ffq_h_key_rename$harmonized_name) %>%
  mutate(visit  = ifelse(visit %in% c("event_1_arm_1","visit_1_arm_1"),"v1","v2")) %>%
  filter(!is.na(hmz_sup_use))

# harmonize_here prospect ffq raw ---
# at this point we can replace NA with zero to agree with bprhs
data_p_1[is.na(data_p_1)] = 0

data_p_ffq = data_perday %>%
  inner_join(data_p_1 , by=c("studyid","visit")) %>%
  mutate(cohort = "prospect")

any(is.na(data_p_ffq$hmz_meal_place_brk))

#write.csv(data_p_ffq, "data/harmonize_ffq_raw_prospect_v1only_25nov24.xlsx")


# FIRST ANALYSIS - harmonized BPRHS baseline & 2 variables with PROSPECT -----

ffq_h_key = read.xlsx("data/harmonize_ffq_26nov24_rebecca.xlsx") %>%
  select("bprhs_baseline", "bpr_2", "prospect_perday_perfood","prospect_ffq_raw", "harmonized_name") %>%
  filter(!is.na(bprhs_baseline) & !is.na(bpr_2)  & (!is.na(prospect_perday_perfood) | !is.na(prospect_ffq_raw)))
# 170 harmonized variables
#nrow(ffq_h_key)

# bprhs ffq -----
# b baseline


b_ffq = rbind(b_1, b_2)

# harmonize_here bprhs: encode diet and meal places -----

# unique(b_ffq$hmz_diet_type)
# unique(b_ffq$hmz_meal_place_din)
# unique(b_ffq$hmz_meal_place_lun)
# unique(b_ffq$hmz_meal_place_din)
#
# b_ffq %>%
#   select("hmz_diet_type",
#          "hmz_meal_place_brk",
#          "hmz_meal_place_lun",
#          "hmz_meal_place_din")

diet_type_rename = data.frame(old_name = c(NA, "Kosher", "Vegetarian", "Weight reduction","Rx"), new_name = c(0,1,2,3,4))
meal_place_rename = data.frame(old_name = c(NA, "Home", "Work", "Cafeteria","Fast food", "Restaurant","MM"), new_name = c(6,1,2,3,4,5,6))

b_ffq = b_ffq %>%
  left_join(diet_type_rename, by=c("hmz_diet_type" = "old_name")) %>%
  select(-hmz_diet_type) %>%
  rename(hmz_diet_type = new_name) %>%
  left_join(meal_place_rename, by=c("hmz_meal_place_brk" = "old_name")) %>%
  select(-hmz_meal_place_brk) %>%
  rename(hmz_meal_place_brk = new_name) %>%
  left_join(meal_place_rename, by=c("hmz_meal_place_lun" = "old_name")) %>%
  select(-hmz_meal_place_lun) %>%
  rename(hmz_meal_place_lun = new_name) %>%
  left_join(meal_place_rename, by=c("hmz_meal_place_din" = "old_name")) %>%
  select(-hmz_meal_place_din) %>%
  rename(hmz_meal_place_din = new_name)

# test = b_ffq %>%
#   select("hmz_diet_type",
#          "hmz_meal_place_brk",
#          "hmz_meal_place_lun",
#          "hmz_meal_place_din")
#
# view(test)
