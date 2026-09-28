#!/usr/bin/env Rscript

# ============================================================
# cohort_longitudinal_summary_plots_and_stats.R
#
# One self-contained script that:
#  0) Builds follow-up time (years_between) from HMZ CSV (V2)
#  1) Baseline (V1) diabetes: crude + age-adjusted cohort differences
#     - exports CSV stats + OR + plots
#  2) Diabetes change (V1→V2): descriptive + adjusted cohort differences
#     - multinomial adjusted for baseline diabetes + age + follow-up time
#     - exports predicted-prob plot + prints model stats
#  3) HbA1c longitudinal:
#     - a1c_v2 ~ a1c_v1 + cohort + age + years_between
#     - delta_a1c ~ cohort + age + years_between (+ optional a1c_v1)
#     - exports plots + prints cohort-effect stats
#
# Uses your EXACT cohort palette:
#   BPRHS   = #7CAE00
#   PROSPECT= #00BFC4
# ============================================================

LIB <- "/cluster/tufts/patralab/rbator01/R_libs/4.4.0/"
.libPaths(LIB)

source("utils.R")

suppressPackageStartupMessages({
  library(openxlsx)
  library(dplyr)
  library(tidyr)
  library(ggplot2)
  library(scales)
  library(nnet)     # multinom
})

# ---------------- Paths ----------------
RDS1    <- "../../analysis/harmonize_2cohort_healthsdohffq_v1_rmmissing_50col_10row.rds"
TRK     <- "../../data/hmz_data/diabetes_tracker_2class_24feb26.xlsx"
HMZ_CSV <- "../../data/hmz_data/df_hmz_bprhs_prospect_2025.csv"

DATE_TAG <- "24feb26"
PLOT_DIR <- "../../analysis/plots_cohort_longitudinal"
dir.create(PLOT_DIR, showWarnings = FALSE, recursive = TRUE)

# ---------------- Cohort palette (EXACT) ----------------
COHORT_LEVELS <- c("BPRHS", "PROSPECT")
COHORT_COLORS <- c("BPRHS" = "#7CAE00", "PROSPECT" = "#00BFC4")

# ---------------- Plot helpers ----------------
save_pdf <- function(p, filename, w = 6.8, h = 4.2) {
  # cairo is nicer for text rendering on cluster; if unavailable, ggplot will fallback
  ggsave(
    filename = filename,
    plot     = p,
    width    = w,
    height   = h,
    units    = "in",
    dpi      = 300,
    device   = grDevices::cairo_pdf
  )
}

theme_set(
  theme_minimal(base_size = 13) +
    theme(
      legend.position = "top",
      panel.grid.major.x = element_blank()
    )
)

# ---------------- Small utilities ----------------
fix_cohort_label <- function(x) {
  x <- as.character(x)
  dplyr::case_when(
    x %in% c("BPRHS", "0")    ~ "BPRHS",
    x %in% c("PROSPECT", "1") ~ "PROSPECT",
    TRUE ~ x
  )
}

# lighten/darken without extra packages
lighten_color <- function(col, alpha = 0.55) {
  rgb_col <- grDevices::col2rgb(col) / 255
  new_col <- rgb_col + (1 - rgb_col) * alpha
  grDevices::rgb(new_col[1], new_col[2], new_col[3])
}
darken_color <- function(col, factor = 0.75) {
  rgb_col <- grDevices::col2rgb(col) / 255
  new_col <- rgb_col * factor
  grDevices::rgb(new_col[1], new_col[2], new_col[3])
}

extract_cohort_effect_lm <- function(model, cohort_term_prefix = "^cohort") {
  sm <- summary(model)$coefficients
  rn <- rownames(sm)
  term <- grep(cohort_term_prefix, rn, value = TRUE)
  if (length(term) != 1) stop("Could not uniquely identify cohort coefficient. Found: ", paste(term, collapse = ", "))
  
  est <- unname(coef(model)[term])
  se  <- sqrt(vcov(model)[term, term])
  tibble(
    term = term,
    estimate = est,
    se = se,
    lwr = est - 1.96 * se,
    upr = est + 1.96 * se,
    p = sm[term, "Pr(>|t|)"]
  )
}

