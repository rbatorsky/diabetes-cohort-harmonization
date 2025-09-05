LIB="/cluster/tufts/patralab/rbator01/R_libs/4.4.0/"
.libPaths(LIB)


library(tidyverse)
library(openxlsx)
library(ggpubr)
library(ggridges)
library(stringr)
library(data.table)

data = readRDS("r_pipeline/analysis/rds/harmonize_2cohort_healthsdohffq_20aug25_v1_rmmissing_50col_10row.rds")

tracker = read.xlsx("data/diabetes_status_wchange_2class_4aug25.xlsx")  %>%
  rename(diabetes = paste0("diabetes_v1")) %>%
  select(studyid, cohort, diabetes) %>%
  filter(!is.na(diabetes))

tracker$cohort = factor(tracker$cohort, levels=c(0,1))

data = data  %>%
  inner_join(tracker, by=c('studyid','cohort'))

data$diabetes = factor(data$diabetes, levels=c(0,1))

# Define metadata and features
metadata_cols <- c("cohort", "diabetes")
features_from_model = read.xlsx("r_pipeline/analysis/plots/relabel_features_plot_edit.xlsx") %>%
  filter(variable_name != "cohort")

features_from_model

feature_cols = unique(features_from_model$long_variable_name)
feature_cols = intersect(feature_cols, colnames(data))
feature_cols

# ---------- pretty-name lookup from features_from_model ----------
name_map <- features_from_model %>%
  transmute(feature = long_variable_name,
            pretty  = dplyr::coalesce(description.new, long_variable_name))

name_map
pretty_name <- function(x) {
  p <- name_map$pretty[match(x, name_map$feature)]
  ifelse(is.na(p), x, p)
}
# ---------------------------------------------------------------------

# ---------- NEW: decode lookup-coded variables BEFORE plotting/tests ----------
educ_map <- tibble(
  hmz_sdoh_hc_educ = as.character(c(1:5)),
  educ_label = c(
    "no schooling or <5th grade",
    "5th–8th grade",
    "9th–12th grade or GED",
    "some college or bachelor’s degree",
    "at least some graduate school"
  )
)

income_map <- tibble(
  hmz_sdoh_hi_total = as.character(c(0:9)),
  income_label = c(
    "$0–10,000",
    "$10,001–15,000",
    "$15,001–20,000",
    "$20,001–25,000",
    "$25,001–30,000",
    "$30,001–40,000",
    "$40,001–50,000",
    "$50,001–75,000",
    "$75,001–100,000",
    "more than $100,000"
  )
)

pob_map <- tibble(
  hmz_sdoh_mh_pob = as.character(c(1:3)),
  pob_label = c("PR", "USA", "Other")
)

str(data$hmz_sdoh_hc_educ)
data <- data %>%
  # join label columns
  left_join(educ_map,  by = "hmz_sdoh_hc_educ") %>%
  left_join(income_map, by = "hmz_sdoh_hi_total") %>%
  left_join(pob_map,    by = "hmz_sdoh_mh_pob") %>%
  # replace coded columns with labeled factors (keeps order from the maps)
  mutate(
    hmz_sdoh_hc_educ = factor(
      dplyr::coalesce(educ_label, as.character(hmz_sdoh_hc_educ)),
      levels = educ_map$educ_label
    ),
    hmz_sdoh_hi_total = factor(
      dplyr::coalesce(income_label, as.character(hmz_sdoh_hi_total)),
      levels = income_map$income_label
    ),
    hmz_sdoh_mh_pob = factor(
      dplyr::coalesce(pob_label, as.character(hmz_sdoh_mh_pob)),
      levels = pob_map$pob_label
    )
  ) %>%
  select(-educ_label, -income_label, -pob_label)
# ---------------------------------------------------------------------

results_list <- list()
feature_cols=c("hmz_health_lab_ldl","hmz_health_ant_avg_waist","hmz_sdoh_soc2a_time_s","hmz_ffq_aspt", "hmz_sdoh_hc", "hmz_sdoh_hc_educ",
               "hmz_sdoh_hi_total","hmz_sdoh_mh_pob","hmz_health_ant_bp_sys","hmz_sdoh_soc_activities")

library(scales)

