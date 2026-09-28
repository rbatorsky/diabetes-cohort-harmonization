#######
## Run the models: diabetes_change_v1_v2 (V1->V2)
#######

LIB="/cluster/tufts/patralab/rbator01/R_libs/4.4.0/"
.libPaths(LIB)

source("utils.R")

pkgs <- c(
  "openxlsx", "tidymodels", "tidyverse", "workflows", "tune", "compositions",
  "caret", "VIM", "visdat", "recipes", "themis", "yardstick", "vip", "Boruta"
)

invisible(lapply(pkgs, function(pkg) {
  suppressPackageStartupMessages(library(pkg, character.only = TRUE))
}))

# ---------------- Args (keep 9 args, ignore 9th) ----------------
args <- commandArgs(trailingOnly = TRUE)

# if running interactively, comment args block and hardcode below
stopifnot(length(args) >= 8)

nclass           <- as.integer(args[1])
outvar           <- args[2]                  # e.g. "diabetes_change"
filter_cohort    <- args[3]                  # "0","1","none"
seed             <- as.integer(args[4])
visit            <- args[5]                  # use "change" (recommended)
importance       <- args[6]                  # "boruta"
data_string      <- args[7]                  # "all" or "sdoh"
cross_cohort_val <- as.integer(args[8])

# nclass           <- 2
# outvar           <- "diabetes_change"
# filter_cohort    <- "none"
# downsample       <- 0
# seed             <- 1
# visit            <- "change"
# importance       <- "none"
# data_string      <- "all"
# cross_cohort_val <- 0
# regress_batch    <- 0

# keep interface same; ignore regress_batch
regress_batch <- if (length(args) >= 9) as.integer(args[9]) else 0L
invisible(regress_batch)

message(paste(
  "\n==========================================",
  "\nRun parameters:",
  "\n  nclass           =", nclass,
  "\n  outvar           =", outvar,
  "\n  filter_cohort    =", filter_cohort,
  "\n  seed             =", seed,
  "\n  visit            =", visit,
  "\n  importance       =", importance,
  "\n  data_string      =", data_string,
  "\n  cross_cohort_val =", cross_cohort_val,
  "\n  regress_batch    =", regress_batch, " (IGNORED)",
  "\n==========================================",
  sep = ""
))

# ---------------- Output naming ----------------
date_tag <- "24feb26"
OUTPATH  <- "../../analysis/"

save_string <- paste0(
  data_string,
  "_", outvar,
  "_", visit,
  "_class", nclass,
  "_filter", filter_cohort,
  "_seed", seed,
  "_tune_caseweights_", importance,
  "_xcohortval_", cross_cohort_val,
  "_resbatch_", regress_batch,  # kept for compatibility; ignored
  "_", date_tag
)

# ---------------- Choose predictors RDS ----------------
# For "change", you typically want V1 predictors.
# If you ever want V2 predictors for the change outcome, you can add that option.
if (visit %in% c("v1","change")) {
  RDS1 <- "../../analysis/harmonize_2cohort_healthsdohffq_v1_rmmissing_50col_10row.rds"
} else if (visit == "v2") {
  RDS1 <- "../../analysis/harmonize_2cohort_healthsdohffq_v2_rmmissing_50col_10row.rds"
} else {
  stop("visit must be 'change', 'v1', or 'v2'")
}

TRK <- "../../data/hmz_data/diabetes_tracker_2class_24feb26.xlsx"

# ---------------- Read + merge outcome ----------------
# IMPORTANT: for delta diabetes, use visit="change" in read_merge_tracker
data <- read_merge_tracker(
  rds_path      = RDS1,
  tracker_path  = TRK,
  visit         = visit,     
  label_cohort  = FALSE,
  filter_cohort = filter_cohort
)

# Expect diabetes_change_v1_v2 in merged data
stopifnot("diabetes_change_v1_v2" %in% names(data))
stopifnot("diabetes_v1" %in% names(data))

# Make a 3-class outcome named "diabetes" 
data <- data %>%
  mutate(
    diabetes = factor(
      diabetes_change_v1_v2,
      levels = c(-1, 0, 1),
      labels = c("Remission", "No_change", "Progression")
    )
  ) 

# Make a 2-class outcome named "diabetes", progression or no_proression
data <- data %>%
  dplyr::mutate(
    diabetes_v1_num = as.integer(as.character(diabetes_v1))  # 0/1
  ) %>%
  dplyr::filter(diabetes_v1_num == 0) %>%                    # at risk
  dplyr::mutate(
    diabetes = factor(
      ifelse(diabetes_change_v1_v2 == 1,
             "Progression", "No_progression"),
      levels = c("No_progression", "Progression")
    )  ) %>%
  dplyr::select(-c(diabetes_v1_num, diabetes_v1, diabetes_v2, diabetes_change_v1_v2))