extract_cohort_or_glm <- function(model, cohort_term_prefix = "^cohort") {
  sm <- summary(model)$coefficients
  rn <- rownames(sm)
  term <- grep(cohort_term_prefix, rn, value = TRUE)
  if (length(term) != 1) stop("Could not uniquely identify cohort coefficient. Found: ", paste(term, collapse = ", "))
  
  logOR <- unname(coef(model)[term])
  se    <- sqrt(vcov(model)[term, term])
  tibble(
    term = term,
    logOR = logOR,
    se = se,
    OR = exp(logOR),
    lwr = exp(logOR - 1.96 * se),
    upr = exp(logOR + 1.96 * se),
    p = sm[term, "Pr(>|z|)"]
  )
}

multinom_pvals <- function(m) {
  s <- summary(m)
  z <- s$coefficients / s$standard.errors
  p <- 2 * (1 - pnorm(abs(z)))
  list(z = z, p = p)
}

# ============================================================
# 0) Follow-up time (years_between) from HMZ CSV (V2)
# ============================================================
hmz_data <- read.csv(HMZ_CSV) %>%
  transmute(
    studyid = as.character(studyid),
    cohort  = fix_cohort_label(cohort),
    visit   = as.character(visit),
    hmz_days_since_visit_1 = hmz_days_since_visit_1
  )

visit_dates <- hmz_data %>%
  filter(visit == "v2") %>%
  mutate(years_between = hmz_days_since_visit_1 / 365) %>%
  select(studyid, cohort, years_between) %>%
  filter(is.finite(years_between), years_between > 0)

p_time <- ggplot(visit_dates, aes(x = years_between, fill = cohort)) +
  geom_histogram(position = "identity", alpha = 0.45, binwidth = 0.2, color = "white") +
  scale_fill_manual(values = COHORT_COLORS, breaks = COHORT_LEVELS) +
  labs(
    title = "Years Between V1 and V2 by Cohort",
    x = "Years between visits", y = "Count", fill = "Cohort"
  )
save_pdf(p_time, file.path(PLOT_DIR, paste0("years_between_by_cohort_", DATE_TAG, ".pdf")), w = 6.8, h = 4.2)

# ============================================================
# 1) Baseline (V1) diabetes: crude + age-adjusted
# ============================================================
data_v1 <- read_merge_tracker(
  rds_path      = RDS1,
  tracker_path  = TRK,
  visit         = "v1",
  label_cohort  = TRUE,
  filter_cohort = "none"
)


df_v1 <- data_v1 %>%
  filter(cohort %in% COHORT_LEVELS, !is.na(hmz_sdoh_age), !is.na(diabetes)) %>%
  mutate(
    cohort = factor(cohort, levels = COHORT_LEVELS),
    diabetes_bin = suppressWarnings(as.numeric(as.character(diabetes))),
    a1c_v1 = suppressWarnings(as.numeric(hmz_health_lab_a1c))  # <-- add this
  ) %>%
  filter(diabetes_bin %in% c(0, 1))

baseline_counts <- df_v1 %>%
  group_by(cohort) %>%
  summarise(
    N = n(),
    n_diabetes = sum(diabetes_bin == 1, na.rm = TRUE),
    prev = n_diabetes / N,
    mean_age = mean(hmz_sdoh_age, na.rm = TRUE),
    sd_age   = sd(hmz_sdoh_age, na.rm = TRUE),
    .groups = "drop"
  )

# --- Age-adjusted baseline HbA1c (V1) by cohort ---
df_v1_a1c <- df_v1 %>%
  filter(!is.na(a1c_v1), is.finite(a1c_v1)) %>%
  filter(a1c_v1 > 0, a1c_v1 < 20)

m_a1c_v1 <- lm(a1c_v1 ~ cohort + hmz_sdoh_age, data = df_v1_a1c)

ref_age_a1c <- mean(df_v1_a1c$hmz_sdoh_age, na.rm = TRUE)
newdat_a1c <- expand.grid(
  cohort = levels(df_v1_a1c$cohort),
  hmz_sdoh_age = ref_age_a1c
)

