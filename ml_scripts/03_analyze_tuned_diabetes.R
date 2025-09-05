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
library(recipes)
library(themis)
library(forcats)
library(tidytext)

filter=dplyr::filter
rename=dplyr::rename
select=dplyr::select

setwd("/cluster/tufts/patralab/rbator01/aiml_ordovas_project/")

# Make the figures for the paper

# variable counting ----
#data = readRDS("r_pipeline/analysis/rds/harmonize_2cohort_healthsdohffq_20jun25_v1_rmmissing_50col_10row.rds")
data = readRDS("r_pipeline/analysis/rds/harmonize_2cohort_healthsdohffq_20aug25_v1_rmmissing_50col_10row_preproc_for_eda.rds")

# Get all column names
all_vars <- colnames(data)

# Identify variables by prefix
health_vars <- all_vars[str_starts(all_vars, "hmz_health")]
sdoh_vars   <- all_vars[str_starts(all_vars, "hmz_sdoh")]
ffq_vars    <- all_vars[str_starts(all_vars, "hmz_ffq")]

# Count and clean prefixes
tally_df <- tibble(
  group = c("health", "sdoh", "ffq"),
  n_vars = c(length(health_vars), length(sdoh_vars), length(ffq_vars))
) %>%
  mutate(group = toupper(group))
  
# If you want to list the variable names without the prefix:
list_df <- tibble(
  variable = c(str_remove(health_vars, "^hmz_"),
               str_remove(sdoh_vars, "^hmz_"),
               str_remove(ffq_vars, "^hmz_")),
  group = c(rep("health", length(health_vars)),
            rep("sdoh", length(sdoh_vars)),
            rep("ffq", length(ffq_vars)))
)

# View tallies
# Define custom colors
custom_colors <- c(
  "FFQ" = "#7BAFD4",     # muted blue
  "HEALTH" = "#88C27C",  # muted green
  "SDOH" = "#F4A259"     # muted orange
)

tally_df

# Create barplot
p = ggplot(tally_df, aes(x = group, y = n_vars, fill = group)) +
  geom_bar(stat = "identity") +
  scale_fill_manual(values = custom_colors, guide = "none") +  # no legend
  labs(
    title = "Filtered V1 Variables",
    x = "",
    y = "Number of Variables"
  ) +
  theme_minimal()

print(p)
ggsave(p, filename = "r_pipeline/analysis/plots/number_of_features_for_mlmodel.pdf", height=4, width = 3)


# diabtes status by year plot ---
library(openxlsx)
library(tidyverse)

# Load and preprocess tracker
tracker <- read.xlsx("data/diabetes_status_wchange_2class_4aug25.xlsx") %>%
  filter(!is.na(diabetes_v1)) %>%
  mutate(cohort = as.character(cohort)) %>%
  mutate(
    cohort = factor(cohort, levels = c("0", "1"), labels = c("BPRHS", "PROSPECT"))
  )

# Reshape v1 and v2 into long format and retain cohort
long_diabetes <- tracker %>%
  select(studyid, cohort, diabetes_v1, diabetes_v2) %>%
  pivot_longer(
    cols = starts_with("diabetes_v"),
    names_to = "visit",
    names_prefix = "diabetes_",
    values_to = "diabetes"
  ) %>%
  mutate(
    visit = toupper(visit),
    diabetes = factor(diabetes, levels = c(0, 1), labels = c("No Diabetes", "Diabetes"))
  )

# Prepare change summary as third bar, grouped by cohort
change_summary <- tracker %>%
  filter(!is.na(diabetes_change)) %>%
  mutate(
    visit = "CHANGE",
    diabetes = case_when(
      diabetes_change == -1 ~ "Remission",
      diabetes_change ==  0 ~ "No Change",
      diabetes_change ==  1 ~ "Progression",
      TRUE ~ NA_character_
    )
  ) %>%
  count(cohort, visit, diabetes)

# Count for V1 and V2, grouped by cohort
v1v2_summary <- long_diabetes %>%
  filter(!is.na(diabetes)) %>%
  count(cohort, visit, diabetes)

# Combine all and set factor levels
plot_df <- bind_rows(v1v2_summary, change_summary) %>%
  mutate(
    visit = factor(visit, levels = c("V1", "V2", "CHANGE")),
    diabetes = factor(
      diabetes,
      levels = c("No Diabetes", "Diabetes", "Remission", "No Change", "Progression")
    )
  )

