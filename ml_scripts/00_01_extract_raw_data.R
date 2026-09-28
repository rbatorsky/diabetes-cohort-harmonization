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

# find the visit dates from the raw data ------
bm1 =  read_sas("../../data/bprhs/main_datasets/fullbaseline_03jan2018.sas7bdat")

head(bm1$vis1_dt)

d1 = bm1 %>%
  select(studyid, vis1_dt)

bm2 =  read_sas("data/bprhs/main_datasets/full2yr_19nov2018.sas7bdat")

d2 = bm2 %>%
  select(studyid, vis1_dt, vis2_dt_2yr) %>%
  mutate(
    days_between = as.numeric(vis2_dt_2yr - vis1_dt)  # difftime in days
  )

d2 = d2 %>%
  mutate(cohort = "BPRHS")

bm3 =  read_sas("../../data/bprhs/main_datasets/released_5yr_bprhs_07dec23.sas7bdat")

diff = read.xlsx("../../data/hmz_data/confirm_val_diffs_6nov25.xlsx")

true_h2 = bm3 %>%
  select(studyid, pdq_2ht_5yr) 

true_i2 = bm3 %>%
  select(studyid, pdq_2it_5yr)

true_i4 = bm3 %>%
  select(studyid, pdq_4it_5yr)

h2 = diff %>%
  filter(visit == "v3" & column == "hmz_sdoh_pdq_2h_other") %>%
  left_join(true_h2, by="studyid")

write.xlsx(h2, "../../data/hmz_data/confirm_val_diffs_hmz_sdoh_pdq_2h_other.xlsx")


i2 = diff %>%
  filter(visit == "v3" & column == "hmz_sdoh_pdq_2i_other")%>%
  left_join(true_i2, by="studyid")

write.xlsx(i2, "../../data/hmz_data/confirm_val_diffs_hmz_sdoh_pdq_2i_other.xlsx")


i4 = diff %>%
  filter(visit == "v3" & column == "hmz_sdoh_pdq_4i_other")%>%
  left_join(true_i4, by="studyid")


write.xlsx(i4, "data/hmz_data/confirm_val_diffs_hmz_sdoh_pdq_4i_other.xlsx")

pr_s = read.xlsx("data/prospect/data_13may24/csv/PROSPECT4_DATA_SPANISH_VISITS1&2__2024-11-26_1522.xlsx") %>%
  filter(!is.na(studyid)) %>%
  mutate(gen1 = {
    x <- gen1
    if (inherits(x, "Date")) x
    else if (is.numeric(x)) as.Date(x, origin = "1899-12-30")  # Excel serials
    else suppressWarnings(ymd(x))                               # or mdy/dmy depending on your data
  }) 

pr_s = pr_s %>%
  filter(!is.na(gen1))

exclude = pr_s %>%
  filter(exclude___1 == 1)

table(exclude$redcap_event_name)

exclude_v1 = exclude %>%
  filter(redcap_event_name == "baseline_arm_1")

exclude_v2 = exclude %>%
  filter(redcap_event_name == "visit_2_arm_1")

exclude_v1$studyid

exclude_v2$studyid

intersect(exclude_v1$studyid, exclude_v2$studyid)

length(exclude_v1$studyid)
length(exclude_v2$studyid)

pr_e = read.xlsx("../../data/prospect/data_13may24/csv/PROSPECT4a_DATA_ENGLISH_VISITS1&2_2024-11-26_1523.xlsx") %>%
  filter(!is.na(studyid)) %>%
  mutate(gen1 = {
    x <- gen1
    if (inherits(x, "Date")) x
    else if (is.numeric(x)) as.Date(x, origin = "1899-12-30")  # Excel serials
    else suppressWarnings(ymd(x))                               # or mdy/dmy depending on your data
  }) 

pr_e = pr_e %>%
  filter(!is.na(gen1))

p2 = pr_s %>%
  select(studyid, redcap_event_name, gen1)

p3 = pr_e %>%
  select(studyid, redcap_event_name, gen1)

p4 = rbind(p2,p3) 

