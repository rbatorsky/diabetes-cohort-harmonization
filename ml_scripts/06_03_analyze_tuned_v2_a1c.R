# ============================================================
# A1c V2 regression results (equivalent to delta-a1c section)
# Reads:
#   - preferred: a1cv2_perf_joined_<save_string>.csv  (per run)
#   - fallback : perf_<save_string>.csv + test_predictions_<save_string>.rds
# Writes:
#   - a1cv2_perf_joined_<date_tag>.csv (combined across seeds)
#   - plots: rmse/mae/rsq + rmse_skill + nrmse
# ============================================================

IN <- "../../analysis/"
OUT <- "../../plots_v2_a1c"
dir.create(OUT, showWarnings = FALSE, recursive = TRUE)

# -----------------------------
# MUST match the V2-A1c training run family
# -----------------------------
outvar <- "a1c_v2"
visit  <- "a1c_change"
data_string <- "all"
cross_cohort_val <- 0
date_tag <- "24feb26"
seeds <- 1:10
filter_cohorts <- c("0","1","none")

# -----------------------------
# save_string builder (must match training script)
# -----------------------------
make_save_string_v2 <- function(filter_cohort, seed) {
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
# Param grid + file paths
# -----------------------------
param_df_v2 <- expand.grid(
  filter_cohort = filter_cohorts,
  seed = seeds,
  stringsAsFactors = FALSE
) %>%
  tibble::as_tibble() %>%
  mutate(
    save_string = purrr::map2_chr(filter_cohort, seed, make_save_string_v2),
    joined_file = file.path(IN, paste0("a1cv2_perf_joined_", save_string, ".csv")),
    perf_file   = file.path(IN, paste0("perf_", save_string, ".csv")),
    pred_file   = file.path(IN, paste0("test_predictions_", save_string, ".rds")),
    log_file    = file.path(IN, paste0("log_", save_string, ".csv"))
  )

recode_filter <- function(f) {
  dplyr::recode(f, "0"="BPRHS", "1"="PROSPECT", "none"="Both cohorts")
}

# -----------------------------
# Preferred: read the per-run joined CSVs (contains baseline + skill)
# -----------------------------
v2_join_list <- list()
missing_join <- 0L

for (i in seq_len(nrow(param_df_v2))) {
  fp <- param_df_v2$joined_file[i]
  if (!file.exists(fp)) {
    missing_join <- missing_join + 1L
    next
  }
  v2_join_list[[length(v2_join_list)+1L]] <- readr::read_csv(fp, show_col_types = FALSE)
}

# If joined files not found, fallback to recompute baseline+skill from preds
if (length(v2_join_list) == 0) {
  message("No a1cv2_perf_joined_<save_string>.csv found; falling back to perf_ + predictions to compute baseline+skill.")
  
  perf_list <- list()
  pred_list <- list()
  
  for (i in seq_len(nrow(param_df_v2))) {
    # perf
    if (file.exists(param_df_v2$perf_file[i])) {
      dfp <- read.csv(param_df_v2$perf_file[i], stringsAsFactors = FALSE) %>%
        dplyr::select(.metric, .estimate) %>%
        tidyr::pivot_wider(names_from = .metric, values_from = .estimate) %>%
        dplyr::mutate(
          filter_cohort_raw = param_df_v2$filter_cohort[i],
          filter_cohort = recode_filter(param_df_v2$filter_cohort[i]),
          seed = param_df_v2$seed[i],
          save_string = param_df_v2$save_string[i]
        )
      perf_list[[length(perf_list)+1L]] <- dfp
    }
    
    # preds
    if (file.exists(param_df_v2$pred_file[i])) {
      tp <- readRDS(param_df_v2$pred_file[i])
      if (all(c(outvar, ".pred", "a1c_v1") %in% names(tp))) {
        pred_list[[length(pred_list)+1L]] <- tp %>%
          dplyr::mutate(
            filter_cohort_raw = param_df_v2$filter_cohort[i],
            filter_cohort = recode_filter(param_df_v2$filter_cohort[i]),
            seed = param_df_v2$seed[i],
            save_string = param_df_v2$save_string[i]
          )
      }
    }
  }
  
  stopifnot(length(perf_list) > 0, length(pred_list) > 0)
  
  perf_by_seed_v2 <- dplyr::bind_rows(perf_list)
  preds_v2 <- dplyr::bind_rows(pred_list)
  
  # Compute baseline ("no-change": a1c_v2 = a1c_v1) + skill, consistent with your training logs
  metrics_from_preds_v2 <- preds_v2 %>%
    dplyr::group_by(filter_cohort, seed, save_string) %>%
    dplyr::summarise(
      n_test = sum(is.finite(.data[[outvar]]) & is.finite(.pred)),
      sd_y   = stats::sd(.data[[outvar]], na.rm = TRUE),
      rmse_base = yardstick::rmse_vec(truth = .data[[outvar]], estimate = .data[["a1c_v1"]]),
      mae_base  = yardstick::mae_vec (truth = .data[[outvar]], estimate = .data[["a1c_v1"]]),
      .groups = "drop"
    )
  
  v2_joined <- perf_by_seed_v2 %>%
    dplyr::left_join(metrics_from_preds_v2, by = c("filter_cohort","seed","save_string")) %>%
    dplyr::mutate(
      nrmse = rmse / sd_y,
      rmse_skill = 1 - (rmse / rmse_base),
      mae_skill  = 1 - (mae  / mae_base)
    )
  
} else {
  # If we found the joined per-run files, bind and (optionally) enforce consistent columns
  v2_joined <- dplyr::bind_rows(v2_join_list) %>%
    dplyr::mutate(
      # In case filter_cohort came through as raw codes:
      filter_cohort = dplyr::case_when(
        filter_cohort %in% c("0","1","none") ~ recode_filter(filter_cohort),
        TRUE ~ as.character(filter_cohort)
      )
    )
}

# -----------------------------
# Write combined across seeds
# -----------------------------
readr::write_csv(
  v2_joined,
  file.path(OUT, paste0("a1cv2_perf_joined_", date_tag, ".csv"))
)

# -----------------------------
# Summaries across seeds + plots (match delta-a1c style)
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
  
  p <- ggplot2::ggplot(sum_df, ggplot2::aes(x = filter_cohort, y = mean, fill = filter_cohort)) +
    ggplot2::geom_col(width = 0.65, show.legend = FALSE, color = "black") +
    ggplot2::geom_errorbar(ggplot2::aes(ymin = lwr, ymax = upr), width = 0.2) +
    ggplot2::labs(title = title, x = NULL, y = ylab) +
    ggplot2::theme_minimal(base_size = 12) +
    ggplot2::theme(axis.text.x = ggplot2::element_text(angle = 15, hjust = 1))
  
  ggplot2::ggsave(p, filename = out_pdf, width = 5.5, height = 4)
  list(summary = sum_df, plot = p)
}

