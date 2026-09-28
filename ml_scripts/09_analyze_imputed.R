LIB="/cluster/tufts/patralab/rbator01/R_libs/4.4.0/"
.libPaths(LIB)

source("utils.R")

pkgs <- c(
  "openxlsx", "tidymodels", "tidyverse", "workflows", "tune", "compositions",
  "caret", "VIM", "visdat", "recipes", "themis", "forcats", "tidytext",
  "purrr", "tibble", "dplyr", "tidyr", "ggplot2"
)

invisible(lapply(pkgs, quiet_library))

OUT_RESULTS <- "../../analysis/"
PLOT_DIR    <- "../../analysis/plots"
RDS1 = "../../analysis/harmonize_2cohort_healthsdohffq_v1_rmmissing_50col_10row_preproc_for_eda.rds"
outpath  = "../../analysis/plots/select_feature_plots"

noBR_df = readRDS("../../analysis/eda_preproc_v1_noBR.rds")
BR_df  = readRDS("../../analysis/eda_preproc_v1_BR.rds")


## ---- Compare key vars: raw (NoBR) vs batch-regressed (BR) ----

dir.create(outpath, recursive = TRUE, showWarnings = FALSE)

# Raw (imputed/corr, pre-normalization)

# choose a few key variables to inspect imputation effect
vi_combined = read.csv("../../analysis/results/combined_vi_17nov25.csv")

# summarize by variable across seeds/runs
vi_summary <- vi_combined %>%
  group_by(Variable, type) %>%
  summarise(mean_importance = mean(Importance, na.rm = TRUE),
            sd_importance = sd(Importance, na.rm = TRUE),
            n = n()) %>%
  ungroup() %>%
  arrange(desc(mean_importance))

# create the full original variable name
vi_summary <- vi_summary %>%
  mutate(full_name = paste0("hmz_", type, "_", Variable))

head(vi_summary)

# get top 10 distinct variables by average importance
top10_summary <- vi_summary %>%
  slice_head(n = 10)

key_vars <- top10_summary$full_name

key_vars

raw_keep <- noBR_df %>%
  dplyr::select(row_id, diabetes, cohort, dplyr::all_of(key_vars)) %>%
  dplyr::rename_with(~ paste0(.x, "__raw"), dplyr::all_of(key_vars))

# BR (pre-normalization)
br_keep <- BR_df %>%
  dplyr::select(row_id, dplyr::all_of(key_vars)) %>%
  dplyr::rename_with(~ paste0(.x, "__br"), dplyr::all_of(key_vars))

compare_tbl <- raw_keep %>%
  dplyr::left_join(br_keep, by = "row_id")

# Deltas (BR - Raw)
for (v in key_vars) {
  raw_col <- paste0(v, "__raw")
  br_col  <- paste0(v, "__br")
  compare_tbl[[paste0(v, "__deltaBR")]] <-
    suppressWarnings(as.numeric(compare_tbl[[br_col]]) - as.numeric(compare_tbl[[raw_col]]))
}

readr::write_csv(compare_tbl, file.path(outpath, "batch_regression_compare_keyvars_wide_nofiltage_17nov25.csv"))

# Long/tidy for plotting
compare_long <- compare_tbl %>%
  dplyr::select(row_id, diabetes, cohort,
                tidyselect::matches(paste0("^(", paste(key_vars, collapse="|"), ")__(raw|br|deltaBR)$"))) %>%
  tidyr::pivot_longer(
    cols = -c(row_id, diabetes, cohort),
    names_to = c("variable", ".value"),
    names_pattern = "^(.*)__(raw|br|deltaBR)$"
  )

readr::write_csv(compare_long, file.path(outpath, "batch_regression_compare_keyvars_long_nofiltage_27oct25.csv"))

## ---- Quick plots ----
p1 <- compare_long %>%
  tidyr::pivot_longer(cols = c(raw, br), names_to = "state", values_to = "value") %>%
  ggplot2::ggplot(ggplot2::aes(x = cohort, y = value, fill = state)) +
  ggplot2::geom_boxplot(outlier.shape = NA, alpha = 0.85, width = 0.7) +
  ggplot2::facet_wrap(~ variable, scales = "free_y") +
  ggplot2::labs(title = "Key variables: raw vs batch-regressed (pre-normalization)",
                x = "Cohort", y = "Value") +
  ggplot2::theme_bw()
#ggplot2::ggsave(file.path(outpath, "keyvars_raw_vs_BR_by_cohort.png"), p1, width = 12, height = 8, dpi = 300)

print(p1)

