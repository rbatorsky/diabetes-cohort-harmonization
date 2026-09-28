#######
## Make a PCA plot with loading vectors
#######

source("utils.R")
suppressPackageStartupMessages({
  library(stringr)
  library(openxlsx)
  library(pheatmap)
  library(haven)
  library(caret)
  library(ggfortify)
  library(FactoMineR)
  library(dplyr)
  library(purrr)
  library(ggpubr)
  library(ggplot2)
  library(tidyr)
  library(data.table)
  library(fastDummies)
  library(ggrepel)
  library(factoextra)
  library(grid)
  library(ggnewscale)
  library(tibble)
})

RDS1 = "../../analysis/harmonize_2cohort_healthsdohffq_v1_rmmissing_50col_10row_preproc_for_eda.rds"
data = readRDS(RDS1)
df <- as.data.frame(data)
rownames(df) <- paste0("id_", seq_len(nrow(df)))

df <- df %>%
  mutate(across(where(is.character), as.factor)) %>%
  mutate(across(where(is.numeric) | where(is.integer), as.numeric)) %>%
  select(-row_id)

names(df)

# logical vectors by type
is_num   <- vapply(df, is.numeric, logical(1))
is_fac   <- vapply(df, is.factor,  logical(1))

names(which(is_num))   # names of numeric columns
names(which(is_fac))   # names of factor columns

# prep for FAMD
prep_for_famd <- function(df, sup_keep = c("cohort")) {
  df %>%
    # use value labels when available
    mutate(across(where(haven::is.labelled),
                  ~ haven::as_factor(.x, levels = "labels"))) %>%
    # characters -> factors
    mutate(across(where(is.character), as.factor)) %>%
    # keep numeric truly numeric
    mutate(across(where(is.numeric) | where(is.integer), as.numeric)) %>%
    # for factors: if levels are numeric-looking or duplicated across vars,
    # prefix with the variable name; leave sup vars as-is
    {
      fctr_cols <- names(.)[sapply(., is.factor)]
      # don’t relabel the supplementary ones (e.g., cohort) if you want original levels
      fctr_cols_relabel <- setdiff(fctr_cols, sup_keep)
      
      relabel_one <- function(x, var) {
        lv <- levels(x)
        # numeric-like?
        numlike <- grepl("^\\s*-?\\d+(?:\\.\\d+)?\\s*$", lv)
        # If all lv are numeric-like OR these levels appear in many variables,
        # add var= prefix; else keep as-is.
        if (all(numlike)) {
          levels(x) <- paste0(var, "=", lv)
        } else {
          # also guard against common generic levels like "0/1/Yes/No"
          common <- lv %in% c("0","1","2","Yes","No","Male","Female")
          if (any(common)) levels(x)[common] <- paste0(var, "=", lv[common])
        }
        x
      }
      
      out <- .
      for (v in fctr_cols_relabel) out[[v]] <- relabel_one(out[[v]], v)
      out
    }
}

df <- prep_for_famd(df, sup_keep = c("cohort"))
sup_vars <- c("cohort")
quali_sup <- which(names(df) %in% sup_vars)
res.famd <- FAMD(df, sup.var = quali_sup, graph = FALSE)

## --- Base individuals plot (unchanged) ---
cohort_cols <- c("BPRHS"="#B39DDB", "PROSPECT"="#9E9E9E")
fill_colors <- c("FFQ"="#7BAFD4", "SDOH"="#F4A259", "HEALTH"="#88C27C")
prefix_levels <- names(fill_colors)

p <- fviz_famd_ind(
  res.famd,
  habillage   = "cohort",
  geom        = "point",
  addEllipses = TRUE,
  mean.point  = FALSE,
  invisible   = "quali.var",  
  repel       = TRUE
) +
  scale_color_manual(values = cohort_cols, name = "Cohort") +
  scale_fill_manual(values  = cohort_cols, name = "Cohort")

## --- Coordinates for scaling (ind + numeric loadings) ---
ind_coords <- as.data.frame(res.famd$ind$coord)