fill_colors <- c(
  "No Diabetes" = "#B2DF8A",        # light green
  "Diabetes" = "#7BAFD4",           # light blue
  "Remission" = "#E6AA68",          # orange-brown (vs. old yellow-orange)
  "No Change" = "#CAB2D6",          # lavender-purple (vs. tan-orange)
  "Progression" = "#D95F02"         # strong red-orange (vs. muted red)
)

# Plot with facet by cohort
p <- ggplot(plot_df, aes(x = visit, y = n, fill = diabetes)) +
  geom_bar(stat = "identity", position = "stack") +
  scale_fill_manual(values = fill_colors) +
  labs(
    title = "Diabetes Status and Change V1-2",
    x = "",
    y = "Number of Participants",
    fill = NULL
  ) +
  facet_wrap(~ cohort) +
  theme_minimal()

p
ggsave(p, filename = "r_pipeline/analysis/plots/number_of_participants_diabetes_change.pdf", height=4, width = 5)

plot_df
# roc curve for various things ----
# Parameters
nclass <- 2
downsample = 0
outvar <- "diabetes"
filter_cohorts <- c("none", "0", "1")
years <- c("v1", "v2")
seeds <- 1:10
data_string <- "all"

# Create an empty list for ROC data
roc_list <- list()

# Common grid for interpolation
common_grid <- seq(0, 1, length.out = 101)

# ---- Loop through combinations and seeds for ROC ----
for (seed in seeds) {
  for (filter_cohort in filter_cohorts) {
    for (year in years) {
      
      # save_string <- paste0(data_string, "_", outvar, "_", year, 
      #                       "_class", nclass, "_filter", filter_cohort, 
      #                       "_ds", downsample, "_", seed, "_tune_balancecohort_boruta_19aug25")

      save_string <- paste0(data_string, "_", outvar, "_", year, 
                            "_class", nclass, "_filter", filter_cohort, 
                            "_ds", downsample, "_", seed, "_tune_caseweights_boruta_25aug25")      
      file_path <- paste0("r_pipeline/analysis/results/log_", save_string, "_roc.rds")
      
      if (file.exists(file_path)) {
        roc <- readRDS(file_path)
        roc$filter_cohort <- filter_cohort
        roc$year <- year
        roc$seed <- seed
        roc$model_label <- paste0("filter=", filter_cohort, ", ", year)
        
        # Interpolate sensitivity on common specificity grid
        interpolated <- approx(1 - roc$specificity, roc$sensitivity, xout = common_grid)
        interpolated_df <- data.frame(
          specificity = 1 - interpolated$x,
          sensitivity = interpolated$y,
          filter_cohort = filter_cohort,
          year = year,
          seed = seed
        )
        
        roc_list[[length(roc_list) + 1]] <- interpolated_df
      } else {
        message("Skipping missing file: ", file_path)
      }
    }
  }
}


# Combine and summarize
roc_combined <- bind_rows(roc_list) %>%
  mutate(filter_cohort = recode(filter_cohort,
                                      "0" = "BPRHS",
                                      "1" = "PROSPECT",
                                      "none" = "Both cohorts"))

roc_summary <- roc_combined %>%
  group_by(filter_cohort, year, specificity) %>%
  summarise(mean_sens = mean(sensitivity, na.rm = TRUE),
            sd_sens = sd(sensitivity, na.rm = TRUE), .groups = "drop")

# --- Plot averaged ROC curves with SD shading ---
plot_a_data <- roc_summary %>%
  filter(filter_cohort == "Both cohorts", year %in% c("v1", "v2"))

plot_a <- ggplot(plot_a_data, aes(x = 1 - specificity, y = mean_sens, color = year)) +
  geom_line(size = 1.2) +
  geom_ribbon(aes(ymin = mean_sens - sd_sens, ymax = mean_sens + sd_sens, fill = year), alpha = 0.2, color = NA) +
  geom_abline(linetype = "dashed", color = "gray") +
  coord_equal() +
  labs(title = "ROC Curves(Visit 1-2)",
       x = "1 - Specificity", y = "Sensitivity", color = "Year", fill = "Year") +
  theme_minimal()

print(plot_a)
ggsave(plot_a, filename = "r_pipeline/analysis/plots/roc_hmz_visit_1_2_avg_caseweight.pdf",height=4, width=4)

# --- Plot B: Average ROC curves for Visit 1 across filter_cohorts ---
plot_b_data <- roc_combined %>%
  filter(year == "v1", filter_cohort %in% c("Both cohorts", "BPRHS", "PROSPECT"))

