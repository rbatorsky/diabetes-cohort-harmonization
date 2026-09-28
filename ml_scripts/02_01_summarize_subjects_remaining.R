#!/usr/bin/env Rscript

# ============================================================
# v1_progressive_filtering_by_cohort_MATCH_read_merge_tracker.R
# ============================================================

LIB <- "/cluster/tufts/patralab/rbator01/R_libs/4.4.0/"
.libPaths(LIB)

source("utils.R")

suppressPackageStartupMessages({
  library(openxlsx)
  library(dplyr)
  library(tidyr)
  library(ggplot2)
})

# ---------------- Paths ----------------
HMZ_CSV    <- "../../data/hmz_data/df_hmz_bprhs_prospect_2025.csv"
RDS1       <- "../../analysis/harmonize_2cohort_healthsdohffq_v1_rmmissing_50col_10row.rds"
TRK     <- "../../data/hmz_data/diabetes_tracker_2class_24feb26.xlsx"

PLOT_DIR <- "../../analysis/plots"
dir.create(PLOT_DIR, showWarnings = FALSE, recursive = TRUE)

DATE_TAG <- "23feb26"

OUT_PDF <- file.path(PLOT_DIR, paste0(
  "v1_progressive_filtering_by_cohort_MATCH_read_merge_tracker_", DATE_TAG, ".pdf"
))
OUT_CSV <- file.path(PLOT_DIR, paste0(
  "v1_progressive_filtering_counts_MATCH_read_merge_tracker_", DATE_TAG, ".csv"
))
OUT_SEG <- file.path(PLOT_DIR, paste0(
  "v1_progressive_filtering_segments_MATCH_read_merge_tracker_", DATE_TAG, ".csv"
))

# ---------------- Plot colors ----------------
step_colors <- c(
  "Invalid FFQ"                             = "#C0C0C0",
  "Missing V1 diabetes status"              = "#E6E6E6",
  "Too many missing features"               = "#D9D9D9",
  "Retained V1, Missing V2 diabetes status" = "#9EC3E6",
  "Retained V1+V2"                          = "#2C7FB8"
)

# ============================================================
# 0) File checks
# ============================================================

stopifnot(file.exists(HMZ_CSV))
stopifnot(file.exists(RDS1))
stopifnot(file.exists(TRK))

# ============================================================
# 1) Raw HMZ V1 and FFQ-valid V1 (cohort encoded 0/1 as character)
# ============================================================

hmz <- read.csv(HMZ_CSV) %>%
  select(studyid, cohort, visit, hmz_ffq_kcal, hmz_days_since_visit_1) %>%
  mutate(
    cohort = ifelse(cohort == "BPRHS", "0", "1"),
    cohort = as.character(cohort)
  )

ids_raw_v1 <- hmz %>%
  filter(visit == "v1") %>%
  distinct(studyid, cohort)

ids_ffq_v1 <- hmz %>%
  filter(visit == "v1", hmz_ffq_kcal > 600, hmz_ffq_kcal < 4800) %>%
  distinct(studyid, cohort)

# ============================================================
# 2) Final filtered V1 (RDS)
# ============================================================

feat_v1_ids <- readRDS(RDS1) %>%
  transmute(studyid, cohort = as.character(cohort)) %>%
  distinct()

ids_final_v1 <- feat_v1_ids

# ============================================================
# 3) Diabetes status known at V1 (from TRK_v1)
#    IMPORTANT: TRK_v1 is LONG (visit + diabetes), not wide.
# ============================================================

trk_v1_ids <- openxlsx::read.xlsx(TRK) %>%
  filter(visit == "v1") %>%
  transmute(
    studyid,
    cohort = as.character(cohort),
    diabetes
  ) %>%
  filter(!is.na(diabetes)) %>%
  distinct(studyid, cohort)

# Ensure nesting for progressive filtering:
# FFQ valid V1 -> Diabetes known V1
ids_diab_v1 <- ids_ffq_v1 %>%
  inner_join(trk_v1_ids, by = c("studyid", "cohort")) %>%
  distinct(studyid, cohort)

# Also ensure nesting for next step:
# Diabetes known V1 -> Final filtered V1 (RDS)
ids_final_v1_nested <- ids_final_v1 %>%
  inner_join(ids_diab_v1, by = c("studyid", "cohort")) %>%
  distinct(studyid, cohort)

# (Use nested version downstream for consistent segments)
ids_final_v1 <- ids_final_v1_nested

# ============================================================
# 4) FINAL STEP (matches your modeling script)
# ============================================================

data_change <- read_merge_tracker(
  rds_path      = RDS1,
  tracker_path  = TRK,
  visit         = "change",
  label_cohort  = TRUE,
  filter_cohort = "none"
)

# visit_dates from HMZ v2 (cohort is already 0/1 here)
visit_dates <- hmz %>%
  filter(visit == "v2") %>%
  mutate(years_between = hmz_days_since_visit_1 / 365) %>%
  select(studyid, cohort, years_between) %>%
  mutate(cohort = as.character(cohort)) 

