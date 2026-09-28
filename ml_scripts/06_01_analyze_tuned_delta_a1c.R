#!/usr/bin/env Rscript

LIB <- "/cluster/tufts/patralab/rbator01/R_libs/4.4.0/"
.libPaths(LIB)

source("utils.R")

pkgs <- c(
  "dplyr","tidyr","purrr","tibble","stringr",
  "ggplot2","scales","readr"
)
invisible(lapply(pkgs, quiet_library))

IN <- "../../analysis/"
OUT    <- "../../plots_deltaa1c"
dir.create(OUT, showWarnings = FALSE, recursive = TRUE)

# -----------------------------
# This matches what you ran
# -----------------------------
nclass <- 2
outvar <- "delta_a1c_v1_v2"
visit  <- "a1c_change"
importance <- "none"
data_string <- "all"
cross_cohort_val <- 0
regress_batch <- 0
seeds <- 1:10
filter_cohorts <- c("0","1","none")

date_tag <- "24feb26"  # must match what your training script used

# -----------------------------
# Helper: rebuild save_string exactly like training
# (this must match your regression script’s save_string)
# -----------------------------
make_save_string <- function(filter_cohort, seed) {
  paste0(
    data_string,
    "_", outvar,
    "_", visit,
    "_filter", filter_cohort,
    "_seed", seed,
    "_xcohortval_", cross_cohort_val,
    "_", date_tag
  )
}

# -----------------------------
# Collect perf files (rmse/mae/rsq)
# -----------------------------
param_df <- expand.grid(
  filter_cohort = filter_cohorts,
  seed = seeds,
  stringsAsFactors = FALSE
) %>%
  tibble::as_tibble() %>%
  mutate(
    save_string = purrr::map2_chr(filter_cohort, seed, make_save_string),
    perf_file   = file.path(IN, paste0("perf_", save_string, ".csv")),
    pred_file   = file.path(IN, paste0("test_predictions_", save_string, ".rds")),
    log_file    = file.path(IN, paste0("log_", save_string, ".csv"))
  )

# -----------------------------
# Read perf_*.csv
# -----------------------------
perf_list <- list()
missing_perf <- 0L

for (i in seq_len(nrow(param_df))) {
  fp <- param_df$perf_file[i]
  if (!file.exists(fp)) {
    missing_perf <- missing_perf + 1L
    message("Missing perf: ", fp)
    next
  }
  
  df <- read.csv(fp, stringsAsFactors = FALSE)
  wide <- df %>%
    dplyr::select(.metric, .estimate) %>%
    tidyr::pivot_wider(names_from = .metric, values_from = .estimate)
  
  perf_list[[length(perf_list) + 1L]] <- wide %>%
    dplyr::mutate(
      filter_cohort = param_df$filter_cohort[i],
      seed = param_df$seed[i],
      save_string = param_df$save_string[i]
    )
}

stopifnot(length(perf_list) > 0)

perf_by_seed <- dplyr::bind_rows(perf_list) %>%
  dplyr::mutate(
    filter_cohort = dplyr::recode(
      filter_cohort,
      "0" = "BPRHS",
      "1" = "PROSPECT",
      "none" = "Both cohorts"
    )
  )

write.csv(
  perf_by_seed,
  file.path(OUT, paste0("deltaa1c_perf_by_seed_", date_tag, ".csv")),
  row.names = FALSE
)

# -----------------------------
# Read test_predictions_*.rds and compute:
#  - baseline (predict mean) RMSE/MAE
#  - skill vs baseline
#  - NRMSE (rmse / sd_y)
#  - shrinkage: slope/intercept + correlation truth vs pred
# -----------------------------
pred_list <- list()
missing_pred <- 0L

for (i in seq_len(nrow(param_df))) {
  fp <- param_df$pred_file[i]
  if (!file.exists(fp)) {
    missing_pred <- missing_pred + 1L
    next
  }
  
  tp <- readRDS(fp)
  if (!(outvar %in% names(tp)) || !(".pred" %in% names(tp))) next
  
  pred_list[[length(pred_list) + 1L]] <- tp %>%
    dplyr::mutate(
      filter_cohort_raw = param_df$filter_cohort[i],
      filter_cohort = dplyr::recode(
        param_df$filter_cohort[i],
        "0" = "BPRHS",
        "1" = "PROSPECT",
        "none" = "Both cohorts"
      ),
      seed = param_df$seed[i],
      save_string = param_df$save_string[i]
    )
}

