library(openxlsx)
library(tidyverse)
library(data.table)
library(optparse)

# How to run this script
# Rscript 00_generate_harmonize_ffq_clean.R \
#--manifest /cluster/tufts/patralab/rbator01/aiml_ordovas_project/data/ffq_data_manifest.xlsx \
#--output_dir /cluster/tufts/patralab/rbator01/aiml_ordovas_project/data/hmz_output/

#/cluster/tufts/biocontainers/tools/r-scrnaseq/4.4.0/bin/Rscript --no-save 00_generate_harmonize_ffq_clean.R --manifest /cluster/tufts/patralab/rbator01/aiml_ordovas_project/data/ffq_data_manifest.xlsx --output_dir /cluster/tufts/patralab/rbator01/aiml_ordovas_project/data/hmz_output/
  
  
option_list <- list(
  make_option(c("--manifest"), type = "character", help = "Manifest File"),
  make_option(c("--output_dir"), type = "character", help = "Output Directory")
)

opt_parser <- OptionParser(option_list = option_list)
opt <- parse_args(opt_parser)

if (is.null(opt$manifest) || is.null(opt$output_dir)) {
  print_help(opt_parser)
  stop("Error: You must provide both --manifest and --output_dir", call. = FALSE)
}

manifest <- opt$manifest
output_dir <- opt$output_dir

print(opt$manifest)
print(opt$output_dir)

ffq_perday_hmz <- function(manifest, output_dir, col, source, visit_name, cohort){
  
  manifest = read.xlsx(manifest)
  manifest_kv = setNames(manifest$name, manifest$type)
  
  if(cohort == "PROSPECT"){
    
    pr_cols_to_rm=c("batch","invalid","SUB_NAME","Sub_id")
    
    data_perday_perfood =  read.csv(manifest_kv[source]) %>% 
      select(-all_of(pr_cols_to_rm))
    
    unique(data_perday_perfood$visit)
    
    data_perfood_df = data_perday_perfood %>%
      filter(visit == gsub("^v","",visit_name)) %>%
      group_by(studyid) %>%
      summarise(across(where(is.numeric), ~ sum(.x, na.rm = TRUE))) 
    
  }else{
    data_perfood_df = read.xlsx(manifest_kv[source]) 
  }
  
  # make all lower case
  colnames(data_perfood_df) = tolower(colnames(data_perfood_df))
  
  metadata = read.xlsx(manifest_kv["metadata"]) %>%
    select(all_of(c(col, "variable.name"))) %>%
    filter(!is.na(get(col)) & !is.na(variable.name)) 
  
  cols_to_select = unique(intersect(metadata[[col]], colnames(data_perfood_df)))
  
  metadata = metadata %>%
    filter(get(col) %in% cols_to_select)
  
  data_perfood_df = data_perfood_df %>%
    select(all_of(c("studyid",cols_to_select))) %>%
    rename_at(vars(metadata[[col]]), ~ metadata$variable.name) %>%
    mutate(cohort = cohort)%>%
    mutate(visit=visit_name)
  
  
  outfile = paste0(output_dir,source,"_",visit_name,"_hmz_23jul25.csv")
  
  fwrite(data_perfood_df, outfile)
  
  return(data_perfood_df)
  
}

manifest="/cluster/tufts/patralab/rbator01/aiml_ordovas_project/data/ffq_data_manifest.xlsx"
output_dir="/cluster/tufts/patralab/rbator01/aiml_ordovas_project/data/hmz_output/"

if (!dir.exists(output_dir)) {
  dir.create(output_dir)
}

print("harmonizing BPRHS FFQ v1")
b1 = ffq_perday_hmz(manifest = manifest,
                    output_dir = output_dir,
                    col= "source.variable.bprhs.v1" ,
                    source="bprhs_v1_ffq",
                    visit_name="v1",
                    cohort="BPRHS")

dim(b1)
print("harmonizing BPRHS FFQ v2")
b2 = ffq_perday_hmz(manifest = manifest,
                    output_dir = output_dir,
                    col="source.variable.bprhs.v2" ,
                    source="bprhs_v2_ffq",
                    visit_name="v2",
                    cohort="BPRHS")

dim(b2)
print("harmonizing BPRHS FFQ v3")
b3 = ffq_perday_hmz(manifest = manifest,
                    output_dir = output_dir,
                    col="source.variable.bprhs.v3", 
                    source="bprhs_v3_ffq",
                    visit_name="v3",
                    cohort="BPRHS")

dim(b3)
print("harmonizing BPRHS FFQ v4")
b4 = ffq_perday_hmz(manifest = manifest,
                    output_dir = output_dir,
                    col="sourcevariable.bprhs.v4", 
                    source="bprhs_v4_ffq",
                    visit_name="v4",
                    cohort="BPRHS")

dim(b4)
print("harmonizing PROSPECT v1")
p1 = ffq_perday_hmz(manifest = manifest,
                    output_dir = output_dir,
                    col="sourcevariable.prospect",
                    source="prospect_ffq",
                    visit_name="v1",
                    cohort="PROSPECT")

dim(p1)
print("harmonizing PROSPECT v2")
p2 = ffq_perday_hmz(manifest = manifest,
                    output_dir = output_dir,
                    col="sourcevariable.prospect",
                    source="prospect_ffq",
                    visit_name="v2",
                    cohort="PROSPECT")

dim(p2)

common_cols = Reduce(intersect, list(colnames(b1),
                                     colnames(b2),
                                     colnames(b3),
                                     colnames(b4),
                                     colnames(p1),
                                     colnames(p2)))

df = rbind( b1 %>%
              select(all_of(common_cols)),
            b2 %>%
              select(all_of(common_cols)),
            b3 %>%
              select(all_of(common_cols)),
            b4 %>%
              select(all_of(common_cols)),
            p1 %>%
              select(all_of(common_cols)),
            p2 %>%
              select(all_of(common_cols)))

dim(df)
print(paste0("writing combined harmonization file to ",output_dir,"harmonize_bpr_prospect_ffq_23jul25.csv"))
fwrite(df, paste0(output_dir,"harmonize_bpr_prospect_ffq_23jul25.csv"))
