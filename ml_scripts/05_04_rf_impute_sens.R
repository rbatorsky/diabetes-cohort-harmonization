#######
## Imputation sensitivity analysis (reviewer comment 6)
## Copy of 05_rf.R; only the numeric imputation step differs, chosen by arg 10:
##   knn     = published recipe (KNN numeric, mode categorical)
##   median  = median numeric, mode categorical
##   knn_ind = KNN + missingness-indicator features (probes non-MAR missingness)
#######

LIB="/cluster/tufts/patralab/rbator01/R_libs/4.4.0/"
.libPaths(LIB)

source("utils.R")

pkgs <- c(
  "openxlsx", "tidymodels", "tidyverse", "workflows", "tune", "compositions",
  "caret", "VIM", "visdat", "recipes", "themis", "yardstick", "vip", "Boruta"
)

invisible(lapply(pkgs, function(pkg) {
  suppressPackageStartupMessages(
    library(pkg, character.only = TRUE)
  )
}))

args <- commandArgs(trailingOnly = TRUE)
nclass           <- as.integer(args[1])
outvar           <- args[2]
filter_cohort    <- args[3]
seed             <- as.integer(args[4])
visit            <- args[5]
importance       <- args[6]
data_string      <- args[7]
cross_cohort_val <- as.integer(args[8])
regress_batch    <- as.integer(args[9])
impute_method    <- args[10]
stopifnot(impute_method %in% c("knn", "median", "knn_ind"))

# nclass           <- 2
# outvar           <- "diabetes"
# filter_cohort    <- "none"
# downsample       <- 0
# seed             <- 1
# visit            <- "v1"
# importance       <- "boruta"
# data_string      <- "all"
# cross_cohort_val <- 0
# regress_batch    <- 1

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
  "\n  regress_batch    =", regress_batch,
  "\n  impute_method    =", impute_method,
  "\n==========================================",
  sep = ""
))


# string for output
save_string = paste0(
  data_string, 
  "_", outvar, 
  "_", visit,
  "_class", nclass,
  "_filter", filter_cohort,
  "_seed", seed,
  "_tune_caseweights_", importance,
  "_xcohortval_", cross_cohort_val,
  "_resbatch_", regress_batch,
  "_imp_", impute_method,
  "_28sep26"
)

# separate folder so nothing overwrites the published runs
OUTPATH  = "../../analysis/impute_sens/"
dir.create(OUTPATH, showWarnings = FALSE, recursive = TRUE)

if (visit == "v1"){
  RDS1 = "../../analysis/harmonize_2cohort_healthsdohffq_v1_rmmissing_50col_10row.rds"
}else if (visit == "v2"){
  RDS1 = "../../analysis/harmonize_2cohort_healthsdohffq_v2_rmmissing_50col_10row.rds"
  
}
TRK  = "../../data/hmz_data/diabetes_tracker_2class_24feb26.xlsx"

data <- read_merge_tracker(
  rds_path     = RDS1,
  tracker_path = TRK,
  visit        = visit,
  label_cohort = FALSE,          
  filter_cohort = filter_cohort         
)

table(data$cohort, data$diabetes)


# sanity check
stopifnot(all(unique(data$cohort) %in% c(0,1)))

# remove variables
# remove v2_progress variables
var_to_rm = c("hmz_health_lab_a1c",
              "hmz_health_lab_gluc",
              "hmz_health_med_1",
              "hmz_health_med_1_age",
              "hmz_health_med_1_medication",
              "hmz_health_med_1_today",
              "hmz_health_lab_insulin",
              "studyid", 
              "visit",
              "hmz_days_since_visit_1")

data = data %>%
  select(-any_of(var_to_rm))

print(table(data$cohort, data$diabetes))
print(prop.table(table(data$cohort,data$diabetes),1) %>% round(2))

if(data_string == "sdoh"){
  sdoh_vars <- grep("^hmz_sdoh", names(data), value = TRUE)
  data <- data %>%
    select(all_of(c(sdoh_vars, "diabetes", "cohort")))
}

set.seed(seed)

# Define cohort codes (adjust if needed)
cohort_bprhs    <- 0L
cohort_prospect <- 1L

