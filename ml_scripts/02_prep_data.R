LIB="/cluster/tufts/patralab/rbator01/R_libs/4.4.0/"
.libPaths(LIB)
library(openxlsx)
library(tidymodels)
library(tidyverse)
library(workflows)
library(tune)
library(compositions)
library(caret)
library(VIM)
library(visdat)
library(ggpubr)

filter=dplyr::filter
rename=dplyr::rename
select=dplyr::select
intersect=base::intersect
setwd("/cluster/tufts/patralab/rbator01/aiml_ordovas_project/")

# function -----

filter_by_missingness <- function(data, cohort_col_missing_threshold = 0.9, overall_col_missing_threshold = 0.5, row_missing_threshold = 0.1, cohort_visits) {
  
  # Convert cohort_visits to data frame if it's a list
  if (is.list(cohort_visits) && !is.data.frame(cohort_visits)) {
    cohort_visits <- bind_rows(
      lapply(names(cohort_visits), function(c) {
        tibble(cohort = c, visit = cohort_visits[[c]])
      })
    )
  }
  
  # Validation check
  stopifnot(all(c("cohort", "visit") %in% names(cohort_visits)))
  
  # Step 1: Convert all non-ID columns to character
  data_char <- data %>%
    mutate(across(-c(studyid, cohort, visit), as.character))
  
  # Step 2: Calculate missingness per cohort and variable
  cohort_missing <- data_char %>%
    pivot_longer(-c(studyid, cohort, visit), names_to = "variable", values_to = "value") %>%
    group_by(cohort, variable) %>%
    summarise(missing_frac = mean(is.na(value)), .groups = "drop")
  
  vars_pass_cohort <- cohort_missing %>%
    filter(missing_frac < cohort_col_missing_threshold) %>%
    group_by(variable) %>%
    summarise(n_cohorts = n(), .groups = "drop") %>%
    filter(n_cohorts == length(unique(data$cohort))) %>%
    pull(variable)
  
  # Step 3: Calculate overall column-wise missingness
  overall_missing <- data_char %>%
    summarise(across(all_of(vars_pass_cohort), ~mean(is.na(.)))) %>%
    pivot_longer(everything(), names_to = "variable", values_to = "missing_frac")
  
  vars_pass_overall <- overall_missing %>%
    filter(missing_frac < overall_col_missing_threshold) %>%
    pull(variable)
  
  # Final set of columns to retain
  variables_passing <- intersect(vars_pass_cohort, vars_pass_overall)
  
  # Step 4: Filter dataset to selected columns
  filtered_data <- data %>%
    select(studyid, cohort, visit, all_of(variables_passing))
  
  # Step 5: Convert selected columns to character
  filtered_data_char <- filtered_data %>%
    mutate(across(all_of(variables_passing), as.character))
  
  # Step 6: Filter out rows with > row_missing_threshold missing
  row_filtered_data <- filtered_data_char %>%
    rowwise() %>%
    mutate(
      missing_prop = mean(is.na(c_across(all_of(variables_passing))))
    ) %>%
    ungroup() %>%
    filter(missing_prop <= row_missing_threshold) %>%
    select(-missing_prop)
  
  return(row_filtered_data)
}

# Strict version: stops if conversion introduces unexpected NAs
safe_as_numeric <- function(x) {
  converted <- as.numeric(x)
  
  # Identify values that failed to convert but weren't originally NA
  problematic_values <- x[is.na(converted) & !is.na(x)]
  
  if (length(problematic_values) > 0) {
    message("The following values caused NA during conversion:")
    print(problematic_values)
    stop("Conversion resulted in NA values. Check non-numeric entries.")
  }
  
  return(converted)
}

