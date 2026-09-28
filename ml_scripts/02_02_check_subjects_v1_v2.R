#!/usr/bin/env Rscript
# ------------------------------------------------------------
# Sanity check V1 vs V2 subject sets (new 2-class tracker)
# - counts subjects with non-missing diabetes at v1 and v2
# - overlap (both), v1-only, v2-only
# - per-cohort breakdowns
# - class balance at each visit
# - missingness patterns (v1 present but v2 missing, etc.)
# ------------------------------------------------------------

suppressPackageStartupMessages({
  library(openxlsx)
  library(dplyr)
  library(tidyr)
})

# ---------------- Paths ----------------
RDS_V1 <- "../../analysis/harmonize_2cohort_healthsdohffq_v1_rmmissing_50col_10row.rds"
RDS_V2 <- "../../analysis/harmonize_2cohort_healthsdohffq_v2_rmmissing_50col_10row.rds"
TRK    <- "../../data/hmz_data/diabetes_tracker_2class_23feb26.xlsx"

# ---------------- Load ----------------
dat_v1 <- readRDS(RDS_V1) %>%
  mutate(
    studyid = as.character(studyid),
    cohort  = as.integer(as.character(cohort))
  )

dat_v2 <- readRDS(RDS_V2) %>%
  mutate(
    studyid = as.character(studyid),
    cohort  = as.integer(as.character(cohort))
  )

tracker <- read.xlsx(TRK) %>%
  mutate(
    studyid = as.character(studyid),
    cohort  = as.integer(cohort),
    visit   = as.character(visit)
  )

# ---------------- Tracker: subject-level wide ----------------
trk_wide <- tracker %>%
  filter(visit %in% c("v1", "v2")) %>%
  select(studyid, cohort, visit, diabetes) %>%
  distinct() %>%
  pivot_wider(
    id_cols = c(studyid, cohort),
    names_from = visit,
    values_from = diabetes,
    names_prefix = "diabetes_"
  ) %>%
  left_join(
    tracker %>%
      select(studyid, cohort, diabetes_change_v1_v2) %>%
      distinct(),
    by = c("studyid", "cohort")
  ) %>%
  mutate(
    has_v1 = !is.na(diabetes_v1),
    has_v2 = !is.na(diabetes_v2),
    has_change = !is.na(diabetes_change_v1_v2),
    group = case_when(
      has_v1 & has_v2 ~ "both_v1_v2",
      has_v1 & !has_v2 ~ "v1_only",
      !has_v1 & has_v2 ~ "v2_only",
      TRUE ~ "neither"
    )
  )

# ---------------- RDS coverage (who is even in each RDS?) ----------------
rds_v1_ids <- dat_v1 %>% distinct(studyid, cohort) %>% mutate(in_rds_v1 = TRUE)
rds_v2_ids <- dat_v2 %>% distinct(studyid, cohort) %>% mutate(in_rds_v2 = TRUE)

coverage <- trk_wide %>%
  select(studyid, cohort, diabetes_v1, diabetes_v2, diabetes_change_v1_v2, has_v1, has_v2, has_change, group) %>%
  left_join(rds_v1_ids, by = c("studyid", "cohort")) %>%
  left_join(rds_v2_ids, by = c("studyid", "cohort")) %>%
  mutate(
    in_rds_v1 = if_else(is.na(in_rds_v1), FALSE, in_rds_v1),
    in_rds_v2 = if_else(is.na(in_rds_v2), FALSE, in_rds_v2)
  )

# ---------------- Pretty cohort labels for printing ----------------
cohort_lab <- function(x) factor(x, levels = c(0, 1), labels = c("BPRHS", "PROSPECT"))
coverage <- coverage %>% mutate(cohort_label = cohort_lab(cohort))

# ---------------- Print summary ----------------
cat("\n============================================================\n")
cat("V1 / V2 Subject Sanity Check (new 2-class tracker)\n")
cat("Tracker:", TRK, "\n")
cat("RDS_V1 :", RDS_V1, "\n")
cat("RDS_V2 :", RDS_V2, "\n")
cat("============================================================\n")

cat("\n--- Overall subject groups (non-missing diabetes) ---\n")
print(table(coverage$group, useNA = "ifany"))

cat("\n--- Subject groups by cohort ---\n")
print(table(coverage$cohort_label, coverage$group, useNA = "ifany"))

cat("\n--- Diabetes class balance at V1 (among has_v1) ---\n")
print(table(coverage$cohort_label[coverage$has_v1], coverage$diabetes_v1[coverage$has_v1], useNA = "ifany"))
cat("\nProportions within cohort:\n")
print(prop.table(table(coverage$cohort_label[coverage$has_v1], coverage$diabetes_v1[coverage$has_v1]), 1))

cat("\n--- Diabetes class balance at V2 (among has_v2) ---\n")
print(table(coverage$cohort_label[coverage$has_v2], coverage$diabetes_v2[coverage$has_v2], useNA = "ifany"))
cat("\nProportions within cohort:\n")
print(prop.table(table(coverage$cohort_label[coverage$has_v2], coverage$diabetes_v2[coverage$has_v2]), 1))

cat("\n--- Change (v2 - v1) distribution (among has_change) ---\n")
print(table(coverage$cohort_label[coverage$has_change], coverage$diabetes_change_v1_v2[coverage$has_change], useNA = "ifany"))

cat("\n--- RDS coverage: how many tracker subjects appear in each RDS? ---\n")
print(table(coverage$in_rds_v1, coverage$in_rds_v2))

cat("\n--- RDS coverage by cohort ---\n")
print(with(coverage, table(cohort_label, in_rds_v1, in_rds_v2)))

cat("\n--- Key sanity: subjects with tracker v2 but missing from V2 RDS (should be 0 ideally) ---\n")
bad_v2 <- coverage %>% filter(has_v2, !in_rds_v2)
cat("N =", nrow(bad_v2), "\n")
if (nrow(bad_v2) > 0) print(head(bad_v2, 20))

cat("\n--- Key sanity: subjects with tracker v1 but missing from V1 RDS (should be 0 ideally) ---\n")
bad_v1 <- coverage %>% filter(has_v1, !in_rds_v1)
cat("N =", nrow(bad_v1), "\n")
if (nrow(bad_v1) > 0) print(head(bad_v1, 20))

cat("\n--- Subjects with V2 label but no V1 label (v2_only) ---\n")
v2_only <- coverage %>% filter(group == "v2_only")
cat("N =", nrow(v2_only), "\n")
if (nrow(v2_only) > 0) {
  cat("By cohort:\n")
  print(table(v2_only$cohort_label))
  cat("First 20:\n")
  print(head(v2_only %>% select(studyid, cohort_label, diabetes_v2, diabetes_change_v1_v2, in_rds_v2), 20))
}

cat("\n--- Subjects with V1 label but no V2 label (v1_only) ---\n")
v1_only <- coverage %>% filter(group == "v1_only")
cat("N =", nrow(v1_only), "\n")
if (nrow(v1_only) > 0) {
  cat("By cohort:\n")
  print(table(v1_only$cohort_label))
  cat("First 20:\n")
  print(head(v1_only %>% select(studyid, cohort_label, diabetes_v1, diabetes_change_v1_v2, in_rds_v1), 20))
}

cat("\nDONE.\n")