p2 <- compare_long %>%
  ggplot2::ggplot(ggplot2::aes(x = cohort, y = deltaBR)) +
  ggplot2::geom_boxplot(outlier.shape = NA, width = 0.7) +
  ggplot2::facet_wrap(~ variable, scales = "free_y") +
  ggplot2::labs(title = "Batch regression deltas (BR - Raw) by cohort",
                x = "Cohort", y = "Δ after batch regression") +
  ggplot2::theme_bw()
#ggplot2::ggsave(file.path(outpath, "keyvars_deltaBR_by_cohort.png"), p2, width = 12, height = 8, dpi = 300)
print(p2)


## -------- Find variables most affected by batch regression --------
# numeric columns present in both (exclude cohort/diabetes/row_id/weight if present)

# columns to exclude from numeric set
exclude_cols <- c("cohort", "diabetes", "row_id", "weight")

# strictly numeric predictors present in both data frames
num_cols <- names(noBR_df)[vapply(noBR_df, is.numeric, logical(1))]
num_cols <- setdiff(num_cols, exclude_cols)
num_cols <- intersect(num_cols, names(BR_df))

# defensively coerce to numeric in both branches
noBR_num <- noBR_df %>%
  mutate(across(all_of(num_cols), ~ suppressWarnings(as.numeric(.))))
BR_num <- BR_df %>%
  mutate(across(all_of(num_cols), ~ suppressWarnings(as.numeric(.))))

# build long, collapse duplicates per (row_id, variable, state), then widen
stacked <- bind_rows(
  noBR_num %>% select(row_id, all_of(num_cols)) %>% mutate(state = "raw"),
  BR_num   %>% select(row_id, all_of(num_cols)) %>% mutate(state = "br")
) %>%
  pivot_longer(cols = all_of(num_cols), names_to = "variable", values_to = "value") %>%
  group_by(row_id, variable, state) %>%
  summarise(value = mean(value, na.rm = TRUE), .groups = "drop") %>%  # <-- collapse dupes
  pivot_wider(names_from = state, values_from = value) %>%
  left_join(noBR_df %>% select(row_id, cohort), by = "row_id") %>%
  mutate(cohort = as.factor(cohort))

stacked


# optional: quick diagnostic of any remaining NAs after coercion
stacked %>% summarise(na_raw = sum(is.na(raw)), na_br = sum(is.na(br)))

# compute effects (now raw/br are plain numeric)
var_effects <- stacked %>%
  group_by(variable) %>%
  summarise(
    n = n(),
    med_abs_delta  = median(abs(br - raw), na.rm = TRUE),
    mean_abs_delta = mean(abs(br - raw), na.rm = TRUE),
    rms_delta      = sqrt(mean((br - raw)^2, na.rm = TRUE)),
    sd_raw         = sd(raw, na.rm = TRUE),
    rel_med_abs_delta = ifelse(sd_raw > 0, med_abs_delta / sd_raw, NA_real_),
    r2_raw = {
      m <- try(lm(raw ~ cohort), silent = TRUE)
      if (inherits(m, "try-error")) NA_real_ else summary(m)$r.squared
    },
    r2_br = {
      m <- try(lm(br ~ cohort), silent = TRUE)
      if (inherits(m, "try-error")) NA_real_ else summary(m)$r.squared
    },
    r2_drop = r2_raw - r2_br,
    .groups = "drop"
  )

# Choose how many more to add:
n_add <- 10  # tweak as you like

# Rank by two criteria and combine:
rank_rel_delta <- var_effects %>%
  arrange(desc(rel_med_abs_delta)) %>%
  filter(!is.na(rel_med_abs_delta)) %>%
  pull(variable)

rank_r2_drop <- var_effects %>%
  arrange(desc(r2_drop)) %>%
  filter(!is.na(r2_drop)) %>%
  pull(variable)

# Weighted combo ranking (tie-break by both signals)
rank_combo <- var_effects %>%
  mutate(
    rank_rel = rank(-replace_na(rel_med_abs_delta, -Inf), ties.method = "average"),
    rank_r2  = rank(-replace_na(r2_drop, -Inf),           ties.method = "average"),
    score = (rank_rel + rank_r2)   # lower is better
  ) %>%
  arrange(score) %>%
  pull(variable)

# Pick the top additional variables not already in your key_vars
add_by_combo <- setdiff(rank_combo, key_vars)[1:n_add]
add_by_combo <- add_by_combo[!is.na(add_by_combo)]

# Final expanded set
key_vars_expanded <- unique(c(key_vars, add_by_combo))
message("Added vars (most affected by batch regression): ",
        paste(setdiff(key_vars_expanded, key_vars), collapse = ", "))