pred <- predict(m_a1c_v1, newdata = newdat_a1c, se.fit = TRUE)
newdat_a1c <- newdat_a1c %>%
  mutate(
    fit = pred$fit,
    se  = pred$se.fit,
    lwr = fit - 1.96 * se,
    upr = fit + 1.96 * se
  )

p_a1c_v1_adj <- ggplot(newdat_a1c, aes(x = cohort, y = fit, color = cohort)) +
  geom_point(size = 3) +
  geom_errorbar(aes(ymin = lwr, ymax = upr), width = 0.12, linewidth = 0.9) +
  geom_hline(yintercept = 6.5, linetype = "dashed", color = "grey30") +
  scale_color_manual(values = COHORT_COLORS, breaks = COHORT_LEVELS) +
  labs(
    title = "Baseline HbA1c by cohort (age-adjusted)",
    subtitle = paste0("Predicted at mean age = ", round(ref_age_a1c, 1), " years"),
    x = NULL, y = "Predicted HbA1c at V1 (%)", color = NULL
  )

save_pdf(
  p_a1c_v1_adj,
  file.path(PLOT_DIR, paste0("a1c_v1_age_adjusted_mean_", DATE_TAG, ".pdf")),
  w = 6.8, h = 4.2
)



# --- age-adjusted logistic model + OR ---
m_base <- glm(diabetes_bin ~ cohort + hmz_sdoh_age, family = binomial, data = df_v1)
or_df  <- extract_cohort_or_glm(m_base)

ref_age <- mean(df_v1$hmz_sdoh_age, na.rm = TRUE)
newdat_base <- expand.grid(
  cohort = levels(df_v1$cohort),
  hmz_sdoh_age = ref_age
)

pred_link <- predict(m_base, newdata = newdat_base, type = "link", se.fit = TRUE)
newdat_base <- newdat_base %>%
  mutate(
    fit_link = pred_link$fit,
    se_link  = pred_link$se.fit,
    lwr_link = fit_link - 1.96 * se_link,
    upr_link = fit_link + 1.96 * se_link,
    adj_prob = plogis(fit_link),
    lwr_prob = plogis(lwr_link),
    upr_prob = plogis(upr_link)
  )

baseline_stats <- baseline_counts %>%
  left_join(newdat_base %>% select(cohort, adj_prob, lwr_prob, upr_prob), by = "cohort") %>%
  mutate(
    prev_pct = 100 * prev,
    adj_pct  = 100 * adj_prob,
    adj_lwr  = 100 * lwr_prob,
    adj_upr  = 100 * upr_prob
  )

write.csv(baseline_stats, file.path(PLOT_DIR, paste0("baseline_diabetes_stats_", DATE_TAG, ".csv")), row.names = FALSE)
write.csv(or_df,          file.path(PLOT_DIR, paste0("baseline_diabetes_OR_", DATE_TAG, ".csv")), row.names = FALSE)

# --- BASELINE PLOT you like: cohort colors + shading, legend, diabetes on bottom ---
fill_map <- c(
  "BPRHS – Diabetes"       = darken_color(COHORT_COLORS["BPRHS"]),
  "BPRHS – No diabetes"    = lighten_color(COHORT_COLORS["BPRHS"]),
  "PROSPECT – Diabetes"    = darken_color(COHORT_COLORS["PROSPECT"]),
  "PROSPECT – No diabetes" = lighten_color(COHORT_COLORS["PROSPECT"])
)

plot_df_base <- df_v1 %>%
  mutate(
    diabetes_lab = factor(diabetes_bin,
                          levels = c(1, 0),   # diabetes first = bottom
                          labels = c("Diabetes", "No diabetes")),
    fill_id = paste(cohort, diabetes_lab, sep = " – ")
  ) %>%
  count(cohort, diabetes_lab, fill_id, name = "n")

p_baseline_shaded <- ggplot(plot_df_base, aes(x = cohort, y = n, fill = fill_id)) +
  geom_col(width = 0.65) +
  scale_fill_manual(values = fill_map, name = NULL) +
  labs(
    title = "Baseline Diabetes by Cohort",
    subtitle = "Cohort colors with shading by diabetes status",
    x = NULL, y = "Participants"
  ) +
  theme(legend.position = "right")