# RMSE / MAE / R2
rmse_out_v2 <- summarize_metric(
  v2_joined, "rmse",
  title = "A1c V2 regression: RMSE (mean ± 95% CI across seeds)",
  ylab  = "RMSE",
  out_pdf = file.path(OUT, paste0("a1cv2_rmse_by_cohort_", date_tag, ".pdf")),
  higher_better = FALSE
)

mae_out_v2 <- summarize_metric(
  v2_joined, "mae",
  title = "A1c V2 regression: MAE (mean ± 95% CI across seeds)",
  ylab  = "MAE",
  out_pdf = file.path(OUT, paste0("a1cv2_mae_by_cohort_", date_tag, ".pdf")),
  higher_better = FALSE
)

rsq_out_v2 <- summarize_metric(
  v2_joined, "rsq",
  title = "A1c V2 regression: R² (mean ± 95% CI across seeds)",
  ylab  = "R²",
  out_pdf = file.path(OUT, paste0("a1cv2_rsq_by_cohort_", date_tag, ".pdf")),
  higher_better = TRUE
)

# Skill + NRMSE (if available)
if (all(c("rmse_skill","nrmse") %in% names(v2_joined))) {
  rmse_skill_out_v2 <- summarize_metric(
    v2_joined, "rmse_skill",
    title = "A1c V2 regression: RMSE skill vs no-change baseline (mean ± 95% CI)",
    ylab  = "RMSE skill = 1 - RMSE/RMSE_base",
    out_pdf = file.path(OUT, paste0("a1cv2_rmse_skill_by_cohort_", date_tag, ".pdf")),
    higher_better = TRUE
  )
  
  nrmse_out_v2 <- summarize_metric(
    v2_joined, "nrmse",
    title = "A1c V2 regression: NRMSE = RMSE / sd(A1c_v2) (mean ± 95% CI)",
    ylab  = "NRMSE",
    out_pdf = file.path(OUT, paste0("a1cv2_nrmse_by_cohort_", date_tag, ".pdf")),
    higher_better = FALSE
  )
}

# -----------------------------
# VI aggregation (mirrors 06_01)
# -----------------------------
vi_files_v2 <- param_df_v2$log_file[file.exists(param_df_v2$log_file)]

if (length(vi_files_v2) > 0) {
  vi_combined_v2 <- purrr::map_dfr(vi_files_v2, function(f) {
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
  
  vi_mean_v2 <- vi_combined_v2 %>%
    dplyr::group_by(filter_cohort, Variable, type) %>%
    dplyr::summarise(mean_imp = mean(Importance, na.rm = TRUE), .groups = "drop") %>%
    dplyr::group_by(filter_cohort) %>%
    dplyr::slice_max(mean_imp, n = 20, with_ties = FALSE) %>%
    dplyr::ungroup()
  
  p_vi_v2 <- ggplot2::ggplot(
    vi_mean_v2,
    ggplot2::aes(x = mean_imp, y = reorder(Variable, mean_imp), fill = type)
  ) +
    ggplot2::geom_col() +
    ggplot2::facet_wrap(~filter_cohort, scales = "free_y") +
    ggplot2::theme_minimal(base_size = 12) +
    ggplot2::labs(
      title = "A1c V2: Top variable importance (mean across seeds)",
      x = "Mean importance", y = NULL
    )
  
  ggplot2::ggsave(
    p_vi_v2,
    filename = file.path(OUT, paste0("a1cv2_vi_top20_mean_", date_tag, ".pdf")),
    width = 10, height = 7
  )
  
  write.csv(vi_combined_v2,
            file.path(OUT, paste0("a1cv2_vi_all_", date_tag, ".csv")),
            row.names = FALSE)
  
  message("Wrote VI outputs to: ", normalizePath(OUT))
}

message("DONE: wrote combined a1cv2_perf_joined + plots to: ", normalizePath(OUT))