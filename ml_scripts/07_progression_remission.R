LIB="/cluster/tufts/patralab/rbator01/R_libs/4.4.0/"
.libPaths(LIB)

source("utils.R")

suppressPackageStartupMessages({
  library(openxlsx)
  library(tidymodels)
  library(tidyverse)
  library(workflows)
  library(tune)
  library(compositions)
  library(caret)
  library(VIM)
  library(visdat)
  library(recipes)
  library(themis)
  library(forcats)
  library(tidytext)
  library(dplyr)
  library(ggplot2)
  library(scales)
  library(nnet)   # multinom
})

RDS1 <- "../../analysis/harmonize_2cohort_healthsdohffq_v1_rmmissing_50col_10row.rds"
TRK  <- "../../data/hmz_data/diabetes_tracker_2class_24feb26.xlsx"

# ============================================================
# 1) Baseline diabetes by cohort (age-adjusted)
# ============================================================

data_v1 <- read_merge_tracker(
  rds_path      = RDS1,
  tracker_path  = TRK,
  visit         = "v1",
  label_cohort  = TRUE,
  filter_cohort = "none"
)

df_v1 <- data_v1 %>%
  filter(!is.na(diabetes), !is.na(hmz_sdoh_age), !is.na(cohort)) %>%
  mutate(
    cohort   = factor(cohort, levels = c("BPRHS", "PROSPECT")),
    diabetes = factor(diabetes, levels = c(0, 1), labels = c("No diabetes", "Diabetes"))
  )

count_df <- df_v1 %>% count(cohort, diabetes, name = "n")
totals   <- df_v1 %>% count(cohort, name = "N")

m <- glm(diabetes ~ cohort + hmz_sdoh_age, family = binomial, data = df_v1)

newdat <- expand.grid(
  cohort = levels(df_v1$cohort),
  hmz_sdoh_age = mean(df_v1$hmz_sdoh_age, na.rm = TRUE)
)
newdat$adj_prob_diabetes <- predict(m, newdata = newdat, type = "response")

label_df <- totals %>%
  left_join(newdat, by = "cohort") %>%
  mutate(label = paste0("N=", N, "\nAdj diabetes: ", sprintf("%.1f%%", 100 * adj_prob_diabetes)))

ggplot(count_df, aes(x = cohort, y = n, fill = diabetes)) +
  geom_col(width = 0.65) +
  geom_text(
    data = label_df,
    aes(x = cohort, y = N, label = label),
    vjust = -0.4,
    size = 5.5,
    inherit.aes = FALSE
  ) +
  scale_fill_manual(values = c("No diabetes" = "grey80", "Diabetes" = "grey30")) +
  labs(
    title = "Baseline (V1) Diabetes by Cohort",
    subtitle = paste0(
      "Stacked bars show raw counts; text shows age-adjusted diabetes probability at mean age (",
      round(mean(df_v1$hmz_sdoh_age, na.rm = TRUE), 1), "y)"
    ),
    x = "", y = "Number of participants", fill = ""
  ) +
  scale_y_continuous(expand = expansion(mult = c(0, 0.12))) +
  theme_minimal(base_size = 18) +
  theme(legend.position = "top", panel.grid.major.x = element_blank())

# ============================================================
# 2) Build years_between (V2-only) and make types match tracker
# ============================================================

hmz_file <- "../../data/hmz_data/df_hmz_bprhs_prospect_2025.csv"

hmz_data <- read.csv(hmz_file) %>%
  select(studyid, cohort, visit, hmz_days_since_visit_1) %>%
  mutate(
    studyid = as.character(studyid),
    cohort  = as.character(cohort),
    visit   = as.character(visit)
  )

visit_dates <- hmz_data %>%
  filter(visit == "v2") %>%
  mutate(
    years_between = hmz_days_since_visit_1 / 365,
    # make cohort labels consistent with label_cohort=TRUE outputs
    cohort = case_when(
      cohort %in% c("BPRHS","PROSPECT") ~ cohort,
      cohort %in% c("0","1")           ~ if_else(cohort == "0", "BPRHS", "PROSPECT"),
      TRUE                             ~ cohort
    )
  ) %>%
  select(studyid, cohort, years_between)

# Optional QC
# visit_dates %>% filter(years_between < 0)
# visit_dates %>% filter(years_between > 4)

ggplot(visit_dates, aes(x = years_between, fill = cohort)) +
  geom_histogram(position = "identity", alpha = 0.45, binwidth = .2) +
  scale_fill_manual(values = c("BPRHS" = "#1f77b4", "PROSPECT" = "#ff7f0e")) +
  labs(
    title = "Years Between V1 and V2 by Cohort",
    x = "Years between visits", y = "Count", fill = "Cohort"
  ) +
  theme_minimal(base_size = 12)

# ============================================================
# 3) Diabetes change model: multinomial (remission / no change / progression)
# ============================================================

data_chg <- read_merge_tracker(
  rds_path      = RDS1,
  tracker_path  = TRK,
  visit         = "change",
  label_cohort  = TRUE,
  filter_cohort = "none"
)

