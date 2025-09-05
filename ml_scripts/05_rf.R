LIB="/cluster/tufts/patralab/rbator01/R_libs/4.4.0/"
.libPaths(LIB)
library(openxlsx)
library(tidymodels)
library(tidyverse)
library(workflows)
library(tune)
library(compositions)
library(caret)
library(VIM)
library(visdat)
library(recipes)
library(themis)
library(yardstick)
library(vip)
library(Boruta)

filter=dplyr::filter
rename=dplyr::rename
select=dplyr::select
setwd("/cluster/tufts/patralab/rbator01/aiml_ordovas_project/")

args <- commandArgs(trailingOnly = TRUE)
nclass = args[1]
outvar = args[2]
filter_cohort = args[3]
downsample = args[4]
seed = args[5]
visit = args[6]
importance = args[7]
data_string = args[8]

# nclass = 2
# outvar = "diabetes"
# filter_cohort = "none"
# downsample = 0
# seed=1
# visit='v2'
# importance = "boruta"
# ##data_string="sdoh"
# data_string="all"

save_string = paste0(data_string, "_",outvar,"_",visit,"_class", nclass,"_filter",filter_cohort,"_ds",downsample,"_", seed,"_tune_caseweights_",importance,"_25aug25")
print(save_string)

data = readRDS("r_pipeline/analysis/rds/harmonize_2cohort_healthsdohffq_20aug25_v1_rmmissing_50col_10row.rds")

table(data$visit, data$cohort)

# diabetes outcome, 2 class
tracker = read.xlsx("data/diabetes_status_wchange_2class_4aug25.xlsx")  %>%
  rename(diabetes = paste0("diabetes_",visit)) %>%
  select(studyid, cohort, diabetes) %>%
  filter(!is.na(diabetes))

tracker$cohort = factor(tracker$cohort, levels=c(0,1))

data = data  %>%
  inner_join(tracker, by=c('studyid','cohort'))

data$diabetes = factor(data$diabetes, levels=c(0,1))

table(data$cohort, data$diabetes)

if(filter_cohort != "none"){
  data <- data %>% filter(cohort == filter_cohort)
}

table(data$cohort, data$diabetes)

# remove variables# remove vw2_progressariables
var_to_rm = c("hmz_health_lab_a1c",
              "hmz_health_lab_gluc",
              "hmz_health_med_1",
              "hmz_health_med_1_age",
              "hmz_health_med_1_medication",
              "hmz_health_med_1_today",
              "hmz_health_lab_insulin",
              "studyid", 
              "visit")

data = data %>%
  select(-any_of(var_to_rm))

print(table(data$cohort, data$diabetes))
print(prop.table(table(data$cohort,data$diabetes),1) %>% round(2))

if(data_string == "sdoh"){
  sdoh_vars <- grep("^hmz_sdoh", names(data), value = TRUE)
  data <- data %>%
    select(all_of(c(sdoh_vars, "diabetes", "cohort")))
}

# split the data into trainng (75%) and testing (25%)
set.seed(seed)
split <- initial_split(data,
                       prop = 3/4,
                       strata = "diabetes")

# extract training and testing sets
train_data <- training(split)
test_data <- testing(split)

vars_to_keep <- c("cohort")

preprocessing_recipe <-
  recipe(diabetes ~ ., data = train_data) %>%
  # all your predictors that should be categorical are explicitly converted to factors before any further processing
  step_string2factor(all_nominal_predictors()) 

preprocessing_recipe = preprocessing_recipe  %>%
  # Step 1: Impute missing values in categorical variables with mode
  step_impute_mode(all_nominal_predictors(), -all_outcomes(),-any_of(vars_to_keep)) %>%
  step_nzv(all_predictors(), -all_outcomes(),-all_of(vars_to_keep)) %>%
  # Step 3: Impute missing values in numeric variables using KNN
  step_impute_knn(all_numeric_predictors(), neighbors = 5,-any_of(vars_to_keep)) %>%
  # Step 5: Remove highly correlated predictors (> 0.9)
  step_corr(all_numeric_predictors(), threshold = 0.9,-any_of(vars_to_keep)) %>%
  # Step 4: Scale numeric variables for better performance (optional)
  step_normalize(all_numeric_predictors(),-any_of(vars_to_keep))

# Prep the recipe and retain the outcome
prepped_recipe <- prep(preprocessing_recipe, training = train_data)

# Use juice() to retain outcome in training data
train_baked <- juice(prepped_recipe)

# Use bake() for testing data
test_baked <- bake(prepped_recipe, new_data = test_data)

saveRDS(train_baked, paste0("r_pipeline/analysis/rf/train_baked_", save_string,".rds"))
saveRDS(test_baked, paste0("r_pipeline/analysis/rf/test_baked_", save_string,".rds"))

train_baked = readRDS(paste0("r_pipeline/analysis/rf/train_baked_", save_string,".rds"))
test_baked = readRDS(paste0("r_pipeline/analysis/rf/test_baked_", save_string,".rds"))