if (length(pred_list) == 0) {
  warning("No test_predictions_*.rds found; will skip baseline/skill + shrinkage diagnostics.")
}

preds <- if (length(pred_list)) dplyr::bind_rows(pred_list) else NULL

metrics_from_preds <- NULL
shrink_from_preds  <- NULL

if (!is.null(preds) && nrow(preds) > 0) {
  
  metrics_from_preds <- preds %>%
    dplyr::group_by(filter_cohort, seed, save_string) %>%
    dplyr::summarise(
      n_test = sum(is.finite(.data[[outvar]]) & is.finite(.pred)),
      sd_y   = sd(.data[[outvar]], na.rm = TRUE),
      
      # model metrics (recompute to ensure alignment with baseline)
      rmse = sqrt(mean((.data[[outvar]] - .pred)^2, na.rm = TRUE)),
      mae  = mean(abs(.data[[outvar]] - .pred), na.rm = TRUE),
      
      # baseline: constant prediction (mean of TEST)  ----
      # NOTE: optimistic lower bound; for strict baseline use TRAIN mean (save it in training)
      rmse_base = {
        mu <- mean(.data[[outvar]], na.rm = TRUE)
        sqrt(mean((.data[[outvar]] - mu)^2, na.rm = TRUE))
      },
      mae_base = {
        mu <- mean(.data[[outvar]], na.rm = TRUE)
        mean(abs(.data[[outvar]] - mu), na.rm = TRUE)
      },
      
      # normalized / skill
      nrmse = rmse / sd_y,
      rmse_skill = 1 - rmse / rmse_base,
      mae_skill  = 1 - mae  / mae_base,
      
      .groups = "drop"
    )
  
  shrink_from_preds <- preds %>%
    dplyr::group_by(filter_cohort, seed, save_string) %>%
    dplyr::summarise(
      slope = {
        fit <- stats::lm(.data[[outvar]] ~ .pred)
        unname(stats::coef(fit)[2])
      },
      intercept = {
        fit <- stats::lm(.data[[outvar]] ~ .pred)
        unname(stats::coef(fit)[1])
      },
      cor = stats::cor(.data[[outvar]], .pred, use = "complete.obs"),
      .groups = "drop"
    )
  
  write.csv(
    metrics_from_preds,
    file.path(OUT, paste0("deltaa1c_pred_metrics_by_seed_", date_tag, ".csv")),
    row.names = FALSE
  )
  
  write.csv(
    shrink_from_preds,
    file.path(OUT, paste0("deltaa1c_shrinkage_by_seed_", date_tag, ".csv")),
    row.names = FALSE
  )
}

# Join perf_by_seed with recomputed pred metrics if available
perf_joined <- perf_by_seed
if (!is.null(metrics_from_preds)) {
  perf_joined <- perf_joined %>%
    dplyr::left_join(
      metrics_from_preds %>% dplyr::select(filter_cohort, seed, rmse_base, mae_base, nrmse, rmse_skill, mae_skill, sd_y, n_test),
      by = c("filter_cohort","seed")
    )
}

write.csv(
  perf_joined,
  file.path(OUT, paste0("deltaa1c_perf_joined_", date_tag, ".csv")),
  row.names = FALSE
)