nice_log1p_breaks <- function(x) {
  x <- x[is.finite(x) & !is.na(x) & x >= 0]
  if (!length(x)) return(0)
  mx <- max(x)
  minpos <- suppressWarnings(min(x[x > 0], na.rm = TRUE))
  if (!is.finite(minpos)) minpos <- 1
  lo <- max(0, floor(log10(minpos)))  # force at least 10^0 (1)
  hi <- ceiling(log10(mx))
  br <- c(0, 10^(lo:hi))
  unique(sort(br[br <= mx]))
}

feat = "hmz_sdoh_soc_activities"

for (feat in feature_cols) {
  message(feat)
  df_feat <- data %>%
    select(cohort, hmz_sdoh_age, diabetes, all_of(feat)) %>%
    filter(!is.na(.data[[feat]])) %>%
    mutate(cohort = ifelse(cohort == 0,"BPRHS","PROSPECT"))
  
  pr = df_feat %>% filter(cohort == "PROSPECT")
  bp = df_feat %>% filter(cohort == "BPRHS")
  
  if (nrow(pr) == 0 | nrow(bp) == 0) {
    results_list[[feat]] <- tibble(
      feature = feat,
      p_cohort = NA,
      stat_cohort = NA,
      p_diabetes_BPRHS = NA,
      stat_diabetes_BPRHS = NA,
      p_diabetes_PROSPECT = NA,
      stat_diabetes_PROSPECT = NA
    )
    next
  }
  
  values <- df_feat[[feat]]
  var_type <- if (is.numeric(values)) "numeric" else if (is.factor(values) || is.character(values)) "categorical" else "other"
  
  feat_pretty <- pretty_name(feat)

  if (var_type == "numeric") {
    library(scales)
    
    detect_log_scale <- function(values, min_orders = 2) {
      v_num <- suppressWarnings(as.numeric(values))
      v_pos <- v_num[v_num >= 0 & is.finite(v_num)]
      if (length(v_pos) < 2) return(FALSE)
      
      span <- log10(max(v_pos + 1, na.rm = TRUE)) - log10(min(v_pos + 1, na.rm = TRUE))
      if (is.finite(span) && span >= min_orders) return(TRUE)
      
      FALSE
    }
    
    cohort_test <- tryCatch(
      wilcox.test(values[df_feat$cohort == "BPRHS"],
                  values[df_feat$cohort == "PROSPECT"]),
      error = function(e) list(p.value = NA, statistic = NA)
    )
    
    bprhs <- df_feat %>% filter(cohort == "BPRHS")
    diab_test_bprhs <- tryCatch(
      wilcox.test(bprhs[[feat]][bprhs$diabetes == 0],
                  bprhs[[feat]][bprhs$diabetes == 1]),
      error = function(e) list(p.value = NA, statistic = NA)
    )
    
    prospect <- df_feat %>% filter(cohort == "PROSPECT")
    diab_test_prospect <- tryCatch(
      wilcox.test(prospect[[feat]][prospect$diabetes == 0],
                  prospect[[feat]][prospect$diabetes == 1]),
      error = function(e) list(p.value = NA, statistic = NA)
    )
    
    df_plot <- df_feat %>%
      mutate(cohort_db = paste0(cohort, "_", diabetes)) %>%
      pivot_longer(cols = c(cohort, cohort_db),
                   names_to = "comparison_type",
                   values_to = "group") %>%
      mutate(group = factor(group,
                            levels = c("BPRHS", "PROSPECT",
                                       "BPRHS_0", "BPRHS_1",
                                       "PROSPECT_0", "PROSPECT_1"))) %>%
      drop_na()
    
    p_cohort = cohort_test$p.value
    p_diabetes_BPRHS = diab_test_bprhs$p.value
    p_diabetes_PROSPECT = diab_test_prospect$p.value
    
    p_label_cohort <- paste0("p = ", signif(p_cohort, 3))
    p_label_diabetes <- paste0("p_BPRHS = ", signif(p_diabetes_BPRHS, 3),
                               "\n", "p_PROSPECT = ", signif(p_diabetes_PROSPECT, 3))
    
    y_max <- max(df_feat[[feat]], na.rm = TRUE)
    
    annotation_df <- tibble(
      comparison_type = c("cohort", "cohort_db"),
      x = c(1, 2),
      y = c(y_max, y_max),
      label = c(p_label_cohort, p_label_diabetes)
    )
    
    p <- ggviolin(df_plot, x = "group", y = feat,  fill = "group") +
      facet_wrap(~comparison_type, scales = "free_x") +
      ggtitle(feat_pretty) +
      ylab(feat_pretty) +   
      theme(axis.text.x = element_text(angle = 45, hjust = 1), size=10) 
    
    use_log <- detect_log_scale(df_feat[[feat]])
    
    if (use_log) {
      br <- log1p_breaks(df_feat[[feat]])
      p <- p +
        scale_y_continuous(
          trans  = scales::log1p_trans(),
          breaks = br,
          labels = label_scientific(digits = 2)  # 0, 1e0, 1e1, 1e2...
        )    
      }
  
    p <- p +
      theme(
        text = element_text(size = 12)  # increase all text
      )
    
    show(p)
  
    
    ridge_df <- dplyr::bind_rows(
      df_feat %>%
        transmute(panel = "BPRHS vs PROSPECT",
                  group2 = cohort,                                # BPRHS, PROSPECT
                  value  = .data[[feat]]),
      
      df_feat %>%
        filter(cohort == "BPRHS") %>%
        transmute(panel = "BPRHS (0 vs 1)",
                  group2 = forcats::fct_recode(factor(diabetes),
                                               "diab_0" = "0", "diab_1" = "1"),
                  value  = .data[[feat]]),
      
      df_feat %>%
        filter(cohort == "PROSPECT") %>%
        transmute(panel = "PROSPECT (0 vs 1)",
                  group2 = forcats::fct_recode(factor(diabetes),
                                               "diab_0" = "0", "diab_1" = "1"),
                  value  = .data[[feat]])
    ) %>%
      mutate(
        panel = factor(panel, levels = c("BPRHS vs PROSPECT",
                                         "BPRHS (0 vs 1)",
                                         "PROSPECT (0 vs 1)"))
      )
    
    # Overlapping transparent ridges (two per panel)
    p1 <- ggplot(ridge_df, aes(x = value, y = panel, fill = group2, color = group2)) +
      geom_density_ridges(
        position       = "identity",   # <-- overlap at the same y
        scale          = 0.95,
        alpha          = 0.35,         # <-- transparency
        rel_min_height = 0.001,
        size           = 0.3
      ) +
      labs(title = feat_pretty, x = feat_pretty, y = NULL) +
      theme_minimal() +
      theme(axis.text.x = element_text(angle = 0, hjust = 0.5))
    
    # Log1p axis with scientific labels; skip 1e-1, 1e-2, ...
    if (use_log) {
      br <- nice_log1p_breaks(ridge_df$value)
      p1 <- p1 +
        scale_x_continuous(
          trans  = scales::log1p_trans(),
          breaks = br,
          labels = scales::label_scientific(digits = 2)
        )
    }
    
    p1 <- p1 +
      theme(
        text = element_text(size = 12)  # increase all text
      )
    
    show(p1)
    
    outdir = "r_pipeline/analysis/select_feature_plots/"
    if (!dir.exists(outdir)) dir.create(outdir, recursive = TRUE)
    
    if(!is.na(p_cohort) & p_cohort < 0.05){
      ggsave(filename = paste0(outdir, feat, "_vln_age38_kcal_filter_sig.pdf"),
             plot = p, width = 10, height = 6)
      ggsave(filename = paste0(outdir, feat, "_hist_age38_kcal_filter_sig.pdf"),
             plot = p1, width = 10, height = 6)
    } else {
      ggsave(filename = paste0(outdir, feat, "_vln_age38_kcal_filter.pdf"),
             plot = p, width = 10, height = 6)
      ggsave(filename = paste0(outdir, feat, "_hist_age38_kcal_filter.pdf"),
             plot = p1, width = 10, height = 6)
    }
    
  } else if (var_type == "categorical") {
    
    cohort_table <- table(df_feat$cohort, values)
    cohort_test <- tryCatch(chisq.test(cohort_table),
                            error = function(e) list(p.value = NA, statistic = NA))
    
    bprhs <- df_feat %>% filter(cohort == "BPRHS")
    diab_table_bprhs <- table(bprhs$diabetes, bprhs[[feat]])
    diab_test_bprhs <- tryCatch(chisq.test(diab_table_bprhs),
                                error = function(e) list(p.value = NA, statistic = NA))
    
    prospect <- df_feat %>% filter(cohort == "PROSPECT")
    diab_table_prospect <- table(prospect$diabetes, prospect[[feat]])
    diab_test_prospect <- tryCatch(chisq.test(diab_table_prospect),
                                   error = function(e) list(p.value = NA, statistic = NA))
    
    df_plot <- df_feat %>%
      mutate(cohort_db = factor(paste0(cohort, "_", diabetes),
                                levels=c("BPRHS_0", "BPRHS_1", "PROSPECT_0", "PROSPECT_1"))) %>%
      pivot_longer(cols = c(cohort, cohort_db),
                   names_to = "comparison_type",
                   values_to = "group") %>%
      drop_na()
    
    p_cohort = cohort_test$p.value
    p_diabetes_BPRHS = diab_test_bprhs$p.value
    p_diabetes_PROSPECT = diab_test_prospect$p.value
    
    p_label_cohort <- paste0("p = ", signif(p_cohort, 3))
    p_label_diabetes <- paste0("p_BPRHS = ", signif(p_diabetes_BPRHS, 3),
                               "\n", "p_PROSPECT = ", signif(p_diabetes_PROSPECT, 3))
    
    annotation_df <- tibble(
      comparison_type = c("cohort", "cohort_db"),
      x = c(1, 2),
      y = c(1, 1),
      label = c(p_label_cohort, p_label_diabetes)
    )
    
    p <- ggplot(df_plot, aes(x = group, fill = .data[[feat]])) +
      geom_bar(position = "fill") +
      scale_y_continuous(labels = scales::percent) +
      facet_wrap(~comparison_type, scales = "free_x") +
      labs(x = "Group", y = "Proportion",
           fill = feat_pretty, title = feat_pretty) +   # <-- NEW: pretty legend/title
      theme_minimal() 
    
    p <- p +
      theme(
        text = element_text(size = 12)  # increase all text
      )
    show(p)
    
    outdir = "r_pipeline/analysis/select_feature_plots/"
    if (!dir.exists(outdir)) dir.create(outdir, recursive = TRUE)
    
    if(!is.na(p_cohort) & p_cohort < 0.05){
      ggsave(filename = paste0(outdir, feat, "_barplot_age38_kcal_filter_sig.pdf"),
             plot = p, width = 10, height = 6)
    } else {
      ggsave(filename = paste0(outdir, feat, "_barplot_age38_kcal_filter.pdf"),
             plot = p, width = 10, height = 6)
    }
    
  } else {
    cohort_test <- diab_test_bprhs <- diab_test_prospect <- list(p.value = NA, statistic = NA)
  }
  
  results_list[[feat]] <- tibble(
    feature = feat,
    p_cohort = cohort_test$p.value,
    stat_cohort = cohort_test$statistic,
    p_diabetes_BPRHS = diab_test_bprhs$p.value,
    stat_diabetes_BPRHS = diab_test_bprhs$statistic,
    p_diabetes_PROSPECT = diab_test_prospect$p.value,
    stat_diabetes_PROSPECT = diab_test_prospect$statistic
  )
}