# Choose split strategy ------
if (identical(data_string, "all") && cross_cohort_val %in% 1:4) {
  
  if (cross_cohort_val == 1) {
    # xcohortval1: train on BOTH, test on PROSPECT
    message("xcohortval1: pooled TRAIN, TEST on PROSPECT (cohort = ", cohort_prospect, ")")
    
    data_eval <- dplyr::filter(data, cohort == cohort_prospect)
    data_rest <- dplyr::filter(data, cohort != cohort_prospect)
    
    # stratified hold-out within PROSPECT
    split_eval <- initial_split(data_eval,
                                prop   = 3/4,
                                strata = "diabetes")
    
    train_eval <- training(split_eval)
    test_data  <- testing(split_eval)
    
    # pooled training = other cohort(s) + training slice of PROSPECT
    train_data <- dplyr::bind_rows(data_rest, train_eval)
    
  } else if (cross_cohort_val == 2) {
    # xcohortval2: train on BOTH, test on BPRHS
    message("xcohortval2: pooled TRAIN, TEST on BPRHS (cohort = ", cohort_bprhs, ")")
    
    data_eval <- dplyr::filter(data, cohort == cohort_bprhs)
    data_rest <- dplyr::filter(data, cohort != cohort_bprhs)
    
    # stratified hold-out within BPRHS
    split_eval <- initial_split(data_eval,
                                prop   = 3/4,
                                strata = "diabetes")
    
    train_eval <- training(split_eval)
    test_data  <- testing(split_eval)
    
    # pooled training = other cohort(s) + training slice of BPRHS
    train_data <- dplyr::bind_rows(data_rest, train_eval)
    
  } else if (cross_cohort_val == 3) {
    # xcohortval3: train on PROSPECT, test on BPRHS
    message("xcohortval3: TRAIN = PROSPECT, TEST = BPRHS")
    
    train_data <- dplyr::filter(data, cohort == cohort_prospect)
    test_data  <- dplyr::filter(data, cohort == cohort_bprhs)
    
  } else if (cross_cohort_val == 4) {
    # xcohortval4: train on BPRHS, test on PROSPECT
    message("xcohortval4: TRAIN = BPRHS, TEST = PROSPECT")
    
    train_data <- dplyr::filter(data, cohort == cohort_bprhs)
    test_data  <- dplyr::filter(data, cohort == cohort_prospect)
  }
  
} else {
  message("Random split")
  set.seed(seed)
  split <- initial_split(data, prop = 3/4, strata = "diabetes")
  train_data <- training(split)
  test_data  <- testing(split)
}


msg_print <- function(x, header = NULL) {
  if (!is.null(header)) message(header)
  message(paste(capture.output(print(x)), collapse = "\n"))
}

msg_print(table(train_data$cohort),         "TRAIN cohort counts:")
msg_print(table(test_data$cohort),          "TEST  cohort counts:")
msg_print(table(train_data$cohort, train_data$diabetes),
          "TRAIN diabetes by cohort:")
msg_print(table(test_data$cohort,  test_data$diabetes),
          "TEST  diabetes by cohort:")

# ----- Save cohort counts for this run -----

train_cohort_tab <- as.data.frame(table(train_data$cohort))
test_cohort_tab  <- as.data.frame(table(test_data$cohort))

cohort_counts <- dplyr::bind_rows(
  train_cohort_tab %>%
    dplyr::mutate(split = "train"),
  test_cohort_tab %>%
    dplyr::mutate(split = "test")
) %>%
  dplyr::rename(
    cohort = Var1,
    n      = Freq
  ) %>%
  dplyr::mutate(
    cohort = as.integer(as.character(cohort))
  )

# Per-run file:
cohort_counts_file <- paste0(OUTPATH, "cohort_counts_", save_string, ".csv")
write.csv(cohort_counts, cohort_counts_file, row.names = FALSE)

# Preprocessing recipe -----
vars_to_keep <- c("cohort")  

preprocessing_recipe <-
  recipe(diabetes ~ ., data = train_data) %>%
  # Make sure character cats become factors
  step_string2factor(all_nominal_predictors())

# knn_ind: add a 0/1 missingness flag per predictor BEFORE imputing
# (flags with no missingness in TRAIN are constant and removed by step_nzv)
if (impute_method == "knn_ind") {
  preprocessing_recipe <- preprocessing_recipe %>%
    step_indicate_na(all_predictors(), -any_of(vars_to_keep))
}

preprocessing_recipe <- preprocessing_recipe %>%
  # Don't touch 'cohort' during preprocessing
  step_impute_mode(all_nominal_predictors(), -all_outcomes(), -any_of(vars_to_keep)) %>%
  step_nzv(all_predictors(), -all_outcomes(), -all_of(vars_to_keep))

if (impute_method == "median") {
  preprocessing_recipe <- preprocessing_recipe %>%
    step_impute_median(all_numeric_predictors(), -any_of(vars_to_keep))
} else {
  preprocessing_recipe <- preprocessing_recipe %>%
    step_impute_knn(all_numeric_predictors(), neighbors = 5, -any_of(vars_to_keep))
}

preprocessing_recipe <- preprocessing_recipe %>%
  step_corr(all_numeric_predictors(), threshold = 0.9, -any_of(vars_to_keep)) %>%
  step_normalize(all_numeric_predictors(), -any_of(vars_to_keep))

