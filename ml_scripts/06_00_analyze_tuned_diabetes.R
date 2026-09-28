LIB="/cluster/tufts/patralab/rbator01/R_libs/4.4.0/"
.libPaths(LIB)

source("utils.R")

pkgs <- c(
  "openxlsx",
  "dplyr", "tidyr", "tibble", "purrr",
  "ggplot2", "scales",
  "stringr",
  "forcats", "tidytext"
)
invisible(lapply(pkgs, quiet_library))

OUT_RESULTS <- "../../analysis/"
PLOT_DIR    <- "../../analysis/plots"
RDS1 = "../../analysis/harmonize_2cohort_healthsdohffq_v1_rmmissing_50col_10row_preproc_for_eda.rds"
TRK  = "../../data/hmz_data/diabetes_tracker_2class_24feb26.xlsx"

dir.create(PLOT_DIR, showWarnings = FALSE, recursive = TRUE)

nclass <- 2
outvar <- "diabetes"   
seeds <- 1:10
data_string <- "all"
visit <- "v1"
cohort <- "none"
importance <- "boruta"
cross_cohort_val <- 0
regress_batch <- 0
date_tag <- "23feb26"
common_grid <- seq(0, 1, length.out = 1001)  # dense grid for AUC

# --- small helpers ---
extract_roc_df <- function(obj) {
  # yardstick roc_curve tibble OR pROC::roc
  if (is.data.frame(obj) && all(c("specificity","sensitivity") %in% names(obj))) {
    tibble(specificity = obj[["specificity"]], sensitivity = obj[["sensitivity"]])
  } else if (inherits(obj, "roc")) {
    tibble(specificity = obj$specificities, sensitivity = obj$sensitivities)
  } else {
    stop("Unknown ROC format: need {specificity,sensitivity} columns or pROC::roc")
  }
}

interp_to_grid <- function(df, xgrid) {
  df <- df %>%
    dplyr::filter(is.finite(specificity), is.finite(sensitivity)) %>%
    dplyr::transmute(
      fpr = pmin(pmax(1 - specificity, 0), 1),
      tpr = pmin(pmax(sensitivity, 0), 1)
    ) %>%
    dplyr::arrange(fpr) %>%
    dplyr::distinct(fpr, .keep_all = TRUE)
  
  if (nrow(df) < 2 || dplyr::n_distinct(df$fpr) < 2) {
    stop("Degenerate ROC: fewer than 2 unique FPR points; cannot interpolate.")
  }
  
  ax <- approx(x = df$fpr, y = df$tpr, xout = xgrid, method = "linear", rule = 2)
  tibble(fpr = ax$x, tpr = ax$y)
}

trapz <- function(x, y) {
  o <- order(x)
  x <- x[o]; y <- y[o]
  sum(diff(x) * (head(y, -1) + tail(y, -1)) / 2)
}


# analyze data (no age filter) ---- 
data = readRDS(RDS1)
head(data)

## Count variables ----
# all_vars <- colnames(data)
# 
# # Identify variables by prefix
# health_vars <- all_vars[str_starts(all_vars, "hmz_health")]
# sdoh_vars   <- all_vars[str_starts(all_vars, "hmz_sdoh")]
# ffq_vars    <- all_vars[str_starts(all_vars, "hmz_ffq")]
# 
# # Count and clean prefixes
# tally_df <- tibble(
#   group = c("health", "sdoh", "ffq"),
#   n_vars = c(length(health_vars), length(sdoh_vars), length(ffq_vars))
# ) %>%
#   mutate(group = toupper(group))
#   
# # If you want to list the variable names without the prefix:
# list_df <- tibble(
#   variable = c(str_remove(health_vars, "^hmz_"),
#                str_remove(sdoh_vars, "^hmz_"),
#                str_remove(ffq_vars, "^hmz_")),
#   group = c(rep("health", length(health_vars)),
#             rep("sdoh", length(sdoh_vars)),
#             rep("ffq", length(ffq_vars)))
# )
# 
# # View tallies
# # Define custom colors
# custom_colors <- c(
#   "FFQ" = "#7BAFD4",     # muted blue
#   "HEALTH" = "#88C27C",  # muted green
#   "SDOH" = "#F4A259"     # muted orange
# )
# 
# tally_df
# 
# # Create barplot
# p = ggplot(tally_df, aes(x = group, y = n_vars, fill = group)) +
#   geom_bar(stat = "identity") +
#   scale_fill_manual(values = custom_colors, guide = "none") +  # no legend
#   labs(
#     title = "Filtered V1 Variables",
#     x = "",
#     y = "Number of Variables"
#   ) +
#   theme_minimal()
# 
# print(p)
# ggsave(p, filename = "../../analysis/plots/number_of_features_for_mlmodel_17nov25.pdf", height=4, width = 3)


# read in all the ROC curves ----
ow <- options(warn = 0)  

nclass <- 2
outvar <- "diabetes"   
seeds <- 1:10
data_string <- "all"
visit <- "v1"
cohort <- "none"
importance <- "boruta"
cross_cohort_val <- 0
regress_batch <- 0
date_tag <- "23feb26"
common_grid <- seq(0, 1, length.out = 1001)  # dense grid for AUC
OUT_RESULTS  <- "../../analysis/"

# ---- Combinations needed for plots ----

# Plot 1: v1, xcv=0, rb=0, filter_cohort = none/0/1
blk1 <- expand.grid(
  year            = "v1",
  filter_cohort   = c("0", "1", "none"),
  cross_cohort_val = 0,
  regress_batch   = 0,
  seed            = seeds,
  KEEP.OUT.ATTRS  = FALSE,
  stringsAsFactors = FALSE
)

# Plot 3: v2, xcv=0, rb=0, filter_cohort = none/0/1
blk2 <- expand.grid(
  year            = "v2",
  filter_cohort   = c("0", "1", "none"),
  cross_cohort_val = 0,
  regress_batch   = 0,
  seed            = seeds,
  KEEP.OUT.ATTRS  = FALSE,
  stringsAsFactors = FALSE
)

# Plot 2: v1, filter_cohort=none, xcv=0:4, rb=0 (baseline + 4 xcohort strategies)
blk3 <- expand.grid(
  year            = "v1",
  filter_cohort   = "none",
  cross_cohort_val = 0:4,
  regress_batch   = 0,
  seed            = seeds,
  KEEP.OUT.ATTRS  = FALSE,
  stringsAsFactors = FALSE
)

# Plot 4: v1, filter_cohort=none, xcv=0, rb=0/1
blk4 <- expand.grid(
  year            = "v1",
  filter_cohort   = "none",
  cross_cohort_val = 0,
  regress_batch   = c(0, 1),
  seed            = seeds,
  KEEP.OUT.ATTRS  = FALSE,
  stringsAsFactors = FALSE
)

param_df <- dplyr::bind_rows(blk1, blk2, blk3, blk4) %>%
  dplyr::distinct()  # avoid duplicates