save_pdf(p_baseline_shaded, file.path(PLOT_DIR, paste0("baseline_diabetes_stacked_shaded_", DATE_TAG, ".pdf")), w = 6.8, h = 4.2)

# optional: crude prevalence bars
p_prev <- ggplot(baseline_counts, aes(x = cohort, y = prev, fill = cohort)) +
  geom_col(width = 0.65) +
  scale_fill_manual(values = COHORT_COLORS, breaks = COHORT_LEVELS) +
  scale_y_continuous(labels = percent_format(accuracy = 1),
                     expand = expansion(mult = c(0, 0.10))) +
  geom_text(
    aes(label = paste0("N=", N, "\n", sprintf("%.1f%%", 100 * prev))),
    vjust = -0.35, size = 4, show.legend = FALSE
  ) +
  labs(
    title = "Baseline diabetes prevalence by cohort (crude)",
    x = NULL, y = "Prevalence", fill = NULL
  )
save_pdf(p_prev, file.path(PLOT_DIR, paste0("baseline_diabetes_prevalence_crude_", DATE_TAG, ".pdf")), w = 6.8, h = 4.2)

# age-adjusted probability with CI
p_adj <- ggplot(newdat_base, aes(x = cohort, y = adj_prob, color = cohort)) +
  geom_point(size = 3) +
  geom_errorbar(aes(ymin = lwr_prob, ymax = upr_prob), width = 0.12, linewidth = 0.9) +
  scale_color_manual(values = COHORT_COLORS, breaks = COHORT_LEVELS) +
  scale_y_continuous(labels = percent_format(accuracy = 1)) +
  labs(
    title = "Baseline diabetes by cohort (age-adjusted)",
    subtitle = paste0("Predicted at mean age = ", round(ref_age, 1), " years"),
    x = NULL, y = "Age-adjusted probability", color = NULL
  )
save_pdf(p_adj, file.path(PLOT_DIR, paste0("baseline_diabetes_age_adjusted_prob_", DATE_TAG, ".pdf")), w = 6.8, h = 4.2)

# ============================================================
# 2) Diabetes change (V1→V2): descriptive + adjusted multinomial
# ============================================================
data_chg <- read_merge_tracker(
  rds_path      = RDS1,
  tracker_path  = TRK,
  visit         = "change",
  label_cohort  = TRUE,
  filter_cohort = "none"
)

df_chg <- data_chg %>%
  filter(
    cohort %in% COHORT_LEVELS,
    !is.na(diabetes_change_v1_v2),
    !is.na(hmz_sdoh_age),
    !is.na(diabetes_v1)
  ) %>%
  inner_join(visit_dates, by = c("studyid", "cohort")) %>%
  mutate(
    cohort = factor(cohort, levels = COHORT_LEVELS),
    diabetes_v1 = factor(as.character(diabetes_v1), levels = c("0", "1"),
                         labels = c("No diabetes", "Diabetes")),
    change = factor(diabetes_change_v1_v2, levels = c(-1, 0, 1),
                    labels = c("Remission", "No change", "Progression"))
  )

p_chg_stack <- df_chg %>%
  count(cohort, change) %>%
  group_by(cohort) %>%
  mutate(prop = n / sum(n)) %>%
  ggplot(aes(x = cohort, y = prop, fill = change)) +
  geom_col(width = 0.65) +
  scale_y_continuous(labels = percent_format()) +
  scale_fill_brewer(palette = "Set2") +
  labs(
    title = "Diabetes change category (V1→V2) by cohort (descriptive)",
    x = NULL, y = "Proportion", fill = NULL
  )
save_pdf(p_chg_stack, file.path(PLOT_DIR, paste0("diabetes_change_stacked_by_cohort_", DATE_TAG, ".pdf")), w = 6.8, h = 4.2)

df_chg$change <- relevel(df_chg$change, ref = "No change")
m_chg <- nnet::multinom(change ~ cohort + diabetes_v1 + hmz_sdoh_age + years_between,
                        data = df_chg, trace = FALSE)
