LIB="/cluster/tufts/patralab/rbator01/R_libs/4.4.0/"
.libPaths(LIB)

library(openxlsx)
library(tidyverse)
library(compositions)
library("corrplot")
library(pheatmap)
library(ComplexHeatmap)
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

# generate harmonized tables for ffq and select main columns
# note this is the final code used for ffq

# Prospect sum up the perfood -----
pr_cols_to_rm=c("batch","invalid","SUB_NAME","Sub_id")
data_perday_perfood =  read.csv("data/prospect/data_13may24/csv/ffq_perday_perfood659_all_copy_Tufts.csv") %>%
  select(-all_of(pr_cols_to_rm))

v1 = data_perday_perfood %>%
  filter(visit == 1) %>%
  group_by(studyid) %>%
  summarise(across(where(is.numeric), ~ sum(.x, na.rm = TRUE))) %>%
  mutate(visit = "w1")

v2 = data_perday_perfood %>%
  filter(visit == 2) %>%
  group_by(studyid) %>%
  summarise(across(where(is.numeric), ~ sum(.x, na.rm = TRUE))) %>%
  mutate(visit = "w2")

data_perfood = rbind(v1,v2)

#write.xlsx(data_perfood, "data/prospect/data_13may24/csv/prospect_ffq_perday_10dec24.xlsx")

# test
#data_perfood = read.xlsx("data/prospect/data_13may24/csv/prospect_ffq_perday_10dec24.xlsx")
#table(data_perfood$visit)

#Generate harmonized FFQ  --------
ffq_perday_hmz <- function(col, file, visit_name, cohort){
  ffq_h_key = read.xlsx("data/harmonize_ffq_26nov24_rebecca.xlsx")

  # ffq_h_key
  col="prospect_perday_perfood"
  file="data/prospect/data_13may24/csv/ffq_perday_10dec24.xlsx"
  visit="w1"
  cohort="prospect"

  ffq_h_key_rename = ffq_h_key %>%
    select(col, "harmonized_name") %>%
    filter(!is.na(get(col)) & !is.na(harmonized_name))

  b_1 =  read.xlsx(file) %>%
    mutate(across(where(is.character), ~na_if(., "N/A")))

  colnames(b_1 ) = tolower(colnames(b_1))

  b_1 = b_1 %>%
    select("studyid",unique(ffq_h_key_rename[[col]]))  %>%
    rename_at(vars(ffq_h_key_rename[[col]]), ~ ffq_h_key_rename$harmonized_name) %>%
    mutate(hmz_cohort = cohort)

  if(cohort == "bprhs"){
    b_1 = b_1 %>%
      mutate(hmz_visit = visit_name)
  }else if(cohort == "prospect"){
    b_1 = b_1 %>%
      filter(hmz_visit == visit_name)
  }

  outfile_rds = paste0(gsub(".xlsx","_",file),visit_name,"_hmz.rds")
  outfile_xlsx = paste0(gsub(".xlsx","_",file),visit_name,"_hmz.xlsx")
  
  saveRDS(b_1, outfile_rds)
  write.xlsx(b_1, outfile_xlsx)
  
}

ffq_perday_hmz(col="bprhs_baseline",
               file="data/bprhs/ffq/baseline_ffq_per_day_011922.xlsx",
               visit="w1",
               cohort="bprhs")

ffq_perday_hmz(col="bpr_2",
               file="data/bprhs/ffq/twoyear_ffq_per_day_011922.xlsx",
               visit="w2",
               cohort="bprhs")

ffq_perday_hmz(col="bpr_5",
               file="data/bprhs/ffq/fiveyear_ffq_per_day_062223.xlsx",
               visit="w3",
               cohort="bprhs")

ffq_perday_hmz(col="bpr_8",
               file="data/bprhs/ffq/eightyear_ffq_per_day_121323.xlsx",
               visit="w4",
               cohort="bprhs")


ffq_perday_hmz(col="prospect_perday_perfood",
               file="data/prospect/data_13may24/csv/prospect_ffq_perday_10dec24.xlsx",
               visit="w1",
               cohort="prospect")

ffq_perday_hmz(col="prospect_perday_perfood",
               file="data/prospect/data_13may24/csv/prospect_ffq_perday_10dec24.xlsx",
               visit="w2",
               cohort="prospect")

# Generate harmonized main ----