# Summarize across seeds
plot_b_summary <- plot_b_data %>%
  group_by(filter_cohort, specificity) %>%
  summarise(
    mean_sens = mean(sensitivity, na.rm = TRUE),
    sd_sens = sd(sensitivity, na.rm = TRUE),
    .groups = "drop"
  )

# Plot mean ± sd ribbon
plot_b <- ggplot(plot_b_summary, aes(x = 1 - specificity, y = mean_sens, color = filter_cohort)) +
  geom_line(size = 1.2) +
  geom_ribbon(aes(ymin = mean_sens - sd_sens, ymax = mean_sens + sd_sens, fill = filter_cohort),
              alpha = 0.2, color = NA) +
  geom_abline(linetype = "dashed", color = "gray") +
  coord_equal() +
  labs(title = "ROC Curves by Cohort (Visit 1)",
       x = "1 - Specificity", y = "Sensitivity",
       color = "Cohort", fill = "Cohort") +
  theme_minimal()

print(plot_b)
ggsave(plot_b, filename = "r_pipeline/analysis/plots/roc_hmz_vs_indiv_visit_1_avg_caseweight.pdf", height = 4.5, width = 4.5)


# ===================== ACCURACY + FEATURE IMPORTANCE =====================

# Read VI data across seeds
vi_list <- list()

for (seed in seeds) {
  for (filter_cohort in filter_cohorts) {
    for (year in years) {
      
      # save_string <- paste0(data_string, "_", outvar, "_", year, 
      #                       "_class", nclass, "_filter", filter_cohort, 
      #                       "_ds", downsample, "_", seed, "_tune_balancecohort_boruta_19aug25")
      
      save_string <- paste0(data_string, "_", outvar, "_", year, 
                            "_class", nclass, "_filter", filter_cohort, 
                            "_ds", downsample, "_", seed, "_tune_caseweights_boruta_25aug25")  
      
      file_path <- paste0("r_pipeline/analysis/results/log_", save_string, ".csv")
      
      if (file.exists(file_path)) {
        vi <- read.csv(file_path)
        vi$filter_cohort <- filter_cohort
        vi$year <- year
        vi$seed <- seed
        vi_list[[length(vi_list) + 1]] <- vi
      } else {
        message("Missing VI file: ", file_path)
      }
    }
  }
}

# combine all runs
vi_combined <- bind_rows(vi_list) %>%
  mutate(
    filter_cohort = case_when(
      filter_cohort == "none" ~ "Both cohorts",
      filter_cohort == "0" ~ "BPRHS",
      filter_cohort == "1"  ~ "PROSPECT",
      filter_cohort %in% c("BPRHS","PROSPECT")     ~ as.character(filter_cohort),
      TRUE                                         ~ as.character(filter_cohort)
    ),
    filter_cohort = factor(filter_cohort,
                          levels = c("Both cohorts", "BPRHS", "PROSPECT"))
  )

head(vi_combined)

# VI PLOTS ------
vi_mean_imp <- vi_combined %>%
  group_by(Variable, filter_cohort, year, type, visit) %>%
  summarise(
    Importance = mean(Importance, na.rm = TRUE),
    rank = mean(rank, na.rm = TRUE),
    .groups = "drop"
  ) %>%
  # force AGE to HEALTH/SDOH if needed
  mutate(type = ifelse(Variable == "age", "HEALTH/SDOH", type)) %>%
  filter(
    visit == "v1",
    filter_cohort %in% c("Both cohorts", "BPRHS", "PROSPECT")
  ) %>%
  mutate(
    type = toupper(type),
    type = factor(type, levels = c("FFQ", "SDOH", "HEALTH", "HEALTH/SDOH")),
    Variable = as.character(Variable)
  )

# variables that appear in the 2-cohort model
vars_in_both <- vi_mean_imp %>%
  filter(filter_cohort == "Both cohorts") %>%
  pull(Variable) %>%
  unique()

vi_mean_imp <- vi_mean_imp %>%
  mutate(
    cohort_specific = case_when(
      !(Variable %in% vars_in_both) & filter_cohort != "Both cohorts" ~ "Unique to 1-cohort models",
      TRUE ~ "2-cohort model"
    ),
    cohort_specific = factor(
      cohort_specific,
      levels = c("2-cohort model", "Unique to 1-cohort models")
    ),
    # order within facet by *descending* Importance (flip sign)
    Variable_plot = reorder_within(Variable, -Importance, filter_cohort) |> fct_rev()
  )