print(table(data$cohort, data$diabetes, useNA = "ifany"))
print(round(prop.table(table(data$cohort, data$diabetes), 1), 2))

# Sanity check cohort codes
stopifnot(all(unique(data$cohort) %in% c(0,1)))

# ---------------- Remove leakage variables ----------------
# Remove variables that define diabetes/change directly or would leak labels
var_to_rm <- c(
  "hmz_health_lab_a1c",
  "hmz_health_lab_gluc",
  "hmz_health_med_1",
  "hmz_health_med_1_age",
  "hmz_health_med_1_medication",
  "hmz_health_med_1_today",
  "hmz_health_lab_insulin",
  "studyid",
  "visit")

data <- data %>%
  select(-any_of(var_to_rm))

# Optional: SDOH-only mode
if (identical(data_string, "sdoh")) {
  sdoh_vars <- grep("^hmz_sdoh", names(data), value = TRUE)
  data <- data %>%
    select(all_of(c(sdoh_vars, "diabetes", "cohort")))
}

set.seed(seed)

# ---------------- Split strategy (same as yours) ----------------
cohort_bprhs    <- 0L
cohort_prospect <- 1L

if (identical(data_string, "all") && cross_cohort_val %in% 1:4) {
  
  if (cross_cohort_val == 1) {
    message("xcohortval1: pooled TRAIN, TEST on PROSPECT (cohort=", cohort_prospect, ")")
    
    data_eval <- dplyr::filter(data, cohort == cohort_prospect)
    data_rest <- dplyr::filter(data, cohort != cohort_prospect)
    
    do_strata <- (sum(data_eval$diabetes == "Progression") >= 5) &&
      (sum(data_eval$diabetes == "No_progression") >= 5)
    
    split_eval <- initial_split(
      data_eval,
      prop = 3/4,
      strata = if (do_strata) "diabetes" else NULL
    )
    
    train_eval <- training(split_eval)
    test_data  <- testing(split_eval)
    
    train_data <- dplyr::bind_rows(data_rest, train_eval)
    
  } else if (cross_cohort_val == 2) {
    message("xcohortval2: pooled TRAIN, TEST on BPRHS (cohort=", cohort_bprhs, ")")
    
    data_eval <- dplyr::filter(data, cohort == cohort_bprhs)
    data_rest <- dplyr::filter(data, cohort != cohort_bprhs)
    
    split_eval <- initial_split(data_eval, prop = 3/4, strata = "diabetes")
    train_eval <- training(split_eval)
    test_data  <- testing(split_eval)
    
    train_data <- dplyr::bind_rows(data_rest, train_eval)
    
  } else if (cross_cohort_val == 3) {
    message("xcohortval3: TRAIN = PROSPECT, TEST = BPRHS")
    train_data <- dplyr::filter(data, cohort == cohort_prospect)
    test_data  <- dplyr::filter(data, cohort == cohort_bprhs)
    
  } else if (cross_cohort_val == 4) {
    message("xcohortval4: TRAIN = BPRHS, TEST = PROSPECT")
    train_data <- dplyr::filter(data, cohort == cohort_bprhs)
    test_data  <- dplyr::filter(data, cohort == cohort_prospect)
  }
  
} else {
  message("Random split")
  split <- initial_split(data, prop = 3/4, strata = "diabetes")
  train_data <- training(split)
  test_data  <- testing(split)
}

msg_print <- function(x, header = NULL) {
  if (!is.null(header)) message(header)
  message(paste(capture.output(print(x)), collapse = "\n"))
}

msg_print(table(train_data$cohort), "TRAIN cohort counts:")
msg_print(table(test_data$cohort),  "TEST  cohort counts:")
msg_print(table(train_data$cohort, train_data$diabetes), "TRAIN outcome by cohort:")
msg_print(table(test_data$cohort,  test_data$diabetes),  "TEST  outcome by cohort:")

# ---------------- Save cohort counts ----------------
train_cohort_tab <- as.data.frame(table(train_data$cohort))
test_cohort_tab  <- as.data.frame(table(test_data$cohort))