roc_list <- list()
found <- 0L; missing <- 0L; kept <- 0L

for (i in seq_len(nrow(param_df))) {
  year <- param_df$year[i]
  filt <- param_df$filter_cohort[i]
  xcv  <- param_df$cross_cohort_val[i]
  rb   <- param_df$regress_batch[i]
  seed <- param_df$seed[i]
  
  save_string <- paste0(
    data_string, "_", outvar, "_", year,
    "_class", nclass,
    "_filter", filt,
    "_seed", seed,
    "_tune_caseweights_boruta",
    "_xcohortval_", xcv,
    "_resbatch_", rb,
    "_", date_tag
  )
  
  file_path_rds <- file.path(OUT_RESULTS, paste0(save_string, "_roc.rds"))
  
  if (!file.exists(file_path_rds)) {
    missing <- missing + 1L
    message("ROC not found: ", file_path_rds)
    next
  }
  
  found <- found + 1L
  roc   <- readRDS(file_path_rds)
  
  interp <- approx(1 - roc$specificity, roc$sensitivity, xout = common_grid)
  
  kept <- kept + 1L
  roc_list[[kept]] <- data.frame(
    specificity      = 1 - interp$x,
    sensitivity      = interp$y,
    filter_cohort    = filt,
    year             = year,
    seed             = seed,
    cross_cohort_val = xcv,
    regress_batch    = rb,
    stringsAsFactors = FALSE
  )
}

cat(sprintf("Expected=%d, Found=%d, Missing=%d, Interpolated=%d\n",
            nrow(param_df), found, missing, kept))
stopifnot(length(roc_list) > 0)

roc_combined <- dplyr::bind_rows(roc_list) %>%
  dplyr::mutate(
    filter_cohort = dplyr::recode(
      filter_cohort,
      "0"    = "BPRHS",
      "1"    = "PROSPECT",
      "none" = "Both cohorts"
    )
  )


# AUC helpers & per-seed AUC table -----------------

roc_to_auc <- function(df, group_vars) {
  df %>%
    dplyr::mutate(fpr = 1 - specificity) %>%
    dplyr::group_by(dplyr::across(all_of(group_vars))) %>%
    dplyr::arrange(fpr, .by_group = TRUE) %>%
    dplyr::summarise(
      auc = trapz(fpr, sensitivity),
      .groups = "drop"
    )
}

auc_by_seed <- roc_to_auc(
  roc_combined,
  c("year", "filter_cohort", "cross_cohort_val", "regress_batch", "seed")
)


summarize_roc <- function(df, by_vars = c("curve")) {
  df %>%
    dplyr::group_by(across(all_of(c(by_vars, "specificity")))) %>%
    dplyr::summarize(
      mean_sens = mean(sensitivity, na.rm = TRUE),
      sd_sens   = sd(sensitivity, na.rm = TRUE),
      .groups = "drop"
    )
}

# ================================
# PLOT 1: v1, four curves (Both, BPRHS, PROSPECT), xcv=0, rb=0
# ================================

plot1_df <- roc_combined %>%
  dplyr::filter(
    year == "v1",
    regress_batch == 0,
    # keep:
    #  - random within-cohort runs (xcv = 0) for all 3 cohorts
    #  - cross-cohort run "Train Both → Test PROSPECT" (xcv = 1, filter_cohort == "Both cohorts")
    (
      cross_cohort_val == 0 & filter_cohort %in% c("Both cohorts", "BPRHS", "PROSPECT")
    ) |
      (
        cross_cohort_val == 1 & filter_cohort == "Both cohorts"
      )
  ) %>%
  dplyr::mutate(
    curve = dplyr::case_when(
      cross_cohort_val == 0 & filter_cohort == "Both cohorts" ~ "Both cohorts",
      cross_cohort_val == 0 & filter_cohort == "BPRHS"        ~ "BPRHS",
      cross_cohort_val == 0 & filter_cohort == "PROSPECT"     ~ "PROSPECT",
      cross_cohort_val == 1 & filter_cohort == "Both cohorts" ~ "Train Both \u2192 Test PROSPECT",
      TRUE ~ NA_character_
    ),
    curve = factor(
      curve,
      levels = c(
        "Both cohorts",
        "BPRHS",
        "PROSPECT",
        "Train Both \u2192 Test PROSPECT"
      )
    )
  ) %>%
  dplyr::filter(!is.na(curve))

sum1 <- summarize_roc(plot1_df, by_vars = "curve")

# Shared colors for the 4 regimes (ROC + barplots)
roc_colors <- c(
  "Both cohorts"           = "#F8766D",
  "BPRHS"                           = "#7CAE00",
  "PROSPECT"                        = "#00BFC4",
  "Train Both \u2192 Test PROSPECT" = "#C77CFF"
)

p1 <- ggplot(sum1, aes(x = 1 - specificity, y = mean_sens, color = curve)) +
  geom_line(linewidth = 1.2) +
  geom_ribbon(
    aes(ymin = mean_sens - sd_sens, ymax = mean_sens + sd_sens, fill = curve),
    alpha = 0.2, linewidth = 0
  ) +  geom_abline(linetype = "dashed", color = "gray50") +
  coord_equal(xlim = c(0, 1), ylim = c(0, 1), expand = FALSE) +
  labs(
    title = "ROC (Visit 1, xcohortval=0, rb=0)",
    x = "1 - Specificity",
    y = "Sensitivity",
    color = "Regime", fill = "Regime"
  ) +
  scale_color_manual(values = roc_colors, drop = FALSE) +
  scale_fill_manual(values = roc_colors, drop = FALSE) +
  theme_minimal()

print(p1)
ggsave(
  p1,
  filename = "../../analysis/plots/roc_v1_three_cohorts_plus_trainBoth_testPROSPECT_23feb26.pdf",
  width = 6.5, height = 4.8
)

# lighter error bars
p1_light <- ggplot(sum1, aes(x = 1 - specificity, y = mean_sens, color = curve)) +
  geom_ribbon(
    aes(
      ymin = mean_sens - sd_sens,
      ymax = mean_sens + sd_sens,
      fill = curve
    ),
    alpha = 0.08,        # << much lighter
    linewidth = 0
  ) +
  geom_line(linewidth = 1.3) +
  geom_abline(linetype = "dashed", color = "gray60") +
  coord_equal(xlim = c(0, 1), ylim = c(0, 1), expand = FALSE) +
  labs(
    title = "ROC (Visit 1, xcohortval=0, rb=0)",
    x = "1 - Specificity",
    y = "Sensitivity",
    color = "Regime"
  ) +
  scale_color_manual(values = roc_colors, drop = FALSE) +
  scale_fill_manual(values = roc_colors, guide = "none") +
  theme_minimal()

p1_light

ggsave(
  p1_light,
  filename = "../../analysis/plots/roc_v1_three_cohorts_plus_trainBoth_testPROSPECT_light_23feb26.pdf",
  width = 6.5, height = 4.8
)



