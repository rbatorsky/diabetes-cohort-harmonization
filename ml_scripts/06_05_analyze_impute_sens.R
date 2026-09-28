#######
## Summarize the imputation sensitivity analysis (05_04_rf_impute_sens.R)
## V1 diabetes, pooled cohorts, random split, 10 seeds x {knn, median, knn_ind}
## Outputs (in ../../analysis/impute_sens/):
##   impute_sens_auc_by_seed.csv   test AUC and accuracy per method and seed
##   impute_sens_auc_summary.csv   mean (95% CI) per method + paired difference vs knn
##   impute_sens_boruta_overlap.csv Jaccard overlap of Boruta-confirmed features vs knn
##   impute_sens_top_features.csv  top 15 features by mean importance per method
#######

LIB <- "/cluster/tufts/patralab/rbator01/R_libs/4.4.0/"
.libPaths(LIB)
suppressPackageStartupMessages({
  library(tidyverse)
  library(yardstick)
})

OUTPATH <- "../../analysis/impute_sens/"
methods <- c("knn", "median", "knn_ind")
seeds   <- 1:10

save_string_for <- function(method, seed) {
  paste0("all_diabetes_v1_class2_filternone_seed", seed,
         "_tune_caseweights_boruta_xcohortval_0_resbatch_0",
         "_imp_", method, "_28sep26")
}

runs <- expand_grid(method = methods, seed = seeds) %>%
  mutate(save_string = map2_chr(method, seed, save_string_for))

# ---- test-set AUC and accuracy per run ----
read_run_metrics <- function(save_string) {
  pred_file <- file.path(OUTPATH, paste0("test_predictions_", save_string, ".rds"))
  if (!file.exists(pred_file)) return(tibble(auc = NA_real_, accuracy = NA_real_))
  preds <- readRDS(pred_file)
  tibble(
    auc      = roc_auc_vec(preds$diabetes, preds$.pred_1, event_level = "second"),
    accuracy = accuracy_vec(preds$diabetes, preds$.pred_class)
  )
}

auc_by_seed <- runs %>%
  mutate(metrics = map(save_string, read_run_metrics)) %>%
  unnest(metrics)

n_missing <- sum(is.na(auc_by_seed$auc))
if (n_missing > 0) message(n_missing, " of ", nrow(auc_by_seed), " runs have no predictions yet")

write_csv(auc_by_seed %>% select(-save_string),
          file.path(OUTPATH, "impute_sens_auc_by_seed.csv"))

# mean and t-based 95% CI across seeds
ci_summary <- function(x) {
  x <- x[!is.na(x)]
  n <- length(x)
  half <- if (n > 1) qt(0.975, n - 1) * sd(x) / sqrt(n) else NA_real_
  tibble(n = n, mean = mean(x), lower = mean(x) - half, upper = mean(x) + half)
}

auc_summary <- auc_by_seed %>%
  group_by(method) %>%
  summarise(auc = list(ci_summary(auc)), acc = list(ci_summary(accuracy)), .groups = "drop") %>%
  unnest_wider(auc, names_sep = "_") %>%
  unnest_wider(acc, names_sep = "_")

# paired difference vs knn: same seed => same train/test split
paired_diff <- auc_by_seed %>%
  select(method, seed, auc) %>%
  pivot_wider(names_from = method, values_from = auc) %>%
  pivot_longer(-c(seed, knn), names_to = "method", values_to = "auc_alt") %>%
  mutate(diff_vs_knn = auc_alt - knn) %>%
  group_by(method) %>%
  summarise(diff = list(ci_summary(diff_vs_knn)), .groups = "drop") %>%
  unnest_wider(diff, names_sep = "_")

auc_summary <- auc_summary %>% left_join(paired_diff, by = "method")
write_csv(auc_summary, file.path(OUTPATH, "impute_sens_auc_summary.csv"))
print(auc_summary, width = Inf)

# ---- Boruta-confirmed features: overlap with knn per seed ----
read_confirmed <- function(save_string) {
  f <- file.path(OUTPATH, paste0("boruta_stats_", save_string, ".csv"))
  if (!file.exists(f)) return(character(0))
  stats <- read_csv(f, show_col_types = FALSE)
  stats[[1]][stats$decision == "Confirmed"]
}

confirmed <- runs %>% mutate(features = map(save_string, read_confirmed))

jaccard <- function(a, b) if (length(union(a, b)) == 0) NA_real_ else length(intersect(a, b)) / length(union(a, b))

boruta_overlap <- confirmed %>%
  select(method, seed, features) %>%
  left_join(confirmed %>% filter(method == "knn") %>% select(seed, knn_features = features), by = "seed") %>%
  filter(method != "knn") %>%
  mutate(
    n_confirmed     = map_int(features, length),
    n_confirmed_knn = map_int(knn_features, length),
    jaccard_vs_knn  = map2_dbl(features, knn_features, jaccard),
    # indicator features are named na_ind_<var>; report how many were selected
    n_na_indicators = map_int(features, ~ sum(str_detect(.x, "^na_ind_")))
  ) %>%
  select(method, seed, n_confirmed, n_confirmed_knn, jaccard_vs_knn, n_na_indicators)

write_csv(boruta_overlap, file.path(OUTPATH, "impute_sens_boruta_overlap.csv"))
print(boruta_overlap %>% group_by(method) %>%
        summarise(across(c(n_confirmed, n_confirmed_knn, jaccard_vs_knn, n_na_indicators), mean)))

# ---- top features by mean importance across seeds ----
read_vi <- function(save_string) {
  f <- file.path(OUTPATH, paste0("log_", save_string, ".csv"))
  if (!file.exists(f)) return(tibble())
  read_csv(f, show_col_types = FALSE) %>% select(Variable, type, Importance)
}

top_features <- runs %>%
  mutate(vi = map(save_string, read_vi)) %>%
  select(method, seed, vi) %>%
  unnest(vi) %>%
  group_by(method, Variable, type) %>%
  summarise(mean_importance = sum(Importance) / length(seeds), n_seeds = n(), .groups = "drop") %>%
  group_by(method) %>%
  slice_max(mean_importance, n = 15, with_ties = FALSE) %>%
  mutate(rank = row_number()) %>%
  ungroup()

write_csv(top_features, file.path(OUTPATH, "impute_sens_top_features.csv"))
print(top_features %>% select(method, rank, Variable) %>%
        pivot_wider(names_from = method, values_from = Variable), n = 15)