cohort_counts <- dplyr::bind_rows(
  train_cohort_tab %>% dplyr::mutate(split = "train"),
  test_cohort_tab  %>% dplyr::mutate(split = "test")
) %>%
  dplyr::rename(cohort = Var1, n = Freq) %>%
  dplyr::mutate(cohort = as.integer(as.character(cohort)))

write.csv(cohort_counts, paste0(OUTPATH, "cohort_counts_", save_string, ".csv"), row.names = FALSE)

# ---------------- Preprocessing recipe ----------------
vars_to_keep <- c("cohort")

preprocessing_recipe <-
  recipe(diabetes ~ ., data = train_data) %>%
  step_string2factor(all_nominal_predictors()) %>%
  step_impute_mode(all_nominal_predictors(), -all_outcomes(), -any_of(vars_to_keep)) %>%
  step_nzv(all_predictors(), -all_outcomes(), -all_of(vars_to_keep)) %>%
  step_impute_knn(all_numeric_predictors(), neighbors = 5, -any_of(vars_to_keep)) %>%
  step_corr(all_numeric_predictors(), threshold = 0.9, -any_of(vars_to_keep)) %>%
  step_normalize(all_numeric_predictors(), -any_of(vars_to_keep))

prepped_recipe <- prep(preprocessing_recipe, training = train_data)
train_baked    <- juice(prepped_recipe)
test_baked     <- bake(prepped_recipe, new_data = test_data)

# ---------------- Case weights (same idea, now 3-class) ----------------
w_tbl <- train_baked %>%
  count(cohort, diabetes, name = "n_cd") %>%
  group_by(cohort) %>%
  mutate(weight = mean(n_cd) / n_cd) %>%
  ungroup()

train_baked <- train_baked %>%
  left_join(w_tbl %>% select(cohort, diabetes, weight), by = c("cohort","diabetes")) %>%
  mutate(weight = importance_weights(weight))

weights_vec <- train_baked$weight

# ---------------- Boruta selection ----------------
if (importance == "boruta") {
  boruta_data <- train_baked %>% select(-weight)
  
  set.seed(seed)
  boruta_result <- Boruta(
    diabetes ~ .,
    data = boruta_data,
    doTrace = 2,
    maxRuns = 100
  )
  
  boruta_vars <- getSelectedAttributes(boruta_result, withTentative = FALSE)
  
  saveRDS(boruta_result, paste0(OUTPATH, "boruta_result_", save_string, ".rds"))
  write.csv(attStats(boruta_result), paste0(OUTPATH, "boruta_stats_", save_string, ".csv"))
  
  keep_cols <- c("diabetes", boruta_vars)
  
  train_baked <- train_baked %>%
    select(all_of(keep_cols)) %>%
    mutate(weight = importance_weights(weights_vec))
  
  test_baked <- test_baked %>%
    select(all_of(keep_cols))
  
  saveRDS(train_baked, paste0(OUTPATH, "train_baked_borutafiltered_", save_string, ".rds"))
  saveRDS(test_baked,  paste0(OUTPATH, "test_baked_borutafiltered_",  save_string, ".rds"))
}

# ---------------- Model + workflow ----------------
rf_model <- rand_forest(
  mode  = "classification",
  mtry  = tune(),
  min_n = tune(),
  trees = 1000
) %>%
  set_engine("ranger", importance = "impurity")

wf <- workflow() %>%
  add_model(rf_model) %>%
  add_formula(diabetes ~ .) %>%
  add_case_weights(weight)

# resampling
set.seed(seed)
folds <- vfold_cv(train_baked, v = 5, repeats = 5, strata = diabetes)

n_predictors <- ncol(dplyr::select(train_baked, -diabetes, -weight))

rf_grid <- grid_latin_hypercube(
  mtry(range = c(1, n_predictors)),
  min_n(range = c(5, 20)),
  size = 20
)

library(doParallel)
cl <- makeCluster(4)
registerDoParallel(cl)
on.exit(stopCluster(cl), add = TRUE)

tuned_results <- tune_grid(
  wf,
  resamples = folds,
  grid = rf_grid,
  metrics = metric_set(roc_auc, pr_auc, accuracy),
  control = control_grid(save_pred = TRUE)
)
saveRDS(tuned_results, paste0(OUTPATH, "rf_tune_res_", save_string, ".rds"))

#best_params <- select_best(tuned_results, metric = "roc_auc")
best_params <- select_best(tuned_results, metric = "pr_auc")

final_wf    <- finalize_workflow(wf, best_params)
saveRDS(final_wf, paste0(OUTPATH, "final_wf_rf_", save_string, ".rds"))