chg_p <- multinom_pvals(m_chg)

pred_grid <- expand.grid(
  cohort = levels(df_chg$cohort),
  diabetes_v1 = levels(df_chg$diabetes_v1),
  hmz_sdoh_age = mean(df_chg$hmz_sdoh_age, na.rm = TRUE),
  years_between = median(df_chg$years_between, na.rm = TRUE)
)
pred_probs <- as.data.frame(predict(m_chg, newdata = pred_grid, type = "probs"))
pred_plot_df <- bind_cols(pred_grid, pred_probs) %>%
  pivot_longer(cols = c("Remission", "No change", "Progression"),
               names_to = "outcome", values_to = "prob")

p_chg_adj <- ggplot(pred_plot_df, aes(x = cohort, y = prob, fill = cohort)) +
  geom_col(width = 0.65) +
  facet_grid(diabetes_v1 ~ outcome) +
  scale_y_continuous(labels = percent_format(accuracy = 1), limits = c(0, 1)) +
  scale_fill_manual(values = COHORT_COLORS, breaks = COHORT_LEVELS) +
  labs(
    title = "Adjusted diabetes change probabilities by cohort",
    subtitle = "Adjusted for baseline diabetes, age, and follow-up time",
    x = NULL, y = "Predicted probability", fill = NULL
  )
save_pdf(p_chg_adj, file.path(PLOT_DIR, paste0("diabetes_change_adjusted_probs_by_cohort_", DATE_TAG, ".pdf")),
         w = 10.5, h = 5.2)

# ============================================================
# 3) HbA1c longitudinal cohort differences (adjusted)
# ============================================================
data_a1c <- read_merge_tracker(
  rds_path      = RDS1,
  tracker_path  = TRK,
  visit         = "a1c_change",
  label_cohort  = TRUE,
  filter_cohort = "none"
)

df_a1c <- data_a1c %>%
  filter(
    cohort %in% COHORT_LEVELS,
    !is.na(a1c_v1), !is.na(a1c_v2),
    !is.na(hmz_sdoh_age)
  ) %>%
  inner_join(visit_dates, by = c("studyid", "cohort")) %>%
  mutate(
    cohort = factor(cohort, levels = COHORT_LEVELS),
    delta_a1c = a1c_v2 - a1c_v1
  )

p_a_scatter <- ggplot(df_a1c, aes(x = a1c_v1, y = a1c_v2, color = cohort)) +
  geom_point(alpha = 0.25, size = 1) +
  geom_abline(slope = 1, intercept = 0, color = "grey40") +
  geom_smooth(method = "lm", se = FALSE, linewidth = 1) +
  scale_color_manual(values = COHORT_COLORS, breaks = COHORT_LEVELS) +
  facet_wrap(~ cohort) +
  labs(
    title = "HbA1c at V2 vs V1 by cohort",
    x = "HbA1c at V1",
    y = "HbA1c at V2",
    color = NULL
  ) +
  theme(legend.position = "none")
save_pdf(p_a_scatter, file.path(PLOT_DIR, paste0("a1c_v2_vs_a1c_v1_by_cohort_", DATE_TAG, ".pdf")), w = 7.8, h = 4.4)

m_a1c_v2 <- lm(a1c_v2 ~ a1c_v1 + cohort + hmz_sdoh_age + years_between, data = df_a1c)
a1c_v2_cohort_eff <- extract_cohort_effect_lm(m_a1c_v2)

grid_a <- expand.grid(
  cohort = levels(df_a1c$cohort),
  a1c_v1 = median(df_a1c$a1c_v1, na.rm = TRUE),
  hmz_sdoh_age = mean(df_a1c$hmz_sdoh_age, na.rm = TRUE),
  years_between = median(df_a1c$years_between, na.rm = TRUE)
)
grid_a$pred_a1c_v2 <- predict(m_a1c_v2, newdata = grid_a)