df_chg <- data_chg %>%
  filter(!is.na(diabetes_change_v1_v2), !is.na(hmz_sdoh_age)) %>%
  inner_join(visit_dates, by = c("studyid", "cohort")) %>%
  mutate(
    change = factor(diabetes_change_v1_v2, levels = c(-1, 0, 1),
                    labels = c("Remission", "No change", "Progression")),
    cohort = factor(cohort, levels = c("BPRHS", "PROSPECT"))
  )

df_chg$change <- relevel(df_chg$change, ref = "No change")

model_chg <- multinom(change ~ cohort + hmz_sdoh_age + years_between, data = df_chg)
summary(model_chg)

z_vals <- summary(model_chg)$coefficients / summary(model_chg)$standard.errors
p_vals <- 2 * (1 - pnorm(abs(z_vals)))
p_vals

# ============================================================
# 4) Analogous A1c change analysis (continuous delta HbA1c)
# ============================================================

data_a1c <- read_merge_tracker(
  rds_path      = RDS1,
  tracker_path  = TRK,
  visit         = "a1c_change",
  label_cohort  = TRUE,
  filter_cohort = "none"
)

df_a1c <- data_a1c %>%
  filter(!is.na(delta_a1c_v1_v2), !is.na(hmz_sdoh_age)) %>%
  inner_join(visit_dates, by = c("studyid", "cohort")) %>%
  mutate(cohort = factor(cohort, levels = c("BPRHS", "PROSPECT")))

# Continuous model (recommended primary)
m_a1c <- lm(delta_a1c_v1_v2 ~ cohort + hmz_sdoh_age + years_between, data = df_a1c)
summary(m_a1c)

# Optional: binned secondary analysis (±0.5)
df_a1c_bin <- df_a1c %>%
  mutate(delta_cat = case_when(
    delta_a1c_v1_v2 >  0.5 ~ "Worsening",
    delta_a1c_v1_v2 < -0.5 ~ "Improvement",
    TRUE                   ~ "Stable"
  ) %>% factor(levels = c("Stable","Improvement","Worsening")))

df_a1c_bin$delta_cat <- relevel(df_a1c_bin$delta_cat, ref = "Stable")

model_a1c_cat <- multinom(delta_cat ~ cohort + hmz_sdoh_age + years_between, data = df_a1c_bin)
summary(model_a1c_cat)

z_vals_a1c <- summary(model_a1c_cat)$coefficients / summary(model_a1c_cat)$standard.errors
p_vals_a1c <- 2 * (1 - pnorm(abs(z_vals_a1c)))
p_vals_a1c

# Visualizations ------

PLOT_DIR    <- "../../analysis/plots"
date_tag <- "23feb26"

# ---- load tracker (long, visit-level) ----
tracker_long <- openxlsx::read.xlsx(TRK) %>%
  dplyr::mutate(
    cohort  = as.integer(cohort),
    studyid = as.character(studyid),
    visit   = as.character(visit)
  ) %>%
  dplyr::mutate(
    cohort = factor(cohort, levels = c(0, 1), labels = c("BPRHS", "PROSPECT"))
  )

# sanity
print(table(tracker_long$cohort, tracker_long$visit, useNA = "ifany"))

# ============================================================
# PLOT A: Diabetes status at V1 + change (V1->V2) by cohort
# (this is the "progression/remission" plot you had before)
# ============================================================

# subject-level table for change (unique per studyid/cohort)
tracker_change <- tracker_long %>%
  dplyr::select(studyid, cohort, diabetes_change_v1_v2) %>%
  dplyr::distinct()

# V1 diabetes status counts
v1_summary <- tracker_long %>%
  dplyr::filter(visit == "v1", !is.na(diabetes)) %>%
  dplyr::mutate(
    visit = "V1",
    diabetes = factor(diabetes, levels = c(0, 1), labels = c("No Diabetes", "Diabetes"))
  ) %>%
  dplyr::count(cohort, visit, diabetes, name = "n")

# Change summary (V2 - V1)
change_summary <- tracker_change %>%
  dplyr::filter(!is.na(diabetes_change_v1_v2)) %>%
  dplyr::mutate(
    visit = "Change V1→V2",
    diabetes = dplyr::case_when(
      diabetes_change_v1_v2 == -1 ~ "Remission",
      diabetes_change_v1_v2 ==  0 ~ "No Change",
      diabetes_change_v1_v2 ==  1 ~ "Progression",
      TRUE ~ NA_character_
    )
  ) %>%
  dplyr::count(cohort, visit, diabetes, name = "n")

plot_df_dm <- dplyr::bind_rows(v1_summary, change_summary) %>%
  dplyr::mutate(
    visit = factor(visit, levels = c("V1", "Change V1→V2")),
    diabetes = factor(
      diabetes,
      levels = c("No Diabetes", "Diabetes", "Remission", "No Change", "Progression")
    )
  )

fill_colors_dm <- c(
  "No Diabetes" = "#B2DF8A",
  "Diabetes"    = "#7BAFD4",
  "Remission"   = "#E6AA68",
  "No Change"   = "#CAB2D6",
  "Progression" = "#D95F02"
)