head(p4)

p4_wide <- p4 %>%
  # 1) make sure the date column is actually Date
  mutate(gen1 = ymd(gen1)) %>%
  filter(!is.na(redcap_event_name) )%>%
  # 3) if duplicates exist per studyid/event, pick the earliest date
  group_by(studyid, redcap_event_name) %>%
  # 4) pivot wider
  pivot_wider(names_from = redcap_event_name, values_from = gen1) %>%
  rename(vis1_dt = baseline_arm_1) %>%
  rename(vis2_dt_2yr = visit_2_arm_1) %>%
  # 5) compute interval in days (signed: vis2 - vis1)
  mutate(days_between = as.numeric(vis2_dt_2yr - vis1_dt))
  
p4_wide %>%
  filter(days_between < 0)

p4_wide = p4_wide %>%
  mutate(cohort = "PROSPECT")

final = rbind(d2, p4_wide)

write.xlsx(final, "../../data/visit_dates_intervals_9oct25.xlsx")


## 
ffq = read.xlsx("../../data/prospect/data_13may24/csv/ffq_perday_9dec24.xlsx")

ca = ffq %>%
  select(studyid, rfca, visit)

ca <- ca %>%
  mutate(
    mad_val = mad(rfca, constant = 1),
    med_val = median(rfca),
    z_mad   = abs(rfca - med_val) / mad_val,
    is_outlier = z_mad > 5   # threshold: 3 MADs from median
  )

ca_out  = ca %>% 
  filter(is_outlier)

table(ca_out$visit)

# raw data ----
ffq_proc = read.csv("../../data/prospect/data_13may24/csv/ffq_perday_perfood659_all_copy_Tufts.csv")
ffq_raw = read.xlsx("../../data/prospect/data_13may24/csv/PROSPECT5_FFQ_DATA_RAW_Spanish_VISITS1&2_2024-11-26.xlsx")
ffq_raw_e = read.xlsx("../../data/prospect/data_13may24/csv/PROSPECT5a_FFQ_DATA_RAW_English_VISITS1&2_2024-11-26.xlsx")


ids <- c(
  "813100760","817101473","817102425","819100566","819102006",
  "832100192","845101679","851100146","851100161","851100313",
  "851100372","851100462","851100609","851101336","851101632",
  "851101913","851102345","865100492","999100116","999100121",
  "999999999"
)

intersect(ffq_raw$studyid, ids)
intersect(ffq_raw_e$studyid, ids)










head(ffq_raw)
test = ffq_raw %>%
  group_by(studyid, visit) %>%
  summarise(n=n())

analyze_invalid = ffq_raw %>%
  select(studyid, invalid, visit) %>%
  filter(invalid == 1) %>%
  group_by(studyid, visit) %>%
  summarise(n=n())

head(analyze_invalid)
table(analyze_invalid$visit, analyze_invalid$n)

ca_raw = ffq_raw %>%
  select(studyid, Sub_id, SUB_NAME, rfca, rfvb6, invalid, batch, visit) %>%
  mutate(visit = ifelse(visit == 1, "v1","v2"))

view(ca_raw)

ca_raw_sum_out = ca_raw %>%
  group_by(studyid, visit) %>%
  summarise(ca_sum = sum(rfca)) %>%
  inner_join(ca_out, by=c("studyid","visit"))


test = ca_raw %>%
  filter(studyid == "101101301")

test1 = ca_raw %>%
  filter(studyid == "201102701")

view(test1)


# vb6 ----

b6_raw = ffq_raw %>%
  select(studyid, Sub_id, SUB_NAME, rfca, invalid, batch, visit) %>%
  mutate(visit = ifelse(visit == 1, "v1","v2"))

view(ca_raw)

ca_raw_sum_out = ca_raw %>%
  group_by(studyid, visit) %>%
  summarise(ca_sum = sum(rfca)) %>%
  inner_join(ca_out, by=c("studyid","visit"))


test = ca_raw %>%
  filter(studyid == "101101301")

test1 = ca_raw %>%
  filter(studyid == "201102701")

view(test1)