# ================================
# PLOT 2: v1, Both cohorts, xcohortval=0:4 (baseline + 4 strategies), rb=0
# ================================

plot2_df <- roc_combined %>%
  dplyr::filter(
    year == "v1",
    filter_cohort == "Both cohorts",
    regress_batch == 0,
    cross_cohort_val %in% 0:4
  ) %>%
  dplyr::mutate(
    curve = dplyr::case_when(
      cross_cohort_val == 0 ~ "Both cohorts",
      cross_cohort_val == 1 ~ "Train Both → Test PROSPECT",
      cross_cohort_val == 2 ~ "Train Both → Test BPRHS",
      cross_cohort_val == 3 ~ "Train PROSPECT → Test BPRHS",
      cross_cohort_val == 4 ~ "Train BPRHS → Test PROSPECT",
      TRUE ~ NA_character_
    ),
    curve = factor(curve,
                   levels = c(
                     "Random pooled (Train=Test Both)",
                     "Train Both → Test PROSPECT",
                     "Train Both → Test BPRHS",
                     "Train PROSPECT → Test BPRHS",
                     "Train BPRHS → Test PROSPECT"
                   ))
  ) %>%
  dplyr::filter(!is.na(curve))

sum2 <- summarize_roc(plot2_df, by_vars = "curve")

p2 <- ggplot(sum2, aes(x = 1 - specificity, y = mean_sens, color = curve)) +
  geom_line(linewidth = 1.2) +
  geom_ribbon(
    aes(ymin = mean_sens - sd_sens, ymax = mean_sens + sd_sens, fill = curve),
    alpha = 0.2, linewidth = 0
  ) +
  geom_abline(linetype = "dashed", color = "gray50") +
  coord_equal(xlim = c(0, 1), ylim = c(0, 1), expand = FALSE) +
  labs(
    title = "Cross-cohort ROC",
    x = "1 - Specificity",
    y = "Sensitivity",
    color = "Strategy", fill = "Strategy"
  ) +
  theme_minimal()

print(p2)

ggsave(
  p2,
  filename = "../../analysis/plots/roc_v1_xcohort_five_curves_rb0_23feb26.pdf",
  width = 6.5, height = 4.8
)

# ================================
# PLOT 3: v2, three curves (Both, BPRHS, PROSPECT), xcv=0, rb=0
# ================================

unique(roc_combined$year)

plot3_df <- roc_combined %>%
  dplyr::filter(
    cross_cohort_val == 0,
    regress_batch == 0,
    filter_cohort == "Both cohorts"
  ) %>%
  dplyr::mutate(curve = factor(
    year,
    levels = c("v1","v2")
  ))

sum3 <- summarize_roc(plot3_df, by_vars = "curve")

p3 <- ggplot(sum3, aes(x = 1 - specificity, y = mean_sens, color = curve)) +
  geom_line(linewidth = 1.2) +
  geom_ribbon(
    aes(ymin = mean_sens - sd_sens, ymax = mean_sens + sd_sens, fill = curve),
    alpha = 0.2, linewidth = 0
  ) +
  geom_abline(linetype = "dashed", color = "gray50") +
  coord_equal(xlim = c(0, 1), ylim = c(0, 1), expand = FALSE) +
  labs(
    title = "Visit comparison, Both Cohorts",
    x = "1 - Specificity",
    y = "Sensitivity",
    color = "Cohort", fill = "Cohort"
  ) +
  theme_minimal()

print(p3)
ggsave(
  p3,
  filename = "../../analysis/plots/roc_v1_v2_xcv0_rb0_23feb26.pdf",
  width = 6.2, height = 4.8
)

# ================================
# PLOT 4: v1, Both cohorts, xcv=0, rb=0 vs rb=1
# ================================

plot4_df <- roc_combined %>%
  dplyr::filter(
    year == "v1",
    filter_cohort == "Both cohorts",
    cross_cohort_val == 0,
    regress_batch %in% c(0, 1)
  ) %>%
  dplyr::mutate(
    curve = factor(
      ifelse(regress_batch == 0, "rb=0", "rb=1"),
      levels = c("rb=0", "rb=1")
    )
  )

sum4 <- summarize_roc(plot4_df, by_vars = "curve")

p4 <- ggplot(sum4, aes(x = 1 - specificity, y = mean_sens, color = curve)) +
  geom_line(linewidth = 1.2) +
  geom_ribbon(
    aes(ymin = mean_sens - sd_sens, ymax = mean_sens + sd_sens, fill = curve),
    alpha = 0.2, linewidth = 0
  ) +
  geom_abline(linetype = "dashed", color = "gray50") +
  coord_equal(xlim = c(0, 1), ylim = c(0, 1), expand = FALSE) +
  labs(
    title = "Batch regression, Both Cohorts, Visit 1",
    x = "1 - Specificity",
    y = "Sensitivity",
    color = "Batch reg.", fill = "Batch reg."
  ) +
  theme_minimal()

print(p4)
ggsave(
  p4,
  filename = "../../analysis/plots/roc_v1_both_rb0_rb1_xcv0_23feb26.pdf",
  width = 6.0, height = 4.5
)


# ================================
# ONE AUC PLOT WITH ALL CURVES
# ================================

auc_all_seed <- auc_by_seed %>%
  dplyr::mutate(
    filter_cohort = dplyr::recode(
      filter_cohort,
      "0"    = "BPRHS",
      "1"    = "PROSPECT",
      "none" = "Both cohorts"
    )
  ) %>%
  dplyr::mutate(
    curve = dplyr::case_when(
      # Plot 1: v1, xcv=0, rb=0, all three cohorts
      year == "v1" & cross_cohort_val == 0 & regress_batch == 0 &
        filter_cohort == "Both cohorts" ~ "v1: Both cohorts (random)",
      year == "v1" & cross_cohort_val == 0 & regress_batch == 0 &
        filter_cohort == "BPRHS"        ~ "v1: BPRHS (random)",
      year == "v1" & cross_cohort_val == 0 & regress_batch == 0 &
        filter_cohort == "PROSPECT"     ~ "v1: PROSPECT (random)",
      
      # Plot 3: v2, xcv=0, rb=0, all three cohorts
      year == "v2" & cross_cohort_val == 0 & regress_batch == 0 &
        filter_cohort == "Both cohorts" ~ "v2: Both cohorts (random)",
      year == "v2" & cross_cohort_val == 0 & regress_batch == 0 &
        filter_cohort == "BPRHS"        ~ "v2: BPRHS (random)",
      year == "v2" & cross_cohort_val == 0 & regress_batch == 0 &
        filter_cohort == "PROSPECT"     ~ "v2: PROSPECT (random)",
      
      # Plot 2: v1, Both cohorts, xcv=0:4, rb=0
      year == "v1" & filter_cohort == "Both cohorts" &
        regress_batch == 0 & cross_cohort_val == 0 ~ "v1: Both cohorts (random)",
      year == "v1" & filter_cohort == "Both cohorts" &
        regress_batch == 0 & cross_cohort_val == 1 ~ "v1: Train Both → Test PROSPECT",
      year == "v1" & filter_cohort == "Both cohorts" &
        regress_batch == 0 & cross_cohort_val == 2 ~ "v1: Train Both → Test BPRHS",
      year == "v1" & filter_cohort == "Both cohorts" &
        regress_batch == 0 & cross_cohort_val == 3 ~ "v1: Train PROSPECT → Test BPRHS",
      year == "v1" & filter_cohort == "Both cohorts" &
        regress_batch == 0 & cross_cohort_val == 4 ~ "v1: Train BPRHS → Test PROSPECT",
      
      # Plot 4: v1, Both cohorts, xcv=0, rb=1
      year == "v1" & filter_cohort == "Both cohorts" &
        cross_cohort_val == 0 & regress_batch == 1 ~ "v1: Both cohorts (random, rb=1)",
      
      TRUE ~ NA_character_
    )
  ) %>%
  dplyr::filter(!is.na(curve))