# Harmonize cohort in data_change to 0/1 strings so the join matches
data_change2 <- data_change %>%
  mutate(
    cohort = case_when(
      cohort %in% c("BPRHS", "0", 0) ~ "0",
      cohort %in% c("PROSPECT", "1", 1) ~ "1",
      TRUE ~ as.character(cohort)
    ),
    cohort = as.character(cohort)
  )

head(data_change2$diabetes_change_v1_v2)
select_data <- data_change2 %>%
  filter(!is.na(diabetes_change_v1_v2), visit == "v1") %>%
  select(studyid, cohort, visit, diabetes_change_v1_v2) %>%
  mutate(studyid= as.numeric(studyid)) %>%
  inner_join(visit_dates, by = c("studyid", "cohort"))

ids_final_step <- select_data %>%
  transmute(studyid, cohort) %>%
  distinct()

# For strict nesting: Final step should be subset of Final filtered V1
ids_final_step <- ids_final_step %>%
  inner_join(ids_final_v1, by = c("studyid", "cohort")) %>%
  distinct(studyid, cohort)

# ============================================================
# 5) Count subjects per cohort at each step
# ============================================================

count_step <- function(ids_df, step_name) {
  ids_df %>%
    mutate(cohort = as.character(cohort)) %>%
    count(cohort, name = "n") %>%
    mutate(step = step_name)
}

counts <- bind_rows(
  count_step(ids_raw_v1,     "Raw V1"),
  count_step(ids_ffq_v1,     "FFQ valid V1"),
  count_step(ids_diab_v1,    "Diabetes known V1"),
  count_step(ids_final_v1,   "Final filtered V1"),
  count_step(ids_final_step, "Final step")
) %>%
  mutate(
    step = factor(step, levels = c(
      "Raw V1",
      "FFQ valid V1",
      "Diabetes known V1",
      "Final filtered V1",
      "Final step"
    ))
  ) %>%
  tidyr::complete(cohort, step, fill = list(n = 0)) %>%
  mutate(
    cohort_label = factor(cohort, levels = c("0","1"), labels = c("BPRHS","PROSPECT"))
  ) %>%
  arrange(cohort, step)

write.csv(counts, OUT_CSV, row.names = FALSE)

wide <- counts %>%
  select(cohort_label, step, n) %>%
  pivot_wider(names_from = step, values_from = n, values_fill = 0)

# ============================================================
# 6) Build stacked segments (now 5 steps => 4 drops + retained)
# ============================================================

seg <- wide %>%
  transmute(
    cohort_label,
    `Dropped: Raw → FFQ`                   = `Raw V1` - `FFQ valid V1`,
    `Dropped: FFQ → Diabetes known V1`     = `FFQ valid V1` - `Diabetes known V1`,
    `Dropped: Diabetes known V1 → Final V1`= `Diabetes known V1` - `Final filtered V1`,
    `Dropped: Final V1 → Final step`       = `Final filtered V1` - `Final step`,
    `Retained: Final step`                 = `Final step`
  ) %>%
  pivot_longer(-cohort_label, names_to = "segment", values_to = "n") %>%
  mutate(
    segment = recode(segment,
                     "Dropped: Raw → FFQ"                    = "Invalid FFQ",
                     "Dropped: FFQ → Diabetes known V1"      = "Missing V1 diabetes status",
                     "Dropped: Diabetes known V1 → Final V1" = "Too many missing features",
                     "Dropped: Final V1 → Final step"        = "Retained V1, Missing V2 diabetes status",
                     "Retained: Final step"                  = "Retained V1+V2"
    ),
    segment = factor(segment, levels = c(
      "Invalid FFQ",
      "Missing V1 diabetes status",
      "Too many missing features",
      "Retained V1, Missing V2 diabetes status",
      "Retained V1+V2"
    ))
  )

write.csv(seg, OUT_SEG, row.names = FALSE)

if (any(seg$n < 0, na.rm = TRUE)) {
  warning(
    "Negative segment(s) found. This means your steps are not nested.\n",
    "Check that each step is a subset of the previous and cohort coding matches."
  )
}

# ============================================================
# 7) Plot
# ============================================================

p <- ggplot(seg, aes(x = cohort_label, y = n, fill = segment)) +
  geom_col(width = 0.65) +
  scale_fill_manual(values = step_colors, drop = FALSE) +
  theme_minimal(base_size = 12) +
  labs(
    title = "Subject Retention for V1 and V2 modeling",
    x = "",
    y = "Number of participants",
    fill = NULL
  )

print(p)

ggsave(OUT_PDF, p, width = 5.2, height = 4.0)

message("Saved plot: ", OUT_PDF)
message("Counts CSV: ", OUT_CSV)
message("Segments CSV: ", OUT_SEG)

# Optional diagnostics
message("\nCounts table:")
print(counts)

message("\nFinal step cohort table (should match select_data$cohort table):")
print(table(select_data$cohort))
