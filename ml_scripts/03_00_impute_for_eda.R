#######
## Process data for exploratory data analysis
#######

suppressPackageStartupMessages({
  library(openxlsx)
  library("corrplot")
  library(pheatmap)
  library(naniar)
  library(sas7bdat)
  library(haven)
  library(caret)
  library(ggpubr)
  library(visdat)
  library(ggfortify)
  library("FactoMineR")
  library(tidymodels)
  library(fastDummies)
  library(dplyr)
  library(ggplot2)
})

source("utils.R")

RDS1 = "../../analysis/harmonize_2cohort_healthsdohffq_v1_rmmissing_50col_10row.rds"
#TRK  = "../../data/hmz_data/diabetes_status_wchange_2class_7nov25.xlsx"
TRK  = "../../data/hmz_data/diabetes_tracker_2class_23feb26.xlsx"

data <- read_merge_tracker(
  rds_path     = RDS1,
  tracker_path = TRK,
  visit        = "v1",
  label_cohort = TRUE,          # keep 0/1
  filter_cohort = "none"         # or 0 / 1 / "BPRHS" / "PROSPECT"
)

table(data$cohort)

data <- data %>%
  mutate(row_id = row_number())

# remove variables
var_to_rm = c("data$hmz_days_since_visit_1",
              "hmz_health_lab_a1c",
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

vars_to_keep <- c("cohort")

preprocessing_recipe <-
  recipe(diabetes ~ ., data = data) %>%
  update_role(row_id, new_role = "id") %>%         # <- protect row_id
  # all your predictors that should be categorical are explicitly converted to factors before any further processing
  step_string2factor(all_nominal_predictors())  %>%
  # Step 1: Impute missing values in categorical variables with mode
  step_impute_mode(all_nominal_predictors(), -all_outcomes(),-any_of(vars_to_keep)) %>%
  step_nzv(all_predictors(), -all_outcomes(),-all_of(vars_to_keep)) %>%
  # Step 3: Impute missing values in numeric variables using KNN
  step_impute_knn(all_numeric_predictors(), neighbors = 5,-any_of(vars_to_keep)) %>%
  # Step 5: Remove highly correlated predictors (> 0.9)
  step_corr(all_numeric_predictors(), threshold = 0.9,-any_of(vars_to_keep)) %>%
  # Step 4: Scale numeric variables for better performance (optional)
  step_normalize(all_numeric_predictors(),-any_of(vars_to_keep))

prepped_recipe <- prep(preprocessing_recipe,
                     training = data)

baked_data <- bake(prepped_recipe, new_data = data)

table(baked_data$cohort)
saveRDS(baked_data, "../../analysis/harmonize_2cohort_healthsdohffq_v1_rmmissing_50col_10row_preproc_for_eda_23feb26.rds")


# # residualize by cohort -----
# noBR_df <- baked_data %>%
#   dplyr::mutate(cohort = as.factor(cohort), diabetes = as.factor(diabetes))
# 
# head(noBR_df$row_id)
# 
# BR_df <- residualize_by_cohort(
#   df = noBR_df,
#   cohort_var = "cohort",
#   outcome    = "diabetes",
#   weight_col = "weight"
# )
# 
# head(BR_df$row_id)
# 
# saveRDS(noBR_df , "../../analysis/eda_preproc_v1_noBR.rds")
# saveRDS(BR_df,   "../../analysis/eda_preproc_v1_BR.rds")