auc_all <- auc_all_seed %>%
  dplyr::group_by(curve) %>%
  dplyr::summarise(
    mean_auc = mean(auc, na.rm = TRUE),
    sd_auc   = sd(auc, na.rm = TRUE),
    n        = dplyr::n(),
    se_auc   = sd_auc / sqrt(n),
    lwr      = mean_auc - 1.96 * se_auc,
    upr      = mean_auc + 1.96 * se_auc,
    .groups  = "drop"
  ) %>%
  dplyr::mutate(
    curve = factor(
      curve,
      levels = c(
        "v1: Both cohorts (random)",
        "v1: BPRHS (random)",
        "v1: PROSPECT (random)",
        "v2: Both cohorts (random)",
        "v2: BPRHS (random)",
        "v2: PROSPECT (random)",
        "v1: Train Both → Test PROSPECT",
        "v1: Train Both → Test BPRHS",
        "v1: Train PROSPECT → Test BPRHS",
        "v1: Train BPRHS → Test PROSPECT",
        "v1: Both cohorts (random, rb=1)"
      )
    )
  )

auc_all <- auc_all %>%
  dplyr::arrange(dplyr::desc(mean_auc)) %>%
  dplyr::mutate(curve = factor(curve, levels = curve))  # levels now in decreasing AUC

p_auc_all <- ggplot(auc_all, aes(x = curve, y = mean_auc, fill = curve)) +
  geom_col(width = 0.6, show.legend = FALSE) +
  geom_errorbar(aes(ymin = lwr, ymax = upr), width = 0.2) +
  coord_cartesian(ylim = c(0.5, 1)) +
  labs(
    title = "AUC across all strategies",
    x = NULL,
    y = "Mean AUC (±95% CI)"
  ) +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 25, hjust = 1))

print(p_auc_all)
ggsave(
  p_auc_all,
  filename = "../../analysis/plots/auc_all_strategies_23feb26.pdf",
  width = 8.0, height = 4.5
)

###

COUNT_DIR <- OUT_RESULTS  # "../../analysis/"
PATTERN   <- "^cohort_counts_all_diabetes_v[0-9]+_class2_"

# 1) find all cohort_counts files
count_files <- list.files(
  path       = COUNT_DIR,
  pattern    = PATTERN,
  full.names = TRUE
)

length(count_files)
head(count_files)

# 2) parse metadata from filenames (no ~, single pattern string)
# Example filename:
# cohort_counts_all_diabetes_v1_class2_filternone_seed1_tune_caseweights_boruta_xcohortval_3_resbatch_0_7nov25.csv

pattern <- "^cohort_counts_([^_]+)_([^_]+)_(v[0-9]+)_class([0-9]+)_filter([^_]+)_seed([0-9]+)_tune_caseweights_boruta_xcohortval_([0-9]+)_resbatch_([0-9]+)_([^.]+)\\.csv$"

meta_mat <- str_match(basename(count_files), pattern)
# meta_mat columns:
# 1 = full match
# 2 = data_string ("all")
# 3 = outvar      ("diabetes")
# 4 = year        ("v1"/"v2")
# 5 = nclass      ("2")
# 6 = filter      ("none","0","1","filternone",...)
# 7 = seed
# 8 = xcohortval
# 9 = resbatch
# 10 = date       ("7nov25")

# guard against any non-matching filenames
if (any(is.na(meta_mat[, 1]))) {
  warning("Some filenames did not match the expected pattern:\n",
          paste(basename(count_files)[is.na(meta_mat[, 1])], collapse = "\n"))
}

meta_df <- as_tibble(meta_mat[, -1, drop = FALSE])
names(meta_df) <- c(
  "data_string", "outvar", "year", "nclass",
  "filter_raw", "seed", "xcohortval", "resbatch", "date"
)

meta_df <- meta_df %>%
  mutate(
    nclass     = as.integer(nclass),
    seed       = as.integer(seed),
    xcohortval = as.integer(xcohortval),
    resbatch   = as.integer(resbatch),
    file_path  = count_files
  )

# 3) read each CSV and attach metadata
cohort_counts_list <- map(seq_len(nrow(meta_df)), function(i) {
  md <- meta_df[i, ]
  df <- read.csv(md$file_path, stringsAsFactors = FALSE)
  
  df %>%
    mutate(
      data_string      = md$data_string,
      outvar           = md$outvar,
      year             = md$year,
      nclass           = md$nclass,
      filter_cohort    = md$filter_raw,
      seed             = md$seed,
      cross_cohort_val = md$xcohortval,
      regress_batch    = md$resbatch,
      date_tag         = md$date
    )
})

cohort_counts_combined <- bind_rows(cohort_counts_list)

# 4) tidy filter labels to match the rest of your script
cohort_counts_combined <- cohort_counts_combined %>%
  mutate(
    filter_cohort = case_when(
      filter_cohort == "none"     ~ "Both cohorts",
      filter_cohort == "0"        ~ "BPRHS",
      filter_cohort == "1"        ~ "PROSPECT",
      filter_cohort == "filternone" ~ "Both cohorts", # if you want to treat like 'none'
      TRUE                        ~ filter_cohort
    ),
    filter_cohort = factor(
      filter_cohort,
      levels = c("Both cohorts", "BPRHS", "PROSPECT")
    )
  )

# Quick sanity check
dplyr::count(cohort_counts_combined, year, filter_cohort, cross_cohort_val, regress_batch, seed)


# 5) write single table to disk
write.csv(
  cohort_counts_combined,
  file = file.path(OUT_RESULTS, "cohort_counts_all_configs_23feb26.csv"),
  row.names = FALSE
)


# ---------- VI FILES: read across seeds/cohorts/years with xcv & eval ----------

