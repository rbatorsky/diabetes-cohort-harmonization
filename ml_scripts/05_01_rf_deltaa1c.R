#!/usr/bin/env Rscript
# ============================================================
# 05_xx_run_delta_a1c_regression_SIMPLE.R
#
# Regression model for continuous delta_a1c_v1_v2 using V1 predictors
# - Reads harmonized V1 predictors RDS
# - Merges subject-level delta_a1c_v1_v2 from tracker via visit="a1c_change"
# - Keeps baseline A1c + follow-up time (NOT leakage)
# - Removes direct diabetes-label / diabetes-change columns if present
# - Cohort balancing via case weights (ON)
# - Repeated CV for stability (5-fold x 5 repeats)
# - Tunes RF (ranger) for RMSE; reports RMSE/MAE/R^2
# ============================================================

LIB <- "/cluster/tufts/patralab/rbator01/R_libs/4.4.0/"
.libPaths(LIB)

source("utils.R")

suppressPackageStartupMessages({
  library(openxlsx)
  library(dplyr)
  library(tidyr)
  library(stringr)
  library(tidymodels)
  library(recipes)
  library(yardstick)
  library(vip)
  library(doParallel)
})

# ---------------- Args (kept compatible with your sbatch interface) ----------------
# Expected args:
#   1 nclass (ignored)
#   2 outvar (ignored; forced to delta_a1c_v1_v2)
#   3 filter_cohort ("none","0","1")
#   4 seed
#   5 visit (ignored; forced to "a1c_change")
#   6 importance (ignored)
#   7 data_string ("all" or "sdoh")
#   8 cross_cohort_val (0..4)

args <- commandArgs(trailingOnly = TRUE)

# Safe defaults for interactive use
if (length(args) < 8) {
  args <- c("2", "delta_a1c_v1_v2", "none", "1", "a1c_change", "none", "all", "0")
}

nclass           <- suppressWarnings(as.integer(args[1]))
filter_cohort    <- args[3]
seed             <- suppressWarnings(as.integer(args[4]))
data_string      <- args[7]
cross_cohort_val <- suppressWarnings(as.integer(args[8]))

# filter_cohort    <- "none"
# seed             <- 1

# Force the intended regression outcome and tracker merge mode
outvar <- "delta_a1c_v1_v2"
visit  <- "a1c_change"
nclass           <- 2
importance       <- "none"
data_string      <- "all"
cross_cohort_val <- 0
regress_batch    <- 0


# ---------------- Paths ----------------
OUTPATH <- "../../analysis/"
TRK     <- "../../data/hmz_data/diabetes_tracker_2class_24feb26.xlsx"

# For delta A1c prediction, you almost always want baseline (V1) predictors
RDS1 <- "../../analysis/harmonize_2cohort_healthsdohffq_v1_rmmissing_50col_10row.rds"

# ---------------- Output naming ----------------
date_tag <- "24feb26"
save_string <- paste0(
  data_string,
  "_", outvar,
  "_", visit,
  "_filter", filter_cohort,
  "_seed", seed,
  "_xcohortval_", cross_cohort_val,
  "_", date_tag
)

message(paste(
  "\n==========================================",
  "\nRun parameters:",
  "\n  outvar           =", outvar,
  "\n  visit            =", visit,
  "\n  filter_cohort    =", filter_cohort,
  "\n  seed             =", seed,
  "\n  data_string      =", data_string,
  "\n  cross_cohort_val =", cross_cohort_val,
  "\n  RDS              =", RDS1,
  "\n  TRK              =", TRK,
  "\n==========================================",
  sep = ""
))

set.seed(seed)

# ---------------- Read + merge outcome ----------------
data <- read_merge_tracker(
  rds_path      = RDS1,
  tracker_path  = TRK,
  visit         = visit,          # subject-level delta outcome merge
  label_cohort  = FALSE,
  filter_cohort = filter_cohort
)

colnames(data)

stopifnot(all(unique(data$cohort) %in% c(0, 1)))
stopifnot(outvar %in% names(data))

# Keep only rows with defined delta A1c
data <- data %>% filter(!is.na(.data[[outvar]]))