## -------- Rebuild compare tables/plots with expanded set --------
outpath <- "r_pipeline/analysis/select_feature_plots"
dir.create(outpath, recursive = TRUE, showWarnings = FALSE)

# Ensure row_id exists
if (!"row_id" %in% names(noBR_df)) {
  noBR_df <- noBR_df %>% mutate(row_id = row_number())
}
if (!"row_id" %in% names(BR_df)) {
  BR_df <- BR_df %>% mutate(row_id = row_number())
}

# Wide compare
raw_keep <- noBR_df %>%
  select(row_id, diabetes, cohort, all_of(key_vars_expanded)) %>%
  rename_with(~ paste0(.x, "__raw"), all_of(key_vars_expanded))

br_keep <- BR_df %>%
  select(row_id, all_of(key_vars_expanded)) %>%
  rename_with(~ paste0(.x, "__br"), all_of(key_vars_expanded))

compare_tbl2 <- raw_keep %>%
  left_join(br_keep, by = "row_id")

for (v in key_vars_expanded) {
  compare_tbl2[[paste0(v, "__deltaBR")]] <-
    suppressWarnings(as.numeric(compare_tbl2[[paste0(v, "__br")]]) -
                       as.numeric(compare_tbl2[[paste0(v, "__raw")]]))
}

readr::write_csv(compare_tbl2, file.path(outpath, "batch_regression_compare_keyvars_wide_EXPANDED_17nov25.csv"))

# Long for plots
compare_long2 <- compare_tbl2 %>%
  select(row_id, diabetes, cohort,
         matches(paste0("^(", paste(key_vars_expanded, collapse="|"),
                        ")__(raw|br|deltaBR)$"))) %>%
  pivot_longer(
    cols = -c(row_id, diabetes, cohort),
    names_to = c("variable", ".value"),
    names_pattern = "^(.*)__(raw|br|deltaBR)$"
  )

readr::write_csv(compare_long2, file.path(outpath, "batch_regression_compare_keyvars_long_EXPANDED_17nov25.csv"))

## -------- Plots (with winsorized y as before) --------
p_cap <- 0.99
df_long_cap <- compare_long2 %>%
  pivot_longer(cols = c(raw, br), names_to = "state", values_to = "value") %>%
  group_by(variable) %>%
  mutate(
    lower_cap = quantile(value, probs = 1 - p_cap, na.rm = TRUE),
    upper_cap = quantile(value, probs = p_cap,     na.rm = TRUE),
    value_capped = pmin(pmax(value, lower_cap), upper_cap)
  ) %>%
  ungroup()

p1_exp <- df_long_cap %>%
  ggplot(aes(x = cohort, y = value_capped, fill = state)) +
  geom_boxplot(outlier.shape = NA, alpha = 0.85, width = 0.7) +
  facet_wrap(~ variable, scales = "free_y") +
  labs(
    title = "Raw vs batch-regressed (expanded set)",
    subtitle = paste0("Added vars = most affected by regression; winsorized at ",
                      100*(1-p_cap), "%–", 100*p_cap, "%"),
    x = "Cohort", y = "Value (winsorized)"
  ) +
  theme_bw()

#ggsave(file.path(outpath, "keyvars_raw_vs_BR_by_cohort_EXPANDED.png"),
#       p1_exp, width = 14, height = 10, dpi = 300)

print(p1_exp)

p2_exp <- compare_long2 %>%
  ggplot(aes(x = cohort, y = deltaBR)) +
  geom_boxplot(outlier.shape = NA, width = 0.7) +
  facet_wrap(~ variable, scales = "free_y") +
  labs(
    title = "Batch regression deltas (expanded set)",
    x = "Cohort", y = "Δ after batch regression"
  ) +
  theme_bw()

print(p2_exp)

#ggsave(file.path(outpath, "keyvars_deltaBR_by_cohort_EXPANDED.png"),
#       p2_exp, width = 14, height = 10, dpi = 300)

# Also save the ranking table for transparency --------
var_effects %>%
  arrange(desc(r2_drop), desc(rel_med_abs_delta)) %>%
  write.csv(file.path(outpath, "variables_batch_affected_ranking.csv"), row.names = FALSE)

var_effects

# --- Paths ---
out_csv_nested <- "../../analysis/batch_summary_table_nested_17nov25.csv"
out_xlsx       <- "../../analysis/batch_summary_table_17nov25.xlsx"

# --- Ensure cohort is factor in both frames ---
noBR_df <- noBR_df %>% mutate(cohort = as.factor(cohort))
BR_df   <- BR_df   %>% mutate(cohort = as.factor(cohort))

