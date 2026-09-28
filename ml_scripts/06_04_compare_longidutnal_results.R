## ============================================================
## make_longitudinal_table.R
##
## Assembles Table 2: Longitudinal Prediction Performance
## from the aggregated summary files produced by your pipeline.
##
## Source files (match paths used in your plotting script):
##   plots_deltadiab/deltadiab_progression_summary_{date_tag}.csv
##     → pr_auc_mean, pr_auc_sd, pr_lift_mean, filter_cohort, cross_cohort_val
##
##   plots_deltaa1c/deltaa1c_perf_joined_{date_tag}.csv
##     → per-seed rows: rmse_skill, rmse, mae, rsq, filter_cohort
##
##   a1cv2_perf_joined_{date_tag}.csv
##     → per-seed rows: rmse_skill, rmse_base, rmse, mae, rsq, filter_cohort, n_test
## ============================================================

library(dplyr)
library(tidyr)
library(readr)
library(openxlsx)
library(ggplot2)

# ── User settings ─────────────────────────────────────────────────────────────
OUT_RESULTS <- "../../"
DATE_TAG    <- "24feb26"
PLOT_DIR    <- file.path(OUT_RESULTS, "plots_slide")
dir.create(PLOT_DIR, showWarnings = FALSE, recursive = TRUE)

PROG_SUMMARY_CSV <- file.path(OUT_RESULTS, "plots_deltadiab",
                              paste0("deltadiab_progression_summary_", DATE_TAG, ".csv"))
DELTA_A1C_CSV    <- file.path(OUT_RESULTS, "plots_deltaa1c",
                              paste0("deltaa1c_perf_joined_", DATE_TAG, ".csv"))
A1CV2_CSV        <- file.path(OUT_RESULTS, "plots_v2_a1c",
                              paste0("a1cv2_perf_joined_", DATE_TAG, ".csv"))

# ── Helper: mean +/- 95% CI from per-seed rows --------------------------------
summ_ci <- function(x) {
  x <- x[is.finite(x)]
  n <- length(x)
  if (n == 0) return(list(mean = NA_real_, lwr = NA_real_, upr = NA_real_, n = 0L))
  m  <- mean(x)
  se <- sd(x) / sqrt(n)
  tc <- qt(0.975, df = max(n - 1, 1))
  list(mean = m, lwr = m - tc * se, upr = m + tc * se, n = as.integer(n))
}

# ── Helper: format "0.xxx (0.xxx-0.xxx)" -------------------------------------
fmt_ci <- function(mean, lwr, upr, digits = 3) {
  ifelse(
    is.na(mean),
    NA_character_,
    sprintf("%.*f (%.*f-%.*f)", digits, mean, digits, lwr, digits, upr)
  )
}

# Cohort label values expected in the files
valid_cohorts <- c("Both cohorts", "BPRHS", "PROSPECT")
cohort_order  <- valid_cohorts
task_order    <- c("Diabetes progression (V1-V2)",
                   "Delta HbA1c regression",
                   "HbA1c at V2 regression")

# ── 1. Diabetes Progression (binary classifier) --------------------------------
# Summary CSV already has one aggregated row per (filter_cohort, cross_cohort_val)
# Columns used: pr_auc_mean, pr_auc_sd, pr_lift_mean, filter_cohort
prog_raw <- read_csv(PROG_SUMMARY_CSV, show_col_types = FALSE)

# Assume 10 seeds if n_seeds column not present; adjust if stored
N_SEEDS <- if ("n_seeds" %in% names(prog_raw)) NULL else 10L

prog_prep <- prog_raw %>%
  filter(cross_cohort_val == 0,
         filter_cohort %in% valid_cohorts) %>%
  mutate(
    n_s = if (!is.null(N_SEEDS)) N_SEEDS else n_seeds,
    tc  = qt(0.975, df = pmax(n_s - 1, 1)),
    pr_auc_lwr = pr_auc_mean - tc * pr_auc_sd / sqrt(n_s),
    pr_auc_upr = pr_auc_mean + tc * pr_auc_sd / sqrt(n_s)
  )

# Keep numeric skill values for the plot (pr_lift; no CI available from summary file)
prog_skill <- prog_prep %>%
  transmute(
    model      = "Progression (binary)",
    Cohort     = filter_cohort,
    skill_mean = pr_lift_mean,
    skill_lwr  = NA_real_,
    skill_upr  = NA_real_
  )

