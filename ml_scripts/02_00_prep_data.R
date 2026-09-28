#######
## select visit data and variables present in both cohorts
#######

suppressPackageStartupMessages({
  library(openxlsx)
  library(tidymodels)
  library(workflows)
  library(tune)
  library(compositions)
  library(caret)
  library(visdat)
  library(ggpubr)
  library(dplyr)
  library(stringr)
  library(ggplot2)
})

# functions -----

filter_by_missingness <- function(data, 
                                  cohort_col_missing_threshold = 0.9, 
                                  overall_col_missing_threshold = 0.5, 
                                  row_missing_threshold = 0.1, 
                                  cohort_visits) {
  
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
  
  # Convert all non-ID columns to character
  data_char <- data %>%
    mutate(across(-c(studyid, cohort, visit), as.character))
  
  # Calculate missingness per cohort and variable
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
  
  # Calculate overall column-wise missingness
  overall_missing <- data_char %>%
    summarise(across(all_of(vars_pass_cohort), ~mean(is.na(.)))) %>%
    pivot_longer(everything(), names_to = "variable", values_to = "missing_frac")
  
  vars_pass_overall <- overall_missing %>%
    filter(missing_frac < overall_col_missing_threshold) %>%
    pull(variable)
  
  # Final set of columns to retain
  variables_passing <- intersect(vars_pass_cohort, vars_pass_overall)
  
  # Filter dataset to selected columns
  filtered_data <- data %>%
    select(studyid, cohort, visit, all_of(variables_passing))
  
  # Convert selected columns to character
  filtered_data_char <- filtered_data %>%
    mutate(across(all_of(variables_passing), as.character))
  
  # Filter out rows with > row_missing_threshold missing
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
                                        max_cat_levels = 10) {
  
  # Ensure variable names in num_cat exist in data
  num_cat <- num_cat %>%
    filter(variable_name %in% colnames(data))
  
  for (i in seq_len(nrow(num_cat))) {
    var_name <- num_cat$variable_name[i]
    var_type <- num_cat$type[i]
    
    if (var_type == "n") {
      data[[var_name]] <- safe_as_numeric(data[[var_name]])
      
    } else if (var_type == "c") {
      data[[var_name]] <- factor(data[[var_name]], levels = unique(data[[var_name]]))
      
      ncat <- nlevels(data[[var_name]])
      if (ncat > max_cat_levels) {
        print("here")
        warning(paste("Categorical variable", var_name, "has", ncat, "levels"))
        print(levels(data[[var_name]]))
      }
    }
  }
  
  return(data)
}

# read in data ----
data_file = "../../data/hmz_data/df_hmz_bprhs_prospect_2025.csv"
data = read.csv(data_file)
meta_file = "../../data/hmz_data/hmz_bprhs_prospect_metadata_2025.xlsx"

# test number visit 1
vis1 = data %>%
  filter(visit == "v1")
table(vis1$cohort)

# filter soc_emo development should not have data level 5 -----
remove <- data %>%
  filter(if_any(
    c(hmz_sdoh_soc_emo2_1, hmz_sdoh_soc_emo2_2, hmz_sdoh_soc_emo2_3,
      hmz_sdoh_soc_emo2_4, hmz_sdoh_soc_emo2_5, hmz_sdoh_soc_emo2_6,
      hmz_sdoh_soc_emo2_7),
    ~ .x == 5
  ))

data = data %>%
  filter(!studyid == remove$studyid)

# read in numeric or categorical data
num_cat = read.xlsx(meta_file) %>%
  mutate(type_of_variable = ifelse(variable_name == "hmz_health_ds",'n',type_of_variable)) %>%
  select(variable_name, type_of_variable) %>%
  mutate(variable_name = gsub(" ","", variable_name)) %>%
  mutate(type_of_variable = ifelse(variable_name == "studyid",'n',type_of_variable))

setdiff(colnames(data),num_cat$variable_name)
setdiff(num_cat$variable_name,colnames(data))

# remove variables that are summarized into comparable aggregate variables -----
avg_vars <- names(data) %>% str_subset("_avg$")
avg_prefixes <- str_remove(avg_vars, "_avg$")

# Add explicitly canonical vars (no _avg, just base names) ---
base_canonicals <- c("hmz_health_pss", "hmz_health_ds","hmz_sdoh_soc_support_ii")

# Their prefixes are just themselves
all_prefixes <- c(avg_prefixes, base_canonicals)

# Find numbered variants in the data ---
number_cols <- names(data) %>% str_subset("_[0-9]+$")    # cols ending in _<number>
number_prefixes <- str_remove(number_cols, "_[0-9]+$")   # strip number suffix

# Also catch vars like hmz_health_pss1 (number glued to base, no underscore)
number_cols2 <- names(data) %>% str_subset("[0-9]+$")
number_prefixes2 <- str_remove(number_cols2, "[0-9]+$")

# Collect to drop ---
to_drop <- c(
  number_cols[number_prefixes %in% all_prefixes],
  number_cols2[number_prefixes2 %in% base_canonicals]
)

# Drop them ---
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

num_cat = rbind(num_cat, data.frame(variable_name = c('hmz_sdoh_soc2a_time_s','hmz_sdoh_soc3a_times_year'), type_of_variable = c('n','n')))

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