clean_and_convert_variables <- function(data, num_cat, 
                                        na_strings_n = c("", 996, 997, 999),
                                        na_strings_c = c("", 96, 97, 98, 99),
                                        max_cat_levels = 40) {
  
  # Ensure variable names in num_cat exist in data
  num_cat <- num_cat %>%
    filter(variable_name %in% colnames(data))
  
  for (i in seq_len(nrow(num_cat))) {
    var_name <- num_cat$variable_name[i]
    var_type <- num_cat$type[i]
    
    if (var_type == "n") {
      data[[var_name]] <- replace(data[[var_name]], data[[var_name]] %in% na_strings_n, NA)
      data[[var_name]] <- safe_as_numeric(data[[var_name]])
      
    } else if (var_type == "c") {
      data[[var_name]] <- replace(data[[var_name]], data[[var_name]] %in% na_strings_c, NA)
      data[[var_name]] <- factor(data[[var_name]], levels = unique(data[[var_name]]))
      
      ncat <- nlevels(data[[var_name]])
      if (ncat > max_cat_levels) {
        warning(paste("Categorical variable", var_name, "has", ncat, "levels"))
        print(levels(data[[var_name]]))
      }
    }
  }
  
  return(data)
}


# combined data ----
#data = read.csv("data/andreia_hmz_data/df_hmz_bprhs_prospect_2025.csv")
#data = read.csv("data/andreia_hmz_data/df_hmz_bprhs_prospect_3june_2025.csv")
data = read.csv("data/andreia_hmz_data/hmz_bprhs_prospect_30july_2025.csv")

num_cat = read.xlsx("data/andreia_hmz_data/hmz_bprhs_prospect_metadata_30july2025.xlsx") %>%
  mutate(type_of_variable = ifelse(variable_name == "hmz_health_ds",'n',type_of_variable)) %>%
  select(variable_name, type_of_variable) %>%
  mutate(variable_name = gsub(" ","", variable_name))

setdiff(colnames(data),num_cat$variable_name)
setdiff(num_cat$variable_name,colnames(data))

# remove variables that are summarized into comparable aggregate variables -----
# --- Step 1. Identify "_avg" canonical vars ---
avg_vars <- names(data) %>% str_subset("_avg$")
avg_prefixes <- str_remove(avg_vars, "_avg$")

# --- Step 2. Add explicitly canonical vars (no _avg, just base names) ---
base_canonicals <- c("hmz_health_pss", "hmz_health_ds","hmz_sdoh_soc_support_ii")

# Their prefixes are just themselves
all_prefixes <- c(avg_prefixes, base_canonicals)

# --- Step 3. Find numbered variants in the data ---
number_cols <- names(data) %>% str_subset("_[0-9]+$")    # cols ending in _<number>
number_prefixes <- str_remove(number_cols, "_[0-9]+$")   # strip number suffix

# Also catch vars like hmz_health_pss1 (number glued to base, no underscore)
number_cols2 <- names(data) %>% str_subset("[0-9]+$")
number_prefixes2 <- str_remove(number_cols2, "[0-9]+$")

# --- Step 4. Collect to drop ---
to_drop <- c(
  number_cols[number_prefixes %in% all_prefixes],
  number_cols2[number_prefixes2 %in% base_canonicals]
)

to_drop

# --- Step 5. Drop them ---
data <- data %>% 
  select(-all_of(to_drop))

# Convert the soc2a/2b variables to seconds ------

data = data %>%
  mutate(
    # convert soc2b categories into a multiplier
    hmz_sdoh_soc2a_time_s = case_when(
      hmz_sdoh_soc2b == 1 ~ hmz_sdoh_soc2a * 60,           # minutes → seconds
      hmz_sdoh_soc2b == 2 ~ hmz_sdoh_soc2a * 60 * 60,      # hours → seconds
      hmz_sdoh_soc2b == 3 ~ hmz_sdoh_soc2a * 60 * 60 * 24, # days → seconds
      TRUE ~ NA_real_
    )
  ) %>%
  select(-c(hmz_sdoh_soc2a,hmz_sdoh_soc2b))

# convert the soc3a/soc3b variables 
data <- data %>%
  mutate(
    hmz_sdoh_soc3a_times_year = case_when(
      hmz_sdoh_soc3b == 1 ~ 0,
      hmz_sdoh_soc3b == 2 ~ hmz_sdoh_soc3a * 1,
      hmz_sdoh_soc3b == 3 ~ hmz_sdoh_soc3a * 12,
      hmz_sdoh_soc3b == 4 ~ hmz_sdoh_soc3a * 52,
      hmz_sdoh_soc3b == 5 ~ hmz_sdoh_soc3a * 365,
      TRUE ~ NA_real_
    )
  )%>%
  select(-c(hmz_sdoh_soc3a,hmz_sdoh_soc3b))