w_tbl <- train_baked %>%
  count(cohort, diabetes, name = "n_cd") %>%
  group_by(cohort) %>%
  mutate(weight = mean(n_cd) / n_cd) %>%
  ungroup()

train_baked <- train_baked %>%
  left_join(w_tbl %>% select(cohort, diabetes, weight),
            by = c("cohort","diabetes")) %>%
  mutate(weight = importance_weights(weight))  

# keep a copy aligned to rows (used if Boruta drops the column)
weights_vec <- train_baked$weight

if(importance == "boruta"){
  set.seed(seed)
  boruta_result <- Boruta(
    formula = diabetes ~ .,
    data = train_baked %>% select(-weight),   # <-- do NOT give Boruta the weight column
    doTrace = 2,
    maxRuns = 100
  )
  
  boruta_vars <- getSelectedAttributes(boruta_result, withTentative = FALSE)
  tentative   <- getSelectedAttributes(boruta_result, withTentative = TRUE)
  confirmed   <- getSelectedAttributes(boruta_result, withTentative = FALSE)
  
  saveRDS(boruta_result, paste0("r_pipeline/analysis/rf/boruta_result_", save_string, ".rds"))
  write.csv(attStats(boruta_result), paste0("r_pipeline/analysis/rf/boruta_stats_", save_string, ".csv"))
  
  # reduce to Boruta-selected predictors + outcome (TRAIN), then reattach weights
  train_baked <- train_baked %>%
    select(all_of(c("diabetes", boruta_vars))) %>%
    mutate(weight = importance_weights(weights_vec))
  
  # reduce TEST the same way (no weights on test)
  test_baked <- test_baked %>%
    select(all_of(c("diabetes", boruta_vars)))
  
  saveRDS(train_baked, paste0("r_pipeline/analysis/rf/train_baked_borutafiltered_", save_string,".rds"))
  saveRDS(test_baked,  paste0("r_pipeline/analysis/rf/test_baked_borutafiltered_",  save_string,".rds"))
}

# ---- Random Forest with case weights via workflow ----
rf_model <- rand_forest(
  mode = "classification",
  mtry = tune(),
  min_n = tune(),
  trees = 1000
) %>%
  set_engine("ranger", importance = "impurity")

wf <- workflow() %>%
  add_model(rf_model) %>%
  add_formula(diabetes ~ .) %>%
  add_case_weights(weight)   # case-weight

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

saveRDS(tuned_results, paste0("r_pipeline/analysis/rf/rf_tune_res_", save_string))

best_params <- select_best(tuned_results, metric = "roc_auc")
final_wf <- finalize_workflow(wf, best_params)
saveRDS(final_wf, paste0("r_pipeline/analysis/rf/final_wf_rf_", save_string))

final_fit <- final_wf %>%
  fit(data = train_baked)      # <-- no case_weights arg; workflow uses `weight` column
saveRDS(final_fit, paste0("r_pipeline/analysis/rf/rf_final_fit_", save_string))

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
ggsave(p, filename = paste0("r_pipeline/analysis/results/log_", save_string, "_confmat.pdf"), width = 3, height = 3)

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

confirmed = getSelectedAttributes(boruta_result, withTentative = FALSE)

if(importance == "boruta"){
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
  ggtitle(paste0(outvar,"_",visit,"_class", nclass,"_filter",filter_cohort,"_ds",downsample,"_", seed)) +
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
ggsave(p, filename = paste0("r_pipeline/analysis/results/log_", save_string, ".pdf"), width = 5, height = 7)

# Prepare log data for saving
log_df <- vi_top %>%
  mutate(
    seed = seed,
    nclass = nclass,
    outvar = outvar,
    visit = visit,
    data_string = data_string,
    filter_cohort = filter_cohort,
    downsample = downsample,
    accuracy = perf_wide$accuracy,
    kap = perf_wide$kap,
    sensitivity = perf_wide$sensitivity,
    specificity = perf_wide$specificity
  ) %>%
  select(seed, nclass, outvar, visit, data_string, filter_cohort, downsample, rank, Variable, type, Importance,
         accuracy, kap, sensitivity, specificity)

# Save log to CSV
write.csv(log_df, paste0("r_pipeline/analysis/results/log_", save_string, ".csv"), row.names = FALSE)

# Save the trained model and results
saveRDS(wf, paste0("r_pipeline/analysis/rf/final_model_", save_string,".rds"))
saveRDS(test_preds, paste0("r_pipeline/analysis/rf/test_predictions_", save_string,".rds"))

# roc
roc_obj <- yardstick::roc_curve(test_preds, truth = diabetes, .pred_1, event_level="second")
saveRDS(roc_obj, paste0("r_pipeline/analysis/results/log_", save_string, "_roc.rds"))

p_roc <- autoplot(roc_obj) +
  ggtitle("ROC Curve")

ggsave(p_roc, filename = paste0("r_pipeline/analysis/results/log_", save_string, "_roc.pdf"), width = 5, height = 4)
