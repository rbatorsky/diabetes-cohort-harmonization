#!/usr/bin/env Rscript

LIB="/cluster/tufts/patralab/rbator01/R_libs/4.4.0/"
.libPaths(LIB)

source("utils.R")

pkgs <- c(
  "openxlsx",
  "dplyr", "tidyr", "tibble", "purrr",
  "ggplot2", "scales",
  "stringr",
  "forcats", "yardstick"
)
invisible(lapply(pkgs, quiet_library))

# ---------------- Paths ----------------
IN <- "../../analysis/"
OUT    <- "../../plots_deltadiab"
dir.create(OUT, showWarnings = FALSE, recursive = TRUE)

# ---------------- Run family: MUST match your modeling script ----------------
nclass <- 2
outvar <- "diabetes_change"
visit  <- "change"
data_string <- "all"
importance  <- "none"
regress_batch <- 0
date_tag <- "24feb26"

seeds <- 1:10
filter_levels_raw <- c("0","1","none")
xcv_levels <- 0:4   # keep 0:4; your bash loop did 0, but your directory has others

POS_CLASS <- "Progression"
NEG_CLASS <- "No_progression"

common_grid <- seq(0, 1, length.out = 1001)

# ---------------- Helpers ----------------
trapz <- function(x, y) {
  o <- order(x)
  x <- x[o]; y <- y[o]
  sum(diff(x) * (head(y, -1) + tail(y, -1)) / 2)
}

# robust: yardstick roc_curve tibble sometimes has columns (.threshold, specificity, sensitivity)
extract_roc_df <- function(obj) {
  if (is.data.frame(obj) && all(c("specificity","sensitivity") %in% names(obj))) {
    tibble(specificity = obj[["specificity"]], sensitivity = obj[["sensitivity"]])
  } else {
    stop("Unknown ROC object format: need data.frame with specificity/sensitivity.")
  }
}

interp_roc_to_grid <- function(roc_df, xgrid) {
  df <- roc_df %>%
    filter(is.finite(specificity), is.finite(sensitivity)) %>%
    transmute(
      fpr = pmin(pmax(1 - specificity, 0), 1),
      tpr = pmin(pmax(sensitivity, 0), 1)
    ) %>%
    arrange(fpr) %>%
    distinct(fpr, .keep_all = TRUE)
  
  if (nrow(df) < 2 || n_distinct(df$fpr) < 2) {
    stop("Degenerate ROC: fewer than 2 unique FPR points.")
  }
  
  ax <- approx(x = df$fpr, y = df$tpr, xout = xgrid, method = "linear", rule = 2)
  tibble(fpr = ax$x, tpr = ax$y)
}

recode_filter <- function(f) {
  dplyr::case_when(
    f == "0" ~ "BPRHS",
    f == "1" ~ "PROSPECT",
    f == "none" ~ "Both cohorts",
    TRUE ~ f
  )
}

recode_xcv <- function(xcv) {
  dplyr::case_when(
    xcv == 0 ~ "Random split",
    xcv == 1 ~ "Train pooled → Test PROSPECT",
    xcv == 2 ~ "Train pooled → Test BPRHS",
    xcv == 3 ~ "Train PROSPECT → Test BPRHS",
    xcv == 4 ~ "Train BPRHS → Test PROSPECT",
    TRUE ~ paste0("xcv=", xcv)
  )
}

# Strict filename builder: matches YOUR modeling save_string
make_save_string <- function(filter_cohort, seed, xcv) {
  paste0(
    data_string, "_", outvar, "_", visit,
    "_class", nclass,
    "_filter", filter_cohort,
    "_seed", seed,
    "_tune_caseweights_", importance,
    "_xcohortval_", xcv,
    "_resbatch_", regress_batch,
    "_", date_tag
  )
}

# ---------------- Build param grid (like your baseline script) ----------------
param_df <- expand.grid(
  filter_cohort    = filter_levels_raw,
  cross_cohort_val = xcv_levels,
  seed             = seeds,
  KEEP.OUT.ATTRS   = FALSE,
  stringsAsFactors = FALSE
) %>% as_tibble()

# ---------------- Read ROC curves ----------------
roc_list <- list()
found <- 0L; missing <- 0L; kept <- 0L

for (i in seq_len(nrow(param_df))) {
  filt <- param_df$filter_cohort[i]
  xcv  <- param_df$cross_cohort_val[i]
  seed <- param_df$seed[i]
  
  save_string <- make_save_string(filt, seed, xcv)
  roc_path <- file.path(IN, paste0(save_string, "_roc.rds"))
  
  if (!file.exists(roc_path)) {
    missing <- missing + 1L
    next
  }
  
  found <- found + 1L
  roc_obj <- readRDS(roc_path)
  roc_df  <- extract_roc_df(roc_obj)
  
  interp <- interp_roc_to_grid(roc_df, common_grid)
  
  kept <- kept + 1L
  roc_list[[kept]] <- tibble(
    specificity = 1 - interp$fpr,
    sensitivity = interp$tpr,
    filter_cohort = filt,
    seed = seed,
    cross_cohort_val = xcv
  )
}

