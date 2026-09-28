# --------------------------------------------
# Diabetes trackers (2-class + 3-class)
# - One tracker per classification (dfm2, dfm3)
# - Each tracker includes:
#     * diabetes_change_v1_v2   (diabetes_v2 - diabetes_v1)
#     * delta_a1c_v1_v2         (a1c_v2 - a1c_v1)
#   (NA if change cannot be defined)
# --------------------------------------------

suppressPackageStartupMessages({
  library(openxlsx)
  library(dplyr)
  library(tidyr)
})

# ---------------- Inputs / Outputs ----------------
IN_CSV <- "../../data/hmz_data/df_hmz_bprhs_prospect_2025.csv"

OUT_2CLASS <- "../../data/hmz_data/diabetes_tracker_2class_24feb26.xlsx"
OUT_3CLASS <- "../../data/hmz_data/diabetes_tracker_3class_24feb26.xlsx"

# ---------------- Read data ----------------
data <- read.csv(IN_CSV)

# ---------------- Assign diabetes status ----------------
assign_diabetes <- function(df, nclass = 3) {
  stopifnot(nclass %in% c(2, 3))
  
  # Thresholds
  a1c_cut2  <- 6.5
  a1c_cut1  <- 5.7
  gluc_cut2 <- 126
  gluc_cut1 <- 100
  
  df %>%
    mutate(
      diabetes = case_when(
        # All relevant fields missing
        is.na(hmz_health_med_1) &
          is.na(hmz_health_med_1_medication) &
          is.na(hmz_health_lab_a1c) &
          is.na(hmz_health_lab_gluc) ~ NA_real_,
        
        # Definite diabetes
        !is.na(hmz_health_med_1_medication) & hmz_health_med_1_medication == 1 ~ ifelse(nclass == 2, 1, 2),
        !is.na(hmz_health_lab_a1c) & hmz_health_lab_a1c >= a1c_cut2             ~ ifelse(nclass == 2, 1, 2),
        !is.na(hmz_health_lab_gluc) & hmz_health_lab_gluc >= gluc_cut2          ~ ifelse(nclass == 2, 1, 2),
        
        # Prediabetes only if nclass == 3
        nclass == 3 & !is.na(hmz_health_lab_a1c)  & hmz_health_lab_a1c  >= a1c_cut1  ~ 1,
        nclass == 3 & !is.na(hmz_health_lab_gluc) & hmz_health_lab_gluc >= gluc_cut1 ~ 1,
        
        # Otherwise: non-diabetic
        TRUE ~ 0
      )
    )
}

# ---------------- Compute V2 - V1 deltas (without dropping people) ----------------
# Returns ONE row per subject (studyid, cohort) with:
#   diabetes_v1, diabetes_v2, diabetes_change_v1_v2
#   a1c_v1, a1c_v2, delta_a1c_v1_v2
get_v1_v2_deltas <- function(df_with_diabetes) {
  df_with_diabetes %>%
    filter(visit %in% c("v1", "v2")) %>%
    select(studyid, cohort, visit,
           diabetes,
           hmz_health_lab_a1c,
           hmz_days_since_visit_1) %>%
    distinct() %>%
    pivot_wider(
      id_cols = c(studyid, cohort),
      names_from = visit,
      values_from = c(diabetes,
                      hmz_health_lab_a1c,
                      hmz_days_since_visit_1),
      names_sep = "_"
    ) %>%
    rename(
      diabetes_v1 = diabetes_v1,
      diabetes_v2 = diabetes_v2,
      a1c_v1      = hmz_health_lab_a1c_v1,
      a1c_v2      = hmz_health_lab_a1c_v2,
      days_v1     = hmz_days_since_visit_1_v1,
      days_v2     = hmz_days_since_visit_1_v2
    ) %>%
    mutate(
      diabetes_change_v1_v2 = if_else(
        !is.na(diabetes_v1) & !is.na(diabetes_v2),
        diabetes_v2 - diabetes_v1,
        NA_real_
      ),
      delta_a1c_v1_v2 = if_else(
        !is.na(a1c_v1) & !is.na(a1c_v2),
        a1c_v2 - a1c_v1,
        NA_real_
      ),
      followup_days_v1_v2 = if_else(
        !is.na(days_v1) & !is.na(days_v2),
        days_v2 - days_v1,
        NA_real_
      )
    )
}