# -----------------------------
# Summaries across seeds + plots
# Uses t-interval (better for n=10)
# -----------------------------
summarize_metric <- function(df, metric_col, title, ylab, out_pdf, higher_better = FALSE) {
  sum_df <- df %>%
    dplyr::group_by(filter_cohort) %>%
    dplyr::summarise(
      mean = mean(.data[[metric_col]], na.rm = TRUE),
      sd   = sd(.data[[metric_col]], na.rm = TRUE),
      n    = dplyr::n(),
      se   = sd / sqrt(n),
      tcrit = stats::qt(0.975, df = pmax(n - 1, 1)),
      lwr  = mean - tcrit * se,
      upr  = mean + tcrit * se,
      .groups = "drop"
    ) %>%
    dplyr::mutate(order_key = if (higher_better) -mean else mean) %>%
    dplyr::arrange(order_key) %>%
    dplyr::mutate(filter_cohort = factor(filter_cohort, levels = filter_cohort)) %>%
    dplyr::select(-order_key)
  
  p <- ggplot(sum_df, aes(x = filter_cohort, y = mean, fill = filter_cohort)) +
    geom_col(width = 0.65, show.legend = FALSE, color = "black") +
    geom_errorbar(aes(ymin = lwr, ymax = upr), width = 0.2) +
    labs(title = title, x = NULL, y = ylab) +
    theme_minimal(base_size = 12) +
    theme(axis.text.x = element_text(angle = 15, hjust = 1))
  
  ggsave(p, filename = out_pdf, width = 5.5, height = 4)
  list(summary = sum_df, plot = p)
}

# RMSE
rmse_out <- summarize_metric(
  perf_joined,
  metric_col = "rmse",
  title = "Delta A1c regression: RMSE (mean ± 95% CI across seeds)",
  ylab = "RMSE",
  out_pdf = file.path(OUT, paste0("deltaa1c_rmse_by_cohort_", date_tag, ".pdf")),
  higher_better = FALSE
)

# MAE
mae_out <- summarize_metric(
  perf_joined,
  metric_col = "mae",
  title = "Delta A1c regression: MAE (mean ± 95% CI across seeds)",
  ylab = "MAE",
  out_pdf = file.path(OUT, paste0("deltaa1c_mae_by_cohort_", date_tag, ".pdf")),
  higher_better = FALSE
)

# R^2 (higher better)
rsq_out <- summarize_metric(
  perf_joined,
  metric_col = "rsq",
  title = "Delta A1c regression: R² (mean ± 95% CI across seeds)",
  ylab = "R²",
  out_pdf = file.path(OUT, paste0("deltaa1c_rsq_by_cohort_", date_tag, ".pdf")),
  higher_better = TRUE
)

write.csv(rsq_out$summary,
          file.path(OUT, paste0("deltaa1c_rsq_summary_", date_tag, ".csv")),
          row.names = FALSE)

# -----------------------------
# NEW: baseline + skill plots (comparable to PR lift in classification)
# -----------------------------
if (!is.null(metrics_from_preds)) {
  
  # Skill: 0 means no improvement over baseline mean predictor
  skill_rmse_out <- summarize_metric(
    perf_joined,
    metric_col = "rmse_skill",
    title = "Delta A1c regression: RMSE skill vs mean baseline (mean ± 95% CI)",
    ylab = "RMSE skill = 1 - RMSE/RMSE_base",
    out_pdf = file.path(OUT, paste0("deltaa1c_rmse_skill_by_cohort_", date_tag, ".pdf")),
    higher_better = TRUE
  )
  
  skill_mae_out <- summarize_metric(
    perf_joined,
    metric_col = "mae_skill",
    title = "Delta A1c regression: MAE skill vs mean baseline (mean ± 95% CI)",
    ylab = "MAE skill = 1 - MAE/MAE_base",
    out_pdf = file.path(OUT, paste0("deltaa1c_mae_skill_by_cohort_", date_tag, ".pdf")),
    higher_better = TRUE
  )
  
  # NRMSE (lower is better)
  nrmse_out <- summarize_metric(
    perf_joined,
    metric_col = "nrmse",
    title = "Delta A1c regression: NRMSE = RMSE / sd(delta) (mean ± 95% CI)",
    ylab = "NRMSE",
    out_pdf = file.path(OUT, paste0("deltaa1c_nrmse_by_cohort_", date_tag, ".pdf")),
    higher_better = FALSE
  )
  
  write.csv(skill_rmse_out$summary,
            file.path(OUT, paste0("deltaa1c_rmse_skill_summary_", date_tag, ".csv")),
            row.names = FALSE)
  
  write.csv(nrmse_out$summary,
            file.path(OUT, paste0("deltaa1c_nrmse_summary_", date_tag, ".csv")),
            row.names = FALSE)
}