# Prep on TRAIN only; then bake both
prepped_recipe <- prep(preprocessing_recipe, training = train_data)
train_baked    <- juice(prepped_recipe)
test_baked     <- bake(prepped_recipe, new_data = test_data)


if (!is.na(regress_batch) && regress_batch == 1) {
  message("Residualizing numeric predictors by cohort on TRAIN and TEST (using TRAIN-based means)")
  
  # fit on TRAIN
  res_train <- residualize_by_cohort(train_baked, cohort_var = "cohort")
  train_baked <- res_train$data
  
  # apply same cohort means to TEST
  res_test <- residualize_by_cohort(test_baked,
                                    cohort_var = "cohort",
                                    ref_means  = res_train$ref_means)
  test_baked <- res_test$data
}

#saveRDS(train_baked, paste0(OUTPATH,"train_baked_", save_string,".rds"))
#saveRDS(test_baked, paste0(OUTPATH,"test_baked_", save_string,".rds"))
#train_baked = readRDS(paste0(OUTPATH,"train_baked_", save_string,".rds"))
#test_baked = readRDS(paste0(OUTPATH,"test_baked_", save_string,".rds"))

# Case Weights ------
w_tbl <- train_baked %>%
  count(cohort, diabetes, name = "n_cd") %>%
  group_by(cohort) %>%
  mutate(weight = mean(n_cd) / n_cd) %>%
  ungroup()

train_baked <- train_baked %>%
  left_join(w_tbl %>% select(cohort, diabetes, weight),
            by = c("cohort","diabetes")) %>%
  mutate(weight = importance_weights(weight))  

weights_vec <- train_baked$weight

# Include cohort ONLY when not doing cross-cohort validation ----
#include_cohort <- (cross_cohort_val == 0)

# Boruta selection aligned with include_cohort -----
if (importance == "boruta") {
  boruta_data <- train_baked %>% 
    select(-weight)
  
  set.seed(seed)
  boruta_result <- Boruta(
    diabetes ~ .,
    data = boruta_data,
    doTrace = 2,
    maxRuns = 100
  )
  
  boruta_vars <- getSelectedAttributes(boruta_result, withTentative = FALSE)
  tentative <- getSelectedAttributes(boruta_result, withTentative = TRUE) 
  confirmed <- getSelectedAttributes(boruta_result, withTentative = FALSE)
  
  saveRDS(boruta_result, paste0(OUTPATH,"boruta_result_", save_string, ".rds"))
  write.csv(attStats(boruta_result), paste0(OUTPATH,"boruta_stats_", save_string, ".csv"))
  
  keep_cols <- c("diabetes", boruta_vars)

  train_baked <- train_baked %>%
    select(all_of(keep_cols)) %>%
    mutate(weight = importance_weights(weights_vec))
  
  test_baked <- test_baked %>% 
    select(all_of(keep_cols))
  
  saveRDS(train_baked, paste0(OUTPATH,"train_baked_borutafiltered_", save_string,".rds"))
  saveRDS(test_baked,  paste0(OUTPATH,"test_baked_borutafiltered_",  save_string,".rds"))
}

# Model + workflow ------
rf_model <- rand_forest(
  mode = "classification",
  mtry = tune(),
  min_n = tune(),
  trees = 1000
) %>%
  set_engine("ranger", importance = "impurity")

model_formula <- diabetes ~ .

wf <- workflow() %>%
  add_model(rf_model) %>%
  add_formula(model_formula) %>%
  add_case_weights(weight)

# resampling
set.seed(seed)
folds <- vfold_cv(train_baked, v = 5, strata = diabetes)

# grid (exclude outcome + weight from predictor count)
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
  control = control_grid(save_pred = TRUE)
)

tuned_results %>%
  collect_metrics() %>%
  filter(.metric == "roc_auc") %>%
  select(mean, min_n, mtry) %>%
  pivot_longer(min_n:mtry, values_to = "value", names_to = "parameter") %>%
  ggplot(aes(value, mean, color = parameter)) +
  geom_point(show.legend = FALSE) +
  facet_wrap(~parameter, scales = "free_x") +
  labs(x = NULL, y = "AUC")

saveRDS(tuned_results, paste0(OUTPATH,"rf_tune_res_", save_string, ".rds"))

best_params <- select_best(tuned_results, metric = "roc_auc")
final_wf <- finalize_workflow(wf, best_params)
saveRDS(final_wf, paste0(OUTPATH,"final_wf_rf_", save_string, ".rds"))

final_fit <- final_wf %>%
  fit(data = train_baked)      # <-- no case_weights arg; workflow uses `weight` column
