#######
## Analyze distributions for selected features
## Figure 1: Numeric features (4-panel RIDGE plots; EXACT original p1 aesthetics)
## Figure 2: SDOH features
##   A) Number of Activities (RIDGE; same ridge style)
##   B/C) Highest Education Degree & Place of Birth (stacked bars; same as original)
##
## Requested changes (ONLY):
## - Time-to-get-here: convert seconds -> HOURS
## - Restore EXACT original ridge behavior (no truncation)
## - For Aspartame + Time-to-get-here: show ticks 0,1,10,100,(1000) with integer labels (no sci)
## - Remove facet strip titles for Fig 2 barplots
## - Diabetes labels: Non-diabetes / Diabetes
## - Titles are the custom human-readable names in your specified order
#######

suppressPackageStartupMessages({
  library(ggpubr)
  library(purrr)
  library(tidyr)
  library(data.table)
  library(ggridges)
  library(dplyr)
  library(ggplot2)
  library(forcats)
  library(scales)
})

# ------------------------------------------------------------
# Paths
# ------------------------------------------------------------
outpath  <- "../../analysis/plots/select_feature_plots"
RDS1     <- "../../analysis/harmonize_2cohort_healthsdohffq_v1_rmmissing_50col_10row.rds"
TRK      <- "../../data/hmz_data/diabetes_status_wchange_2class_7nov25.xlsx"

source("utils.R")

# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------
make_diabetes01 <- function(x) {
  x_chr <- as.character(x)
  dplyr::case_when(
    x_chr %in% c("1","Diabetes","Diabetic","diabetes","diabetic") ~ 1L,
    x_chr %in% c("0","Non-diabetes","Non-diabetic","No Diabetes",
                 "non-diabetes","non-diabetic","no diabetes") ~ 0L,
    suppressWarnings(!is.na(as.integer(x_chr))) ~ as.integer(x_chr),
    TRUE ~ NA_integer_
  )
}

nice_log1p_breaks <- function(x) {
  x <- x[is.finite(x) & !is.na(x) & x >= 0]
  if (!length(x)) return(0)
  mx <- max(x); minpos <- suppressWarnings(min(x[x > 0], na.rm = TRUE))
  if (!is.finite(minpos)) minpos <- 1
  lo <- max(0, floor(log10(minpos))); hi <- ceiling(log10(mx))
  br <- c(0, 10^(lo:hi))
  unique(sort(br[br <= mx]))
}

use_log1p <- function(values, min_orders = 2) {
  v <- suppressWarnings(as.numeric(values))
  v <- v[v >= 0 & is.finite(v)]
  if (length(v) < 2) return(FALSE)
  span <- log10(max(v + 1, na.rm = TRUE)) - log10(min(v + 1, na.rm = TRUE))
  is.finite(span) && span >= min_orders
}

# ------------------------------------------------------------
# Custom titles (explicit, as requested)
# ------------------------------------------------------------
pretty_name <- function(x) {
  dplyr::case_when(
    x == "hmz_ffq_aspt"              ~ "Aspartame",
    x == "hmz_health_lab_ldl"        ~ "Low Density Lipoprotein",
    x == "hmz_health_ant_avg_waist"  ~ "Waist Circumference",
    x == "hmz_sdoh_soc2a_time_s"     ~ "How Quickly Can Your Child Get Here",
    x == "hmz_sdoh_soc_activities"   ~ "Number of Activities",
    x == "hmz_sdoh_hc_educ"          ~ "Highest Education Degree",
    x == "hmz_sdoh_mh_pob"           ~ "Place of Birth",
    TRUE ~ x
  )
}

pretty_xlab <- function(x) {
  dplyr::case_when(
    x == "hmz_ffq_aspt"              ~ "Aspartame (mg/day)",
    x == "hmz_health_lab_ldl"        ~ "Low Density Lipoprotein (mg/dL)",
    x == "hmz_health_ant_avg_waist"  ~ "Waist Circumference (inches)",
    x == "hmz_sdoh_soc2a_time_s"     ~ "How Quickly Can Your Child Get Here (hours)",
    TRUE ~ pretty_name(x)
  )
}