##Read relabel file and join pretty names
##Do this only once to create the names
# features = data.frame(variable_name = unique(vi_mean_imp$Variable))
# view(features)
# metadata = read.xlsx("data/andreia_hmz_data/hmz_bprhs_prospect_metadata_30july2025.xlsx") %>%
#   mutate(long_variable_name = variable_name) %>%
#   mutate(variable_name = gsub("hmz_health_","", variable_name)) %>%
#   mutate(variable_name = gsub("hmz_sdoh_","", variable_name)) %>%
#   mutate(variable_name = gsub("hmz_ffq_","", variable_name)) %>%
#   select(long_variable_name, variable_name, description) %>%
#   mutate(description = gsub("\\ $","",description)) %>%
#   mutate(description = gsub("\\ ","_",description)) %>%
#   mutate(description = gsub("\\(","",description)) %>%
#   mutate(description = gsub("\\)","",description)) %>%
#   mutate(description = gsub("average_","", description)) %>%
#   mutate(description = gsub("serum_","", description))
# head(metadata)
# features = features %>%
#   left_join(metadata, by="variable_name")
# 
# view(features)
# 
# tmp <- read.xlsx("r_pipeline/analysis/plots/relabel_features_plot_edit.xlsx")
# 
# colnames(tmp)
# tmp = tmp %>%
#   select(-c(description, description.new.tmp)) %>%
#   rename(description.new.tmp = description.new)
# colnames(tmp)
# colnames(features)
# 
# features = features %>%
#   left_join(tmp, by=c("variable_name","long_variable_name")) %>%
#   mutate(description.new = ifelse(is.na(description.new.tmp), description, description.new.tmp))
# 
# view(features)
# write.xlsx(features,"r_pipeline/analysis/plots/relabel_features_plot.xlsx")

features <- read.xlsx("r_pipeline/analysis/plots/relabel_features_plot_edit.xlsx") %>%
  transmute(
    Variable = variable_name,
    description.new = str_to_sentence(description.new)
  )

top_vars <- vi_mean_imp %>%
  group_by(filter_cohort) %>%              # facet-level grouping
  slice_max(order_by = Importance, n = 25, with_ties = FALSE) %>%
  ungroup()

top_vars <- top_vars %>%
  left_join(features, by = "Variable") %>%
  mutate(
    description.new = ifelse(
      is.na(description.new) | description.new == "",
      Variable,
      description.new
    )
  )

# Build a NAMED VECTOR for label lookup: names = "var___facet", values = pretty labels
label_map <- top_vars %>%
  transmute(key = paste0(Variable, "___", filter_cohort), label = description.new) %>%
  distinct()

label_lookup <- setNames(label_map$label, label_map$key)

fill_colors <- c("FFQ" = "#7BAFD4", "SDOH" = "#F4A259", "HEALTH" = "#88C27C", "HEALTH/SDOH" = "grey")

p <- ggplot(top_vars, aes(x = Importance, y = Variable_plot, fill = type)) +
  geom_col(aes(color = cohort_specific), width = 0.8, linewidth = 1) +
  scale_fill_manual(values = fill_colors) +
  # outline for cohort-specific only; hide color legend to avoid clutter
  scale_color_manual(values = c("2-cohort model" = NA, "Unique to 1-cohort models" = "black"), 
                     drop = FALSE,
                     guide = guide_legend(title = NULL, override.aes = list(fill = NA))) +
  guides(fill = guide_legend(title = NULL)) +
  facet_wrap(~ filter_cohort, scales = "free_y") +
  labs(
    title = " Most Important Variables (V1, Avg Across Seeds)",
    x = "Average Permutation Importance", y = NULL
  ) +
  # >>> FIX: use the named vector for labels <<<
  scale_y_reordered(labels = function(x) {
    out <- label_lookup[x]
    # fallback: if any labels are missing, strip the facet suffix "___.*"
    out[is.na(out)] <- gsub("___.*$", "", x[is.na(out)])
    out
  }) +
  theme_minimal(base_size = 12) +
  theme(
    strip.text = element_text(face = "bold"),
    axis.text.y = element_text(size = 10)
  )

print(p)
ggsave(filename = "r_pipeline/analysis/plots/compare_vi_v1_avg_caseweight.pdf", plot = p, width = 12, height = 7)

# SDOH only -----