# -----------------------------
# Optional: pooled truth vs predicted across seeds (already had)
# plus: mean-predictor reference line (horizontal at mean truth)
# -----------------------------
if (!is.null(preds) && nrow(preds) > 0) {
  
  # pooled scatter
  p_sc <- ggplot(preds, aes(x = .data[[outvar]], y = .pred)) +
    geom_point(alpha = 0.25) +
    geom_abline(slope = 1, intercept = 0) +
    facet_wrap(~filter_cohort, nrow = 1) +
    theme_bw() +
    labs(
      title = "Truth vs Predicted (pooled across seeds)",
      x = "Truth (delta_a1c_v1_v2)",
      y = "Predicted"
    )
  
  ggsave(p_sc,
         filename = file.path(OUT, paste0("deltaa1c_truth_vs_pred_pooled_", date_tag, ".pdf")),
         width = 9, height = 3.8)
  
  # NEW: distribution separation (pred vs truth density) — “mean-dominance” visual
  p_dens <- ggplot(preds, aes(x = .pred)) +
    geom_density(alpha = 0.2, linewidth = 0.9) +
    facet_wrap(~filter_cohort, nrow = 1, scales = "free_y") +
    theme_bw() +
    labs(
      title = "Predicted delta A1c distribution (pooled across seeds)",
      x = "Predicted delta_a1c_v1_v2",
      y = "Density"
    )
  
  ggsave(p_dens,
         filename = file.path(OUT, paste0("deltaa1c_pred_density_pooled_", date_tag, ".pdf")),
         width = 9, height = 3.4)
  
  # NEW: calibration-style bin plot (mean truth vs mean pred in bins)
  calib_df <- preds %>%
    group_by(filter_cohort, seed) %>%
    mutate(bin = ntile(.pred, 10)) %>%
    group_by(filter_cohort, seed, bin) %>%
    summarise(
      pred_mean = mean(.pred, na.rm=TRUE),
      truth_mean = mean(.data[[outvar]], na.rm=TRUE),
      n = n(),
      .groups="drop"
    )
  
  calib_sum <- calib_df %>%
    group_by(filter_cohort, bin) %>%
    summarise(
      pred_mean = mean(pred_mean, na.rm=TRUE),
      truth_mean = mean(truth_mean, na.rm=TRUE),
      .groups="drop"
    )
  
  p_cal <- ggplot(calib_sum, aes(x = pred_mean, y = truth_mean)) +
    geom_point(size = 2.2) +
    geom_abline(slope = 1, intercept = 0, linetype = "dashed") +
    facet_wrap(~filter_cohort, nrow = 1) +
    theme_bw() +
    labs(
      title = "Binned calibration (mean truth vs mean predicted delta A1c)",
      x = "Mean predicted (deciles)",
      y = "Mean truth (deciles)"
    )
  
  ggsave(p_cal,
         filename = file.path(OUT, paste0("deltaa1c_binned_calibration_", date_tag, ".pdf")),
         width = 9, height = 3.8)
}