## --- Numeric loadings: scale FIRST, then rank by length ---
load_q <- as.data.frame(res.famd$quanti.var$coord) %>%
  tibble::rownames_to_column("variable") %>%
  dplyr::mutate(
    prefix = dplyr::case_when(
      grepl("^hmz_ffq",    variable, TRUE) ~ "FFQ",
      grepl("^hmz_sdoh",   variable, TRUE) ~ "SDOH",
      grepl("^hmz_health", variable, TRUE) ~ "HEALTH",
      TRUE ~ NA_character_
    )
  ) %>%
  dplyr::filter(!is.na(prefix)) %>%
  dplyr::mutate(prefix = factor(prefix, levels = prefix_levels))

# scale to individual space
sx <- max(abs(ind_coords$Dim.1), na.rm = TRUE) / max(abs(load_q$Dim.1),  na.rm = TRUE)
sy <- max(abs(ind_coords$Dim.2), na.rm = TRUE) / max(abs(load_q$Dim.2),  na.rm = TRUE)
s  <- 0.9 * min(sx, sy)

load_scaled <- load_q %>%
  dplyr::mutate(
    x = s * Dim.1,
    y = s * Dim.2,
    len12 = sqrt(x^2 + y^2)   # <-- rank using POST-SCALE length
  )

## --- Qualitative modalities: already in individual space; rank on x,y ---
quali_pts <- as.data.frame(res.famd$quali.var$coord) %>%
  tibble::rownames_to_column("modality") %>%
  dplyr::mutate(
    var_name = ifelse(grepl("=", modality), sub("=.*$", "", modality), modality),
    prefix = dplyr::case_when(
      grepl("^hmz_ffq",    var_name, TRUE) ~ "FFQ",
      grepl("^hmz_sdoh",   var_name, TRUE) ~ "SDOH",
      grepl("^hmz_health", var_name, TRUE) ~ "HEALTH",
      TRUE ~ NA_character_
    )
  ) %>%
  dplyr::filter(!is.na(prefix)) %>%
  dplyr::mutate(prefix = factor(prefix, levels = prefix_levels)) %>%
  dplyr::transmute(
    id = modality, label = modality, prefix,
    x = Dim.1, y = Dim.2,
    len12 = sqrt(x^2 + y^2),       # <-- rank on same metric/space
    type = "factor"
  )

## --- Joint ranking stays the same ---
num_for_rank <- load_scaled %>%
  dplyr::transmute(id = variable, label = variable, prefix, len12, x, y, type = "numeric")

both <- dplyr::bind_rows(num_for_rank, quali_pts)

top3_both <- both %>%
  dplyr::group_by(prefix) %>%
  dplyr::slice_max(order_by = len12, n = 3, with_ties = FALSE) %>%
  dplyr::ungroup()

head(top3_both)

top_num <- dplyr::filter(top3_both, type == "numeric")
top_num
top_fac <- dplyr::filter(top3_both, type == "factor")
top_fac
leftovers_num <- dplyr::anti_join(load_scaled, top_num, by = c("variable" = "id"))


## --- Optional: pretty labels for numeric top-3 from your Excel map ---
lab <- openxlsx::read.xlsx("../../analysis/plots/relabel_features_plot_28oct25_edit.xlsx")
head(lab)
lab_clean <- lab %>%
  select(long_variable_name, description.new) %>%
  mutate(across(everything(), as.character)) %>%
  distinct(long_variable_name, .keep_all = TRUE)

head(top_num)
top_num <- top_num %>%
  dplyr::left_join(lab_clean, by = c("label" = "long_variable_name")) %>%
  dplyr::mutate(
    desc = dplyr::coalesce(description.new, ""),
    desc = stringr::str_trim(desc),
    # use dplyr::na_if (NOT stringr::na_if)
    desc = dplyr::na_if(desc, ""),
    label_use = dplyr::coalesce(desc, label),
    .keep = "unused"
  )

top_num

# Factor labels: use the modality string (already like "var=level")
top_fac <- top_fac %>%
  dplyr::mutate(label_use = label)

top_fac

