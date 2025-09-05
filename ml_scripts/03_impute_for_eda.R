LIB="/cluster/tufts/patralab/rbator01/R_libs/4.4.0/"
.libPaths(LIB)

library(openxlsx)
library(tidyverse)
library("corrplot")
library(pheatmap)
library(VIM)
library(naniar)
library(sas7bdat)
library(haven)
library(caret)
library(ggpubr)
library(visdat)
library(ggfortify)
library("FactoMineR")
library(ggcorrplot)
library(tidymodels)
filter=dplyr::filter
rename=dplyr::rename
select=dplyr::select
library(fastDummies)

setwd("/cluster/tufts/patralab/rbator01/aiml_ordovas_project/")

# impute mean for categorical -----
#data = readRDS("r_pipeline/analysis/rds/harmonize_2cohort_healthsdohffq_24apr25_v1_rmmissing_50col_10row.rds")
data = readRDS("r_pipeline/analysis/rds/harmonize_2cohort_healthsdohffq_20aug25_v1_rmmissing_50col_10row.rds")

table(data$visit, data$cohort)

tracker = read.xlsx("data/diabetes_status_2class_4aug25.xlsx")  %>%
  filter(!is.na(diabetes)) 

tracker$cohort = factor(tracker$cohort, levels=c(0,1))

data = data  %>%
  inner_join(tracker, by=c('studyid','visit','cohort'))

dim(data)

data$diabetes = factor(data$diabetes, levels=c(0,1))

# remove variables
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

vars_to_keep <- c("cohort")

preprocessing_recipe <-
  recipe(diabetes ~ ., data = data) %>%
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
saveRDS(baked_data, "r_pipeline/analysis/rds/harmonize_2cohort_healthsdohffq_20aug25_v1_rmmissing_50col_10row_preproc_for_eda.rds")