cat(sprintf("ROC expected=%d, found=%d, missing=%d, kept=%d\n",
            nrow(param_df), found, missing, kept))
stopifnot(length(roc_list) > 0)

roc_combined <- bind_rows(roc_list) %>%
  mutate(
    filter_cohort = recode_filter(filter_cohort),
    xcv_label     = recode_xcv(cross_cohort_val)
  )

# AUC by seed
auc_by_seed <- roc_combined %>%
  mutate(fpr = 1 - specificity) %>%
  group_by(filter_cohort, cross_cohort_val, xcv_label, seed) %>%
  arrange(fpr, .by_group = TRUE) %>%
  summarise(roc_auc = trapz(fpr, sensitivity), .groups="drop")

# ---------------- Read test predictions + compute PR-AUC + prevalence ----------------
read_pred_metrics <- function(filt, seed, xcv) {
  save_string <- make_save_string(filt, seed, xcv)
  pred_path <- file.path(IN, paste0("test_predictions_", save_string, ".rds"))
  if (!file.exists(pred_path)) return(NULL)
  
  df <- readRDS(pred_path)
  
  # guard: must be the progression binary pipeline
  if (!("diabetes" %in% names(df))) return(NULL)
  if (!(".pred_Progression" %in% names(df))) return(NULL)
  
  df <- df %>%
    mutate(
      diabetes = factor(diabetes, levels = c(NEG_CLASS, POS_CLASS)),
      truth_pos = (diabetes == POS_CLASS)
    )
  
  prev <- mean(df$truth_pos, na.rm = TRUE)
  
  pr <- tryCatch(
    yardstick::pr_auc(df, truth = diabetes, .pred_Progression, event_level = "second")$.estimate,
    error = function(e) NA_real_
  )
  
  acc <- tryCatch(
    yardstick::accuracy(df, truth = diabetes, estimate = .pred_class)$.estimate,
    error = function(e) NA_real_
  )
  
  tibble(
    filter_cohort = filt,
    seed = seed,
    cross_cohort_val = xcv,
    pr_auc = pr,
    accuracy = acc,
    test_prev = prev,
    pr_lift = pr - prev
  )
}

pred_metrics <- pmap_dfr(
  list(param_df$filter_cohort, param_df$seed, param_df$cross_cohort_val),
  read_pred_metrics
) %>%
  mutate(
    filter_cohort = recode_filter(filter_cohort),
    xcv_label     = recode_xcv(cross_cohort_val)
  )

stopifnot(nrow(pred_metrics) > 0)

# Merge ROC AUC (from roc files) with PR metrics
metrics_by_seed <- pred_metrics %>%
  left_join(
    auc_by_seed %>% select(filter_cohort, cross_cohort_val, seed, roc_auc),
    by = c("filter_cohort","cross_cohort_val","seed")
  )

# ---------------- Print the metrics you need ----------------
cat("\n=== Per-regime summary (mean ± sd across seeds) ===\n")
summary_tbl <- metrics_by_seed %>%
  group_by(filter_cohort, xcv_label, cross_cohort_val) %>%
  summarise(
    n = n(),
    prev_mean = mean(test_prev, na.rm=TRUE),
    pr_auc_mean = mean(pr_auc, na.rm=TRUE),
    pr_auc_sd   = sd(pr_auc, na.rm=TRUE),
    pr_lift_mean= mean(pr_lift, na.rm=TRUE),
    roc_auc_mean= mean(roc_auc, na.rm=TRUE),
    acc_mean    = mean(accuracy, na.rm=TRUE),
    .groups="drop"
  ) %>%
  arrange(filter_cohort, cross_cohort_val)

print(summary_tbl)

write.csv(summary_tbl, file.path(OUT, paste0("deltadiab_progression_summary_", date_tag, ".csv")), row.names = FALSE)

# ---------------- PLOT 1: mean ROC curves (±sd) for xcv=0, three cohort filters ----------------
summarize_roc <- function(df, by_vars) {
  df %>%
    group_by(across(all_of(c(by_vars, "specificity")))) %>%
    summarise(mean_sens = mean(sensitivity, na.rm=TRUE),
              sd_sens   = sd(sensitivity, na.rm=TRUE),
              .groups="drop")
}

roc_colors <- c(
  "Both cohorts" = "#F8766D",
  "BPRHS" = "#7CAE00",
  "PROSPECT" = "#00BFC4"
)

plot_roc_df <- roc_combined %>%
  filter(cross_cohort_val == 0, filter_cohort %in% c("Both cohorts","BPRHS","PROSPECT")) %>%
  mutate(curve = factor(filter_cohort, levels = c("Both cohorts","BPRHS","PROSPECT")))