# Build final plot ---
p_final <- p +
  ggnewscale::new_scale_color() +  # fresh color scale for numeric arrows
  
  # Background numeric arrows (faint)
  geom_segment(
    data = leftovers_num,
    aes(x = 0, y = 0, xend = x, yend = y, color = prefix),
    inherit.aes = FALSE,
    alpha = 0.35, linewidth = 0.7,
    arrow = arrow(length = unit(2, "mm"))
  ) +
  
  # Top numeric arrows (opaque)
  geom_segment(
    data = top_num,
    aes(x = 0, y = 0, xend = x, yend = y, color = prefix),
    inherit.aes = FALSE,
    linewidth = 1.0,
    arrow = arrow(length = unit(2.5, "mm"))
  ) +
  
  # Labels for top numeric arrows
  geom_text_repel(
    data = top_num,
    aes(x = x, y = y, label = label_use),
    inherit.aes = FALSE,
    color = "black",
    size = 4.2,
    box.padding = 0.45,
    point.padding = 0.25,
    max.overlaps = Inf
  ) +
  
  scale_color_manual(values = fill_colors, name = "Vector family") +
  guides(color = guide_legend(override.aes = list(alpha = 1, linewidth = 1.2))) +
  
  ggnewscale::new_scale_fill() +   # fresh fill scale for factor points
  
  # Top qualitative modalities (points only, shown ONLY if they make top-3)
  geom_point(
    data = top_fac,
    aes(x = x, y = y, fill = prefix),
    inherit.aes = FALSE,
    shape = 21, size = 3.6, stroke = 0.8, color = "black", alpha = 0.9
  ) +
  
  # Labels for factor modalities
  geom_text_repel(
    data = top_fac,
    aes(x = x, y = y, label = label_use),
    inherit.aes = FALSE,
    color = "black",
    size = 4.0,
    box.padding = 0.4,
    point.padding = 0.2,
    max.overlaps = Inf
  ) +
  
#  scale_fill_manual(values = fill_colors, name = "Factor family") +
  
  labs(title = NULL, subtitle = NULL) +
  theme(plot.title = element_blank(), plot.subtitle = element_blank(),
        legend.box = "vertical")


p_final <- p_final +
  theme(
    text = element_text(size = 14),          # base size
    axis.title = element_text(size = 15),
    axis.text  = element_text(size = 13),
    legend.title = element_text(size = 14),
    legend.text  = element_text(size = 12),
    strip.text = element_text(size = 14),
    plot.margin = margin(10, 10, 10, 10)
  )

print(p_final)

## --- Save PDF ---
out_dir <- "../../analysis/plots"
if (!dir.exists(out_dir)) dir.create(out_dir, recursive = TRUE)

ggplot2::ggsave(
  filename = file.path(out_dir, "famd_ind_top3_numeric_and_factors.pdf"),
  plot = p_final,
  device = cairo_pdf, width = 8, height = 6, units = "in"
)

p_final