head(num_cat)
num_cat = rbind(num_cat, data.frame(variable_name = c('hmz_sdoh_soc2a_time_s','hmz_sdoh_soc3a_times_year'), type_of_variable = c('n','n')))

setdiff(colnames(data),num_cat$variable_name)
setdiff(num_cat$variable_name,colnames(data))

# test for all NA and non NA variables 
na.test <-  function (x) {
  w <- sapply(x, function(x)all(is.na(x)))
  if (any(w)) {
    stop(paste("All NA in columns", paste(which(w), collapse=", ")))
  }
}

no.na.test <- function(x) {
  w <- sapply(x, function(col) all(!is.na(col)))
  cols_no_na <- names(x)[w]
  cols_no_na <- cols_no_na[!grepl("^hmz_ffq_", cols_no_na)]
  return(cols_no_na)
}

pr = data %>%
  filter(cohort == "PROSPECT")
na.test(pr)
no.na.test(pr)

bp = data %>%
  filter(cohort == "BPRHS")
na.test(bp)
no.na.test(bp)

# check non-numeric cols
non_numeric_cols <- names(data)[!sapply(data, is.numeric)]

# [1] "visit"                            "cohort"                           "hmz_sdoh_disc_other_ii"           "hmz_sdoh_disc_life_main_other_ii"
# [5] "hmz_sdoh_disc_life_main_other"    "hmz_health_slp2"  

data <- data %>%
  mutate(across(where(is.character), trimws))

# remove remaining non-numeric
non_numeric_cols = setdiff(non_numeric_cols, c('visit','cohort'))

data = data %>%
  select(-non_numeric_cols)

# make numeric and categorical -----
data <- clean_and_convert_variables(data = data, num_cat = num_cat)


# save alltime data before filtering to v1 -----

all_times = data

saveRDS(all_times, "r_pipeline/analysis/rds/all_times_unfiltered_19aug25.rds")

# filter visit 1 ------
all_times = readRDS("r_pipeline/analysis/rds/all_times_unfiltered_19aug25.rds")

data = all_times %>%
  filter(visit == "v1") 

# move to eda
# ggviolin(data, x = "cohort", y = "hmz_health_ds_a",
#          add = "boxplot") +
#   ggtitle("ds_a distribution visit 1")
# 
# ggviolin(data, x = "cohort", y = "hmz_health_pss_a",
#          add = "boxplot") +
#   ggtitle("pss_a distribution visit 1")


# filter the age 
ggviolin(data, x = "cohort", y = "hmz_sdoh_age",
         add = "boxplot") +
  stat_compare_means(label="p.format",method="wilcox.test") +
  ggtitle("age distribution visit 1")

data = data %>%
  filter(hmz_sdoh_age>38)

ggviolin(data, x = "cohort", y = "hmz_sdoh_age",
         add = "boxplot") +
  stat_compare_means(label="p.format",method="wilcox.test") +
  ggtitle("age distribution visit 1")

# KCAL
ggviolin(data, x = "cohort", y = "hmz_ffq_kcal",
         add = "boxplot") +
  stat_compare_means(label="p.format",method="wilcox.test") +
  ggtitle("kcal visit 1")


data =  data %>% 
  filter(hmz_ffq_kcal > 600 & hmz_ffq_kcal < 4800)

ggviolin(data, x = "cohort", y = "hmz_ffq_kcal",
         add = "boxplot") +
  stat_compare_means(label="p.format",method="wilcox.test") +
  ggtitle("kcal visit 1, kcal > 600 & kcal < 4800")


ggscatter(data, x = "hmz_sdoh_age", y = "hmz_ffq_kcal",
          add = "reg.line",                         # Add regression line
          conf.int = TRUE,                          # Add confidence interval
          color = "cohort", palette = "jco",           # Color by groups "cyl"
          shape = "cohort"                             # Change point shape by groups "cyl"
) +
  stat_cor(aes(color = cohort), label.x = 30)           # Add correlation coefficient