saveRDS(final_fit, paste0(OUTPATH,"rf_final_fit_", save_string, ".rds"))

# Make predictions on test data
test_preds <- predict(final_fit, new_data = test_baked, type = "prob") %>%
  bind_cols(predict(final_fit, new_data = test_baked)) %>%
  bind_cols(test_baked)

# Calculate performance metrics
perf_metrics <- bind_rows(
  metrics(data = test_preds, truth = diabetes, estimate = .pred_class),
  yardstick::sensitivity(data = test_preds, truth = diabetes, estimate = .pred_class, event_level="second"),
  yardstick::specificity(data = test_preds, truth = diabetes, estimate = .pred_class, event_level="second"),
  yardstick::roc_auc(data = test_preds, truth = diabetes, .pred_1, event_level="second")
)

# Convert to wide format for logging
perf_wide <- perf_metrics %>%
  select(.metric, .estimate) %>%
  pivot_wider(names_from = .metric, values_from = .estimate)

# Generate and print confusion matrix
conf_mat_result <- test_preds %>%
  conf_mat(truth = diabetes, estimate = .pred_class)

p = autoplot(conf_mat_result, type = "heatmap") +
  ggtitle("Confusion Matrix Heatmap") +
  scale_fill_gradient(low = "white", high = "blue")

show(p)
ggsave(p, filename = paste0(OUTPATH, save_string, "_confmat.pdf"), width = 3, height = 3)

# Extract variable importance
fitted_model <- extract_fit_parsnip(final_fit)
vi_top <- fitted_model %>%
  vi() %>%
  slice_max(order_by = Importance, n = 50) %>%
  mutate(rank = row_number()) %>%
  mutate(type = case_when(
    grepl("^hmz_ffq", Variable) ~ "ffq",
    grepl("^hmz_health", Variable) ~ "health",
    grepl("^hmz_sdoh", Variable) ~ "sdoh",
    TRUE ~ "other"
  ))

if(importance == "boruta"){
  
  confirmed = getSelectedAttributes(boruta_result, withTentative = FALSE)
  vi_top = vi_top %>%
    mutate(boruta = ifelse(Variable %in% confirmed, 'confirmed','tentative'))
}

vi_top = vi_top %>%
  mutate(Variable = str_remove(Variable, paste0("^hmz_", type, "_")))

# Plot variable importance
p <- ggplot(vi_top, aes(
  x = reorder(Variable, Importance),
  y = Importance,
  fill = type,
  color = boruta
)) +
  geom_bar(stat = "identity", position = "dodge") +
  coord_flip() +
  ylab("Variable Importance") +
  xlab("") +
  ggtitle(paste0(outvar,"_",visit,"_class", nclass,"_filter",filter_cohort,"_", seed)) +
  theme_bw()+
  scale_fill_manual(values = c(
    "ffq"    = "steelblue",
    "health" = "firebrick",
    "sdoh"   = "forestgreen")) +
  theme(
      plot.title = element_text(size = 6)  # Change size to desired value
    ) +
  geom_col(position = "dodge", size = 1.2) +
  scale_color_manual(values = c(
    "confirmed" = "black",
    "tentative" = "gray60"
  )) +
  theme(
    plot.title = element_text(size = 6),
    legend.position = "right"
  )

show(p)
# Save variable importance plot
ggsave(p, filename = paste0(OUTPATH, save_string, ".pdf"), width = 5, height = 7)

# Prepare log data for saving
log_df <- vi_top %>%
  mutate(
    seed = seed,
    nclass = nclass,
    outvar = outvar,
    visit = visit,
    data_string = data_string,
    filter_cohort = filter_cohort,
    accuracy = perf_wide$accuracy,
    kap = perf_wide$kap,
    sensitivity = perf_wide$sensitivity,
    specificity = perf_wide$specificity
  ) %>%
  select(seed, nclass, outvar, visit, data_string, filter_cohort, rank, Variable, type, Importance,
         accuracy, kap, sensitivity, specificity)

# Save log to CSV
write.csv(log_df, paste0(OUTPATH, "log_", save_string, ".csv"), row.names = FALSE)

# Save the trained model and results
saveRDS(wf, paste0(OUTPATH,"final_model_", save_string,".rds"))
saveRDS(test_preds, paste0(OUTPATH,"test_predictions_", save_string,".rds"))

# roc
roc_obj <- yardstick::roc_curve(test_preds, truth = diabetes, .pred_1, event_level="second")
saveRDS(roc_obj, paste0(OUTPATH, save_string, "_roc.rds"))

p_roc <- autoplot(roc_obj) +
  ggtitle("ROC Curve")

ggsave(p_roc, filename = paste0(OUTPATH, save_string, "_roc.pdf"), width = 5, height = 4)
