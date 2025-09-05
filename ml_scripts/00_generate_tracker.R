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
filter=dplyr::filter
rename=dplyr::rename
select=dplyr::select

setwd("/cluster/tufts/patralab/rbator01/aiml_ordovas_project/")

# Define whether subject has diabetes at each timepoint ----

data = read.csv("data/andreia_hmz_data/hmz_bprhs_prospect_30july_2025.csv")

# simplified diabetes function using harmonized data only
assign_diabetes <- function(df, nclass = 3) {
  
  # Thresholds
  a1c_cut2 <- 6.5
  a1c_cut1 <- 5.7
  gluc_cut2 <- 126
  gluc_cut1 <- 100
  
  df <- df %>%
    mutate(
      diabetes = case_when(
        # All relevant fields missing
        is.na(hmz_health_med_1) & is.na(hmz_health_med_1_medication) &
          is.na(hmz_health_lab_a1c) & is.na(hmz_health_lab_gluc) ~ NA_real_,
        
        # Definite diabetes
        !is.na(hmz_health_med_1_medication) & hmz_health_med_1_medication == 1 ~ ifelse(nclass == 2, 1, 2),
        !is.na(hmz_health_lab_a1c) & hmz_health_lab_a1c >= a1c_cut2             ~ ifelse(nclass == 2, 1, 2),
        !is.na(hmz_health_lab_gluc) & hmz_health_lab_gluc >= gluc_cut2         ~ ifelse(nclass == 2, 1, 2),
        
        # Prediabetes only if nclass == 3
        nclass == 3 & !is.na(hmz_health_lab_a1c) & hmz_health_lab_a1c >= a1c_cut1 ~ 1,
        nclass == 3 & !is.na(hmz_health_lab_gluc) & hmz_health_lab_gluc >= gluc_cut1 ~ 1,
        
        # Otherwise: non-diabetic
        TRUE ~ 0
      )
    )
  
  return(df)
}                                                     


dfm3 = assign_diabetes(data) %>%
  select(cohort, visit, studyid, diabetes) %>%
  mutate(cohort = ifelse(cohort == "BPRHS",0,1))
write.xlsx(dfm3, "data/diabetes_status_3class_4aug25.xlsx")

dfm2 = assign_diabetes(data, nclass=2) %>%
  select(cohort, visit, studyid, diabetes) %>%
  mutate(cohort = ifelse(cohort == "BPRHS",0,1))

write.xlsx(dfm2, "data/diabetes_status_2class_4aug25.xlsx")

get_diabetes_change <- function(df_with_diabetes) {
  df_with_diabetes %>%
    filter(visit %in% c("v1", "v2")) %>%
    pivot_wider(
      id_cols = c(studyid, cohort),
      names_from = visit,
      values_from = diabetes,
      names_prefix = "diabetes_"
    ) %>%
    mutate(
      diabetes_change = diabetes_v2 - diabetes_v1
    )
}

dfm2_change <- get_diabetes_change(dfm2)
write.xlsx(dfm2_change, "data/diabetes_status_wchange_2class_4aug25.xlsx")

head(dfm2_change )
dfm3_change <- get_diabetes_change(dfm3)
write.xlsx(dfm2_change, "data/diabetes_status_wchange_3class_4aug25.xlsx")