# ---------------- Remove non-model fields / leakage ----------------
# Baseline A1c and follow-up time are allowed; remove IDs and diabetes labels/change vars.
var_to_rm <- c(
  "a1c_v2",              # outcome component — algebraic leakage (delta = a1c_v2 - a1c_v1)
  "hmz_health_lab_a1c",  # harmonized A1c
  "lab_a1c",             # raw tracker-merged A1c
  "hmz_health_lab_gluc",
  "lab_gluc",            # raw tracker-merged glucose
  "hmz_health_med_1",
  "hmz_health_med_1_age",
  "hmz_health_med_1_medication",
  "hmz_health_med_1_today",
  "hmz_health_lab_insulin",
  "studyid",
  "visit",
  "hmz_days_since_visit_1",
  "diabetes",
  "diabetes_change_v1_v2",
  "diabetes_v1",
  "diabetes_v2"
)

data <- data %>% select(-any_of(var_to_rm))

# Optional: SDOH-only mode
if (identical(data_string, "sdoh")) {
  sdoh_vars <- grep("^hmz_sdoh", names(data), value = TRUE)
  keep <- unique(c(sdoh_vars, outvar, "cohort"))
  data <- data %>% select(any_of(keep))
}

# ---------------- Split strategy helpers ----------------
make_delta_bins <- function(x, k = 5) {
  qs <- unique(as.numeric(quantile(x, probs = seq(0, 1, length.out = k + 1), na.rm = TRUE)))
  if (length(qs) < 3) qs <- unique(pretty(x, n = 3))
  cut(x, breaks = qs, include.lowest = TRUE, ordered_result = TRUE)
}

data <- data %>% mutate(.delta_bin = make_delta_bins(.data[[outvar]], k = 5))

cohort_bprhs    <- 0L
cohort_prospect <- 1L

if (identical(data_string, "all") && cross_cohort_val %in% 1:4) {
  
  if (cross_cohort_val == 1) {
    message("xcohortval1: pooled TRAIN, TEST on PROSPECT (cohort=1)")
    data_eval <- filter(data, cohort == cohort_prospect)
    data_rest <- filter(data, cohort != cohort_prospect)
    split_eval <- initial_split(data_eval, prop = 3/4, strata = ".delta_bin")
    train_data <- bind_rows(data_rest, training(split_eval))
    test_data  <- testing(split_eval)
    
  } else if (cross_cohort_val == 2) {
    message("xcohortval2: pooled TRAIN, TEST on BPRHS (cohort=0)")
    data_eval <- filter(data, cohort == cohort_bprhs)
    data_rest <- filter(data, cohort != cohort_bprhs)
    split_eval <- initial_split(data_eval, prop = 3/4, strata = ".delta_bin")
    train_data <- bind_rows(data_rest, training(split_eval))
    test_data  <- testing(split_eval)
    
  } else if (cross_cohort_val == 3) {
    message("xcohortval3: TRAIN=PROSPECT, TEST=BPRHS")
    train_data <- filter(data, cohort == cohort_prospect)
    test_data  <- filter(data, cohort == cohort_bprhs)
    
  } else if (cross_cohort_val == 4) {
    message("xcohortval4: TRAIN=BPRHS, TEST=PROSPECT")
    train_data <- filter(data, cohort == cohort_bprhs)
    test_data  <- filter(data, cohort == cohort_prospect)
  }
  
} else {
  message("Random split (stratified by delta bins)")
  split <- initial_split(data, prop = 3/4, strata = ".delta_bin")
  train_data <- training(split)
  test_data  <- testing(split)
}

# Remove split-only column
train_data <- train_data %>% select(-.delta_bin)
test_data  <- test_data  %>% select(-.delta_bin)

msg_print <- function(x, header = NULL) {
  if (!is.null(header)) message(header)
  message(paste(capture.output(print(x)), collapse = "\n"))
}

msg_print(table(train_data$cohort), "TRAIN cohort counts:")
msg_print(table(test_data$cohort),  "TEST  cohort counts:")

# If cohort is constant (within-cohort run), drop it and don't reference it in recipe selectors
drop_cohort <- FALSE
if ("cohort" %in% names(train_data) && dplyr::n_distinct(train_data$cohort) == 1) {
  train_data <- train_data %>% dplyr::select(-cohort)
  test_data  <- test_data  %>% dplyr::select(-cohort)
  drop_cohort <- TRUE
}

