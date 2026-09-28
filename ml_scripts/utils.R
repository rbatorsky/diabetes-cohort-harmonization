#' Read data and merge diabetes tracker; optionally return v1/v2, change, or a1c_change outcomes
#'
#' Tracker format expected:
#'   cohort, visit, studyid, diabetes, diabetes_change_v1_v2, delta_a1c_v1_v2
#'
#' @param rds_path path to harmonized RDS
#' @param tracker_path path to tracker xlsx
#' @param visit "v1", "v2", "change", or "a1c_change"
#' @param label_cohort FALSE keeps 0/1, TRUE renames to "BPRHS"/"PROSPECT"
#' @param filter_cohort "none", 0, 1, "BPRHS", or "PROSPECT"
#' @return merged data.frame (inner join for change modes; modeling-ready for "a1c_change")
read_merge_tracker <- function(
    rds_path,
    tracker_path,
    visit,
    label_cohort  = FALSE,
    filter_cohort = "none"
) {
  
  stopifnot(length(visit) == 1)
  
  dat <- readRDS(rds_path)
  
  tracker <- openxlsx::read.xlsx(tracker_path) %>%
    dplyr::mutate(
      cohort  = as.integer(cohort),
      studyid = as.character(studyid),
      visit   = as.character(visit)
    )
  
  dat <- dat %>%
    dplyr::mutate(
      studyid = as.character(studyid),
      cohort  = as.integer(as.character(cohort))
    )
  
  has_delta <- "delta_a1c_v1_v2" %in% names(tracker)
  
  # ---------------------------------------------------------
  # CASE 1: v1 / v2 (visit-level classification)
  # ---------------------------------------------------------
  if (visit %in% c("v1", "v2")) {
    
    dat <- dat %>% dplyr::mutate(visit = as.character(visit))
    
    tr <- tracker %>%
      dplyr::filter(visit == !!visit) %>%
      dplyr::select(studyid, cohort, visit, diabetes) %>%
      dplyr::distinct()
    
    dat <- dat %>%
      dplyr::inner_join(tr, by = c("studyid","cohort","visit")) %>%
      dplyr::mutate(
        cohort   = factor(cohort, levels = c(0, 1)),
        diabetes = factor(diabetes, levels = c(0, 1))
      ) %>%
      dplyr::filter(!is.na(diabetes))
    
    if (isTRUE(label_cohort)) {
      dat <- dat %>% dplyr::mutate(cohort = ifelse(cohort == 0, "BPRHS", "PROSPECT"))
    }
    if (!identical(filter_cohort, "none")) {
      dat <- dat %>% dplyr::filter(cohort == filter_cohort)
    }
    
    return(dat)
  }
  
  # ---------------------------------------------------------
  # CASE 2: diabetes change (subject-level)
  # ---------------------------------------------------------
  if (visit == "change") {
    
    tr <- tracker %>%
      dplyr::select(studyid, cohort, diabetes_v1, diabetes_v2, diabetes_change_v1_v2) %>%
      dplyr::distinct()
    
    dat <- dat %>%
      dplyr::inner_join(tr, by = c("studyid","cohort")) %>%
      dplyr::mutate(
        cohort = factor(cohort, levels = c(0, 1)),
        diabetes_v1 = factor(diabetes_v1, levels = c(0, 1, 2)),   # if using 3-class tracker
        diabetes_v2 = factor(diabetes_v2, levels = c(0, 1, 2)),
        diabetes_change_v1_v2 = factor(diabetes_change_v1_v2, levels = c(-1, 0, 1))
      ) %>%
      dplyr::filter(!is.na(diabetes_change_v1_v2), !is.na(diabetes_v1))
    
    if (isTRUE(label_cohort)) {
      dat <- dat %>% dplyr::mutate(cohort = ifelse(cohort == 0, "BPRHS", "PROSPECT"))
    }
    if (!identical(filter_cohort, "none")) {
      dat <- dat %>% dplyr::filter(cohort == filter_cohort)
    }
    
    return(dat)
  }
  
  # ---------------------------------------------------------
  # CASE 3: A1C CHANGE (for predictive modeling)
  # ---------------------------------------------------------
  if (visit == "a1c_change") {
    
    if (!has_delta) {
      stop("Tracker does not contain 'delta_a1c_v1_v2'. Rebuild tracker first.")
    }
    
    has_a1c_v1 <- "a1c_v1" %in% names(tracker)
    has_a1c_v2 <- "a1c_v2" %in% names(tracker)
    has_time   <- "followup_days_v1_v2" %in% names(tracker)
    
    tr_keep <- c("studyid", "cohort", "delta_a1c_v1_v2")
    if (has_a1c_v1) tr_keep <- c(tr_keep, "a1c_v1")
    if (has_a1c_v2) tr_keep <- c(tr_keep, "a1c_v2")
    if (has_time)   tr_keep <- c(tr_keep, "followup_days_v1_v2")
    
    tr <- tracker %>%
      dplyr::select(dplyr::all_of(tr_keep)) %>%
      dplyr::distinct()
    
    dat <- dat %>%
      dplyr::inner_join(tr, by = c("studyid", "cohort")) %>%
      dplyr::filter(!is.na(delta_a1c_v1_v2)) %>%
      dplyr::mutate(cohort = factor(cohort, levels = c(0, 1)))
    
    # Remove leakage / non-model columns (do NOT drop a1c_v1/a1c_v2)
    var_to_rm <- c(
      "diabetes",
      "diabetes_change_v1_v2",
      "diabetes_v1",
      "diabetes_v2"
    )
    dat <- dat %>% dplyr::select(-dplyr::any_of(var_to_rm))
    
    if (isTRUE(label_cohort)) {
      dat <- dat %>% dplyr::mutate(cohort = ifelse(cohort == 0, "BPRHS", "PROSPECT"))
    }
    if (!identical(filter_cohort, "none")) {
      dat <- dat %>% dplyr::filter(cohort == filter_cohort)
    }
    
    return(dat)
  }
  
  stop("visit must be 'v1', 'v2', 'change', or 'a1c_change'")
}
# residualize_by_cohort <- function(df, cohort_var = "cohort",
#                                   outcome = "diabetes",
#                                   weight_col = "weight") {
#   stopifnot(cohort_var %in% names(df))
#   fct_cohort <- as.factor(df[[cohort_var]])
#   
#   # exclude id columns too
#   id_cols <- intersect(c("row_id", "studyid"), names(df))
#   
#   num_cols <- names(df)[vapply(df, is.numeric, logical(1))]
#   num_cols <- setdiff(num_cols, c(cohort_var, outcome, weight_col, id_cols))
#   if (length(num_cols) == 0) return(df)
#   
#   for (col in num_cols) {
#     fit <- lm(df[[col]] ~ fct_cohort, na.action = na.exclude)
#     df[[col]] <- naresid(na.exclude(df[[col]] ~ fct_cohort), resid(fit))
#   }
#   df
# }