# Combine into one data frame
results_df <- bind_rows(results_list)

results_df = results_df %>%
  mutate(category = str_extract(feature, "(?<=hmz_)[^_]+")) %>%
  select(feature, category, everything())

fwrite(results_df, "r_pipeline/analysis/select_feature_plots/results_age38_kcal_filter_20aug25.tsv", sep="\t",quote=F)






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
library(ggridges)

filter=dplyr::filter
rename=dplyr::rename
select=dplyr::select
setwd("/cluster/tufts/patralab/rbator01/aiml_ordovas_project/")
library(fastDummies)


# do the same with the prepped data -----
#data = readRDS("r_pipeline/analysis/rds/harmonize_2cohort_healthsdohffq_23apr25_v1_rmmissing_50col_10row.rds")
#data = readRDS("r_pipeline/analysis/rds/harmonize_2cohort_healthsdohffq_24apr25_v1_rmmissing_50col_10row_preproc_for_eda.rds")
#data = readRDS("r_pipeline/analysis/rds/harmonize_2cohort_healthsdohffq_18aug25_v1_rmmissing_50col_10row_preproc_for_eda.rds")
data = readRDS("r_pipeline/analysis/rds/harmonize_2cohort_healthsdohffq_20aug25_v1_rmmissing_50col_10row.rds")