# ---- 1) Filter and take top 5 per cohort ----
top_vars <- vi_mean_imp %>%
  #filter(filter_cohort %in% c("Both cohorts")) %>%
  filter(type %in% c("SDOH", "HEALTH/SDOH")) %>%
  group_by(filter_cohort) %>%
  slice_max(order_by = Importance, n = 5, with_ties = FALSE) %>%
  ungroup()

top_vars <- top_vars %>%
  left_join(features, by = "Variable") %>%
  mutate(
    description.new = ifelse(
      is.na(description.new) | description.new == "",
      Variable,
      description.new
    )
  )


# Build a NAMED VECTOR for label lookup: names = "var___facet", values = pretty labels
label_map <- top_vars %>%
  transmute(key = paste0(Variable, "___", filter_cohort), label = description.new) %>%
  distinct()

label_lookup <- setNames(label_map$label, label_map$key)


# Ensure cohort_specific exists for outline coloring (fallback if not present)
if (!"cohort_specific" %in% names(top_vars)) {
  top_vars <- top_vars %>%
    mutate(cohort_specific = factor("2-cohort model",
                                    levels = c("2-cohort model", "Unique to 1-cohort models")))
}

# Order within facet so largest is at the TOP
top_vars <- top_vars %>%
  mutate(
    Variable_plot = tidytext::reorder_within(Variable, -Importance, filter_cohort) |> forcats::fct_rev()
  )

# ---- 2) Plot ----
p <- ggplot(top_vars, aes(x = Importance, y = Variable_plot, fill = type)) +
  geom_col() +
  scale_fill_manual(values = fill_colors) +
  # Outline only for "Unique to 1-cohort models"; hide color legend
  scale_color_manual(values = c("2-cohort model" = NA,
                                "Unique to 1-cohort models" = "black"),
                     guide = "none") +
  guides(fill = guide_legend(title = NULL)) +
  facet_wrap(~ filter_cohort, scales = "free_y") +
  labs(
    title = "SDOH Variables",
    x = "Average Permutation Importance", y = NULL
  ) +
  # Map pretty labels to the hidden "var___facet" keys
  tidytext::scale_y_reordered(labels = function(x) {
    out <- unname(label_lookup[x])
    # fallback if any are missing
    out[is.na(out)] <- gsub("___.*$", "", x[is.na(out)])
    out
  }) +
  theme_minimal(base_size = 12) +
  theme(
    strip.text = element_text(face = "bold"),
  )

print(p)
ggsave(filename = "r_pipeline/analysis/plots/top5_sdh_by_cohort_caseweight.pdf",
       plot = p, width = 12, height = 3)



# ACCURACY PLOTS -----
# 1) one accuracy per seed × cohort × visit
acc_by_seed <- vi_combined %>%
  filter(filter_cohort %in% c("Both cohorts", "BPRHS", "PROSPECT"),
         visit %in% c("v1", "v2")) %>%     # if you use `year` instead, swap to `year %in% c("v1","v2")`
  group_by(outvar, data_string, filter_cohort, visit, seed) %>%
  summarise(accuracy = first(accuracy), .groups = "drop")

# 2) average across seeds (+ 95% CI)
acc_summary <- acc_by_seed %>%
  group_by(outvar, data_string, filter_cohort, visit) %>%
  summarise(
    mean_acc = mean(accuracy, na.rm = TRUE),
    sd_acc   = sd(accuracy, na.rm = TRUE),
    n        = dplyr::n(),
    se_acc   = sd_acc / sqrt(n),
    lwr      = mean_acc - 1.96 * se_acc,
    upr      = mean_acc + 1.96 * se_acc,
    .groups  = "drop"
  )

acc_summary
# 3) plot
p_acc = ggplot(acc_summary, aes(x = filter_cohort, y = mean_acc, fill = visit)) +
  geom_col(position = position_dodge(width = 0.7), width = 0.6) +
  geom_errorbar(aes(ymin = lwr, ymax = upr),
                position = position_dodge(width = 0.7), width = 0.2) +
  scale_y_continuous(labels = percent_format(accuracy = 1), limits = c(0, 1)) +
  labs(
    title = "Accuracy",
    x = "Cohort",
    y = "Avg. Accuracy",
    fill = "Visit"
  ) +
  theme_minimal(base_size = 12)
show(p_acc)

ggsave(p_acc, filename = "r_pipeline/analysis/plots/p_acc_caseweight.pdf", height = 4, width = 4)