# choose which rb to include for VI logs; set to c(0) for rb=0 only, or c(0,1) for both
rb_filter <- 0

# ---- restrict the combos to the rb you want for VI ----
param_vi <- subset(param_df, regress_batch %in% rb_filter)

# sanity: if rb_filter == 0, expect 100 rows (5 xcohortval levels × 2 years × 10 seeds)
if (all(rb_filter == 0)) stopifnot(nrow(param_vi) == 100)

vi_list <- list()
found <- 0L; missing <- 0L

for (i in seq_len(nrow(param_vi))) {
  year  <- param_vi$year[i]
  filt  <- param_vi$filter_cohort[i]
  xcv   <- param_vi$cross_cohort_val[i]
  rb    <- param_vi$regress_batch[i]
  seed  <- param_vi$seed[i]
  
  save_string <- paste0(
    data_string, "_", outvar, "_", year,
    "_class", nclass,
    "_filter", filt,
    "_seed", seed,
    "_tune_caseweights_boruta",
    "_xcohortval_", xcv,
    "_resbatch_", rb,
    "_", date_tag
  )
  
  file_path <- file.path(OUT_RESULTS, paste0("log_", save_string, ".csv"))
  
  if (!file.exists(file_path)) {
    missing <- missing + 1L
    message("Missing VI file: ", file_path)
    next
  }
  
  found <- found + 1L
  vi <- read.csv(file_path)
  vi$filter_cohort    <- filt
  vi$year             <- year
  vi$seed             <- seed
  vi$cross_cohort_val <- xcv
  vi$regress_batch    <- rb
  vi_list[[length(vi_list) + 1L]] <- vi
}

cat(sprintf(
  "Expected VI logs (rb in {%s}): %d  Found: %d  Missing: %d\n",
  paste(rb_filter, collapse = ","),
  nrow(param_vi), found, missing
))

vi_combined <- if (length(vi_list)) dplyr::bind_rows(vi_list) else data.frame()

message("Rows in VI combined: ", nrow(vi_combined))
if (nrow(vi_combined)) {
  message("Unique variables: ", dplyr::n_distinct(vi_combined$Variable))
}

# tidy labels
vi_combined <- vi_combined %>%
  dplyr::mutate(
    filter_cohort = dplyr::case_when(
      filter_cohort == "none" ~ "Both cohorts",
      filter_cohort == "0"    ~ "BPRHS",
      filter_cohort == "1"    ~ "PROSPECT",
      TRUE ~ as.character(filter_cohort)
    ),
    filter_cohort = factor(filter_cohort, levels = c("Both cohorts","BPRHS","PROSPECT")),
    cross_label = dplyr::case_when(
      cross_cohort_val == 0 ~ "Both cohorts",
      cross_cohort_val == 1 ~ "Train Both cohorts, Test on PROSPECT",
      cross_cohort_val == 2 ~ "Train Both cohorts, Test on BPRHS",
      cross_cohort_val == 3 ~ "Train PROSPECT, Test BPRHS",
      cross_cohort_val == 4 ~ "Train BPRHS, Test PROSPECT",
      TRUE                  ~ paste("xcv", cross_cohort_val)
    ),
    cross_label = factor(
      cross_label,
      levels = c(
        "Both cohorts",
        "Train Both cohorts, Test on BPRHS",
        "Train Both cohorts, Test on PROSPECT",
        "Train PROSPECT, Test BPRHS",
        "Train BPRHS, Test PROSPECT"
      )
    )
  )

print(dplyr::count(vi_combined, year, filter_cohort, cross_cohort_val, cross_label, regress_batch, name = "n_files"))

write.csv(vi_combined, "../../analysis/results/combined_vi_23feb26.csv")

vi_mean_imp <- vi_combined %>%
  mutate(
    regime = case_when(
      # pooled both-cohort model (train+test both)
      cross_cohort_val == 0 & filter_cohort == "Both cohorts" ~ "Both cohorts",
      # single-cohort train=test models
      cross_cohort_val == 0 & filter_cohort == "BPRHS"        ~ "BPRHS",
      cross_cohort_val == 0 & filter_cohort == "PROSPECT"     ~ "PROSPECT",
      # cross-cohort directions (keep available, but will be excluded later in vi_panel)
      cross_cohort_val == 1 ~ "Train Both cohorts, Test on PROSPECT",
      cross_cohort_val == 2 ~ "Train Both cohorts, Test on BPRHS",
      # explicitly drop cross-cohort_val 3 & 4 for VI plots
      cross_cohort_val %in% c(3, 4) ~ NA_character_,
      TRUE ~ NA_character_
    ),
    regime = factor(
      regime,
      levels = c(
        "Both cohorts",
        "Train Both cohorts, Test on BPRHS",
        "Train Both cohorts, Test on PROSPECT",
        "Train PROSPECT, Test BPRHS",
        "Train BPRHS, Test PROSPECT",
        "BPRHS",
        "PROSPECT"
      )
    )
  ) %>%
  # drop anything without a regime (including xcv=3,4)
  filter(!is.na(regime)) %>%
  group_by(Variable, regime, year, type, visit) %>%
  summarise(
    Importance = mean(Importance, na.rm = TRUE),
    rank       = mean(rank, na.rm = TRUE),
    .groups    = "drop"
  ) %>%
  mutate(
    # force AGE to HEALTH/SDOH if needed
    type = ifelse(Variable == "age", "HEALTH/SDOH", type)
  ) %>%
  # ---- filter to v1 and regimes of interest
  filter(
    visit == "v1",
    !is.na(regime)
  ) %>%
  mutate(
    type      = toupper(type),
    type      = factor(type, levels = c("FFQ", "SDOH", "HEALTH", "HEALTH/SDOH")),
    Variable  = as.character(Variable)
  )


# --- 2) Identify variables present in pooled Both-cohort model (optional flag) ----
vars_in_both <- vi_mean_imp %>%
  filter(regime == "Both cohorts") %>%
  pull(Variable) %>%
  unique()

vi_mean_imp <- vi_mean_imp %>%
  mutate(
    cohort_specific = case_when(
      !(Variable %in% vars_in_both) & regime %in% c("BPRHS","PROSPECT")
      ~ "Unique to 1-cohort models",
      TRUE ~ "2-cohort model"
    ),
    cohort_specific = factor(
      cohort_specific,
      levels = c("2-cohort model", "Unique to 1-cohort models")
    )
  )

# Relabel pretty names --------------------------------------------------
features <- read.xlsx("../../analysis/plots/relabel_features_plot_17nov25_edit.xlsx") %>%
  dplyr::transmute(
    Variable = variable_name,
    description.new = stringr::str_to_sentence(description.new)
  )

# --- Keep only the three regimes you want -------------------------------------
vi_panel <- vi_mean_imp %>%
  dplyr::filter(regime %in% c(
    "Both cohorts",
    "BPRHS",
    "PROSPECT"
  )) %>%
  dplyr::mutate(
    regime = factor(
      regime,
      levels = c("Both cohorts", "BPRHS", "PROSPECT")
    )
  )