# check non-numeric cols before conversion ----
non_numeric_cols <- names(data)[!sapply(data, is.numeric)]
non_numeric_cols
# [1] "visit"                            "cohort"                           "hmz_sdoh_disc_other_ii"           "hmz_sdoh_disc_life_main_other_ii"
# [5] "hmz_sdoh_disc_life_main_other"    "hmz_health_slp2"  

data <- data %>%
  mutate(across(where(is.character), trimws))

# make numeric and categorical -----
data <- clean_and_convert_variables(data = data, num_cat = num_cat)

unique(data$hmz_sdoh_pdq_2h_other)
unique(data$hmz_sdoh_pdq_2i_other)
unique(data$hmz_sdoh_pdq_4i_other)
unique(data$hmz_health_hb_slp2)

# convert HH:MM → minutes since midnight
library(lubridate)
convert_to_minutes <- function(x) {
  x <- na_if(x, "")
  x <- if_else(
    !is.na(x) & str_detect(x, "^\\d{1,2}:\\d{2}$"),
    paste0(x, ":00"),
    x
  )
  as.numeric(hms(x)) / 60
}

data$slp_min <- convert_to_minutes(data$hmz_health_hb_slp2)

library(Hmisc)
data$slp_bin_q <- cut2(data$slp_min, g = 4)  # quartiles

table(data$cohort, data$slp_bin_q)

# remove remaining non-numeric
#non_numeric_cols = setdiff(non_numeric_cols, c('visit','cohort'))
#non_numeric_cols
#data = data %>%
#  select(-non_numeric_cols)

# save alltime data before filtering to v1 -----

all_times = data

# test number
vis1 = data %>%
  filter(visit == "v1")
table(vis1$cohort)

saveRDS(all_times, "../../analysis/all_times_unfiltered.rds")

# filter visit 1 ------
data = all_times %>%
  filter(visit == "v1") 

table(data$cohort)
# BPRHS PROSPECT 
# 1509     1738 

data =  data %>% 
  filter(hmz_ffq_kcal > 600 & hmz_ffq_kcal < 4800)

table(data$cohort)
#BPRHS PROSPECT 
#1418     1003 

ggviolin(data, x = "cohort", y = "hmz_ffq_kcal",
         add = "boxplot") +
  stat_compare_means(label="p.format",method="wilcox.test") +
  ggtitle("kcal visit 1, kcal > 600 & kcal < 4800")

# investigate age filtering ---------
ggviolin(data, x = "cohort", y = "hmz_sdoh_age",
         add = "boxplot") +
  stat_compare_means(label="p.format",method="wilcox.test") +
  ggtitle("age distribution visit 1")

data_agefilt = data %>%
 filter(hmz_sdoh_age>38)

ggviolin(data_agefilt, x = "cohort", y = "hmz_sdoh_age",
         add = "boxplot") +
  stat_compare_means(label="p.format",method="wilcox.test") +
  ggtitle("age distribution visit 1")

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

variables_passing
dim(data_select)

table(data_select$cohort)
# 0    1 
# 1407  947  

saveRDS(data_select, "../../analysis/harmonize_2cohort_healthsdohffq_v1_rmmissing_50col_10row.rds")

# Count how many retained variables belong to each prefix category
table(case_when(
  grepl("^hmz_sdoh", variables_passing) ~ "sdoh",
  grepl("^hmz_ffq", variables_passing) ~ "ffq",
  grepl("^hmz_health", variables_passing) ~ "health",
  TRUE ~ "other"
))

# filter visit 2 ------
data = all_times %>%
  filter(visit == "v2") 

table(data$cohort)
# BPRHS PROSPECT 
# 1273     1718 

ggviolin(data, x = "cohort", y = "hmz_ffq_kcal",
         add = "boxplot") +
  stat_compare_means(label="p.format",method="wilcox.test") +
  ggtitle("kcal visit 2")

data =  data %>% 
  filter(hmz_ffq_kcal > 600 & hmz_ffq_kcal < 4800)

# test = data %>% 
#   filter(hmz_ffq_kcal < 600 | hmz_ffq_kcal > 4800)
# 
# test = data %>%
#   filter(is.na(hmz_ffq_kcal))
# 
# view(test %>% select(studyid, cohort, visit, hmz_ffq_kcal))
### HERE 
table(data$cohort)
# BPRHS PROSPECT 
# 1208       92 

# investigate age filtering ---------
ggviolin(data, x = "cohort", y = "hmz_sdoh_age",
         add = "boxplot") +
  stat_compare_means(label="p.format",method="wilcox.test") +
  ggtitle("age distribution visit 1")

data_agefilt = data %>%
  filter(hmz_sdoh_age>38)

ggviolin(data_agefilt, x = "cohort", y = "hmz_sdoh_age",
         add = "boxplot") +
  stat_compare_means(label="p.format",method="wilcox.test") +
  ggtitle("age distribution visit 1")

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

variables_passing
dim(data_select)

table(data_select$cohort)
# 0    1 
# 1190   80  

saveRDS(data_select, "../../analysis/harmonize_2cohort_healthsdohffq_v2_rmmissing_50col_10row.rds")

# Count how many retained variables belong to each prefix category
table(case_when(
  grepl("^hmz_sdoh", variables_passing) ~ "sdoh",
  grepl("^hmz_ffq", variables_passing) ~ "ffq",
  grepl("^hmz_health", variables_passing) ~ "health",
  TRUE ~ "other"
))