# convert to xlsx
# filename="data/data/main_datasets/fullbaseline_03jan2018.sas7bdat"
# filename= "data/data/main_datasets/full2yr_19nov2018.sas7bdat"
# filename= "data/data/main_datasets/released_8yr_010424.sas7bdat"
# filename= "data/data/main_datasets/released_5yr_bprhs_07dec23.sas7bdat"
# b_main_1 =  read_sas(filename)
# write.xlsx(b_main_1, gsub("sas7bdat","xlsx", filename))


main_hmz <- function(file, col, visit_name, cohort){
  
  main_h_key = read.xlsx("data/harmonize_select_main_7feb25.xlsx")

  # file = "data/prospect/data_13may24/csv/PROSPECT4_DATA_2024-11-26_1522.xlsx"
  # col = "prospect"
  # visit_name = "w1"
  # cohort = "prospect"
  
  main_h_key_rename = main_h_key %>%
    filter(!is.na(get(col)) & !is.na(harmonized_name)) 

  if(cohort == "bprhs"){
    
    b_main_1 =  read.xlsx(file)%>%
      mutate(across(where(is.character), ~na_if(., "N/A"))) 
    
    colnames(b_main_1) = tolower(colnames(b_main_1))
    
    b_main_1 = b_main_1 %>%
      select("studyid", main_h_key_rename[[col]]) %>%
      mutate(hmz_visit = visit_name) %>%
      rename_at(vars(main_h_key_rename[[col]]), ~ main_h_key_rename$harmonized_name) 
    
    }else if (cohort == "prospect"){
    
    # add the main variables from prospect
    data_p_main_s = read.xlsx("data/prospect/data_13may24/csv/PROSPECT4_DATA_SPANISH_VISITS1&2__2024-11-26_1522.xlsx") %>%
      filter(!is.na(studyid))
    
    data_p_main_e = read.xlsx("data/prospect/data_13may24/csv/PROSPECT4a_DATA_ENGLISH_VISITS1&2_2024-11-26_1523.xlsx") %>%
      filter(!is.na(studyid))
    
    data_p_main_s = data_p_main_s %>%
      select("studyid", "redcap_event_name", main_h_key_rename[[col]])
    
    data_p_main_e = data_p_main_e %>%
      select("studyid", "redcap_event_name", main_h_key_rename[[col]])
    
    b_main_1 = rbind(data_p_main_s, data_p_main_e) %>%
      rename(hmz_visit = redcap_event_name) %>%
      mutate(hmz_visit = ifelse(hmz_visit == "baseline_arm_1","BASELINE","v2")) %>%
      rename_at(vars(main_h_key_rename[[col]]), ~ main_h_key_rename$harmonized_name) 

    
    # harmonize here
    #b_main_1$hmz_med1x = ifelse(is.na(b_main_1$hmz_med1x),0,b_main_1$hmz_med1x)
    b_main_1 = b_main_1 %>%
      filter(hmz_visit == visit_name)
  }
  
  b_main_1 = b_main_1 %>%
    mutate(hmz_cohort = cohort)
  
  saveRDS(b_main_1, gsub(".xlsx", paste0("_", visit_name, "_hmz.rds"), file))
}

b0 = read.xlsx("data/bprhs/main_datasets/fullbaseline_03jan2018.xlsx")
b2 = read.xlsx("data/bprhs/main_datasets/full2yr_19nov2018.xlsx")
b5 = read.xlsx("data/bprhs/main_datasets/released_5yr_bprhs_07dec23.xlsx")
b8 = read.xlsx("data/bprhs/main_datasets/released_8yr_010424.xlsx")
pr0 = read.xlsx("data/prospect/data_13may24/csv/PROSPECT4_DATA_SPANISH_VISITS1&2__2024-11-26_1522.xlsx")

pr0$med1c


main_hmz(file = "data/bprhs/main_datasets/fullbaseline_03jan2018.xlsx",
         col = "bprhs_0",
         visit_name = "v1",
         cohort="bprhs")

main_hmz(file = "data/bprhs/main_datasets/full2yr_19nov2018.xlsx",
         col = "bprhs_2",
         visit_name = "v2",
         cohort="bprhs")

main_hmz(file = "data/bprhs/main_datasets/released_5yr_bprhs_07dec23.xlsx",
         col = "bprhs_5",
         visit_name = "v3",
         cohort="bprhs")

main_hmz(file = "data/bprhs/main_datasets/released_8yr_010424.xlsx",
         col = "bprhs_8",
         visit_name = "v4",
         cohort="bprhs")