residualize_by_cohort <- function(df,
                                  cohort_var = "cohort",
                                  outcome    = "diabetes",
                                  weight_col = "weight",
                                  ref_means  = NULL) {
  stopifnot(cohort_var %in% names(df))
  
  # numeric predictors to residualize
  id_cols  <- intersect(c("row_id", "studyid"), names(df))
  num_cols <- names(df)[vapply(df, is.numeric, logical(1))]
  num_cols <- setdiff(num_cols, c(cohort_var, outcome, weight_col, id_cols))
  
  if (length(num_cols) == 0) {
    return(list(data = df, ref_means = ref_means, num_cols = num_cols))
  }
  
  # either fit means on df (train) or reuse ones from TRAIN
  if (is.null(ref_means)) {
    ref_means <- df %>%
      group_by(.data[[cohort_var]]) %>%
      summarise(across(all_of(num_cols), ~ mean(.x, na.rm = TRUE)),
                .groups = "drop")
  }
  
  # join means and subtract (residuals = x - cohort_mean)
  df_resid <- df %>%
    left_join(ref_means, by = cohort_var,
              suffix = c("", "_mean")) %>%
    mutate(across(all_of(num_cols),
                  ~ .x - get(paste0(cur_column(), "_mean")))) %>%
    select(-ends_with("_mean"))
  
  list(data = df_resid, ref_means = ref_means, num_cols = num_cols)
}

quiet_library <- function(pkg) {
  suppressPackageStartupMessages(
    suppressWarnings(
      library(pkg, character.only = TRUE, quietly = TRUE, warn.conflicts = FALSE)
    )
  )
}