# visualize NA - before selection
#sdoh_data = data[,colnames(data)[grep("hmz_sdoh",colnames(data))]]
#vis_miss(sdoh_data,warn_large_data = FALSE)+ theme(axis.text.x = element_text(angle = 90, vjust = 0.5, hjust=1))
#
#health_data = data[,colnames(data)[grep("hmz_health",colnames(data))]]
#vis_miss(health_data,warn_large_data = FALSE)+ theme(axis.text.x = element_text(angle = 90, vjust = 0.5, hjust=1))
#
#ffq_data = data[,colnames(data)[grep("hmz_ffq",colnames(data))]]
#vis_miss(ffq_data,warn_large_data = FALSE)+ theme(axis.text.x = element_text(angle = 90, vjust = 0.5, hjust=1))

# find data that is present in both bprhs and prospect ------
# Define visits per cohort
cohort_visits <- list(
  BPRHS = c("v1"),
  PROSPECT = c("v1")
)

data_select <- filter_by_missingness(
  data = data,
  cohort_col_missing_threshold = 0.9, 
  overall_col_missing_threshold = 0.5,
  row_missing_threshold = 0.1,
  cohort_visits = cohort_visits
)

str(data_select$cohort)

data_select = data_select %>%
  mutate(cohort = ifelse(cohort == "BPRHS",0,1))

data_select$cohort = factor(data_select$cohort, levels=c(0,1))

data_select <- clean_and_convert_variables(data = data_select, num_cat = num_cat)

variables_passing = colnames(data_select)

# Count how many retained variables belong to each prefix category

table(case_when(
  grepl("^hmz_sdoh", variables_passing) ~ "sdoh",
  grepl("^hmz_ffq", variables_passing) ~ "ffq",
  grepl("^hmz_health", variables_passing) ~ "health",
  TRUE ~ "other"
))

saveRDS(data_select, "r_pipeline/analysis/rds/harmonize_2cohort_healthsdohffq_20aug25_v1_rmmissing_50col_10row.rds")

# Outlier examination, not removing outliers for now ------
# 
# remove_outlier <- function(dataframe, columns = names(dataframe),low,high) {
# 
#   studyid = dataframe$studyid
# 
#   dataframe = dataframe %>%
#     select(-c('cohort','visit','studyid'))
# 
#   # Identify discrete vs. continuous variables
#   for (col in columns) {
#     x = dataframe[[col]]
#     Quantile1 <- quantile(x, probs=low, na.rm=T)
#     Quantile3 <- quantile(x, probs=high, na.rm=T)
#     IQR = Quantile3 - Quantile1
#     test = (!is.na(x) & (x > Quantile3 + (IQR * 1.5) | x < Quantile1 - (IQR * 1.5)))
#     
#     if(any(test)){
#       print(col)
#       print(studyid[test])
#       print(x[test])
#     }
#       #dataframe <- dataframe[!detect_outlier(dataframe[[col]],low,high), ]
#   }
# }
# 
# pr = data_select %>%
#   filter(cohort == "PROSPECT")
# 
# bp = data_select %>%
#   filter(cohort == "BPRHS")
# 
# # want to remove outliers but not from the ffq 
# numeric_cols <- names(data_select)[sapply(data_select, is.numeric)]
# ffq_cols = colnames(data_select)[grep("hmz_ffq",colnames(data_select))]
# numeric_cols = setdiff(numeric_cols, ffq_cols)
# 
# pr_ro = remove_outlier(pr, numeric_cols, low = 0.05, high = 0.95)
# bp_ro = remove_outlier(bp, numeric_cols, low = 0.05, high = 0.95)
# 
# # slp questions - don't do this - the slp questionaire is only at 5 yr
# # data <- data %>%
# #   mutate(
# #     hmz_health_slp_problem_sum = rowSums(
# #       across(matches("^hmz_health_slp_problem_[iv]+$"), ~ as.numeric(as.character(.))),
# #       na.rm = F
# #     )
# #   ) %>%
# #   select(-matches("^hmz_health_slp_problem_[iv]+$"))
# # 
# # 
# #
# # note that these are removed # step_mutate(
# #   hmz_health_slp_problem_sum = 
# #     hmz_health_slp_problem_i + 
# #     hmz_health_slp_problem_ii + 
# #     hmz_health_slp_problem_iii + 
# #     hmz_health_slp_problem_iv + 
# #     hmz_health_slp_problem_v) %>%
# #   step_rm(matches("^hmz_health_slp_problem_[iv]+$")) %>%
# #   