prog <- prog_prep %>%
  transmute(
    Task          = "Diabetes progression (V1-V2)",
    Cohort        = filter_cohort,
    `PR-AUC`      = fmt_ci(pr_auc_mean, pr_auc_lwr, pr_auc_upr),
    `PR lift`     = round(pr_lift_mean, 3),
    `RMSE`        = NA_character_,
    `R-squared`   = NA_character_,
    `Baseline RMSE` = NA_real_,
    `RMSE skill`  = NA_character_
  )

# ── 2. Delta HbA1c Regression -------------------------------------------------
delta_raw <- read_csv(DELTA_A1C_CSV, show_col_types = FALSE)

delta_agg <- delta_raw %>%
  filter(filter_cohort %in% valid_cohorts) %>%
  group_by(Cohort = filter_cohort) %>%
  summarise(
    rmse_ci   = list(summ_ci(rmse)),
    rsq_ci    = list(summ_ci(rsq)),
    skill_ci  = list(summ_ci(rmse_skill)),
    .groups   = "drop"
  )

# Keep numeric skill values for the plot
delta_skill <- delta_agg %>%
  rowwise() %>%
  transmute(
    model      = "Delta A1c (regression)",
    Cohort,
    skill_mean = skill_ci$mean,
    skill_lwr  = skill_ci$lwr,
    skill_upr  = skill_ci$upr
  ) %>%
  ungroup()

delta <- delta_agg %>%
  rowwise() %>%
  transmute(
    Task          = "Delta HbA1c regression",
    Cohort,
    `PR-AUC`      = NA_character_,
    `PR lift`     = NA_real_,
    `RMSE`        = fmt_ci(rmse_ci$mean,  rmse_ci$lwr,  rmse_ci$upr),
    `R-squared`   = fmt_ci(rsq_ci$mean,   rsq_ci$lwr,   rsq_ci$upr),
    `Baseline RMSE` = NA_real_,
    `RMSE skill`  = fmt_ci(skill_ci$mean, skill_ci$lwr, skill_ci$upr)
  )

# ── 3. HbA1c at V2 Regression -------------------------------------------------
a1cv2_raw <- read_csv(A1CV2_CSV, show_col_types = FALSE)

a1cv2_agg <- a1cv2_raw %>%
  filter(filter_cohort %in% valid_cohorts) %>%
  group_by(Cohort = filter_cohort) %>%
  summarise(
    rmse_ci    = list(summ_ci(rmse)),
    rsq_ci     = list(summ_ci(rsq)),
    skill_ci   = list(summ_ci(rmse_skill)),
    rmse_base  = mean(rmse_base, na.rm = TRUE),
    .groups    = "drop"
  )

# Keep numeric skill values for the plot
a1cv2_skill <- a1cv2_agg %>%
  rowwise() %>%
  transmute(
    model      = "A1c V2 (regression)",
    Cohort,
    skill_mean = skill_ci$mean,
    skill_lwr  = skill_ci$lwr,
    skill_upr  = skill_ci$upr
  ) %>%
  ungroup()

a1cv2 <- a1cv2_agg %>%
  rowwise() %>%
  transmute(
    Task          = "HbA1c at V2 regression",
    Cohort,
    `PR-AUC`      = NA_character_,
    `PR lift`     = NA_real_,
    `RMSE`        = fmt_ci(rmse_ci$mean,  rmse_ci$lwr,  rmse_ci$upr),
    `R-squared`   = fmt_ci(rsq_ci$mean,   rsq_ci$lwr,   rsq_ci$upr),
    `Baseline RMSE` = round(rmse_base, 3),
    `RMSE skill`  = fmt_ci(skill_ci$mean, skill_ci$lwr, skill_ci$upr)
  )

# ── Combine and order ---------------------------------------------------------
table2 <- bind_rows(prog, delta, a1cv2) %>%
  mutate(
    Task   = factor(Task,   levels = task_order),
    Cohort = factor(Cohort, levels = cohort_order)
  ) %>%
  arrange(Task, Cohort)

table2

# ── Print to console ----------------------------------------------------------
cat("\nTable 2: Longitudinal Prediction Performance\n")
cat(strrep("-", 90), "\n")
print(knitr::kable(table2, format = "simple", na = "---"))

# ── Save as Excel -------------------------------------------------------------
wb <- createWorkbook()
addWorksheet(wb, "Table2")