# archive this
# # For a single factor column in df
# levels(df$cohort)
# 
# # For your prefixes
# levels(top_fac$prefix)        # if it's a factor
# unique(top_fac$prefix)        # works for character or factor
# 
# # If you’re not sure it’s a factor:
# is.factor(top_fac$prefix)
# 
# table(top_fac$prefix, useNA = "ifany")
# dplyr::count(top_fac, prefix)
# 
# 
# 
# # make the standard PCA ------
# pca_norm.pca <- princomp(data_numeric)
# 
# nonfinite_summary <- sapply(data_numeric, function(x) any(!is.finite(x)))
# nonfinite_columns <- names(nonfinite_summary[nonfinite_summary])
# print(nonfinite_columns)
# 
# summary(pca_norm.pca)
# library(factoextra)
# fviz_eig(pca_norm.pca, addlabels = TRUE)
# fviz_pca_var(pca_norm.pca, col.var = "black")
# 
# 
# # Show only the top 20 contributing variables on PCs 1 & 2
# fviz_pca_biplot(
#   pca_norm.pca,
#   geom.ind = "point",
#   habillage = data$cohort,   # color by cohort
#   addEllipses = FALSE,
#   label = "var",             # show variable names (loadings)
#   select.var = list(contrib = 55),   # <— only top 20 loadings
#   repel = TRUE,
#   col.var = "black",
#   col.ind = "grey50"
# ) +
#   ggtitle("PCA biplot visit 1 (top 55 variable loadings)")
# 
# 
# # make a umap -----
# library(plotly)
# library(umap)
# 
# data.umap <- umap(data_numeric, random_state=123)
# layout <- data.frame(data.umap$layout)
# meta = data %>%
#   select(cohort) %>%
#   mutate(cohort = factor(cohort, labels = c("0","1")))
# 
# final <- cbind(layout, meta) %>%
#   mutate(cohort = ifelse(cohort == 0,"BPRHS", "PROSPECT"))
# colnames(final)
# colnames(final) = c("UMAP1","UMAP2","cohort")
# 
# 
# # # https://plotly.com/r/t-sne-and-umap-projections/
# # p = plot_ly(final, x = ~UMAP1, y = ~UMAP2, color = ~cohort,
# #         type = 'scatter', mode = 'markers', alpha=0.5) %>%
# #   layout(
# #     legend=list(title=list(text='Cohort')),
# #     xaxis = list(
# #       title = "UMAP1",range = list(-10, 10)),
# #     yaxis = list(
# #       title = "UMAP2"))
# # 
# # dev.off()
# # show(p)
# # ggsave(p, "r_pipeline/analysis/plots/umap.pdf", height)
# 
# # can I add something like loading vectors 
# 
# cor_matrix <- cor(data_numeric, layout)
# # Scale the correlation values to visualize as arrows
# vectors <- as.data.frame(cor_matrix) * 5  # scaling factor for visual effect
# vectors$feature <- rownames(vectors)
# 
# colnames(vectors)[1:2] <- c("xend", "yend")
# vectors$x <- 0
# vectors$y <- 0
# 
# # reduce number of vectors that I plot
# vectors$magnitude <- sqrt(vectors$xend^2 + vectors$yend^2)
# 
# # direction
# vectors$unit_x <- vectors$xend / vectors$magnitude
# vectors$unit_y <- vectors$yend / vectors$magnitude
# 
# #3. Cluster Directions (e.g., K-means or angular bins)
# set.seed(123)
# direction_clusters <- kmeans(vectors[, c("unit_x", "unit_y")], centers = 10)  # pick 6–12 for coverage
# vectors$dir_cluster <- direction_clusters$cluster
# 
# #select top n by magnitude within each cluster
# vectors_filtered <- vectors %>%
#   group_by(dir_cluster) %>%
#   slice_max(order_by = magnitude, n = 1) %>%  # can change to 2 or 3 per cluster
#   ungroup() %>%
#   mutate(feature = gsub("hmz_","", feature))
# 
# 
# # plot filtered
# p = ggplot(final, aes(x = UMAP1, y = UMAP2, color = cohort)) +
#   geom_point(alpha = 0.5) +
#   geom_segment(data = vectors_filtered,
#                aes(x = 0, y = 0, xend = xend, yend = yend),
#                arrow = arrow(length = unit(0.2, "cm")),
#                color = "black",
#                inherit.aes = FALSE) +
#   geom_text(data = vectors_filtered,
#             aes(x = xend, y = yend, label = feature),
#             size = 3, hjust = 0.5, vjust = -0.5,
#             inherit.aes = FALSE) +
#   theme_minimal()
# 
# show(p)
# ggsave(p, filename = "r_pipeline/analysis/plots/umap_with_vectors.pdf",height=6, width=6)
# 


# correlation analysis, find correlated variables across modalities ----
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