tracker = read.xlsx("data/diabetes_status_wchange_2class_4aug25.xlsx")  %>%
  rename(diabetes = paste0("diabetes_v1")) %>%
  select(studyid, cohort, diabetes) %>%
  filter(!is.na(diabetes))

tracker$cohort = factor(tracker$cohort, levels=c(0,1))

data = data  %>%
  inner_join(tracker, by=c('studyid','cohort'))

data$diabetes = factor(data$diabetes, levels=c(0,1))

# Define metadata and features
metadata_cols <- c("cohort", "diabetes")
features_from_model = read.xlsx("r_pipeline/analysis/plots/relabel_features_plot_edit.xlsx")
colnames(features_from_model)
feature_cols = unique(features_from_model$long_variable_name)

#feature_cols <- setdiff(names(data), metadata_cols)
results_list <- list()
#feature_cols = c("hmz_health_fh_diabetes","hmz_sdoh_assault")

feature_cols = intersect(feature_cols, colnames(data))

head(features_from_model)
### figure out where to add this stuff ###

# Lookup tables
educ_map <- tibble(
  hc_educ = 1:5,
  educ_label = c(
    "no schooling or <5th grade",
    "5th–8th grade",
    "9th–12th grade or GED",
    "some college or bachelor’s degree",
    "at least some graduate school"
  )
)