# --- Top per regime + pretty labels ----------------------------------------
top_vars <- vi_panel %>%
  dplyr::group_by(regime) %>%
  dplyr::slice_max(order_by = Importance, n = 20, with_ties = FALSE) %>%
  dplyr::ungroup() %>%
  dplyr::left_join(features, by = "Variable") %>%
  dplyr::mutate(
    description.new = dplyr::if_else(
      is.na(description.new) | description.new == "",
      Variable,
      description.new
    )
  )

# Build facet-aware label lookup (key = "Variable___regime")
label_map <- top_vars %>%
  dplyr::transmute(key = paste0(Variable, "___", regime), label = description.new) %>%
  dplyr::distinct()
label_lookup <- stats::setNames(label_map$label, label_map$key)

# Facet-aware ordering: descending Importance inside each regime
top_vars <- top_vars %>%
  dplyr::mutate(
    Variable_plot = tidytext::reorder_within(Variable, -Importance, regime) |> forcats::fct_rev()
  )

head(top_vars)
# --- Combined 3-panel plot -----------------------------------------------------
fill_colors <- c("FFQ" = "#7BAFD4", "SDOH" = "#F4A259", "HEALTH" = "#88C27C", "HEALTH/SDOH" = "grey70")

head(top_vars %>% 
       filter(description.new == "Zinc"))

view(top_vars)
p_combined <- ggplot2::ggplot(top_vars, ggplot2::aes(x = Importance, y = Variable_plot, fill = type)) +
  ggplot2::geom_col(ggplot2::aes(color = cohort_specific), width = 0.8, linewidth = 1) +
  ggplot2::scale_fill_manual(values = fill_colors, drop = FALSE) +
  ggplot2::scale_color_manual(
    values = c("2-cohort model" = NA, "Unique to 1-cohort models" = "black"),
    drop = FALSE,
    guide = ggplot2::guide_legend(title = NULL, override.aes = list(fill = NA))
  ) +
  ggplot2::guides(fill = ggplot2::guide_legend(title = NULL)) +
  ggplot2::facet_wrap(~ regime, nrow = 1, scales = "free_y") +
  ggplot2::labs(
    title = "Most Important Variables (Visit 1, Avg Across Seeds)",
    x = "Average Permutation Importance", y = NULL
  ) +
  # facet-aware label substitution
  tidytext::scale_y_reordered(labels = function(x) {
    out <- label_lookup[x]
    out[is.na(out)] <- gsub("___.*$", "", x[is.na(out)])
    out
  }) +
  ggplot2::theme_minimal(base_size = 12) +
  ggplot2::theme(
    strip.text = ggplot2::element_text(face = "bold"),
    axis.text.y = ggplot2::element_text(size = 10)
  )

print(p_combined)

p_combined
ggplot2::ggsave(
  filename = "../../analysis/plots/vi_v1_avg_caseweight_three_panels_23feb26.pdf",
  plot = p_combined, width = 12, height = 7
)

# SDOH only -----

# Top vars (SDOH and HEALTH/SDOH only)
top_vars <- vi_panel %>%
  filter(type %in% c("SDOH", "HEALTH/SDOH")) %>%
  group_by(regime) %>%
  slice_max(order_by = Importance, n = 5, with_ties = FALSE) %>%
  ungroup()

head(top_vars)

# Join pretty labels
top_vars <- top_vars %>%
  left_join(features, by = "Variable") %>%
  mutate(
    description.new = ifelse(
      is.na(description.new) | description.new == "",
      Variable,
      description.new
    )
  )

# Build a NAMED VECTOR for label lookup: names = "var___facet", values = pretty labels
label_map <- top_vars %>%
  transmute(
    key   = paste0(Variable, "___", regime),
    label = description.new
  ) %>%
  distinct()

label_lookup <- setNames(label_map$label, label_map$key)

# Ensure cohort_specific exists for outline coloring (fallback if not present)
if (!"cohort_specific" %in% names(top_vars)) {
  top_vars <- top_vars %>%
    mutate(
      cohort_specific = factor(
        "2-cohort model",
        levels = c("2-cohort model", "Unique to 1-cohort models")
      )
    )
}

top_vars <- top_vars %>%
  dplyr::mutate(
    Variable_plot = tidytext::reorder_within(Variable, -Importance, regime) |> forcats::fct_rev()
  )

head(top_vars)

p_sdoh <- ggplot2::ggplot(top_vars, ggplot2::aes(x = Importance, y = Variable_plot, fill = type)) +
  ggplot2::geom_col(ggplot2::aes(color = cohort_specific), width = 0.8, linewidth = 1) +
  ggplot2::scale_fill_manual(values = fill_colors, drop = FALSE) +
  ggplot2::scale_color_manual(
    values = c("2-cohort model" = NA, "Unique to 1-cohort models" = "black"),
    drop = FALSE,
    guide = ggplot2::guide_legend(title = NULL, override.aes = list(fill = NA))
  ) +
  ggplot2::guides(fill = ggplot2::guide_legend(title = NULL)) +
  ggplot2::facet_wrap(~ regime, nrow = 1, scales = "free_y") +
  ggplot2::labs(
    title = "SDOH variables",
    x = "Average Permutation Importance", y = NULL
  ) +
  # facet-aware label substitution
  tidytext::scale_y_reordered(labels = function(x) {
    out <- label_lookup[x]
    out[is.na(out)] <- gsub("___.*$", "", x[is.na(out)])
    out
  }) +
  ggplot2::theme_minimal(base_size = 12) +
  ggplot2::theme(
    strip.text = ggplot2::element_text(face = "bold"),
    axis.text.y = ggplot2::element_text(size = 10)
  )

view(top_vars)

print(p_sdoh)
ggplot2::ggsave(
  filename = "../../analysis/plots/vi_v1_sdoh_23feb26.pdf",
  plot = p_sdoh, width = 12, height = 3
)


##Read relabel file and join pretty names, do this only once to create the names
# features = data.frame(variable_name = unique(vi_mean_imp$Variable))
# metadata = read.xlsx("data/andreia_hmz_data/hmz_bprhs_prospect_metadata_30july2025.xlsx") %>%
#   mutate(long_variable_name = variable_name) %>%
#   mutate(variable_name = gsub("hmz_health_","", variable_name)) %>%
#   mutate(variable_name = gsub("hmz_sdoh_","", variable_name)) %>%
#   mutate(variable_name = gsub("hmz_ffq_","", variable_name)) %>%
#   select(long_variable_name, variable_name, description) %>%
#   mutate(description = gsub("\\ $","",description)) %>%
#   mutate(description = gsub("\\ ","_",description)) %>%
#   mutate(description = gsub("\\(","",description)) %>%
#   mutate(description = gsub("\\)","",description)) %>%
#   mutate(description = gsub("average_","", description)) %>%
#   mutate(description = gsub("serum_","", description))
# features = features %>%
#   left_join(metadata, by="variable_name")
# 
# tmp <- read.xlsx("r_pipeline/analysis/plots/relabel_features_plot_edit.xlsx")
# colnames(tmp)
# tmp = tmp %>%
#   rename(tmp.name = description.new.tmp) %>%
#   select(-c(description)) %>%
#   rename(description.new.tmp = description.new)
# colnames(tmp)
# colnames(features)
# 
# features = features %>%
#   full_join(tmp, by=c("variable_name","long_variable_name")) %>%
#   mutate(description.new = ifelse(is.na(description.new.tmp), description, description.new.tmp))
# 
# view(features)
# write.xlsx(features,"r_pipeline/analysis/plots/relabel_features_plot_17nov25.xlsx")


