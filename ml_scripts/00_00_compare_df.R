#######
## Compare different versions of the dataframe using development
#######

suppressPackageStartupMessages({
  library(dplyr)
  library(tidyr)
  library(readr)
  library(purrr)
  library(tibble)
  library(rlang)
  library(openxlsx)
})

# ---- Inputs ----
data_file_old <- "../../data/hmz_data/df_hmz_bprhs_prospect_2025_old.csv"
data_file     <- "../../data/hmz_data/df_hmz_bprhs_prospect_2025.csv"

data_old_raw <- read_csv(data_file_old, show_col_types = FALSE, progress = FALSE)
data_raw     <- read_csv(data_file,     show_col_types = FALSE, progress = FALSE)

# ---- Parameters ----
keys <- c("studyid","visit")
numeric_tolerance <- 1e-8

# ---- 0) Harmonize key types early (so joins/duplicates are consistent) ----
data_old <- data_old_raw %>%
  mutate(
    studyid = suppressWarnings(as.numeric(studyid)),
    visit   = as.character(visit) |> trimws()
  )

data <- data_raw %>%
  mutate(
    studyid = suppressWarnings(as.numeric(studyid)),
    visit   = as.character(visit) |> trimws()
  )

if (any(is.na(data_old$studyid)) || any(is.na(data$studyid))) {
  warning("Coercing studyid to numeric introduced NAs; check for non-numeric IDs.")
}

# ---- 1) Column-level differences ----
cols_old <- names(data_old)
cols_new <- names(data)

cols_only_in_old <- setdiff(cols_old, cols_new)
cols_only_in_new <- setdiff(cols_new, cols_old)
cols_in_both     <- intersect(cols_old, cols_new)

cat("# Columns only in OLD:\n"); print(cols_only_in_old)
cat("# Columns only in NEW:\n"); print(cols_only_in_new)
#cat("# Columns in BOTH (shared):\n"); print(cols_in_both)

# The set of non-key shared columns to compare
non_key_shared <- setdiff(cols_in_both, keys)

# ---- 2) Row-level diagnostics: duplicates and key presence ----

# (a) Duplicates by key in raw inputs (before distinct())
dup_old <- data_old_raw %>%
  count(across(all_of(keys)), name = "n") %>%
  filter(n > 1)
dup_new <- data_raw %>%
  count(across(all_of(keys)), name = "n") %>%
  filter(n > 1)

cat("\n# Duplicate keys in OLD (raw):\n"); print(dup_old, n = 20)
cat("\n# Duplicate keys in NEW (raw):\n"); print(dup_new, n = 20)

# (b) Key presence differences (after harmonization)
keys_old <- data_old %>% distinct(across(all_of(keys)))
keys_new <- data     %>% distinct(across(all_of(keys)))

keys_only_in_old <- dplyr::anti_join(keys_old, keys_new, by = keys)
keys_only_in_new <- dplyr::anti_join(keys_new, keys_old, by = keys)
keys_in_both     <- dplyr::inner_join(keys_old, keys_new, by = keys)

cat("\n# Keys only in OLD:\n"); print(keys_only_in_old, n = 50)
cat("\n# Keys only in NEW:\n"); print(keys_only_in_new, n = 50)
#cat("\n# Keys present in BOTH:\n"); print(keys_in_both, n = 50)

# ---- 3) Build pairwise alignment and compute value diffs ----

# Align on keys and rename columns with _old/_new for comparison
old_aligned <- data_old %>%
  select(all_of(c(keys, non_key_shared))) %>%
  distinct() %>%
  rename_with(~ paste0(.x, "_old"), non_key_shared)

new_aligned <- data %>%
  select(all_of(c(keys, non_key_shared))) %>%
  distinct() %>%
  rename_with(~ paste0(.x, "_new"), non_key_shared)

joined <- inner_join(old_aligned, new_aligned, by = keys)

# Comparator with numeric tolerance (only applied if both vectors are numeric)
compare_one_col <- function(jd, colname) {
  lhs <- jd[[paste0(colname, "_old")]]
  rhs <- jd[[paste0(colname, "_new")]]
  
  both_na <- is.na(lhs) & is.na(rhs)
  one_na  <- xor(is.na(lhs), is.na(rhs))
  
  both_num <- is.numeric(lhs) && is.numeric(rhs)
  near_eq  <- if (both_num) { (!one_na) & (abs(lhs - rhs) <= numeric_tolerance) } else { rep(FALSE, length(lhs)) }
  
  exact_eq <- (!one_na) & (as.character(lhs) == as.character(rhs))
  is_diff  <- !(both_na | near_eq | exact_eq)
  
  tibble(
    studyid   = jd[["studyid"]],
    visit     = jd[["visit"]],
    column    = colname,
    value_old = ifelse(is.na(lhs), NA_character_, as.character(lhs)),
    value_new = ifelse(is.na(rhs), NA_character_, as.character(rhs))
  ) %>% filter(is_diff)
}

value_diffs <- purrr::map_dfr(non_key_shared, ~ compare_one_col(joined, .x))
cat("\n# Value-level diffs (first 50 rows):\n"); print(value_diffs, n = 50)

# ---- 4) Whole-row change status among shared keys ----
changed_keys <- value_diffs %>%
  distinct(across(all_of(keys)))

unchanged_keys <- dplyr::anti_join(keys_in_both, changed_keys, by = keys)

cat("\n# Keys with ANY column changes (tolerance-aware):\n"); print(changed_keys, n = 50)

# ---- 5) Optional summaries ----
row_summary <- tibble::tibble(
  total_rows_old            = nrow(data_old),
  total_rows_new            = nrow(data),
  distinct_keys_old         = nrow(keys_old),
  distinct_keys_new         = nrow(keys_new),
  keys_only_in_old          = nrow(keys_only_in_old),
  keys_only_in_new          = nrow(keys_only_in_new),
  keys_in_both              = nrow(keys_in_both),
  keys_changed_in_both      = nrow(changed_keys),
  keys_unchanged_in_both    = nrow(unchanged_keys)
)

cat("\n# Row-level summary:\n"); print(row_summary)

per_row_first_diffs <- value_diffs %>%
  group_by(across(all_of(keys))) %>%
  slice_head(n = 5) %>%
  ungroup()

cat("\n# Up to first 5 diffs per changed key:\n"); print(per_row_first_diffs, n = 50)