vars_to_keep <- if (!drop_cohort && "cohort" %in% names(train_data)) "cohort" else character(0)

# ---------------- Case weights (cohort balancing only) ----------------
library(hardhat)

if (!drop_cohort && "cohort" %in% names(train_data)) {
  w_tbl <- train_data %>%
    count(cohort, name = "n_c") %>%
    mutate(weight = mean(n_c) / n_c)
  
  train_data <- train_data %>%
    left_join(w_tbl %>% select(cohort, w_raw = weight), by = "cohort") %>%
    mutate(w_case = hardhat::importance_weights(w_raw)) %>%
    select(-w_raw)
  
  test_data <- test_data %>%
    mutate(w_case = hardhat::importance_weights(1))
  
} else {
  # single-cohort run: no cohort balancing possible/needed
  train_data <- train_data %>% mutate(w_case = hardhat::importance_weights(1))
  test_data  <- test_data  %>% mutate(w_case = hardhat::importance_weights(1))
}
# ---------------- Recipe (regression) ----------------
# Build recipe on data without w_case — workflow handles weights separately
train_recipe_data <- train_data %>% select(-w_case)

# Keep w_case in data so workflow can find it; exclude it from all steps explicitly
rec_base <-
  recipe(stats::as.formula(paste0(outvar, " ~ .")), data = train_data) %>%
  step_string2factor(all_nominal_predictors()) %>%
  step_impute_mode(all_nominal_predictors()) %>%
  step_nzv(all_predictors(), -any_of("w_case"))

if (length(vars_to_keep) > 0) {
  rec <- rec_base %>%
    step_impute_knn(all_numeric_predictors(), neighbors = 5, -any_of(c(vars_to_keep, "w_case"))) %>%
    step_corr(all_numeric_predictors(), threshold = 0.9,    -any_of(c(vars_to_keep, "w_case"))) %>%
    step_normalize(all_numeric_predictors(),                 -any_of(c(vars_to_keep, "w_case")))
} else {
  rec <- rec_base %>%
    step_impute_knn(all_numeric_predictors(), neighbors = 5, -any_of("w_case")) %>%
    step_corr(all_numeric_predictors(), threshold = 0.9,    -any_of("w_case")) %>%
    step_normalize(all_numeric_predictors(),                 -any_of("w_case"))
}

# Add imputation, correlation filter, and normalization once,
# excluding cohort from these steps when it is present as a predictor.
if (length(vars_to_keep) > 0) {
  rec <- rec_base %>%
    step_impute_knn(all_numeric_predictors(), neighbors = 5, -any_of(vars_to_keep)) %>%
    step_corr(all_numeric_predictors(), threshold = 0.9, -any_of(vars_to_keep)) %>%
    step_normalize(all_numeric_predictors(), -any_of(vars_to_keep))
} else {
  rec <- rec_base %>%
    step_impute_knn(all_numeric_predictors(), neighbors = 5) %>%
    step_corr(all_numeric_predictors(), threshold = 0.9) %>%
    step_normalize(all_numeric_predictors())
}

# ---------------- Model + workflow (RF regression) ----------------
rf_model <- rand_forest(
  mode  = "regression",
  mtry  = tune(),
  min_n = tune(),
  trees = 1000
) %>%
  set_engine("ranger", importance = "impurity")

wf <- workflow() %>%
  add_model(rf_model) %>%
  add_recipe(rec) %>%
  add_case_weights(w_case)

# ---------------- Resampling (Repeated CV; stratify by binned delta) ----------------
train_for_folds <- train_data %>%
  mutate(.delta_bin = make_delta_bins(.data[[outvar]], k = 5))

set.seed(seed)
#folds <- vfold_cv(train_for_folds, v = 5, repeats = 5, strata = ".delta_bin")
folds <- vfold_cv(train_for_folds, v = 3, repeats = 1, strata = ".delta_bin")

# ---------------- Tune grid ----------------
# Estimate number of predictors after preprocessing (rough, based on baked train)
prep_rec <- prep(rec, training = train_data)
tmp_baked <- juice(prep_rec)

# exclude outcome + weight
n_predictors <- ncol(tmp_baked %>% select(-all_of(outvar), -any_of("w_case")))

# rf_grid <- grid_latin_hypercube(
#   mtry(range = c(1, max(2, n_predictors))),
#   min_n(range = c(5, 40)),
#   size = 25
# )