final_fit <- final_wf %>% fit(data = train_baked)
saveRDS(final_fit, paste0(OUTPATH, "rf_final_fit_", save_string, ".rds"))

# ---------------- Predictions ----------------
test_preds <- predict(final_fit, new_data = test_baked, type = "prob") %>%
  bind_cols(predict(final_fit, new_data = test_baked)) %>%
  bind_cols(test_baked)

# ---------------- Metrics (binary progression model) ----------------
perf_metrics <- bind_rows(
  yardstick::metrics(test_preds, truth = diabetes, estimate = .pred_class),
  yardstick::roc_auc(test_preds, truth = diabetes, .pred_Progression),
  yardstick::pr_auc(test_preds, truth = diabetes, .pred_Progression)
)

print(yardstick::pr_auc(test_preds, truth = diabetes, .pred_Progression))


perf_wide <- perf_metrics %>%
  select(.metric, .estimate) %>%
  pivot_wider(names_from = .metric, values_from = .estimate)

print(perf_wide)

# Confusion matrix
conf_mat_result <- test_preds %>%
  conf_mat(truth = diabetes, estimate = .pred_class)

p_cm <- autoplot(conf_mat_result, type = "heatmap") +
  ggtitle("Confusion Matrix (diabetes_change_v1_v2)")

ggsave(p_cm, filename = paste0(OUTPATH, save_string, "_confmat.pdf"), width = 3.5, height = 3.2)

# ---------------- Variable importance ----------------
fitted_model <- extract_fit_parsnip(final_fit)

vi_top <- fitted_model %>%
  vi() %>%
  slice_max(order_by = Importance, n = 50) %>%
  mutate(rank = row_number()) %>%
  mutate(type = case_when(
    grepl("^hmz_ffq",    Variable) ~ "ffq",
    grepl("^hmz_health", Variable) ~ "health",
    grepl("^hmz_sdoh",   Variable) ~ "sdoh",
    TRUE ~ "other"
  ))

if (importance == "boruta") {
  confirmed <- getSelectedAttributes(boruta_result, withTentative = FALSE)
  vi_top <- vi_top %>% mutate(boruta = ifelse(Variable %in% confirmed, "confirmed", "tentative"))
} else {
  vi_top$boruta <- "na"
}

vi_top <- vi_top %>%
  mutate(Variable = str_remove(Variable, paste0("^hmz_", type, "_")))

p_vi <- ggplot(vi_top, aes(x = reorder(Variable, Importance), y = Importance, fill = type, color = boruta)) +
  geom_col(position = "dodge", linewidth = 1.0) +
  coord_flip() +
  labs(
    title = paste0(outvar, "_", visit, "_class", nclass, "_filter", filter_cohort, "_seed", seed),
    x = NULL,
    y = "Variable Importance"
  ) +
  theme_bw() +
  scale_fill_manual(values = c("ffq"="steelblue", "health"="firebrick", "sdoh"="forestgreen", "other"="grey70")) +
  scale_color_manual(values = c("confirmed"="black", "tentative"="gray60", "na"="gray60")) +
  theme(plot.title = element_text(size = 7))

ggsave(p_vi, filename = paste0(OUTPATH, save_string, "_vi.pdf"), width = 5, height = 7)

# ---------------- Logs ----------------
log_df <- vi_top %>%
  mutate(
    seed         = seed,
    nclass       = nclass,
    outvar       = outvar,
    visit        = visit,
    data_string  = data_string,
    filter_cohort= filter_cohort,
    accuracy     = perf_wide$accuracy,
    kap          = perf_wide$kap,
    roc_auc      = perf_wide$roc_auc,
    pr_auc       = perf_wide$pr_auc
  ) %>%
  select(seed, nclass, outvar, visit, data_string, filter_cohort,
         rank, Variable, type, Importance, accuracy, kap, roc_auc, pr_auc, boruta)

write.csv(log_df, paste0(OUTPATH, "log_", save_string, ".csv"), row.names = FALSE)

saveRDS(test_preds, paste0(OUTPATH, "test_predictions_", save_string, ".rds"))

# Multiclass ROC curve object (one-vs-all curves returned with .level)
roc_obj <- yardstick::roc_curve(test_preds, truth = diabetes, .pred_Progression)

saveRDS(roc_obj, paste0(OUTPATH, save_string, "_roc.rds"))

p_roc <- autoplot(roc_obj) + ggtitle("ROC Curves (one-vs-all)")
ggsave(p_roc, filename = paste0(OUTPATH, save_string, "_roc.pdf"), width = 5.5, height = 4.2)