income_map <- tibble(
  hi_total = 0:9,
  income_label = c(
    "$0–10,000",
    "$10,001–15,000",
    "$15,001–20,000",
    "$20,001–25,000",
    "$25,001–30,000",
    "$30,001–40,000",
    "$40,001–50,000",
    "$50,001–75,000",
    "$75,001–100,000",
    "more than $100,000"
  )
)

pob_map <- tibble(
  mh_pob = 1:3,
  pob_label = c("PR", "USA", "Other")
)

# Example: recode into a new dataframe
data_recoded <- data %>%
  left_join(educ_map, by = "hc_educ") %>%
  left_join(income_map, by = "hi_total") %>%
  left_join(pob_map, by = "mh_pob")

######

for (feat in feature_cols) {
  print(feat)
  df_feat <- data %>%
    select(cohort, hmz_sdoh_age, diabetes, all_of(feat)) %>%
    filter(!is.na(.data[[feat]])) %>%
    mutate(cohort = ifelse(cohort == 0,"BPRHS","PROSPECT"))
  
  pr = df_feat %>%
    filter(cohort == "PROSPECT")
  
  bp = df_feat %>%
    filter(cohort == "BPRHS")
  
  
  if (nrow(pr) == 0 | nrow(bp) == 0) {
    results_list[[feat]] <- tibble(
      feature = feat,
      p_cohort = NA,
      stat_cohort = NA,
      p_diabetes_BPRHS = NA,
      stat_diabetes_BPRHS = NA,
      p_diabetes_PROSPECT = NA,
      stat_diabetes_PROSPECT = NA
    )
    next
  }
  
  values <- df_feat[[feat]]
  
  # Identify variable type
  var_type <- if (is.numeric(values)) {
    "numeric"
  } else if (is.factor(values) || is.character(values)) {
    "categorical"
  } else {
    "other"
  }
  
  var_type
  
  if (var_type == "numeric") {
    # Wilcoxon tests for numeric variables
    cohort_test <- tryCatch(
      wilcox.test(values[df_feat$cohort == "BPRHS"],
                  values[df_feat$cohort == "PROSPECT"]),
      error = function(e) list(p.value = NA, statistic = NA)
    )
    
    bprhs <- df_feat %>% 
      filter(cohort == "BPRHS")
    
    diab_test_bprhs <- tryCatch(
      wilcox.test(bprhs[[feat]][bprhs$diabetes == 0],
                  bprhs[[feat]][bprhs$diabetes == 1]),
      error = function(e) list(p.value = NA, statistic = NA)
    )
    
    prospect <- df_feat %>% filter(cohort == "PROSPECT")
    diab_test_prospect <- tryCatch(
      wilcox.test(prospect[[feat]][prospect$diabetes == 0],
                  prospect[[feat]][prospect$diabetes == 1]),
      error = function(e) list(p.value = NA, statistic = NA)
    )
  
    # Reshape data for plotting with panel type
    df_plot <- df_feat %>%
      mutate(cohort_db = paste0(cohort, "_", diabetes)) %>%
      pivot_longer(cols = c(cohort, cohort_db),
                   names_to = "comparison_type",
                   values_to = "group") %>%
      mutate(group = factor(group, levels = c("BPRHS", "PROSPECT", "BPRHS_0", "BPRHS_1", "PROSPECT_0", "PROSPECT_1"))) %>%
      drop_na()
    
    comparisons_list <- list(
      c("BPRHS", "PROSPECT"),
      c("BPRHS_0", "BPRHS_1"),
      c("PROSPECT_0", "PROSPECT_1")
    )
    
    # check if sig
    p_cohort = cohort_test$p.value
    p_diabetes_BPRHS = diab_test_bprhs$p.value
    p_diabetes_PROSPECT = diab_test_prospect$p.value
    
    p_label_cohort <- paste0("p = ", signif(p_cohort, 3))
    p_label_diabetes <- paste0(
      "p_BPRHS = ", signif(p_diabetes_BPRHS, 3), 
      "\n", 
      "p_PROSPECT = ", signif(p_diabetes_PROSPECT, 3)
    )
    
    y_max <- max(df_feat[[feat]], na.rm = TRUE)
    
    # Format your p-values as text
    annotation_df <- tibble(
      comparison_type = c("cohort", "cohort_db"),
      x = c(1, 2),           # Adjust X position if needed
      y = c(y_max, y_max),      # Adjust Y position if needed
      label = c(p_label_cohort, p_label_diabetes)
    )
    
    p <- ggviolin(df_plot, x = "group", y = feat, add = "boxplot", fill = "group") +
      facet_wrap(~comparison_type, scales = "free_x") +
      ggtitle(feat) +
      theme(axis.text.x = element_text(angle = 45, hjust = 1)) +
      geom_text(data = annotation_df, 
                aes(x = x, y = y, label = label), 
                inherit.aes = FALSE, 
                size = 3.5)
    
    show(p)
    
    # 2) Dot/strip version (no box), if you prefer
    p1 <- ggplot(df_plot, aes(x = .data[[feat]], y = group, fill = group)) +
      geom_density_ridges(
        stat = "binline",      # <-- binned ridges for discrete data
        binwidth = 1,          # or use `bins = length(unique(df_plot[[feat]]))`
        scale = 0.95,
        alpha = 0.6,
        draw_baseline = FALSE
      ) +
      facet_wrap(~comparison_type, scales = "free_y") +
      scale_x_continuous(breaks = sort(unique(df_plot[[feat]]))) +
      labs(title = feat, x = feat, y = NULL) +
      theme_minimal() +
      theme(axis.text.x = element_text(angle = 0, hjust = 0.5))
    
    print(p1)
    
    outdir = "r_pipeline/analysis/select_feature_plots/"
    
    # Create if it does not exist
    if (!dir.exists(outdir)) {
      dir.create(outdir, recursive = TRUE)
    }
    
    if(!is.na(p_cohort) & p_cohort < 0.05){
      ggsave(
        filename = paste0(outdir, feat, "_vln_age38_kcal_filter_sig.pdf"),
        plot = p, width = 10, height = 6
      )
      ggsave(
        filename = paste0(outdir, feat, "_hist_age38_kcal_filter_sig.pdf"),
        plot = p1, width = 10, height = 6
      )
    }else{
      ggsave(
        filename = paste0(outdir, feat, "_vln_age38_kcal_filter.pdf"),
        plot = p, width = 10, height = 6
      )
      ggsave(
        filename = paste0(outdir, feat, "_hist_age38_kcal_filter.pdf"),
        plot = p1, width = 10, height = 6
      )
    }
  
    
    } else if (var_type == "categorical") {
    # Chi-squared test for categorical variables
    cohort_table <- table(df_feat$cohort, values)
    cohort_test <- tryCatch(
      chisq.test(cohort_table),
      error = function(e) list(p.value = NA, statistic = NA)
    )
    
    bprhs <- df_feat %>% filter(cohort == "BPRHS")
    diab_table_bprhs <- table(bprhs$diabetes, bprhs[[feat]])
    diab_test_bprhs <- tryCatch(
      chisq.test(diab_table_bprhs),
      error = function(e) list(p.value = NA, statistic = NA)
    )
    
    prospect <- df_feat %>% filter(cohort == "PROSPECT")
    diab_table_prospect <- table(prospect$diabetes, prospect[[feat]])
    diab_test_prospect <- tryCatch(
      chisq.test(diab_table_prospect),
      error = function(e) list(p.value = NA, statistic = NA)
    )
    
    # Reshape data for plotting with panel type
    df_plot <- df_feat %>%
      mutate(cohort_db = factor(paste0(cohort, "_", diabetes), levels=c("BPRHS_0", "BPRHS_1", "PROSPECT_0", "PROSPECT_1")))%>%
      pivot_longer(cols = c(cohort, cohort_db),
                   names_to = "comparison_type",
                   values_to = "group") %>%
      drop_na() 
    
    
    
    # check if sig
    p_cohort = cohort_test$p.value
    p_diabetes_BPRHS = diab_test_bprhs$p.value
    p_diabetes_PROSPECT = diab_test_prospect$p.value
    
    
    p_label_cohort <- paste0("p = ", signif(p_cohort, 3))
    p_label_diabetes <- paste0(
      "p_BPRHS = ", signif(p_diabetes_BPRHS, 3), 
      "\n", 
      "p_PROSPECT = ", signif(p_diabetes_PROSPECT, 3)
    )
    
    # Format your p-values as text
    annotation_df <- tibble(
      comparison_type = c("cohort", "cohort_db"),
      x = c(1, 2),           # Adjust X position if needed
      y = c(1, 1),      # Adjust Y position if needed
      label = c(p_label_cohort, p_label_diabetes)
    )
    
    p <- ggplot(df_plot, aes(x = group, fill = .data[[feat]])) +
      geom_bar(position = "fill") +
      scale_y_continuous(labels = scales::percent) +
      facet_wrap(~comparison_type, scales = "free_x") +
      labs(x = "Group", y = "Proportion", fill = feat, title = feat) +
      theme_minimal() +
      theme(axis.text.x = element_text(angle = 45, hjust = 1)) +
      geom_text(data = annotation_df, 
                aes(x = x, y = y, label = label), 
                inherit.aes = FALSE, 
                size = 3.5)
    show(p)
    
    if(!is.na(p_cohort) & p_cohort < 0.05){
      
      ggsave(
        filename = paste0("r_pipeline/analysis/select_feature_plots/", feat, "_barplot_age38_kcal_filter_sig.pdf"),
        plot = p, width = 10, height = 6
      )
    }else{
      ggsave(
        filename = paste0("r_pipeline/analysis/select_feature_plots/", feat, "_barplot_age38_kcal_filter.pdf"),
        plot = p, width = 10, height = 6
      )
    }
    
  } else {
    cohort_test <- diab_test_bprhs <- diab_test_prospect <- list(p.value = NA, statistic = NA)
  }
  
  # Store results
  results_list[[feat]] <- tibble(
    feature = feat,
    p_cohort = cohort_test$p.value,
    stat_cohort = cohort_test$statistic,
    p_diabetes_BPRHS = diab_test_bprhs$p.value,
    stat_diabetes_BPRHS = diab_test_bprhs$statistic,
    p_diabetes_PROSPECT = diab_test_prospect$p.value,
    stat_diabetes_PROSPECT = diab_test_prospect$statistic
  )
  
}

# Combine into one data frame
results_df <- bind_rows(results_list)

library(data.table)

results_df = results_df %>%
  mutate(category = str_extract(feature, "(?<=hmz_)[^_]+")) %>%
  select(feature, category, everything())

fwrite(results_df, "r_pipeline/analysis/select_feature_plots/results_age38_kcal_filter_20aug25.tsv", sep="\t",quote=F)

# make specific plots for paper -------