# ------------------------------------------------------------
# Ridge plot maker: EXACT original aesthetics, with tick override only for A & D
# ------------------------------------------------------------
make_ridge_plot <- function(df_feat, feat, feat_pretty) {
  vals <- df_feat[[feat]]
  
  ridge_df <- bind_rows(
    df_feat %>% transmute(panel="BPRHS vs PROSPECT", group2=cohort, value=.data[[feat]]),
    df_feat %>% filter(cohort=="BPRHS") %>%
      transmute(panel="BPRHS (Non-diabetes vs Diabetes)",
                group2=factor(ifelse(diabetes01 == 1, "Diabetes", "Non-diabetes"),
                              levels=c("Non-diabetes","Diabetes")),
                value=.data[[feat]]),
    df_feat %>% filter(cohort=="PROSPECT") %>%
      transmute(panel="PROSPECT (Non-diabetes vs Diabetes)",
                group2=factor(ifelse(diabetes01 == 1, "Diabetes", "Non-diabetes"),
                              levels=c("Non-diabetes","Diabetes")),
                value=.data[[feat]])
  ) %>%
    mutate(panel = factor(panel,
                          levels=c("BPRHS vs PROSPECT",
                                   "BPRHS (Non-diabetes vs Diabetes)",
                                   "PROSPECT (Non-diabetes vs Diabetes)")))
  
  # ---- EXACT original ridge aesthetic block (fill + color outlines) ----
  p1 <- ggplot(ridge_df, aes(x=value, y=panel, fill=group2, color=group2)) +
    ggridges::geom_density_ridges(position="identity", scale=0.95, alpha=0.35,
                                  rel_min_height=0.001, size=0.3) +
    labs(
      title = feat_pretty,
      x     = pretty_xlab(feat),
      y     = NULL
    ) +
    theme_minimal(base_size = 12)
  
  # ---- Original log1p decision, but override ticks/labels only for Aspartame + Time ----
  if (use_log1p(vals)) {
    if (feat %in% c("hmz_ffq_aspt", "hmz_sdoh_soc2a_time_s")) {
      # KEEP trans=log1p_trans(), but choose “nice” ticks and integer labels
      p1 <- p1 + scale_x_continuous(
        trans  = scales::log1p_trans(),
        breaks = c(0, 1, 10, 100, 1000),   # remove 1000 if you truly only want up to 100
        labels = scales::label_number(accuracy = 1)
      )
    } else {
      # unchanged from your original
      p1 <- p1 + scale_x_continuous(
        trans  = scales::log1p_trans(),
        breaks = nice_log1p_breaks(ridge_df$value),
        labels = scales::label_scientific(digits = 2)
      )
    }
  }
  
  p1
}

# ------------------------------------------------------------
# Categorical barplot: same as original style, but remove facet strip titles
# ------------------------------------------------------------
make_categorical_barplot <- function(df_feat, feat, feat_pretty) {
  df_plot <- df_feat %>%
    mutate(
      cohort_db = factor(paste0(cohort,"_",diabetes01),
                         levels = c("BPRHS_0","BPRHS_1","PROSPECT_0","PROSPECT_1"))
    ) %>%
    pivot_longer(c(cohort, cohort_db), names_to="comparison_type", values_to="group") %>%
    drop_na() %>%
    mutate(
      group = fct_recode(group,
                         "BPRHS_Non-diabetes"     = "BPRHS_0",
                         "BPRHS_Diabetes"         = "BPRHS_1",
                         "PROSPECT_Non-diabetes"  = "PROSPECT_0",
                         "PROSPECT_Diabetes"      = "PROSPECT_1")
    )
  
  ggplot(df_plot, aes(x = group, fill = .data[[feat]])) +
    geom_bar(position = "fill") +
    scale_y_continuous(labels = scales::percent) +
    facet_wrap(~comparison_type, scales="free_x") +
    labs(x="Group", y="Proportion", fill=feat_pretty, title=feat_pretty) +
    theme_minimal(base_size = 12) +
    theme(
      axis.text.x = element_text(angle=45, hjust=1),
      strip.text  = element_blank()
    )
}