rf_grid <- grid_latin_hypercube(
  mtry(range = c(1, max(2, n_predictors))),
  min_n(range = c(5, 40)),
  size = 6
)


# library(doParallel)
# n_cores <- as.integer(Sys.getenv("SLURM_CPUS_PER_TASK", unset = "1"))
# cl <- makeCluster(n_cores)
# registerDoParallel(cl)
# on.exit(stopCluster(cl), add = TRUE)

tuned_results <- tune_grid(
  wf,
  resamples = folds,
  grid = rf_grid,
  metrics = metric_set(rmse, mae, rsq),
  control = control_grid(save_pred = TRUE)
)

saveRDS(tuned_results, file.path(OUTPATH, paste0("rf_tune_res_", save_string, ".rds")))

best_params <- select_best(tuned_results, metric = "rmse")
final_wf    <- finalize_workflow(wf, best_params)
saveRDS(final_wf, file.path(OUTPATH, paste0("final_wf_rf_", save_string, ".rds")))

# ---------------- Fit final model ----------------
final_fit <- fit(final_wf, data = train_data)
saveRDS(final_fit, file.path(OUTPATH, paste0("rf_final_fit_", save_string, ".rds")))

# ---------------- Predict + evaluate on test ----------------
test_preds <- predict(final_fit, new_data = test_data) %>%
  bind_cols(test_data)

perf_metrics <- metric_set(rmse, mae, rsq)(
  test_preds,
  truth    = !!rlang::sym(outvar),
  estimate = .pred
)

perf_wide <- perf_metrics %>%
  select(.metric, .estimate) %>%
  pivot_wider(names_from = .metric, values_from = .estimate)

print(perf_wide)

write.csv(perf_metrics, file.path(OUTPATH, paste0("perf_", save_string, ".csv")), row.names = FALSE)
saveRDS(test_preds,  file.path(OUTPATH, paste0("test_predictions_", save_string, ".rds")))

# ---------------- Plot: Truth vs Predicted ----------------
p_scatter <- ggplot(test_preds, aes(x = !!rlang::sym(outvar), y = .pred)) +
  geom_point(alpha = 0.5) +
  geom_abline(slope = 1, intercept = 0) +
  theme_bw() +
  labs(
    title = paste0("Truth vs Predicted: ", outvar),
    x = "Truth",
    y = "Predicted"
  )

ggsave(
  p_scatter,
  filename = file.path(OUTPATH, paste0(save_string, "_truth_vs_pred.pdf")),
  width = 5,
  height = 4
)

# ---------------- Variable importance ----------------
fitted_model <- extract_fit_parsnip(final_fit)

vi_top <- fitted_model %>%
  vi() %>%
  slice_max(order_by = Importance, n = 50) %>%
  mutate(
    rank = row_number(),
    type = case_when(
      grepl("^hmz_ffq",    Variable) ~ "ffq",
      grepl("^hmz_health", Variable) ~ "health",
      grepl("^hmz_sdoh",   Variable) ~ "sdoh",
      TRUE ~ "other"
    ),
    Variable = str_remove(Variable, paste0("^hmz_", type, "_"))
  )

p_vi <- ggplot(vi_top, aes(x = reorder(Variable, Importance), y = Importance, fill = type)) +
  geom_col() +
  coord_flip() +
  theme_bw() +
  labs(
    title = paste0("VI (RF regression): ", save_string),
    x = NULL,
    y = "Importance"
  )

ggsave(
  p_vi,
  filename = file.path(OUTPATH, paste0(save_string, "_vi.pdf")),
  width = 6,
  height = 7
)

# ---------------- Logging ----------------
log_df <- vi_top %>%
  mutate(
    seed          = seed,
    outvar        = outvar,
    visit         = visit,
    data_string   = data_string,
    filter_cohort = filter_cohort,
    rmse          = perf_wide$rmse,
    mae           = perf_wide$mae,
    rsq           = perf_wide$rsq
  ) %>%
  select(seed, outvar, visit, data_string, filter_cohort,
         rank, Variable, type, Importance,
         rmse, mae, rsq)

write.csv(log_df, file.path(OUTPATH, paste0("log_", save_string, ".csv")), row.names = FALSE)

message("DONE: ", save_string)