# -----------------------------
# NEW: shrinkage diagnostics plots (slope, cor)
# -----------------------------
if (!is.null(shrink_from_preds) && nrow(shrink_from_preds) > 0) {
  
  # slope summary (mean ± 95% CI)
  slope_sum <- shrink_from_preds %>%
    group_by(filter_cohort) %>%
    summarise(
      mean = mean(slope, na.rm=TRUE),
      sd   = sd(slope, na.rm=TRUE),
      n    = n(),
      se   = sd / sqrt(n),
      tcrit = stats::qt(0.975, df = pmax(n - 1, 1)),
      lwr  = mean - tcrit * se,
      upr  = mean + tcrit * se,
      .groups="drop"
    ) %>%
    arrange(desc(mean)) %>%
    mutate(filter_cohort = factor(filter_cohort, levels = filter_cohort))
  
  p_slope <- ggplot(slope_sum, aes(x = filter_cohort, y = mean, fill = filter_cohort)) +
    geom_col(width = 0.65, show.legend = FALSE, color = "black") +
    geom_errorbar(aes(ymin = lwr, ymax = upr), width = 0.2) +
    geom_hline(yintercept = 1, linetype = "dashed", color = "gray55") +
    labs(
      title = "Shrinkage diagnostic: slope of truth ~ predicted (mean ± 95% CI)",
      subtitle = "Slope << 1 indicates predictions compressed toward the mean",
      x = NULL,
      y = "Slope"
    ) +
    theme_minimal(base_size = 12) +
    theme(axis.text.x = element_text(angle = 15, hjust = 1))
  
  ggsave(
    p_slope,
    filename = file.path(OUT, paste0("deltaa1c_shrinkage_slope_", date_tag, ".pdf")),
    width = 5.8, height = 4
  )
  
  # correlation summary
  cor_sum <- shrink_from_preds %>%
    group_by(filter_cohort) %>%
    summarise(
      mean = mean(cor, na.rm=TRUE),
      sd   = sd(cor, na.rm=TRUE),
      n    = n(),
      se   = sd / sqrt(n),
      tcrit = stats::qt(0.975, df = pmax(n - 1, 1)),
      lwr  = mean - tcrit * se,
      upr  = mean + tcrit * se,
      .groups="drop"
    ) %>%
    arrange(desc(mean)) %>%
    mutate(filter_cohort = factor(filter_cohort, levels = filter_cohort))
  
  p_cor <- ggplot(cor_sum, aes(x = filter_cohort, y = mean, fill = filter_cohort)) +
    geom_col(width = 0.65, show.legend = FALSE, color = "black") +
    geom_errorbar(aes(ymin = lwr, ymax = upr), width = 0.2) +
    labs(
      title = "Truth–prediction correlation (mean ± 95% CI across seeds)",
      x = NULL, y = "Correlation"
    ) +
    theme_minimal(base_size = 12) +
    theme(axis.text.x = element_text(angle = 15, hjust = 1))
  
  ggsave(
    p_cor,
    filename = file.path(OUT, paste0("deltaa1c_truth_pred_correlation_", date_tag, ".pdf")),
    width = 5.8, height = 4
  )
  
  write.csv(slope_sum,
            file.path(OUT, paste0("deltaa1c_shrinkage_slope_summary_", date_tag, ".csv")),
            row.names = FALSE)
  write.csv(cor_sum,
            file.path(OUT, paste0("deltaa1c_truth_pred_correlation_summary_", date_tag, ".csv")),
            row.names = FALSE)
}

# -----------------------------
# Optional: VI aggregation (as you had)
# -----------------------------
vi_files <- param_df$log_file[file.exists(param_df$log_file)]

if (length(vi_files) > 0) {
  vi_combined <- purrr::map_dfr(vi_files, function(f) {
    df <- read.csv(f, stringsAsFactors = FALSE)
    df$filter_cohort <- as.character(df$filter_cohort)
    df
  }) %>%
    dplyr::mutate(
      filter_cohort = dplyr::recode(filter_cohort,
                                    "0" = "BPRHS",
                                    "1" = "PROSPECT",
                                    "none" = "Both cohorts")
    )
  
  vi_mean <- vi_combined %>%
    group_by(filter_cohort, Variable, type) %>%
    summarise(mean_imp = mean(Importance, na.rm = TRUE), .groups = "drop") %>%
    group_by(filter_cohort) %>%
    slice_max(mean_imp, n = 20, with_ties = FALSE) %>%
    ungroup()
  
  p_vi <- ggplot(vi_mean, aes(x = mean_imp, y = reorder(Variable, mean_imp), fill = type)) +
    geom_col() +
    facet_wrap(~filter_cohort, scales = "free_y") +
    theme_minimal(base_size = 12) +
    labs(title = "Top variable importance (mean across seeds)",
         x = "Mean importance", y = NULL)
  
  ggsave(p_vi,
         filename = file.path(OUT, paste0("deltaa1c_vi_top20_mean_", date_tag, ".pdf")),
         width = 10, height = 7)
  
  write.csv(vi_combined,
            file.path(OUT, paste0("deltaa1c_vi_all_", date_tag, ".csv")),
            row.names = FALSE)
}

library(dplyr)

message("DONE.")