# ------------------------------------------------------------
# Load + preprocess data
# ------------------------------------------------------------
if (!dir.exists(outpath)) dir.create(outpath, recursive = TRUE)

data0 <- read_merge_tracker(
  rds_path      = RDS1,
  tracker_path  = TRK,
  visit         = "v1",
  label_cohort  = TRUE,
  filter_cohort = "none"
) %>%
  mutate(
    diabetes01 = make_diabetes01(diabetes),
    # seconds -> HOURS
    hmz_sdoh_soc2a_time_s = as.numeric(hmz_sdoh_soc2a_time_s) / 3600
  )

# ------------------------------------------------------------
# Figure 1: Numeric ridges (order requested)
# ------------------------------------------------------------
numeric_features <- c(
  "hmz_ffq_aspt",
  "hmz_health_lab_ldl",
  "hmz_health_ant_avg_waist",
  "hmz_sdoh_soc2a_time_s"
)

missing1 <- setdiff(numeric_features, colnames(data0))
if (length(missing1)) stop("Missing numeric features: ", paste(missing1, collapse=", "))

num_plots <- purrr::map(numeric_features, function(feat) {
  df_feat <- data0 %>%
    select(cohort, diabetes01, all_of(feat)) %>%
    filter(!is.na(.data[[feat]]))
  make_ridge_plot(df_feat, feat, pretty_name(feat))
})

fig1 <- ggpubr::ggarrange(
  plotlist = num_plots,
  ncol = 2, nrow = 2,
  labels = c("A","B","C","D")
)

ggsave(file.path(outpath, "figure1_numeric_ridges_4panel.pdf"),
       fig1, width = 14, height = 10)

# ------------------------------------------------------------
# Figure 2: SDOH panels in requested order
# ------------------------------------------------------------
feat_act  <- "hmz_sdoh_soc_activities"
feat_educ <- "hmz_sdoh_hc_educ"
feat_pob  <- "hmz_sdoh_mh_pob"

missing2 <- setdiff(c(feat_act, feat_educ, feat_pob), colnames(data0))
if (length(missing2)) stop("Missing SDOH features: ", paste(missing2, collapse=", "))

# A: Number of Activities (ridge)
df_act <- data0 %>%
  select(cohort, diabetes01, all_of(feat_act)) %>%
  filter(!is.na(.data[[feat_act]]))
p_act <- make_ridge_plot(df_act, feat_act, pretty_name(feat_act))

# B: Highest Education Degree (categorical)
df_educ <- data0 %>%
  select(cohort, diabetes01, all_of(feat_educ)) %>%
  filter(!is.na(.data[[feat_educ]]))
p_educ <- make_categorical_barplot(df_educ, feat_educ, pretty_name(feat_educ))

# C: Place of Birth (categorical)
df_pob <- data0 %>%
  select(cohort, diabetes01, all_of(feat_pob)) %>%
  filter(!is.na(.data[[feat_pob]]))
p_pob <- make_categorical_barplot(df_pob, feat_pob, pretty_name(feat_pob))

fig2 <- ggpubr::ggarrange(
  plotlist = list(p_act, p_educ, p_pob),
  ncol = 1, nrow = 3,
  labels = c("A","B","C")
)

ggsave(file.path(outpath, "figure2_sdoh_panels_23feb26.pdf"),
       fig2, width = 12, height = 16)

message("Saved figures to: ", outpath)