sum_roc <- summarize_roc(plot_roc_df, by_vars = "curve")

p_roc <- ggplot(sum_roc, aes(x = 1 - specificity, y = mean_sens, color = curve)) +
  geom_ribbon(aes(ymin = mean_sens - sd_sens, ymax = mean_sens + sd_sens, fill = curve),
              alpha = 0.10, linewidth = 0) +
  geom_line(linewidth = 1.2) +
  geom_abline(linetype = "dashed", color = "gray60") +
  coord_equal(xlim = c(0,1), ylim = c(0,1), expand = FALSE) +
  scale_color_manual(values = roc_colors) +
  scale_fill_manual(values = roc_colors, guide = "none") +
  labs(
    title = "Progression ROC (xcohortval=0; mean ± sd across seeds)",
    x = "1 - Specificity", y = "Sensitivity", color = "Model"
  )

ggsave(p_roc, filename = file.path(OUT, paste0("roc_progression_xcv0_three_filters_", date_tag, ".pdf")),
       width = 6.5, height = 4.8)

# ---------------- PLOT 2: PR-AUC vs prevalence baseline (xcv=0 only) ----------------
p_pr <- metrics_by_seed %>%
  filter(cross_cohort_val == 0) %>%
  ggplot(aes(x = filter_cohort, y = pr_auc)) +
  geom_point(position = position_jitter(width = 0.12, height = 0), size = 2.2, alpha = 0.85) +
  geom_hline(aes(yintercept = test_prev), linetype = "dashed", color = "gray55") +
  labs(
    title = "Progression prediction: PR-AUC vs prevalence baseline (xcohortval=0)",
    subtitle = "Dashed line = test-set prevalence (no-skill PR-AUC)",
    x = NULL, y = "PR-AUC"
  )

ggsave(p_pr, filename = file.path(OUT, paste0("pr_auc_vs_prevalence_xcv0_", date_tag, ".pdf")),
       width = 6.2, height = 4.2)

# ---------------- PLOT 3: PR lift (PR-AUC - prevalence) ----------------
p_lift <- metrics_by_seed %>%
  filter(cross_cohort_val == 0) %>%
  ggplot(aes(x = filter_cohort, y = pr_lift)) +
  geom_hline(yintercept = 0, color = "gray55") +
  geom_point(position = position_jitter(width = 0.12, height = 0), size = 2.2, alpha = 0.85) +
  labs(
    title = "Progression prediction: PR lift over base rate (xcohortval=0)",
    subtitle = "0 = no improvement over prevalence",
    x = NULL, y = "PR-AUC − prevalence"
  )

ggsave(p_lift, filename = file.path(OUT, paste0("pr_lift_xcv0_", date_tag, ".pdf")),
       width = 6.2, height = 4.2)

# ---------------- PLOT 4: Risk separation (distribution of predicted risk) ----------------
# Use a few seeds per filter to keep file size reasonable
pick <- metrics_by_seed %>%
  filter(cross_cohort_val == 0) %>%
  group_by(filter_cohort) %>%
  slice_head(n = 2) %>%
  ungroup() %>%
  transmute(filter_cohort_raw = case_when(
    filter_cohort == "BPRHS" ~ "0",
    filter_cohort == "PROSPECT" ~ "1",
    filter_cohort == "Both cohorts" ~ "none",
    TRUE ~ NA_character_
  ), seed)

read_preds_for_plot <- function(filter_raw, seed) {
  save_string <- make_save_string(filter_raw, seed, 0)
  pred_path <- file.path(IN, paste0("test_predictions_", save_string, ".rds"))
  df <- readRDS(pred_path)
  df %>%
    mutate(
      filter_cohort = recode_filter(filter_raw),
      truth = factor(diabetes, levels = c(NEG_CLASS, POS_CLASS))
    ) %>%
    select(filter_cohort, truth, .pred_Progression)
}

pred_plot_df <- pmap_dfr(list(pick$filter_cohort_raw, pick$seed), read_preds_for_plot)

p_sep <- ggplot(pred_plot_df, aes(x = .pred_Progression, fill = truth)) +
  geom_density(alpha = 0.5) +
  facet_wrap(~ filter_cohort, nrow = 1) +
  scale_x_continuous(labels = percent_format(accuracy = 1)) +
  labs(
    title = "Predicted progression risk by true outcome (example splits)",
    subtitle = "Heavy overlap + narrow predictions = 'mean-dominated' model behavior",
    x = "Predicted P(Progression)", y = "Density", fill = "Truth"
  )

ggsave(p_sep, filename = file.path(OUT, paste0("predicted_risk_separation_examples_", date_tag, ".pdf")),
       width = 9.5, height = 3.6)

cat("\nWrote plots + summary CSV to:\n  ", normalizePath(OUT), "\n")