library(dplyr)
library(ggplot2)
library(scales)

## 1) Accuracy across *all* regimes ----
acc_by_seed_all <- vi_combined %>%
  mutate(
    regime = case_when(
      cross_cohort_val == 0 & filter_cohort == "Both cohorts" ~ "Both cohorts",
      cross_cohort_val == 0 & filter_cohort == "BPRHS"        ~ "BPRHS",
      cross_cohort_val == 0 & filter_cohort == "PROSPECT"     ~ "PROSPECT",
      cross_cohort_val == 1 ~ "Train Both cohorts, Test on PROSPECT",
      cross_cohort_val == 2 ~ "Train Both cohorts, Test on BPRHS",
      cross_cohort_val == 3 ~ "Train PROSPECT, Test BPRHS",
      cross_cohort_val == 4 ~ "Train BPRHS, Test PROSPECT",
      TRUE ~ NA_character_
    )
  ) %>%
  filter(!is.na(regime), visit == "v1") %>%
  group_by(regime, seed) %>%
  summarise(accuracy = first(accuracy), .groups = "drop")

acc_summary_all <- acc_by_seed_all %>%
  group_by(regime) %>%
  summarise(
    mean_acc = mean(accuracy, na.rm = TRUE),
    sd_acc   = sd(accuracy, na.rm = TRUE),
    n        = n(),
    se_acc   = sd_acc / sqrt(n),
    lwr      = mean_acc - 1.96 * se_acc,
    upr      = mean_acc + 1.96 * se_acc,
    .groups  = "drop"
  ) %>%
  arrange(desc(mean_acc)) %>%
  mutate(regime = factor(regime, levels = regime))

acc_summary_all

p_acc_all <- ggplot(acc_summary_all,
                    aes(x = regime, y = mean_acc, fill = regime)) +
  geom_col(width = 0.6, color = "black", show.legend = FALSE) +
  geom_errorbar(aes(ymin = lwr, ymax = upr), width = 0.2) +
  scale_y_continuous(labels = percent_format(accuracy = 1)) +
  coord_cartesian(ylim = c(0.5, 1)) +
  labs(
    title = "Accuracy across all strategies (Visit 1)",
    x = NULL,
    y = "Mean accuracy (±95% CI)"
  ) +
  theme_minimal(base_size = 12) +
  theme(axis.text.x = element_text(angle = 20, hjust = 1))

print(p_acc_all)

ggsave(
  filename = "../../analysis/plots/acc_all_strategies_v1_23feb26.pdf",
  plot     = p_acc_all,
  height   = 4,
  width    = 7
)


## 2) Accuracy for just the 4 ROC-plot-1 regimes ----

acc_4 <- vi_combined %>%
  filter(
    visit == "v1",
    regress_batch == 0
  ) %>%
  mutate(
    regime = case_when(
      cross_cohort_val == 0 & filter_cohort == "Both cohorts" ~ "Both cohorts",
      cross_cohort_val == 0 & filter_cohort == "BPRHS"        ~ "BPRHS",
      cross_cohort_val == 0 & filter_cohort == "PROSPECT"     ~ "PROSPECT",
      cross_cohort_val == 1 & filter_cohort == "Both cohorts" ~ "Train Both \u2192 Test PROSPECT",
      TRUE ~ NA_character_
    )
  ) %>%
  filter(!is.na(regime)) %>%
  group_by(regime, seed) %>%
  summarise(accuracy = first(accuracy), .groups = "drop")

acc_4_summary <- acc_4 %>%
  group_by(regime) %>%
  summarise(
    mean_acc = mean(accuracy, na.rm = TRUE),
    sd_acc   = sd(accuracy, na.rm = TRUE),
    n        = n(),
    se_acc   = sd_acc / sqrt(n),
    lwr      = mean_acc - 1.96 * se_acc,
    upr      = mean_acc + 1.96 * se_acc,
    .groups  = "drop"
  ) %>%
  mutate(
    regime = factor(regime,
                    levels = c("Both cohorts", "BPRHS", "PROSPECT",
                               "Train Both \u2192 Test PROSPECT"))
  )

p_acc_4 <- ggplot(acc_4_summary,
                  aes(x = regime, y = mean_acc, fill = regime)) +
  geom_col(width = 0.6, color = "black", show.legend = FALSE) +
  geom_errorbar(aes(ymin = lwr, ymax = upr), width = 0.2) +
  scale_y_continuous(labels = percent_format(accuracy = 1)) +
  coord_cartesian(ylim = c(0.5, 1)) +
  labs(
    title = "Accuracy (Visit 1) for ROC-plot-1 regimes",
    x = NULL,
    y = "Mean accuracy (±95% CI)"
  ) +
  theme_minimal(base_size = 12) +
  theme(axis.text.x = element_text(angle = 20, hjust = 1))

print(p_acc_4)

ggsave(
  filename = "../../analysis/plots/acc_four_regimes_rocplot1_v1_23feb26.pdf",
  plot     = p_acc_4,
  width    = 4.5,
  height   = 4.2
)

## 3) ROC AUC across all strategies (Visit 1) ----

auc_by_seed_all <- auc_by_seed %>%
  filter(year == "v1") %>%
  mutate(
    regime = case_when(
      cross_cohort_val == 0 & filter_cohort == "Both cohorts" ~ "Both cohorts",
      cross_cohort_val == 0 & filter_cohort == "BPRHS"        ~ "BPRHS",
      cross_cohort_val == 0 & filter_cohort == "PROSPECT"     ~ "PROSPECT",
      cross_cohort_val == 1 ~ "Train Both cohorts, Test on PROSPECT",
      cross_cohort_val == 2 ~ "Train Both cohorts, Test on BPRHS",
      cross_cohort_val == 3 ~ "Train PROSPECT, Test BPRHS",
      cross_cohort_val == 4 ~ "Train BPRHS, Test PROSPECT",
      TRUE ~ NA_character_
    )
  ) %>%
  filter(!is.na(regime))

