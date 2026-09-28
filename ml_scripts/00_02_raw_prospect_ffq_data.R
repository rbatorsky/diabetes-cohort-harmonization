#######
## Check the raw data during development
#######

suppressPackageStartupMessages({
  library(openxlsx)
  library(visdat)
  library(haven)
  library(dplyr)
  library(tibble)
})

ffq_raw = read.csv("../../data/prospect/data_13may24/csv/ffq_perday_perfood659_all_copy_Tufts.csv")

analyze_invalid = ffq_raw %>%
  select(studyid, invalid, visit) %>%
  filter(invalid == 1) %>%
  group_by(studyid, visit) %>%
  summarise(n=n())

test = ffq_raw %>%
  select('studyid','Sub_id','SUB_NAME','servings','gramamt','rfca') %>%
  filter(SUB_NAME == "calcium")

view(test)