# experiment with clustering the data first ------
# correlation + distance between variables -----
# cor_mat  <- cor(data_numeric, use = "pairwise.complete.obs")
# dist_vars <- as.dist(1 - abs(cor_mat))
# hc <- hclust(dist_vars, method = "average")
# 
# # (optional) shorten long names to avoid overlap
# #lbls <- abbreviate(colnames(data_numeric), minlength = 10, strict = TRUE)
# 
# # widen margins if needed
# op <- par(mar = c(5, 4, 2, 1) + 0.1)
# plot(hc,
#      labels = colnames(data_numeric),
#      main = "Variable clustering dendrogram (1 - |cor|)",
#      xlab = "", sub = "", cex = 0.6, hang = -1)
# par(op)
# 
# 
# clusters <- cutree(hc, h = 0.2)  # adjust h depending on your data
# table(clusters)
# 
# library(tidyverse)
#
# --- inputs assumed available ---
# clusters: named integer vector from cutree(hc, k=...) or cutree(hc, h=...)
# names(clusters) are variable names (columns of data_numeric)
# 
# # 1) Tidy long table
# cluster_members <- tibble(
#   variable = names(clusters),
#   cluster_id = as.integer(clusters)
# ) %>%
#   arrange(cluster_id, variable)
# 
# # 2) Define allowed prefixes (you can add more)
# prefixes <- c("hmz_ffq", "hmz_sdoh", "hmz_health")
# 
# # helper: does every var in 'vars' start with the given prefix (with boundary)?
# has_uniform_prefix <- function(vars, prefix) {
#   all(grepl(paste0("^", prefix, "([._]|$)"), vars))
# }
# 
# # 3) Assign cluster labels under your rules
# prefix_counts <- setNames(integer(length(prefixes)), prefixes)
# generic_count <- 0L
# 
# cluster_labels <- cluster_members %>%
#   group_by(cluster_id) %>%
#   summarise(vars = list(variable), n = n(), .groups = "drop") %>%
#   mutate(
#     # find a matching prefix that EVERY member has (if any)
#     matched_prefix = map_chr(vars, function(vs) {
#       mp <- prefixes[vapply(prefixes, function(p) has_uniform_prefix(vs, p), logical(1))]
#       if (length(mp) == 1) mp else NA_character_
#     }),
#     # build the label per your rules
#     label = pmap_chr(list(n, matched_prefix), function(n_members, mp) {
#       if (n_members == 1) {
#         NA_character_  # placeholder; will replace with the variable name later
#       } else if (!is.na(mp)) {
#         prefix_counts[mp] <<- prefix_counts[mp] + 1L
#         paste0(mp, "_", prefix_counts[mp])
#       } else {
#         generic_count <<- generic_count + 1L
#         paste0("cluster_", generic_count)
#       }
#     })
#   )
# 
# # 4) Merge labels back to each variable; singletons inherit their own name
# cluster_members_renamed <- cluster_members %>%
#   left_join(cluster_labels %>% select(cluster_id, vars, n, label), by = "cluster_id") %>%
#   mutate(
#     new_name = case_when(
#       n == 1 ~ variable,             # singleton -> keep original variable name
#       TRUE   ~ label                 # multi-member -> cluster label
#     )
#   ) %>%
#   select(variable, cluster_id, new_name) %>%
#   arrange(cluster_id, variable)
# 
# # View the mapping
# cluster_members_renamed
# 
# # unique meta-feature names (cluster labels + singletons)
# meta_names <- unique(cluster_members_renamed$new_name)
# 
# # function to build one meta-feature by name
# build_meta_feature <- function(nm) {
#   vars <- cluster_members_renamed %>%
#     filter(new_name == nm) %>%
#     pull(variable)
#   
#   M <- scale(as.matrix(data_numeric[, vars, drop = FALSE]))
#   if (ncol(M) == 1L) {
#     as.numeric(M[, 1])                         # singleton → scaled original
#   } else {
#     pc1 <- prcomp(M, center = FALSE, scale. = FALSE)$x[, 1]  # cluster → PC1
#     as.numeric(pc1)
#   }
# }
# 
# # construct meta-feature matrix (data.frame), columns named by new_name
# data_meta <- set_names(
#   map(meta_names, build_meta_feature),
#   meta_names
# ) %>% as_tibble()
# 
# dim(data_meta)   # n_samples x n_meta_features
# 
# cluster_dict <- cluster_members_renamed %>%
#   group_by(new_name) %>%
#   summarise(members = paste(variable, collapse = ", "), .groups = "drop")
# cluster_dict
#
# princomp expects a matrix/data.frame of numerics
# pca_meta <- princomp(as.data.frame(data_meta), cor = FALSE)  # already standardized inside each meta
# 
# # variance explained / scree
# summary(pca_meta)
# fviz_eig(pca_meta, addlabels = TRUE)
# 
# 
# # Show only the top 20 contributing variables on PCs 1 & 2
# fviz_pca_biplot(
#   pca_meta,
#   geom.ind = "point",
#   habillage = data$cohort,   # color by cohort
#   addEllipses = FALSE,
#   label = "var",             # show variable names (loadings)
#   select.var = list(contrib = 10),   # <— only top 20 loadings
#   repel = TRUE,
#   col.var = "black",
#   col.ind = "grey50"
# ) +
#   ggtitle("PCA biplot (top 10 variable loadings)")
# 
# 
# 
# 
# 
# 
# 
# 


