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


setwd("/cluster/tufts/patralab/rbator01/aiml_ordovas_project/")

# add the numeric and categorical
data = readRDS("data/harmonized_bprhs_prospect_sdoh_health_ffq_dataset_3_2025/output full hmz file (ffq sdoh health)/df_hmz_bprhs_prospect_3_2025_recodena.rds")

#data$hmz_health_eye_prospect.1_v2

ffq_nc = read.xlsx("data/numeric_categorical_ffq.xlsx") %>%
  mutate(across(where(is.character), trimws))
health_nc = read.xlsx("data/numeric_categorical_health.xlsx") %>%
  mutate(across(where(is.character), trimws))
sdoh_nc = read.xlsx("data/numeric_categorical_sdoh.xlsx") %>%
  mutate(across(where(is.character), trimws))

nc = rbind(ffq_nc, health_nc, sdoh_nc) %>%
  mutate(variable_trim = gsub("(_f|_1|_2|_3|_4|_5|_6|_7|_8|_9|_10)$","",variable)) %>%
  select(-variable)

all_cols = data.frame(variable = colnames(data) )  %>%
  mutate(variable_trim = gsub("ffq_|health_|sdoh_", "", variable)) %>%
  mutate(variable_trim = gsub("(_f|_1|_2|_3|_4|_5|_6|_7|_8|_9|_10)$","",variable_trim)) %>%
  left_join(nc, by="variable_trim") 

all_cols %>%
  filter(is.na(numeric_categorical))

write.xlsx(all_cols, "data/numeric_categorical.xlsx")

tmp = read.xlsx("data/numeric_categorical.xlsx") %>%
  select(-variable)

all_cols = all_cols %>%
  left_join(tmp, by="variable_trim")

write.xlsx(all_cols, "data/numeric_categorical.xlsx")