# --- Variables to summarize ---
exclude_cols <- c("cohort", "diabetes", "row_id", "weight")
num_cols <- names(noBR_df)[vapply(noBR_df, is.numeric, logical(1))]
num_cols <- setdiff(num_cols, exclude_cols)
num_cols <- intersect(num_cols, names(BR_df))

# --- Helper: one variable ---
consistent_rows <- TRUE
summarize_var <- function(var) {
  d_raw <- noBR_df %>% select(cohort, !!sym(var)) %>% rename(value = !!sym(var))
  d_br  <- BR_df    %>% select(cohort, !!sym(var)) %>% rename(value = !!sym(var))
  
  if (consistent_rows) {
    ok <- complete.cases(d_raw$cohort, d_raw$value, d_br$value)
    d_raw <- d_raw[ok, , drop = FALSE]
    d_br  <- d_br[ok,  , drop = FALSE]
  }
  
  m_raw <- lm(value ~ cohort, data = d_raw)
  m_br  <- lm(value ~ cohort, data = d_br)
  r2_raw <- summary(m_raw)$r.squared
  r2_br  <- summary(m_br)$r.squared
  p_raw  <- anova(m_raw)[["Pr(>F)"]][1]
  p_br   <- anova(m_br)[["Pr(>F)"]][1]
  
  summ_raw <- d_raw %>%
    group_by(cohort) %>%
    summarise(mean_raw = mean(value, na.rm = TRUE),
              sd_raw   = sd(value,   na.rm = TRUE),
              n_raw    = dplyr::n(), .groups = "drop")
  summ_br <- d_br %>%
    group_by(cohort) %>%
    summarise(mean_br = mean(value, na.rm = TRUE),
              sd_br   = sd(value,   na.rm = TRUE),
              n_br    = dplyr::n(), .groups = "drop")
  cohort_summaries <- full_join(summ_raw, summ_br, by = "cohort")
  
  tibble(
    variable = var,
    r2_raw = r2_raw, r2_br = r2_br, r2_drop = r2_raw - r2_br,
    p_raw = p_raw,   p_br  = p_br,
    cohort_summaries = list(cohort_summaries)
  )
}

# --- Build nested table ---
batch_summary_tbl <- map_dfr(num_cols, summarize_var)

# --- Add var_effects metrics ---
batch_summary_tbl <- batch_summary_tbl %>%
  left_join(var_effects %>%
              select(variable, med_abs_delta, mean_abs_delta,
                     rms_delta, rel_med_abs_delta),
            by = "variable")

# --- Join VI summary ---
vi_for_join <- vi_summary %>%
  group_by(full_name) %>%
  summarise(
    vi_mean_importance = mean(mean_importance, na.rm = TRUE),
    vi_sd_importance   = mean(sd_importance,   na.rm = TRUE),
    vi_n               = sum(n, na.rm = TRUE),
    vi_type            = dplyr::first(type),
    .groups = "drop"
  ) %>%
  rename(variable = full_name)

batch_summary_tbl <- batch_summary_tbl %>%
  left_join(vi_for_join, by = "variable") %>%
  mutate(
    vi_mean_importance = as.numeric(vi_mean_importance),
    vi_rank = dplyr::if_else(
      is.na(vi_mean_importance),
      as.integer(NA),
      dplyr::min_rank(-vi_mean_importance)  # higher VI -> smaller rank
    )
  ) %>%
  arrange(dplyr::desc(r2_drop), dplyr::desc(rel_med_abs_delta))

# --- Export 1: CSV with nested col (marker text in place of list) ---
write_csv(
  batch_summary_tbl %>% mutate(cohort_summaries = map_chr(cohort_summaries, ~ "see Excel sheet")),
  out_csv_nested
)

# --- Make flat sheets for Excel ---
# Metrics sheet (drop list-col)
metrics_flat <- batch_summary_tbl %>%
  select(-cohort_summaries)

# Cohort summaries as long sheet (unnest)
cohort_long <- batch_summary_tbl %>%
  select(variable, cohort_summaries) %>%
  unnest(cohort_summaries) %>%
  arrange(variable, cohort)

# --- Export 2: nice Excel workbook with two sheets ---
wb <- createWorkbook()
addWorksheet(wb, "metrics")
addWorksheet(wb, "cohort_summaries")
writeData(wb, "metrics", metrics_flat)
writeData(wb, "cohort_summaries", cohort_long)
saveWorkbook(wb, out_xlsx, overwrite = TRUE)

message("Wrote nested CSV:  ", out_csv_nested)
message("Wrote Excel file: ", out_xlsx)