# ---------------- Build trackers ----------------
make_tracker <- function(df, nclass) {
  tracker <- assign_diabetes(df, nclass = nclass) %>%
    transmute(
      cohort  = if_else(cohort == "BPRHS", 0, 1),
      visit,
      studyid,
      diabetes,
      hmz_health_lab_a1c,
      hmz_days_since_visit_1
    )
  
  deltas <- get_v1_v2_deltas(tracker)
  
  # Merge deltas back into per-visit tracker.
  # Everyone stays; deltas are NA unless both v1 and v2 are present & non-missing.
  tracker %>%
    left_join(
      deltas %>% select(
        studyid, cohort,
        diabetes_v1, diabetes_v2,
        diabetes_change_v1_v2,
        a1c_v1, a1c_v2,
        delta_a1c_v1_v2,
        followup_days_v1_v2
      ),
      by = c("studyid", "cohort")
    )
}

dfm2 <- make_tracker(data, nclass = 2)
dfm3 <- make_tracker(data, nclass = 3)

# ---------------- Write outputs ----------------
write.xlsx(dfm2, OUT_2CLASS, overwrite = TRUE)
write.xlsx(dfm3, OUT_3CLASS, overwrite = TRUE)

# Optional quick sanity checks (comment out if you don't want console output)
print(table(dfm2$cohort, dfm2$visit, useNA = "ifany"))
print(table(dfm2$cohort, dfm2$diabetes_change_v1_v2, useNA = "ifany"))
print(table(dfm2$cohort, is.na(dfm2$delta_a1c_v1_v2), dfm2$visit, useNA = "ifany"))


# ---------------- Summary: delta_a1c by cohort & visit ----------------

summ_delta <- dfm2 %>%
  filter(visit %in% c("v1","v2")) %>%
  group_by(cohort, visit) %>%
  summarise(
    n_rows              = n(),
    n_subjects          = n_distinct(studyid),
    n_delta_nonmissing  = sum(!is.na(delta_a1c_v1_v2)),
    prop_delta_defined  = mean(!is.na(delta_a1c_v1_v2)),
    mean_delta          = mean(delta_a1c_v1_v2, na.rm = TRUE),
    sd_delta            = sd(delta_a1c_v1_v2, na.rm = TRUE),
    median_delta        = median(delta_a1c_v1_v2, na.rm = TRUE),
    q25_delta           = quantile(delta_a1c_v1_v2, 0.25, na.rm = TRUE),
    q75_delta           = quantile(delta_a1c_v1_v2, 0.75, na.rm = TRUE),
    min_delta           = min(delta_a1c_v1_v2, na.rm = TRUE),
    max_delta           = max(delta_a1c_v1_v2, na.rm = TRUE),
    .groups = "drop"
  ) %>%
  arrange(cohort, visit)

cat("\n==============================\n")
cat("Delta HbA1c (V2 - V1) summary by cohort and visit (dfm2)\n")
cat("Cohort: 0=BPRHS, 1=PROSPECT\n")
cat("==============================\n")
print(summ_delta)

# Optional: also show distribution of binned change by cohort & visit
summ_bins <- dfm2 %>%
  filter(visit %in% c("v1","v2")) %>%
  mutate(delta_cat = case_when(
    is.na(delta_a1c_v1_v2)        ~ NA_character_,
    delta_a1c_v1_v2 >  0.5        ~ "worsening",
    delta_a1c_v1_v2 < -0.5        ~ "improvement",
    TRUE                         ~ "stable"
  )) %>%
  group_by(cohort, visit, delta_cat) %>%
  summarise(n = n_distinct(studyid), .groups = "drop") %>%
  tidyr::pivot_wider(names_from = delta_cat, values_from = n, values_fill = 0) %>%
  arrange(cohort, visit)

cat("\n==============================\n")
cat("Delta HbA1c categories by cohort and visit (unique subjects)\n")
cat("==============================\n")
print(summ_bins)