auc_summary_all <- auc_by_seed_all %>%
  group_by(regime) %>%
  summarise(
    mean_auc = mean(auc, na.rm = TRUE),
    sd_auc   = sd(auc, na.rm = TRUE),
    n        = n(),
    se_auc   = sd_auc / sqrt(n),
    lwr      = mean_auc - 1.96 * se_auc,
    upr      = mean_auc + 1.96 * se_auc,
    .groups  = "drop"
  ) %>%
  arrange(desc(mean_auc)) %>%
  mutate(regime = factor(regime, levels = regime))

auc_summary_all

p_auc_all <- ggplot(auc_summary_all,
                    aes(x = regime, y = mean_auc, fill = regime)) +
  geom_col(width = 0.6, color = "black", show.legend = FALSE) +
  geom_errorbar(aes(ymin = lwr, ymax = upr), width = 0.2) +
  coord_cartesian(ylim = c(0.5, 1)) +
  labs(
    title = "ROC AUC across all strategies (Visit 1)",
    x = NULL,
    y = "Mean AUC (±95% CI)"
  ) +
  theme_minimal(base_size = 12) +
  theme(axis.text.x = element_text(angle = 20, hjust = 1))

print(p_auc_all)

ggsave(
  filename = "../../analysis/plots/auc_all_strategies_v1_23feb26.pdf",
  plot     = p_auc_all,
  height   = 4,
  width    = 7
)


## 4) ROC AUC for just the 4 ROC-plot-1 regimes ----

auc_4 <- auc_by_seed %>%
  filter(
    year == "v1",
    regress_batch == 0
  ) %>%
  mutate(
    regime = case_when(
      cross_cohort_val == 0 & filter_cohort == "Both cohorts" ~ "Both cohorts",
      cross_cohort_val == 0 & filter_cohort == "BPRHS"        ~ "BPRHS",
      cross_cohort_val == 0 & filter_cohort == "PROSPECT"     ~ "PROSPECT",
      cross_cohort_val == 1 & filter_cohort == "Both cohorts" ~ "Train Both \u2192 Test PROSPECT",
      TRUE ~ NA_character_
    )
  ) %>%
  filter(!is.na(regime))

auc_4_summary <- auc_4 %>%
  group_by(regime) %>%
  summarise(
    mean_auc = mean(auc, na.rm = TRUE),
    sd_auc   = sd(auc, na.rm = TRUE),
    n        = n(),
    se_auc   = sd_auc / sqrt(n),
    lwr      = mean_auc - 1.96 * se_auc,
    upr      = mean_auc + 1.96 * se_auc,
    .groups  = "drop"
  ) %>%
  mutate(
    regime = factor(
      regime,
      levels = c("Both cohorts", "BPRHS", "PROSPECT", "Train Both \u2192 Test PROSPECT")
    )
  )

# Palette consistent with ROC curves
pal_auc4 <- roc_colors[as.character(levels(auc_4_summary$regime))]
print(pal_auc4)  # quick check: no NAs

auc_4_summary <- auc_4_summary %>%
  arrange(desc(mean_auc)) %>%
  mutate(regime = factor(regime, levels = regime))


p_auc_4 <- ggplot(auc_4_summary,
                  aes(x = regime, y = mean_auc, fill = regime)) +
  geom_col(width = 0.6, color = "black", show.legend = FALSE) +
  geom_errorbar(aes(ymin = lwr, ymax = upr), width = 0.2) +
  coord_cartesian(ylim = c(0.5, 1)) +
  scale_fill_manual(values = pal_auc4, drop = FALSE) +
  labs(
    title = "ROC AUC (Visit 1)",
    x = NULL,
    y = "Mean AUC (±95% CI)"
  ) +
  theme_minimal(base_size = 12) +
  theme(
    axis.text.x = element_text(angle = 20, hjust = 1)
  )

print(p_auc_4)

ggsave(
  filename = "../../analysis/plots/auc_four_regimes_rocplot1_v1_23feb26.pdf",
  plot     = p_auc_4,
  width    = 4,
  height   =4
)

#############################################
## ROC AUC for the 5 cross-cohort regimes (Plot 2 set)
#############################################

# Per-seed AUC for these 5 regimes, visit 1, rb = 0, filter_cohort = Both cohorts
auc_xcv5 <- auc_by_seed %>%
  dplyr::filter(
    year == "v1",
    filter_cohort == "Both cohorts",
    regress_batch == 0,
    cross_cohort_val %in% 0:4
  ) %>%
  dplyr::mutate(
    regime = dplyr::case_when(
      cross_cohort_val == 0 ~ "Both cohorts",
      cross_cohort_val == 1 ~ "Train Both \u2192 Test PROSPECT",
      cross_cohort_val == 2 ~ "Train Both \u2192 Test BPRHS",
      cross_cohort_val == 3 ~ "Train PROSPECT \u2192 Test BPRHS",
      cross_cohort_val == 4 ~ "Train BPRHS \u2192 Test PROSPECT",
      TRUE ~ NA_character_
    )
  ) %>%
  dplyr::filter(!is.na(regime))

# Summarise mean AUC + 95% CI across seeds
auc_xcv5_summary <- auc_xcv5 %>%
  dplyr::group_by(regime) %>%
  dplyr::summarise(
    mean_auc = mean(auc, na.rm = TRUE),
    sd_auc   = sd(auc, na.rm = TRUE),
    n        = dplyr::n(),
    se_auc   = sd_auc / sqrt(n),
    lwr      = mean_auc - 1.96 * se_auc,
    upr      = mean_auc + 1.96 * se_auc,
    .groups  = "drop"
  ) %>%
  # order bars by descending AUC
  dplyr::arrange(dplyr::desc(mean_auc)) %>%
  dplyr::mutate(regime = factor(regime, levels = regime))

print(auc_xcv5_summary)

# If you want to reuse the same palette as p2 and you have roc_colors defined:
# pal_xcv5 <- roc_colors[as.character(levels(auc_xcv5_summary$regime))]

p_auc_xcv5 <- ggplot(auc_xcv5_summary,
                     aes(x = regime, y = mean_auc, fill = regime)) +
  geom_col(width = 0.6, color = "black", show.legend = FALSE) +
  geom_errorbar(aes(ymin = lwr, ymax = upr), width = 0.2) +
  coord_cartesian(ylim = c(0.5, 1)) +
  # if you have a manual palette, uncomment this and define pal_xcv5 above:
  # scale_fill_manual(values = pal_xcv5, drop = FALSE) +
  labs(
    title = "Cross Cohort AUC ROC (Visit 1) ",
    x = NULL,
    y = "Mean AUC (±95% CI)"
  ) +
  theme_minimal(base_size = 12) +
  theme(
    axis.text.x = element_text(angle = 20, hjust = 1)
  )

print(p_auc_xcv5)

ggsave(
  filename = "../../analysis/plots/auc_v1_xcohort_five_curves_rb0_23feb26.pdf",
  plot     = p_auc_xcv5,
  width    = 4,
  height   = 4
)