main_hmz(file = "data/prospect/data_13may24/csv/PROSPECT4_DATA_2024-11-26_1522.xlsx",
         col = "prospect",
         visit_name = "w1",
         cohort = "prospect")

main_hmz(file = "data/prospect/data_13may24/csv/PROSPECT4_DATA_2024-11-26_1522.xlsx",
         col = "prospect",
         visit_name = "w2",
         cohort = "prospect")

# read in harmonized ffq files -----
b1 = readRDS("data/bprhs/ffq/baseline_ffq_per_day_011922_w1_hmz.rds")
b2 = readRDS("data/bprhs/ffq/twoyear_ffq_per_day_011922_w2_hmz.rds")
b3 = readRDS("data/bprhs/ffq/fiveyear_ffq_per_day_062223_w3_hmz.rds")
b4 = readRDS("data/bprhs/ffq/eightyear_ffq_per_day_121323_w4_hmz.rds")
p1 = readRDS("data/prospect/data_13may24/csv/prospect_ffq_perday_10dec24_w1_hmz.rds")
p2 = readRDS("data/prospect/data_13may24/csv/prospect_ffq_perday_10dec24_w2_hmz.rds")

nrow(p1)
nrow(p2)

common_cols = Reduce(intersect, list(colnames(b1),
                                     colnames(b2),
                                     colnames(b3),
                                     colnames(b4),
                                     colnames(p1),
                                     colnames(p2)))

df = rbind( b1 %>%
              select(all_of(common_cols)),
            b2 %>%
              select(all_of(common_cols)),
            b3 %>%
              select(all_of(common_cols)),
            b4 %>%
              select(all_of(common_cols)),
            p1 %>%
              select(all_of(common_cols)),
            p2 %>%
              select(all_of(common_cols)))

saveRDS(df, "data/harmonize_bpr_prospect_ffq_10feb25.rds")
write.xlsx(df, "data/harmonize_bpr_prospect_ffq_10feb25.xlsx")

# read in harmonized main files ----
b1m = readRDS("data/bprhs/main_datasets/fullbaseline_03jan2018_w1_hmz.rds")
b2m = readRDS("data/bprhs/main_datasets/full2yr_19nov2018_w2_hmz.rds")
b3m = readRDS("data/bprhs/main_datasets/released_5yr_bprhs_07dec23_w3_hmz.rds")
b4m = readRDS("data/bprhs/main_datasets/released_8yr_010424_w4_hmz.rds")
p1m = readRDS("data/prospect/data_13may24/csv/PROSPECT4_DATA_2024-11-26_1522_w1_hmz.rds")
p2m = readRDS("data/prospect/data_13may24/csv/PROSPECT4_DATA_2024-11-26_1522_w2_hmz.rds")

table(p2m$hmz_med1)

# it's missing but we want to retain it as a column
b4m$hmz_glyhgb = NA
b1m$hmz_med1a = NA
b2m$hmz_med1 = NA
b3m$hmz_med1 = NA
b1m$hmz_med2 = NA
b2m$hmz_med2 = NA
b3m$hmz_med2 = NA
b4m$hmz_med2 = NA
b1m$hmz_med2a = NA
b2m$hmz_med2a = NA
b3m$hmz_med2a = NA
b4m$hmz_med2a = NA
b1m$hmz_med2d = NA
b2m$hmz_med2d = NA
b3m$hmz_med2d = NA
b4m$hmz_med2d = NA
p1m$hmz_med1a = NA
p2m$hmz_med1a = NA
p1m$hmz_mantidb = NA
p2m$hmz_mantidb = NA
b3m$hmz_med1b = NA

common_cols = Reduce(intersect, list(colnames(b1m),
                                     colnames(b2m),
                                     colnames(b3m),
                                     colnames(b4m),
                                     colnames(p1m),
                                     colnames(p2m)))

common_cols

dfm = rbind( b1m %>%
               select(all_of(common_cols)),
             b2m %>%
               select(all_of(common_cols)),
             b3m %>%
               select(all_of(common_cols)),
             b4m %>%
               select(all_of(common_cols)),
             p1m %>%
               select(all_of(common_cols)),
             p2m %>%
               select(all_of(common_cols))) %>%
  distinct()

saveRDS(dfm, "data/harmonize_select_main_10feb25.rds")

join = df %>%
  full_join(dfm, by=c("hmz_studyid", "hmz_visit","hmz_cohort"))

saveRDS(join, "data/harmonize_ffq_select_main_commoncols_fulljoin.rds")