p_a_adj <- ggplot(grid_a, aes(x = cohort, y = pred_a1c_v2, fill = cohort)) +
  geom_col(width = 0.65) +
  scale_fill_manual(values = COHORT_COLORS, breaks = COHORT_LEVELS) +
  labs(
    title = "Adjusted follow-up HbA1c (V2) by cohort",
    subtitle = "Predicted at median baseline HbA1c and median follow-up time; adjusted for age",
    x = NULL, y = "Predicted HbA1c at V2", fill = NULL
  )
save_pdf(p_a_adj, file.path(PLOT_DIR, paste0("a1c_v2_adjusted_by_cohort_", DATE_TAG, ".pdf")), w = 6.8, h = 4.2)

p_delta <- ggplot(df_a1c, aes(x = cohort, y = delta_a1c, fill = cohort)) +
  geom_violin(trim = TRUE, alpha = 0.55, color = NA) +
  geom_boxplot(width = 0.18, outlier.shape = NA, alpha = 0.85) +
  geom_hline(yintercept = 0, linetype = "dashed", color = "grey30") +
  scale_fill_manual(values = COHORT_COLORS, breaks = COHORT_LEVELS) +
  labs(
    title = "ΔHbA1c (V2 − V1) by cohort (descriptive)",
    x = NULL, y = "ΔHbA1c", fill = NULL
  ) +
  theme(legend.position = "none")
save_pdf(p_delta, file.path(PLOT_DIR, paste0("delta_a1c_by_cohort_", DATE_TAG, ".pdf")), w = 6.8, h = 4.2)

m_delta1 <- lm(delta_a1c ~ cohort + hmz_sdoh_age + years_between, data = df_a1c)
m_delta2 <- lm(delta_a1c ~ a1c_v1 + cohort + hmz_sdoh_age + years_between, data = df_a1c)
delta_cohort_eff1 <- extract_cohort_effect_lm(m_delta1)
delta_cohort_eff2 <- extract_cohort_effect_lm(m_delta2)

write.csv(a1c_v2_cohort_eff, file.path(PLOT_DIR, paste0("a1c_v2_cohort_effect_", DATE_TAG, ".csv")), row.names = FALSE)
write.csv(delta_cohort_eff1, file.path(PLOT_DIR, paste0("delta_a1c_cohort_effect_adj_age_followup_", DATE_TAG, ".csv")), row.names = FALSE)
write.csv(delta_cohort_eff2, file.path(PLOT_DIR, paste0("delta_a1c_cohort_effect_adj_baseline_age_followup_", DATE_TAG, ".csv")), row.names = FALSE)

# ============================================================
# PRINT: stats you can paste into slides / story
# ============================================================
cat("\n======================= OUTPUTS =======================\n")
cat("Wrote plots + CSVs to:\n  ", normalizePath(PLOT_DIR), "\n\n")

cat("=== BASELINE (V1) diabetes: crude + age-adjusted ===\n")
print(baseline_stats)
cat("\nAge-adjusted cohort OR (PROSPECT vs BPRHS):\n")
print(or_df)

cat("\n=== DIABETES CHANGE (multinomial): adjusted for baseline status + age + follow-up ===\n")
cat("\nModel summary:\n")
print(summary(m_chg))
cat("\nApprox z-tests (rows = outcomes vs ref 'No change'):\n")
print(chg_p$z)
cat("\nApprox p-values:\n")
print(chg_p$p)

cat("\n=== A1c longitudinal (PRIMARY): a1c_v2 ~ a1c_v1 + cohort + age + follow-up ===\n")
print(summary(m_a1c_v2))
cat("\nCohort effect (PROSPECT vs BPRHS) on a1c_v2 (adjusted):\n")
print(a1c_v2_cohort_eff)

cat("\n=== A1c longitudinal (SECONDARY): delta_a1c cohort differences ===\n")
cat("\nDelta model (cohort + age + follow-up):\n")
print(summary(m_delta1))
cat("\nCohort effect on delta_a1c (adjusted age+follow-up):\n")
print(delta_cohort_eff1)

cat("\nDelta model (baseline a1c + cohort + age + follow-up):\n")
print(summary(m_delta2))
cat("\nCohort effect on delta_a1c (adjusted baseline+age+follow-up):\n")
print(delta_cohort_eff2)

cat("\nDONE.\n")