p_dm <- ggplot2::ggplot(plot_df_dm, ggplot2::aes(x = visit, y = n, fill = diabetes)) +
  ggplot2::geom_col(position = "stack") +
  ggplot2::scale_fill_manual(values = fill_colors_dm, drop = FALSE) +
  ggplot2::labs(
    title = "Diabetes Status (2-class) and Change (V1→V2)",
    x = NULL,
    y = "Number of participants",
    fill = NULL
  ) +
  ggplot2::facet_wrap(~ cohort) +
  ggplot2::theme_minimal(base_size = 12) +
  ggplot2::theme(
    legend.position = "top",
    panel.grid.major.x = ggplot2::element_blank()
  )

print(p_dm)

ggplot2::ggsave(
  p_dm,
  filename = file.path(PLOT_DIR, paste0("diabetes_v1_and_change_by_cohort_", date_tag, ".pdf")),
  height = 4,
  width  = 5
)

# ============================================================
# PLOT B: Analogous A1c-change visualization by cohort
# - (1) distribution (violin/box + points) of delta_a1c_v1_v2
# - (2) stacked bar of categories (Improvement/Stable/Worsening)
# ============================================================

if (!("delta_a1c_v1_v2" %in% names(tracker_long))) {
  warning("Tracker does not have delta_a1c_v1_v2. Use the 24feb26 tracker (or newer) that includes A1c delta.")
} else {
  
  # subject-level delta (unique per studyid/cohort)
  tracker_a1c <- tracker_long %>%
    dplyr::select(studyid, cohort, delta_a1c_v1_v2) %>%
    dplyr::distinct() %>%
    dplyr::filter(!is.na(delta_a1c_v1_v2))
  
  # --- (1) Distribution plot: cohort differences in delta HbA1c ---
  p_a1c_dist <- ggplot2::ggplot(tracker_a1c, ggplot2::aes(x = cohort, y = delta_a1c_v1_v2)) +
    ggplot2::geom_violin(trim = TRUE) +
    ggplot2::geom_boxplot(width = 0.2, outlier.shape = NA) +
    ggplot2::geom_jitter(width = 0.12, alpha = 0.25, size = 1) +
    ggplot2::geom_hline(yintercept = 0, linetype = "dashed", linewidth = 0.6) +
    ggplot2::labs(
      title = expression(Delta * "HbA1c (V2 - V1) by Cohort"),
      x = NULL,
      y = expression(Delta * "HbA1c")
    ) +
    ggplot2::theme_minimal(base_size = 12) +
    ggplot2::theme(panel.grid.major.x = ggplot2::element_blank())
  
  print(p_a1c_dist)
  
  ggplot2::ggsave(
    p_a1c_dist,
    filename = file.path(PLOT_DIR, paste0("delta_a1c_distribution_by_cohort_", date_tag, ".pdf")),
    height = 4,
    width  = 5
  )
  
  # --- (2) Categorical stacked bar (like progression/remission) ---
  a1c_cat <- tracker_a1c %>%
    dplyr::mutate(
      visit = "ΔHbA1c V1→V2",
      delta_cat = dplyr::case_when(
        delta_a1c_v1_v2 >  0.5 ~ "Worsening (> +0.5)",
        delta_a1c_v1_v2 < -0.5 ~ "Improvement (< -0.5)",
        TRUE                   ~ "Stable (±0.5)"
      ),
      delta_cat = factor(delta_cat, levels = c("Improvement (< -0.5)", "Stable (±0.5)", "Worsening (> +0.5)"))
    ) %>%
    dplyr::count(cohort, visit, delta_cat, name = "n")
  
  fill_colors_a1c <- c(
    "Improvement (< -0.5)" = "#66C2A5",
    "Stable (±0.5)"        = "#BDBDBD",
    "Worsening (> +0.5)"   = "#FC8D62"
  )
  
  p_a1c_cat <- ggplot2::ggplot(a1c_cat, ggplot2::aes(x = visit, y = n, fill = delta_cat)) +
    ggplot2::geom_col(position = "stack") +
    ggplot2::scale_fill_manual(values = fill_colors_a1c, drop = FALSE) +
    ggplot2::labs(
      title = expression(Delta * "HbA1c categories (V1→V2)"),
      x = NULL,
      y = "Number of participants",
      fill = NULL
    ) +
    ggplot2::facet_wrap(~ cohort) +
    ggplot2::theme_minimal(base_size = 12) +
    ggplot2::theme(
      legend.position = "top",
      panel.grid.major.x = ggplot2::element_blank()
    )
  
  print(p_a1c_cat)
  
  ggplot2::ggsave(
    p_a1c_cat,
    filename = file.path(PLOT_DIR, paste0("delta_a1c_categories_by_cohort_", date_tag, ".pdf")),
    height = 4,
    width  = 5
  )
  
  # Optional quick cohort test (kept out of the plots)
  # t.test(delta_a1c_v1_v2 ~ cohort, data = tracker_a1c)
}