# Styles
header_style <- createStyle(
  fontSize = 11, fontColour = "#FFFFFF", bgFill = "#2E4057",
  halign = "center", valign = "center", textDecoration = "bold",
  wrapText = TRUE
)
task_fills <- list(
  createStyle(bgFill = "#EBF3FB"),   # progression - blue tint
  createStyle(bgFill = "#FEF9F0"),   # delta A1c   - warm tint
  createStyle(bgFill = "#F0FAF2")    # V2 A1c      - green tint
)
bold_style   <- createStyle(textDecoration = "bold")
center_style <- createStyle(halign = "center")


writeData(wb, "Table2", table2, startRow = 1, startCol = 1)

nc <- ncol(table2)
nr <- nrow(table2)

# Header row
addStyle(wb, "Table2", header_style, rows = 1, cols = 1:nc, gridExpand = TRUE)

# Task-group row shading: 3 rows per task -> data rows 2-4, 5-7, 8-10
for (t in seq_along(task_fills)) {
  data_rows <- seq(1 + (t - 1) * 3 + 1, 1 + t * 3)
  for (r in data_rows) {
    addStyle(wb, "Table2", task_fills[[t]], rows = r, cols = 1:nc,
             gridExpand = TRUE, stack = TRUE)
  }
}

# Center numeric columns; bold "Both cohorts" rows
for (r in 2:(nr + 1)) {
  addStyle(wb, "Table2", center_style, rows = r, cols = 3:nc,
           gridExpand = TRUE, stack = TRUE)
  if (as.character(table2$Cohort[r - 1]) == "Both cohorts") {
    addStyle(wb, "Table2", bold_style, rows = r, cols = 1:nc,
             gridExpand = TRUE, stack = TRUE)
  }
}

# Column widths
setColWidths(wb, "Table2", cols = 1, widths = 26)
setColWidths(wb, "Table2", cols = 2, widths = 14)
setColWidths(wb, "Table2", cols = 3:nc, widths = 20)

freezePane(wb, "Table2", firstRow = TRUE)

out_xlsx <- file.path(OUT_RESULTS,
                      paste0("table2_longitudinal_performance_", DATE_TAG, ".xlsx"))
saveWorkbook(wb, out_xlsx, overwrite = TRUE)
message("Saved: ", out_xlsx)

# ── Skill vs Baseline Plot ─────────────────────────────────────────────────────
# Combines all three models; one panel per cohort.
# Progression uses PR lift; regressions use RMSE skill (1 - RMSE_model/RMSE_base).
# Note: progression skill_lwr/upr are NA because the summary file stores pr_auc_sd
# but not sd(pr_lift). Add per-seed pr_lift to the summary file to enable those CIs.

model_levels <- c("Progression (binary)", "Delta A1c (regression)", "A1c V2 (regression)")

plot_df <- bind_rows(prog_skill, delta_skill, a1cv2_skill) %>%
  mutate(
    model  = factor(model,  levels = model_levels),
    Cohort = factor(Cohort, levels = cohort_order)
  )

p_skill <- ggplot(plot_df, aes(x = model, y = skill_mean, color = Cohort, shape = Cohort)) +
  geom_hline(yintercept = 0, color = "gray60", linetype = "dashed") +
  geom_point(size = 3, position = position_dodge(width = 0.4)) +
  geom_errorbar(
    aes(ymin = skill_lwr, ymax = skill_upr),
    width = 0.15,
    na.rm = TRUE,
    position = position_dodge(width = 0.4)
  ) +
  coord_flip() +
  scale_color_manual(values = c(
    "Both cohorts" = "#2E4057",
    "BPRHS"        = "#E07A5F",
    "PROSPECT"     = "#3D9970"
  )) +
  labs(
    title    = "Model skill vs baseline — longitudinal tasks",
    subtitle = paste(
      "Progression: PR lift over prevalence baseline",
      "Regressions: RMSE skill vs carry-forward baseline (a1c_v1)",
      sep = "\n"
    ),
    x     = NULL,
    y     = "Skill score (higher is better; 0 = no improvement over baseline)",
    color = "Cohort",
    shape = "Cohort"
  ) +
  theme_minimal(base_size = 13) +
  theme(
    legend.position  = "right",
    plot.subtitle    = element_text(size = 10, color = "gray40"),
    panel.grid.minor = element_blank()
  )

out_pdf <- file.path(PLOT_DIR,
                     paste0("skill_vs_baseline_three_models_", DATE_TAG, ".pdf"))
ggsave(out_pdf, p_skill, width = 9, height = 4)
message("Saved: ", out_pdf)