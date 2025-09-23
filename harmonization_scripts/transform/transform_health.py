

def transform_health(config):

    import pandas as pd
    import numpy as np
 


    #------------------------------------------------------------------------------------------------
    # Loading the data: Spanish
    # -----------------------------------------------------------------------------------------------

    from harmonization_scripts.load.loader_health import load_health_spanish_data

    data = load_health_spanish_data(config)

    df_hmz_health_bprhs_0 = data['bprhs_0']
    df_hmz_health_bprhs_2 = data['bprhs_2']
    df_hmz_health_bprhs_5 = data['bprhs_5']
    df_hmz_health_bprhs_8 = data['bprhs_8']
    df_hmz_health_prospect = data['prospect']

   
    def add_visit_cohort_suffix(df, visit_code, cohort_name):
        df['visit'] = visit_code
        df['cohort'] = cohort_name
        return df

    df_hmz_health_bprhs_0 = add_visit_cohort_suffix(df_hmz_health_bprhs_0, "v1", "BPRHS")
    df_hmz_health_bprhs_2 = add_visit_cohort_suffix(df_hmz_health_bprhs_2, "v2", "BPRHS")
    df_hmz_health_bprhs_5 = add_visit_cohort_suffix(df_hmz_health_bprhs_5, "v3", "BPRHS")
    df_hmz_health_bprhs_8 = add_visit_cohort_suffix(df_hmz_health_bprhs_8, "v4", "BPRHS")
    df_hmz_health_prospect = add_visit_cohort_suffix(df_hmz_health_prospect, "v1", "PROSPECT")



    #------------------------------------------------------------------------------------------------
    # Lab 
    # -----------------------------------------------------------------------------------------------
    # blood
    # --------------------------------------
    # BPRHS
    # --------------------------------------

    df_hmz_health_bprhs_8['bld_8yr'] = df_hmz_health_bprhs_8['bld_8yr'].apply(
        lambda x: int(x.strip()) if isinstance(x, str) and x.strip().isdigit() else x)

    # Recoding 9 → NaN
    df_hmz_health_bprhs_8['bld_8yr'] = df_hmz_health_bprhs_8['bld_8yr'].replace({9.0: np.nan, 9: np.nan})

    # Renaming
    df_hmz_health_bprhs_8.rename(columns={'bld_8yr': 'hmz_lab_bld_bprhs_8'}, inplace=True)
    print("Renaming complete.")

    # Saving
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)



    # --------------------------------------
    # PROSPECT
    # --------------------------------------
    # Recoding and renaming 
    df_hmz_health_prospect['bld2'] = df_hmz_health_prospect['bld2'].replace({96: np.nan, 97: np.nan, 98: np.nan})
    df_hmz_health_prospect.rename(columns={'bld2': 'hmz_lab_bld_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)



    # blood pressure
    # --------------------------------------
    # BPRHS
    # --------------------------------------
    base_variables = ["sysbp", "diasbp"]

    bprhs_datasets = {
        "Baseline": (df_hmz_health_bprhs_0, ""),
        "2-Year": (df_hmz_health_bprhs_2, "_2yr"),
        "5-Year": (df_hmz_health_bprhs_5, "_5yr"),
        "8-Year": (df_hmz_health_bprhs_8, "_8yr")
    }

    # Numeric conversion
    for name, (df, suffix) in bprhs_datasets.items():
        for var in base_variables:
            variable_name = var + suffix
            if variable_name in df.columns:
                df[variable_name] = df[variable_name].apply(
                    lambda x: int(x.strip()) if isinstance(x, str) and x.strip().isdigit() else x
                )

    # Renaming
    df_hmz_health_bprhs_0.rename(columns={'sysbp': 'hmz_ant_bp_sys_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'sysbp_2yr': 'hmz_ant_bp_sys_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_5.rename(columns={'sysbp_5yr': 'hmz_ant_bp_sys_bprhs_5'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'sysbp_8yr': 'hmz_ant_bp_sys_bprhs_8'}, inplace=True)

    df_hmz_health_bprhs_0.rename(columns={'diasbp': 'hmz_ant_bp_dias_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'diasbp_2yr': 'hmz_ant_bp_dias_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_5.rename(columns={'diasbp_5yr': 'hmz_ant_bp_dias_bprhs_5'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'diasbp_8yr': 'hmz_ant_bp_dias_bprhs_8'}, inplace=True)

    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)



    # --------------------------------------
    # PROSPECT
    # --------------------------------------
    # Renaming 
    df_hmz_health_prospect.rename(columns={'bpsys_avg': 'hmz_ant_bp_sys_prospect','bpdias_avg': 'hmz_ant_bp_dias_prospect' }, inplace=True)

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)






    # weight
    # --------------------------------------
    # BPRHS
    # --------------------------------------

    var = "wt_kg"

    bprhs_datasets = {
        "Baseline": (df_hmz_health_bprhs_0, ""),
        "2-Year": (df_hmz_health_bprhs_2, "_2yr"),
        "5-Year": (df_hmz_health_bprhs_5, "_5yr"),
        "8-Year": (df_hmz_health_bprhs_8, "_8yr")
    }

    # Converting strings to integers 
    for _, (df, suffix) in bprhs_datasets.items():
        variable_name = var + suffix
        if variable_name in df.columns:
            df[variable_name] = df[variable_name].apply(
                lambda x: int(x.strip()) if isinstance(x, str) and x.strip().isdigit() else x
            )

    # Converting kg to lbs
    kg_to_lbs = 2.20462
    for _, (df, suffix) in bprhs_datasets.items():
        variable_name = var + suffix
        if variable_name in df.columns:
            df[variable_name] *= kg_to_lbs

    # Renaming
    df_hmz_health_bprhs_0.rename(columns={'wt_kg':     'hmz_ant_wt_avg_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'wt_kg_2yr': 'hmz_ant_wt_avg_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_5.rename(columns={'wt_kg_5yr': 'hmz_ant_wt_avg_bprhs_5'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'wt_kg_8yr': 'hmz_ant_wt_avg_bprhs_8'}, inplace=True)

    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)




    # --------------------------------------
    # PROSPECT
    # --------------------------------------
    # Renaming
    df_hmz_health_prospect.rename(columns={'wt_avg': 'hmz_ant_wt_avg_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)





    # bmi
    # --------------------------------------
    # BPRHS
    # --------------------------------------


    # Renaming
    df_hmz_health_bprhs_0.rename(columns={'bmi': 'hmz_ant_bmi_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'bmi_2yr': 'hmz_ant_bmi_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_5.rename(columns={'bmi_5yr': 'hmz_ant_bmi_bprhs_5'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'bmi_8yr': 'hmz_ant_bmi_bprhs_8'}, inplace=True)


    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)




    # --------------------------------------
    # PROSPECT
    # --------------------------------------

    # Renaming 
    df_hmz_health_prospect.rename(columns={'bmi': 'hmz_ant_bmi_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)






    # hip
    # --------------------------------------
    # BPRHS
    # --------------------------------------
    bprhs_datasets = {
        "Baseline": (df_hmz_health_bprhs_0, ""),
        "2-Year": (df_hmz_health_bprhs_2, "_2yr")
    }

    # Conversion factor: 1 cm = 0.393701 inches
    # Some values may be in inches, so we assume that if value is below 50, it is already in inches
    cm_to_inch = 0.393701

    # Looping through each dataset to convert hip variables
    for name, (df, suffix) in bprhs_datasets.items():
        variable_name = "hip" + suffix  # Variable name in cm

        if variable_name in df.columns:
            mean_value = df[variable_name].mean()
            if mean_value > 50:
                df[variable_name] = df[variable_name] * cm_to_inch
                print(f"Converted {variable_name} from cm to inches in {name} dataset.")
            else:
                print(f"{variable_name} in {name} dataset seems already converted to inches. Skipping conversion.")
        else:
            print(f"{variable_name} not found in {name} dataset.")


    # Renaming
    df_hmz_health_bprhs_0.rename(columns={'hip': 'hmz_ant_hip_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'hip_2yr': 'hmz_ant_hip_bprhs_2'}, inplace=True)

    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)




    # --------------------------------------
    # PROSPECT
    # --------------------------------------
    # Renaming
    df_hmz_health_prospect.rename(columns={'hc_avg': 'hmz_ant_hip_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)





    # cholesterol
    # --------------------------------------
    # BPRHS
    # --------------------------------------

    # Renaming
    df_hmz_health_bprhs_0.rename(columns={'chol': 'hmz_lab_chol_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'chol_2yr': 'hmz_lab_chol_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_5.rename(columns={'chol_5yr': 'hmz_lab_chol_bprhs_5'}, inplace=True)

    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)




    # --------------------------------------
    # PROSPECT
    # --------------------------------------
    # Renaming
    df_hmz_health_prospect.rename(columns={'lab1': 'hmz_lab_chol_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)





    # Ldl
    # --------------------------------------
    # BPRHS
    # --------------------------------------
    # Renaming
    df_hmz_health_bprhs_0.rename(columns={'ldl':      'hmz_lab_ldl_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'ldl_2yr': 'hmz_lab_ldl_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_5.rename(columns={'ldl_5yr': 'hmz_lab_ldl_bprhs_5'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'ldl_8yr': 'hmz_lab_ldl_bprhs_8'}, inplace=True)


    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)




    # --------------------------------------
    # PROSPECT
    # --------------------------------------
    # Renaming 
    df_hmz_health_prospect.rename(columns={'lab2': 'hmz_lab_ldl_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)



    # hdl
    # --------------------------------------
    # BPRHS
    # --------------------------------------
    # Renaming
    df_hmz_health_bprhs_0.rename(columns={'hdl':     'hmz_lab_hdl_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'hdl_2yr': 'hmz_lab_hdl_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_5.rename(columns={'hdl_5yr': 'hmz_lab_hdl_bprhs_5'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'hdl_8yr': 'hmz_lab_hdl_bprhs_8'}, inplace=True)

    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)


    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)




    # --------------------------------------
    # PROSPECT
    # --------------------------------------
    # Renaming 
    df_hmz_health_prospect.rename(columns={'lab3': 'hmz_lab_hdl_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)





    # triglyceride
    # --------------------------------------
    # BPRHS
    # --------------------------------------

    # Renaming
    df_hmz_health_bprhs_0.rename(columns={'trig': 'hmz_lab_trig_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'trig_2yr': 'hmz_lab_trig_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_5.rename(columns={'trig_5yr': 'hmz_lab_trig_bprhs_5'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'trig_8yr': 'hmz_lab_trig_bprhs_8'}, inplace=True)


    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)




    # --------------------------------------
    # PROSPECT
    # --------------------------------------
    # Renaming 
    df_hmz_health_prospect.rename(columns={'lab4': 'hmz_lab_trig_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)




    # --------------------------------------
    # BPRHS
    # --------------------------------------
    # Renaming
    df_hmz_health_bprhs_0.rename(columns={'gluc': 'hmz_lab_gluc_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'gluc_2yr': 'hmz_lab_gluc_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_5.rename(columns={'gluc_5yr': 'hmz_lab_gluc_bprhs_5'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'gluc_8yr': 'hmz_lab_gluc_bprhs_8'}, inplace=True)

    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)


    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)





    # --------------------------------------
    # PROSPECT
    # --------------------------------------

    # Renaming 
    df_hmz_health_prospect.rename(columns={'lab5': 'hmz_lab_gluc_prospect'}, inplace=True)
    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)





    # Glucose
    # a1c
    # --------------------------------------
    # BPRHS
    # --------------------------------------

    # Renaming
    df_hmz_health_bprhs_0.rename(columns={'glyhgb': 'hmz_lab_a1c_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'glyhgb_2yr': 'hmz_lab_a1c_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_5.rename(columns={'glyhgb_5yr': 'hmz_lab_a1c_bprhs_5'}, inplace=True)

    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)





    # --------------------------------------
    # PROSPECT
    # --------------------------------------

    # Renaming 
    df_hmz_health_prospect.rename(columns={'lab6': 'hmz_lab_a1c_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)






    # bun/creatinine ratio

    # --------------------------------------
    # BPRHS
    # --------------------------------------
    # Transformation: creating the ratio variable
    df_hmz_health_bprhs_0['hmz_lab_bun_creat_bprhs_0'] = df_hmz_health_bprhs_0['bun'] / df_hmz_health_bprhs_0['creat']
    df_hmz_health_bprhs_2['hmz_lab_bun_creat_bprhs_2'] = df_hmz_health_bprhs_2['bun_2yr'] / df_hmz_health_bprhs_2['creat_2yr']
    df_hmz_health_bprhs_5['hmz_lab_bun_creat_bprhs_5'] = df_hmz_health_bprhs_5['bun_5yr'] / df_hmz_health_bprhs_5['creat_5yr']

    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)



    # --------------------------------------
    # PROSPECT
    # --------------------------------------
    # Renaming 
    df_hmz_health_prospect.rename(columns={'lab19': 'hmz_lab_bun_creat_prospect'}, inplace=True)
    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)





    # serum blood urea nitrogen
    # --------------------------------------
    # BPRHS
    # --------------------------------------
    # Renaming
    df_hmz_health_bprhs_0.rename(columns={'bun': 'hmz_lab_bun_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'bun_2yr': 'hmz_lab_bun_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_5.rename(columns={'bun_5yr': 'hmz_lab_bun_bprhs_5'}, inplace=True)

    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)




    # --------------------------------------
    # PROSPECT
    # --------------------------------------
    # Renaming 
    df_hmz_health_prospect.rename(columns={'lab17': 'hmz_lab_bun_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)





    # creatinine
    # --------------------------------------
    # BPRHS
    # --------------------------------------
    # Renaming
    df_hmz_health_bprhs_0.rename(columns={'creat': 'hmz_lab_creat_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'creat_2yr': 'hmz_lab_creat_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_5.rename(columns={'creat_5yr': 'hmz_lab_creat_bprhs_5'}, inplace=True)

    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)





    # --------------------------------------
    # PROSPECT
    # --------------------------------------
    # Renaming
    df_hmz_health_prospect.rename(columns={'lab18': 'hmz_lab_creat_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)






    # Albumin
    # --------------------------------------
    # BPRHS
    # --------------------------------------
    # Renaming
    df_hmz_health_bprhs_0.rename(columns={'alb': 'hmz_lab_alb_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'alb_2yr': 'hmz_lab_alb_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_5.rename(columns={'alb_5yr': 'hmz_lab_alb_bprhs_5'}, inplace=True)


    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)




    # --------------------------------------
    # PROSPECT
    # --------------------------------------

    # Renaming
    df_hmz_health_prospect.rename(columns={'lab28': 'hmz_lab_alb_prospect'}, inplace=True)
    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)





    # chol/hdl

    # --------------------------------------
    # BPRHS
    # --------------------------------------
    # Computing the ratio since this ratio is not captured in a variable in bprhs

    base_variables = ["hmz_lab_chol_bprhs", "hmz_lab_hdl_bprhs" ]

    # Dictionary with datasets and corresponding suffixes
    bprhs_datasets = {
        "Baseline": (df_hmz_health_bprhs_0, "_0"),
        "2-Year": (df_hmz_health_bprhs_2, "_2"),
        "5-Year": (df_hmz_health_bprhs_5, "_5"),
        "8-Year": (df_hmz_health_bprhs_8, "_8")
    }


    # Name of the new variable
    ratio_variable_chol_ldl = "hmz_lab_chol_hdl_bprhs"

    for name, (df, suffix) in bprhs_datasets.items():
        chol_variable = "hmz_lab_chol_bprhs" + suffix  # Cholesterol variable name
        hdl_variable = "hmz_lab_hdl_bprhs" + suffix    # HDL variable name
        ratio_variable = ratio_variable_chol_ldl + suffix  # Ratio variable name

        if chol_variable in df.columns and hdl_variable in df.columns:
            # Compute the ratio and handle division by zero or missing values
            df[ratio_variable] = df[chol_variable] / df[hdl_variable]
            print(f"Computed {ratio_variable} in {name} dataset.")
        else:
            print(f"Cannot compute {ratio_variable}: Required variables not found in {name} dataset.")



    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)





    # --------------------------------------
    # PROSPECT
    # --------------------------------------
    # Renaming
    df_hmz_health_prospect.rename(columns={'lab37': 'hmz_lab_chol_hdl_prospect'}, inplace=True)
    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)





    # LDL/HDL
    # --------------------------------------
    # BPRHS
    # --------------------------------------

    base_variables = ["hmz_lab_ldl_bprhs", "hmz_lab_hdl_bprhs" ]

    bprhs_datasets = {
        "Baseline": (df_hmz_health_bprhs_0, "_0"),
        "2-Year": (df_hmz_health_bprhs_2, "_2"),
        "5-Year": (df_hmz_health_bprhs_5, "_5"),
        "8-Year": (df_hmz_health_bprhs_8, "_8")}


    ratio_variable_ldl_hdl = "hmz_lab_ldl_hdl_bprhs"

    for name, (df, suffix) in bprhs_datasets.items():
        ldl_variable = "hmz_lab_ldl_bprhs" + suffix  # Cholesterol variable name
        hdl_variable = "hmz_lab_hdl_bprhs" + suffix    # HDL variable name
        ratio_variable = ratio_variable_ldl_hdl + suffix  # Ratio variable name

        if ldl_variable in df.columns and hdl_variable in df.columns:
            # Compute the ratio and handle division by zero or missing values
            df[ratio_variable] = df[ldl_variable] / df[hdl_variable]
            print(f"Computed {ratio_variable} in {name} dataset.")
        else:
            print(f"Cannot compute {ratio_variable}: Required variables not found in {name} dataset.")


    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)




    # --------------------------------------
    # PROSPECT
    # --------------------------------------
    # Renaming
    df_hmz_health_prospect.rename(columns={'lab38': 'hmz_lab_ldl_hdl_prospect'}, inplace=True)
    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)





    # insulin
    # --------------------------------------
    # BPRHS
    # --------------------------------------

    # Renaming
    df_hmz_health_bprhs_0.rename(columns={'insulin': 'hmz_lab_insulin_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'insulin_2yr': 'hmz_lab_insulin_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_5.rename(columns={'insulin_5yr': 'hmz_lab_insulin_bprhs_5'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'insulin_8yr': 'hmz_lab_insulin_bprhs_8'}, inplace=True)

    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)



    # --------------------------------------
    # PROSPECT
    # --------------------------------------
    # Renaming
    df_hmz_health_prospect.rename(columns={'lab12': 'hmz_lab_insulin_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)






    # crp
    # --------------------------------------
    # BPRHS
    # --------------------------------------

    # Renaming
    df_hmz_health_bprhs_0.rename(columns={'crp':    'hmz_lab_crp_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'crp_2yr': 'hmz_lab_crp_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_5.rename(columns={'crp_5yr': 'hmz_lab_crp_bprhs_5'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'crp_8yr': 'hmz_lab_crp_bprhs_8'}, inplace=True)


    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)


    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)


    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)




    # --------------------------------------
    # PROSPECT
    # --------------------------------------

    # Converting CRP-High Sensitivity from mg/dL to mg/L
    df_hmz_health_prospect["lab14"] = df_hmz_health_prospect["lab14"] * 10

    # Renaming
    df_hmz_health_prospect.rename(columns={'lab14': 'hmz_lab_crp_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)


    # platelet
    # --------------------------------------
    # BPRHS
    # --------------------------------------
    # Renaming
    df_hmz_health_bprhs_0.rename(columns={'platcount_adj':    'hmz_lab_platelet_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'platcount_adj_2yr': 'hmz_lab_platelet_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_5.rename(columns={'platcount_adj_5yr': 'hmz_lab_platelet_bprhs_5'}, inplace=True)

    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)


    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)


    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)




    # --------------------------------------
    # PROSPECT
    # --------------------------------------

    # Renaming
    df_hmz_health_prospect.rename(columns={'lab11': 'hmz_lab_platelet_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)



    #------------------------------------------------------------------------------------------------
    # Anthropometric measurements
    # -----------------------------------------------------------------------------------------------

    #pounds

    # --------------------------------------
    # BPRHS
    # --------------------------------------

    # Dictionary with datasets and corresponding suffixes
    bprhs_datasets = {
        "Baseline": (df_hmz_health_bprhs_0, ""),
        "2-Year": (df_hmz_health_bprhs_2, "_2yr"),
        "5-Year": (df_hmz_health_bprhs_5, "_5yr"),
        "8-Year": (df_hmz_health_bprhs_8, "_8yr")
    }

    # Variable 
    var = "ant2a"

    # Looping through each dataset and stripping whitespace from string values 
    for name, (df, suffix) in bprhs_datasets.items():
        variable_name = var + suffix
        if variable_name in df.columns:
            if df[variable_name].dtype == object:
                df[variable_name] = df[variable_name].astype(str).str.strip()



    # Renaming
    df_hmz_health_bprhs_0.rename(columns={'ant2a':'hmz_ant_pounds_i_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'ant2a_2yr': 'hmz_ant_pounds_i_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_5.rename(columns={'ant2a_5yr': 'hmz_ant_pounds_i_bprhs_5'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'ant2a_8yr': 'hmz_ant_pounds_i_bprhs_8'}, inplace=True)



    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)




    # --------------------------------------
    # PROSPECT
    # --------------------------------------

    # renaming
    df_hmz_health_prospect.rename(columns={'ant3a': 'hmz_ant_pounds_i_prospect'}, inplace=True)
    # Saving 
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)





    # ant2b
    # --------------------------------------
    # BPRHS
    # --------------------------------------

    base_variables = ["ant2b"]

    # Dictionary with datasets and corresponding suffixes
    bprhs_datasets = {
        "Baseline": (df_hmz_health_bprhs_0, ""),
        "2-Year": (df_hmz_health_bprhs_2, "_2yr"),
        "5-Year": (df_hmz_health_bprhs_5, "_5yr"),
        "8-Year": (df_hmz_health_bprhs_8, "_8yr")
    }


    # Checking if the variables exist in all datasets and printing value counts for categories
    # Looping through each dataset and count categories for specified variables with appropriate suffix
    for name, (df, suffix) in bprhs_datasets.items():
        print(f"\nCategory counts for {name} dataset:")
        for var in base_variables:
            variable_name = var + suffix  # Add the suffix to the base variable name
            if variable_name in df.columns:
                # Ensure string values are stripped of extra spaces
                if df[variable_name].dtype == object:
                    df[variable_name] = df[variable_name].astype(str).str.strip()

                # Print category counts, including NaNs
                print(f"\n  {variable_name} category counts:")
                print(df[variable_name].value_counts(dropna=False).sort_index())  
            else:
                print(f"  Column '{variable_name}' not found in {name}")


    # recoding the variable in bprhs v3
    recode_map = {
        "Lost": 1, 
        "Subio (Gained)": 2, 
        "Bajo (Lost)": 1, 
        "Gained": 2,
        "No": np.nan, 
        "Si": np.nan,
        "No Sabe": np.nan
    }

    # Apply replacement
    df_hmz_health_bprhs_5["ant2b_5yr"] = df_hmz_health_bprhs_5["ant2b_5yr"].replace(recode_map)

    # Convert any remaining strings to NaN
    df_hmz_health_bprhs_5["ant2b_5yr"] = pd.to_numeric(df_hmz_health_bprhs_5["ant2b_5yr"], errors='coerce')

    # check
    print(df_hmz_health_bprhs_5["ant2b_5yr"].value_counts(dropna=False).sort_index())


    # Renaming
    df_hmz_health_bprhs_0.rename(columns={'ant2b':'hmz_ant_pounds_ii_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'ant2b_2yr': 'hmz_ant_pounds_ii_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_5.rename(columns={'ant2b_5yr': 'hmz_ant_pounds_ii_bprhs_5'}, inplace=True)
    


    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)




    # --------------------------------------
    # PROSPECT
    # --------------------------------------
    # Recoding 96,97, 98 as nan
    df_hmz_health_prospect["ant3b"] = df_hmz_health_prospect["ant3b"].replace({96: np.nan, 97: np.nan, 98: np.nan})
    # renaming
    df_hmz_health_prospect.rename(columns={'ant3b': 'hmz_ant_pounds_ii_prospect'}, inplace=True)
    # Renaming
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)




    # pounds intentional 
    # --------------------------------------
    # BPRHS
    # --------------------------------------
    base_variable = ["ant3"]

    # Dictionary with datasets and corresponding suffixes
    bprhs_datasets = {
        "Baseline": (df_hmz_health_bprhs_0, ""),
        "2-Year": (df_hmz_health_bprhs_2, "_2yr"),
        "5-Year": (df_hmz_health_bprhs_5, "_5yr"),
        "8-Year": (df_hmz_health_bprhs_8, "_8yr") }



    # Checking if the variables exist in all datasets and printing value counts for categories
    # Looping through each dataset and count categories for specified variables with appropriate suffix
    for name, (df, suffix) in bprhs_datasets.items():
        print(f"\nCategory counts for {name} dataset:")
        for var in base_variable:
            variable_name = var + suffix  # Add the suffix to the base variable name
            if variable_name in df.columns:
                print(f"\n  {variable_name} category counts:")
                print(df[variable_name].value_counts(dropna=False).sort_index())  # Count categories, including NaN
            else:
                print(f"  Column '{variable_name}' not found in {name}")



        recode_map = {
            "No": 0, 
            "Si": 1, 
            "Yes": 1, 
            "No Sabe": np.nan }  



    df_hmz_health_bprhs_5["ant3_5yr"] = df_hmz_health_bprhs_5["ant3_5yr"].replace(recode_map)

    # Convert any remaining strings to NaN
    df_hmz_health_bprhs_5["ant3_5yr"] = pd.to_numeric(df_hmz_health_bprhs_5["ant3_5yr"], errors='coerce')

    # check
    print(df_hmz_health_bprhs_5["ant3_5yr"].value_counts(dropna=False).sort_index())

    # Recoding for the 8-Year dataset
    if "ant3_8yr" in df_hmz_health_bprhs_8.columns:
        print("\nRecoding for 8-Year dataset: ant3_8yr")
        print("Counts before recoding:")
        print(df_hmz_health_bprhs_8["ant3_8yr"].value_counts(dropna=False).sort_index())

        # Recode 98 to nan
        df_hmz_health_bprhs_8["ant3_8yr"] = df_hmz_health_bprhs_8["ant3_8yr"].replace({ 98: np.nan})
        print("Counts after recoding:")
        print(df_hmz_health_bprhs_8["ant3_8yr"].value_counts(dropna=False).sort_index())

    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)



    # Renaming
    df_hmz_health_bprhs_0.rename(columns={'ant3':'hmz_ant_pounds_iii_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'ant3_2yr': 'hmz_ant_pounds_iii_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_5.rename(columns={'ant3_5yr': 'hmz_ant_pounds_iii_bprhs_5'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'ant3_8yr': 'hmz_ant_pounds_iii_bprhs_8'}, inplace=True)

    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)





    # --------------------------------------
    # PROSPECT
    # --------------------------------------
    # recoding 98 to nan
    df_hmz_health_prospect["ant3c"] = df_hmz_health_prospect["ant3c"].replace({96: np.nan, 97: np.nan, 98: np.nan})

    # Renaming
    df_hmz_health_prospect.rename(columns={'ant3c': 'hmz_ant_pounds_iii_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)






    # height
    # --------------------------------------
    # BPRHS
    # --------------------------------------
    # Dictionary with datasets and corresponding suffixes
    bprhs_datasets = {
        "Baseline": (df_hmz_health_bprhs_0, ""),
        "2-Year": (df_hmz_health_bprhs_2, "_2yr"),
        "5-Year": (df_hmz_health_bprhs_5, "_5yr"),
        "8-Year": (df_hmz_health_bprhs_8, "_8yr")
    }

    # Conversion factor: 1 meter = 39.3701 inches
    meter_to_inch = 39.3701

    # Looping through each dataset to convert height variables
    for name, (df, suffix) in bprhs_datasets.items():
        variable_name = "ht_m" + suffix  # Variable name in meters
        # Convert the data in-place from meters to inches
        df[variable_name] *= meter_to_inch
        print(f"Converted {variable_name} from meters to inches in {name} dataset.")

    # Renaming
    df_hmz_health_bprhs_0.rename(columns={'ht_m': 'hmz_ant_ht_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'ht_m_2yr': 'hmz_ant_ht_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_5.rename(columns={'ht_m_5yr': 'hmz_ant_ht_bprhs_5'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'ht_m_8yr': 'hmz_ant_ht_bprhs_8'}, inplace=True)

    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)





    # --------------------------------------
    # PROSPECT
    # --------------------------------------
    # Renaming
    df_hmz_health_prospect.rename(columns={'ht_avg': 'hmz_ant_ht_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)





    # waist

    # --------------------------------------
    # BPRHS
    # --------------------------------------
    # Dictionary with datasets and corresponding suffixes
    bprhs_datasets = {
        "Baseline": (df_hmz_health_bprhs_0, ""),
        "5-Year": (df_hmz_health_bprhs_5, "_5yr"),
        "8-Year": (df_hmz_health_bprhs_8, "_8yr")
    }

    # Conversion factor: 1 cm = 0.393701 inches
    cm_to_inch = 0.393701

    # Looping through each dataset to convert waist variables
    for name, (df, suffix) in bprhs_datasets.items():
        variable_name = "waist" + suffix  # Variable name in cm
        # Convert the data in-place from cm to inches
        df[variable_name] *= cm_to_inch
        print(f"Converted {variable_name} from cm to inches in {name} dataset.")


    # Renaming columns
    df_hmz_health_bprhs_0.rename(columns={'waist': 'hmz_ant_avg_waist_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'waist_2yr': 'hmz_ant_avg_waist_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_5.rename(columns={'waist_5yr': 'hmz_ant_avg_waist_bprhs_5'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'waist_8yr': 'hmz_ant_avg_waist_bprhs_8'}, inplace=True)

    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)




    # --------------------------------------
    # PROSPECT
    # --------------------------------------
    # Renaming
    df_hmz_health_prospect.rename(columns={'wc_avg': 'hmz_ant_avg_waist_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)


    #------------------------------------------------------------------------------------------------
    # Medical Diagnosis
    # -----------------------------------------------------------------------------------------------
    # arthritis

    # --------------------------------------
    # BPRHS
    # --------------------------------------

    base_variables = ["med4", "med4x"]

    # Dictionary with datasets and corresponding suffixes
    bprhs_datasets = {
        "Baseline": (df_hmz_health_bprhs_0, ""),
        "2-Year": (df_hmz_health_bprhs_2, "_2yr"),
        "5-Year": (df_hmz_health_bprhs_5, "_5yr"),
        "8-Year": (df_hmz_health_bprhs_8, "_8yr")
    }

    # Value counts
    for name, (df, suffix) in bprhs_datasets.items():
        print(f"\n{name}:")  
        for var in base_variables:
            variable_name = var + suffix  
            if variable_name in df.columns:
                print(df[variable_name].value_counts())  
            else:
                print(f"Column '{variable_name}' not found")



    # Renaming
    df_hmz_health_bprhs_0.rename(columns={'med4': 'hmz_med_arthritis_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'med4x_2yr': 'hmz_med_arthritis_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_5.rename(columns={'med4x_5yr': 'hmz_med_arthritis_bprhs_5'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'med4_8yr': 'hmz_med_arthritis_bprhs_8'}, inplace=True)


    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)




    # --------------------------------------
    # PROSPECT
    # --------------------------------------


    df_hmz_health_prospect['med29'] = df_hmz_health_prospect['med29'].replace({96: np.nan,98: np.nan})

    # Renaming
    df_hmz_health_prospect.rename(columns={'med29': 'hmz_med_arthritis_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)





    # medication for arthritis
    # --------------------------------------
    # BPRHS
    # --------------------------------------
    # bprhs v1
    if "hmz_med_arthritis_bprhs_0" in df_hmz_health_bprhs_0.columns and "med4b" in df_hmz_health_bprhs_0.columns:
        df_hmz_health_bprhs_0["hmz_med_arthritis_bprhs_0"] = pd.to_numeric(df_hmz_health_bprhs_0["hmz_med_arthritis_bprhs_0"], errors="coerce")
        df_hmz_health_bprhs_0.loc[df_hmz_health_bprhs_0["hmz_med_arthritis_bprhs_0"].isna(), "med4b"] = np.nan
        df_hmz_health_bprhs_0.loc[df_hmz_health_bprhs_0["hmz_med_arthritis_bprhs_0"] == 0, "med4b"] = np.nan


    # bprhs v2
    if "hmz_med_arthritis_bprhs_2" in df_hmz_health_bprhs_2.columns and "med4b_2yr" in df_hmz_health_bprhs_2.columns:
        df_hmz_health_bprhs_2["hmz_med_arthritis_bprhs_2"] = pd.to_numeric(df_hmz_health_bprhs_2["hmz_med_arthritis_bprhs_2"], errors="coerce")
        df_hmz_health_bprhs_2.loc[df_hmz_health_bprhs_2["hmz_med_arthritis_bprhs_2"].isna(), "med4b_2yr"] = np.nan
        df_hmz_health_bprhs_2.loc[df_hmz_health_bprhs_2["hmz_med_arthritis_bprhs_2"] == 0, "med4b_2yr"] = np.nan


    # Renaming
    df_hmz_health_bprhs_0.rename(columns={'med4b': 'hmz_med_arthritis_medication_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'med4b_2yr': 'hmz_med_arthritis_medication_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'med4b_8yr': 'hmz_med_arthritis_medication_bprhs_8'}, inplace=True)



    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)





    # --------------------------------------
    # PROSPECT
    # --------------------------------------

    df_hmz_health_prospect['med29a'] = df_hmz_health_prospect['med29a'].replace({98: np.nan})

    # Renaming
    df_hmz_health_prospect.rename(columns={'med29a': 'hmz_med_arthritis_medication_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)




    # arthritis condition today

    # --------------------------------------
    # BPRHS
    # --------------------------------------

    # Apply transformation: if hmz_med_arthritis == 0 --> med4c is NaN; if hmz_med_arthritis == nan --> med4c is Nan
    # bprhs v1 (hmz_med_arthritis_bprhs_0, med4c)
    if "hmz_med_arthritis_bprhs_0" in df_hmz_health_bprhs_0.columns and "med4c" in df_hmz_health_bprhs_0.columns:
        df_hmz_health_bprhs_0["hmz_med_arthritis_bprhs_0"] = pd.to_numeric(df_hmz_health_bprhs_0["hmz_med_arthritis_bprhs_0"], errors="coerce")
        df_hmz_health_bprhs_0.loc[df_hmz_health_bprhs_0["hmz_med_arthritis_bprhs_0"].isna(), "med4c"] = np.nan
        df_hmz_health_bprhs_0.loc[df_hmz_health_bprhs_0["hmz_med_arthritis_bprhs_0"] == 0, 'med4c'] = np.nan

    # bprhs v2 (hmz_med_arthritis_bprhs_2, med4c_2yr)
    if "hmz_med_arthritis_bprhs_2" in df_hmz_health_bprhs_2.columns and "med4c_2yr" in df_hmz_health_bprhs_2.columns:
        df_hmz_health_bprhs_2["hmz_med_arthritis_bprhs_2"] = pd.to_numeric(df_hmz_health_bprhs_2["hmz_med_arthritis_bprhs_2"], errors="coerce")
        df_hmz_health_bprhs_2.loc[df_hmz_health_bprhs_2["hmz_med_arthritis_bprhs_2"].isna(), "med4c_2yr"] = np.nan
        df_hmz_health_bprhs_2.loc[df_hmz_health_bprhs_2["hmz_med_arthritis_bprhs_2"] == 0, "med4c_2yr"] = np.nan

    # bprhs v3
    if "hmz_med_arthritis_bprhs_5" in df_hmz_health_bprhs_5.columns and "med4c_5yr" in df_hmz_health_bprhs_5.columns:
        df_hmz_health_bprhs_5["hmz_med_arthritis_bprhs_5"] = pd.to_numeric(df_hmz_health_bprhs_5["hmz_med_arthritis_bprhs_5"], errors="coerce")
        df_hmz_health_bprhs_5.loc[df_hmz_health_bprhs_5["hmz_med_arthritis_bprhs_5"].isna(), "med4c_5yr"] = np.nan
        df_hmz_health_bprhs_5.loc[df_hmz_health_bprhs_5["hmz_med_arthritis_bprhs_5"] == 0, "med4c_5yr"] = np.nan


    # Renaming
    df_hmz_health_bprhs_0.rename(columns={'med4c': 'hmz_med_arthritis_today_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'med4c_2yr': 'hmz_med_arthritis_today_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_5.rename(columns={'med4c_5yr': 'hmz_med_arthritis_today_bprhs_5'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'med4c_8yr': 'hmz_med_arthritis_today_bprhs_8'}, inplace=True)


    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)




    # --------------------------------------
    # PROSPECT
    # --------------------------------------

    # recoding 96, 98 as nan
    df_hmz_health_prospect['med29d'] = df_hmz_health_prospect['med29d'].replace({96: np.nan, 98: np.nan})
    # Renaming
    df_hmz_health_prospect.rename(columns={'med29d': 'hmz_med_arthritis_today_prospect'}, inplace=True)
    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)




    # osteoporosis
    # --------------------------------------
    # BPRHS
    # --------------------------------------


    # Renaming
    df_hmz_health_bprhs_0.rename(columns={'med5': 'hmz_med_osteoporosis_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'med5x_2yr': 'hmz_med_osteoporosis_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_5.rename(columns={'med5x_5yr': 'hmz_med_osteoporosis_bprhs_5'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'med5_8yr': 'hmz_med_osteoporosis_bprhs_8'}, inplace=True)


    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)






    # --------------------------------------
    # PROSPECT
    # --------------------------------------

    df_hmz_health_prospect['med30'] = df_hmz_health_prospect['med30'].replace({97: np.nan,98: np.nan})

    # Renaming
    df_hmz_health_prospect.rename(columns={'med30': 'hmz_med_osteoporosis_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)





    # medication for osteoporosis
    # --------------------------------------
    # BPRHS
    # --------------------------------------

    # bprhs v1
    if "hmz_med_osteoporosis_bprhs_0" in df_hmz_health_bprhs_0.columns and "med5b" in df_hmz_health_bprhs_0.columns:
        df_hmz_health_bprhs_0["hmz_med_osteoporosis_bprhs_0"] = pd.to_numeric(df_hmz_health_bprhs_0["hmz_med_osteoporosis_bprhs_0"], errors="coerce")
        df_hmz_health_bprhs_0.loc[df_hmz_health_bprhs_0["hmz_med_osteoporosis_bprhs_0"].isna(), "med5b"] = np.nan
        df_hmz_health_bprhs_0.loc[df_hmz_health_bprhs_0["hmz_med_osteoporosis_bprhs_0"] == 0, "med5b"] = np.nan


    # bprhs v2 
    if "hmz_med_osteoporosis_bprhs_2" in df_hmz_health_bprhs_2.columns and "med5b_2yr" in df_hmz_health_bprhs_2.columns:
        df_hmz_health_bprhs_2["hmz_med_osteoporosis_bprhs_2"] = pd.to_numeric(df_hmz_health_bprhs_2["hmz_med_osteoporosis_bprhs_2"], errors="coerce")
        df_hmz_health_bprhs_2.loc[df_hmz_health_bprhs_2["hmz_med_osteoporosis_bprhs_2"].isna(), "med5b_2yr"] = np.nan
        df_hmz_health_bprhs_2.loc[df_hmz_health_bprhs_2["hmz_med_osteoporosis_bprhs_2"] == 0, "med5b_2yr"] = np.nan


    # Renaming
    df_hmz_health_bprhs_0.rename(columns={'med5b': 'hmz_med_osteoporosis_medication_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'med5b_2yr': 'hmz_med_osteoporosis_medication_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'med5b_8yr': 'hmz_med_osteoporosis_medication_bprhs_8'}, inplace=True)


    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)





    # --------------------------------------
    # PROSPECT
    # --------------------------------------

    # Recoding
    df_hmz_health_prospect['med30a'] = df_hmz_health_prospect['med30a'].replace({98: np.nan})

    # Renaming
    df_hmz_health_prospect.rename(columns={'med30a': 'hmz_med_osteoporosis_medication_prospect'}, inplace=True)

    print(df_hmz_health_prospect['hmz_med_osteoporosis_medication_prospect'].value_counts())

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)




    # osteoporosis condition today
    # --------------------------------------
    # BPRHS
    # --------------------------------------

    # transformation
    # Apply transformation: if hmz_med_osteoporosis == 0 --> med5c is NaN; if hmz_med_osteoporosis == nan --> med5c is Nan
    # bprhs v1 (hmz_med_osteoporosis_bprhs_0, med5c)
    if "hmz_med_osteoporosis_bprhs_0" in df_hmz_health_bprhs_0.columns and "med5c" in df_hmz_health_bprhs_0.columns:
        df_hmz_health_bprhs_0["hmz_med_osteoporosis_bprhs_0"] = pd.to_numeric(df_hmz_health_bprhs_0["hmz_med_osteoporosis_bprhs_0"], errors="coerce")
        df_hmz_health_bprhs_0.loc[df_hmz_health_bprhs_0["hmz_med_osteoporosis_bprhs_0"].isna(), "med5c"] = np.nan
        df_hmz_health_bprhs_0.loc[df_hmz_health_bprhs_0["hmz_med_osteoporosis_bprhs_0"] == 0, 'med5c'] = np.nan

    # bprhs v2 (hmz_med_osteoporosis_bprhs_2, med5c_2yr)
    if "hmz_med_osteoporosis_bprhs_2" in df_hmz_health_bprhs_2.columns and "med5c_2yr" in df_hmz_health_bprhs_2.columns:
        df_hmz_health_bprhs_2["hmz_med_osteoporosis_bprhs_2"] = pd.to_numeric(df_hmz_health_bprhs_2["hmz_med_osteoporosis_bprhs_2"], errors="coerce")
        df_hmz_health_bprhs_2.loc[df_hmz_health_bprhs_2["hmz_med_osteoporosis_bprhs_2"].isna(), "med5c_2yr"] = np.nan
        df_hmz_health_bprhs_2.loc[df_hmz_health_bprhs_2["hmz_med_osteoporosis_bprhs_2"] == 0, "med5c_2yr"] = np.nan

    # bprhs v3
    if "hmz_med_osteoporosis_bprhs_5" in df_hmz_health_bprhs_5.columns and "med5c_5yr" in df_hmz_health_bprhs_5.columns:
        df_hmz_health_bprhs_5["hmz_med_osteoporosis_bprhs_5"] = pd.to_numeric(df_hmz_health_bprhs_5["hmz_med_osteoporosis_bprhs_5"], errors="coerce")
        df_hmz_health_bprhs_5.loc[df_hmz_health_bprhs_5["hmz_med_osteoporosis_bprhs_5"].isna(), "med5c_5yr"] = np.nan
        df_hmz_health_bprhs_5.loc[df_hmz_health_bprhs_5["hmz_med_osteoporosis_bprhs_5"] == 0, "med5c_5yr"] = np.nan

    # Renaming
    df_hmz_health_bprhs_0.rename(columns={'med5c': 'hmz_med_osteoporosis_today_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'med5c_2yr': 'hmz_med_osteoporosis_today_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_5.rename(columns={'med5c_5yr': 'hmz_med_osteoporosis_today_bprhs_5'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'med5c_8yr': 'hmz_med_osteoporosis_today_bprhs_8'}, inplace=True)



    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)





    # --------------------------------------
    # PROSPECT
    # --------------------------------------


    # Recoding 96 as nan
    df_hmz_health_prospect['med30d'] = df_hmz_health_prospect['med30d'].replace({96: np.nan})

    # Renaming
    df_hmz_health_prospect.rename(columns={'med30d': 'hmz_med_osteoporosis_today_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)




    # respiratory

    # --------------------------------------
    # BPRHS
    # --------------------------------------


    # Renaming
    df_hmz_health_bprhs_0.rename(columns={'med9': 'hmz_med_respiratory_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'med9x_2yr': 'hmz_med_respiratory_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_5.rename(columns={'med9x_5yr': 'hmz_med_respiratory_bprhs_5'}, inplace=True)
    #df_hmz_health_bprhs_8.rename(columns={'med4_8yr': 'hmz_med_arthritis_bprhs_8'}, inplace=True)



    # creating a new variable for bprhs v4
    # Creating a variable about respiratory problems for bprhs_8
    respiratory_vars = ['med9_1_8yr', 'med9_2_8yr', 'med9_3_8yr', 'med9_4_8yr', 'med9_5_8yr']

    # Creating the new variable: 1 if any column has 1, else 0
    df_hmz_health_bprhs_8['med9_added_8yr'] = df_hmz_health_bprhs_8[respiratory_vars].max(axis=1)

    print(df_hmz_health_bprhs_8['med9_added_8yr'].value_counts())


    # Renaming variable
    df_hmz_health_bprhs_8.rename(columns={'med9_added_8yr': 'hmz_med_respiratory_bprhs_8'}, inplace=True)


    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)



    # --------------------------------------
    # PROSPECT
    # --------------------------------------


    df_hmz_health_prospect['med31'] = df_hmz_health_prospect['med31'].replace({97: np.nan,98: np.nan})
    df_hmz_health_prospect.rename(columns={'med31': 'hmz_med_respiratory_prospect'}, inplace=True)
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)



    # medication for respiratory

    # --------------------------------------
    # BPRHS
    # --------------------------------------
    # bprhs v1
    if "hmz_med_respiratory_bprhs_0" in df_hmz_health_bprhs_0.columns and "med9b" in df_hmz_health_bprhs_0.columns:
        df_hmz_health_bprhs_0["hmz_med_respiratory_bprhs_0"] = pd.to_numeric(df_hmz_health_bprhs_0["hmz_med_respiratory_bprhs_0"], errors="coerce")
        df_hmz_health_bprhs_0.loc[df_hmz_health_bprhs_0["hmz_med_respiratory_bprhs_0"].isna(), "med9b"] = np.nan
        df_hmz_health_bprhs_0.loc[df_hmz_health_bprhs_0["hmz_med_respiratory_bprhs_0"] == 0, "med9b"] = np.nan


    # bprs v2
    if "hmz_med_respiratory_bprhs_2" in df_hmz_health_bprhs_2.columns and "med9b_2yr" in df_hmz_health_bprhs_2.columns:
        df_hmz_health_bprhs_2["hmz_med_respiratory_bprhs_2"] = pd.to_numeric(df_hmz_health_bprhs_2["hmz_med_respiratory_bprhs_2"], errors="coerce")
        df_hmz_health_bprhs_2.loc[df_hmz_health_bprhs_2["hmz_med_respiratory_bprhs_2"].isna(), "med9b_2yr"] = np.nan
        df_hmz_health_bprhs_2.loc[df_hmz_health_bprhs_2["hmz_med_respiratory_bprhs_2"] == 0, "med9b_2yr"] = np.nan


    # Renaming
    df_hmz_health_bprhs_0.rename(columns={'med9b': 'hmz_med_respiratory_medication_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'med9b_2yr': 'hmz_med_respiratory_medication_bprhs_2'}, inplace=True)


    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)


    # creating a new variable for bprhs v4
    respiratory_vars = ['med9_1b_8yr', 'med9_2b_8yr', 'med9_3b_8yr', 'med9_4b_8yr', 'med9_5b_8yr']

    # Creating the new variable: 1 if any column has 1, else 0
    df_hmz_health_bprhs_8['med9_added_ii_8yr'] = df_hmz_health_bprhs_8[respiratory_vars].max(axis=1)


    # Renaming variable
    df_hmz_health_bprhs_8.rename(columns={'med9_added_ii_8yr': 'hmz_med_respiratory_medication_bprhs_8'}, inplace=True)



    # --------------------------------------
    # PROSPECT
    # --------------------------------------

    # Renaming
    df_hmz_health_prospect.rename(columns={'med31a': 'hmz_med_respiratory_medication_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)



    # respiratory condition today

    # --------------------------------------
    # BPRHS
    # --------------------------------------
    # transformation
    # Apply transformation: if hmz_med_respiratory == 0 --> med9c is NaN; if hmz_med_respiratory == nan --> med9c is Nan
    # bprhs v1 (hmz_med_respiratory_bprhs_0, med9c)
    if "hmz_med_respiratory_bprhs_0" in df_hmz_health_bprhs_0.columns and "med9c" in df_hmz_health_bprhs_0.columns:
        df_hmz_health_bprhs_0["hmz_med_respiratory_bprhs_0"] = pd.to_numeric(df_hmz_health_bprhs_0["hmz_med_respiratory_bprhs_0"], errors="coerce")
        df_hmz_health_bprhs_0.loc[df_hmz_health_bprhs_0["hmz_med_respiratory_bprhs_0"].isna(), "med9c"] = np.nan
        df_hmz_health_bprhs_0.loc[df_hmz_health_bprhs_0["hmz_med_respiratory_bprhs_0"] == 0, 'med9c'] = np.nan

    # bprhs v2 (hmz_med_respiratory_bprhs_2, med9c_2yr)
    if "hmz_med_respiratory_bprhs_2" in df_hmz_health_bprhs_2.columns and "med9c_2yr" in df_hmz_health_bprhs_2.columns:
        df_hmz_health_bprhs_2["hmz_med_respiratory_bprhs_2"] = pd.to_numeric(df_hmz_health_bprhs_2["hmz_med_respiratory_bprhs_2"], errors="coerce")
        df_hmz_health_bprhs_2.loc[df_hmz_health_bprhs_2["hmz_med_respiratory_bprhs_2"].isna(), "med9c_2yr"] = np.nan
        df_hmz_health_bprhs_2.loc[df_hmz_health_bprhs_2["hmz_med_respiratory_bprhs_2"] == 0, "med9c_2yr"] = np.nan

    # bprhs v3
    if "hmz_med_respiratory_bprhs_5" in df_hmz_health_bprhs_5.columns and "med9c_5yr" in df_hmz_health_bprhs_5.columns:
        df_hmz_health_bprhs_5["hmz_med_respiratory_bprhs_5"] = pd.to_numeric(df_hmz_health_bprhs_5["hmz_med_respiratory_bprhs_5"], errors="coerce")
        df_hmz_health_bprhs_5.loc[df_hmz_health_bprhs_5["hmz_med_respiratory_bprhs_5"].isna(), "med9c_5yr"] = np.nan
        df_hmz_health_bprhs_5.loc[df_hmz_health_bprhs_5["hmz_med_respiratory_bprhs_5"] == 0, "med9c_5yr"] = np.nan


    # Renaming
    df_hmz_health_bprhs_0.rename(columns={'med9c': 'hmz_med_respiratory_today_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'med9c_2yr': 'hmz_med_respiratory_today_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_5.rename(columns={'med9c_5yr': 'hmz_med_respiratory_today_bprhs_5'}, inplace=True)


    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)




    # transformation
    # Creating the variable for bprhs v4
    respiratory_vars = ['med9_1c_8yr', 'med9_2c_8yr', 'med9_3c_8yr', 'med9_4c_8yr', 'med9_5c_8yr']

    # logic: 1 if any column has 1, else 0
    df_hmz_health_bprhs_8['med9_added_iii_8yr'] = df_hmz_health_bprhs_8[respiratory_vars].max(axis=1)

    # Renaming 
    df_hmz_health_bprhs_8.rename(columns={'med9_added_iii_8yr': 'hmz_med_respiratory_today_bprhs_8'}, inplace=True)

    # Saving
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)




    # --------------------------------------
    # PROSPECT
    # --------------------------------------

    df_hmz_health_prospect['med31d'] = df_hmz_health_prospect['med31d'].replace({98: np.nan})

    # Renaming
    df_hmz_health_prospect.rename(columns={'med31d': 'hmz_med_respiratory_today_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)



    # type of respiratory problem

    # --------------------------------------
    # BPRHS
    # --------------------------------------
    base_variable = ["med9_1_8yr","med9_2_8yr", "med9_3_8yr", "med9_4_8yr", "med9_5_8yr" ]

    for var in base_variable:
        print(f"Value counts for {var}:")
        print(df_hmz_health_bprhs_8[var].value_counts(), "\n")



    # Renaming
    df_hmz_health_bprhs_8.rename(columns={'med9_1_8yr': 'hmz_med_respiratory_emphysema_bprhs_8', 
                                          'med9_2_8yr': 'hmz_med_respiratory_copd_bprhs_8',
                                          'med9_3_8yr': 'hmz_med_respiratory_asthma_bprhs_8',
                                          'med9_4_8yr': 'hmz_med_respiratory_chronic_bronchitis_bprhs_8',
                                          'med9_5_8yr': 'hmz_med_respiratory_other_bprhs_8' }, inplace=True)



    # Saving
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)




    # --------------------------------------
    # PROSPECT
    # --------------------------------------
    base_variable = ["med31e___1","med31e___2", "med31e___3", "med31e___4", "med31e___5" ]

    for var in base_variable:
        print(f"Value counts for {var}:")
        print(df_hmz_health_prospect[var].value_counts(), "\n")


    # Renaming
    df_hmz_health_prospect.rename(columns={'med31e___1': 'hmz_med_respiratory_emphysema_prospect',
                                           'med31e___2': 'hmz_med_respiratory_chronic_bronchitis_prospect',
                                           'med31e___3': 'hmz_med_respiratory_asthma_prospect',
                                           'med31e___4': 'hmz_med_respiratory_copd_prospect',
                                           'med31e___5': 'hmz_med_respiratory_other_prospect' }, inplace=True)

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)



    # diabetes
    # --------------------------------------
    # BPRHS
    # --------------------------------------
    base_variable = ["med1", "med1x"]

    # Renaming
    df_hmz_health_bprhs_0.rename(columns={'med1': 'hmz_med_1_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'med1x_2yr': 'hmz_med_1_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'med1_8yr': 'hmz_med_1_bprhs_8'}, inplace=True)

    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)




    # --------------------------------------
    # PROSPECT
    # --------------------------------------

    # 
    df_hmz_health_prospect['med1'] = df_hmz_health_prospect['med1'].replace({96: np.nan, 97: np.nan, 98: np.nan})

    # Renaming
    df_hmz_health_prospect.rename(columns={'med1': 'hmz_med_1_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)




    # diabetes medication

    # --------------------------------------
    # BPRHS
    # --------------------------------------
    # transformation
    # Apply transformation: if hmz_med_1 == 0 --> med1b is NaN; if hmz_med_1 == nan --> med1b is Nan
    # bprhs v1 (hmz_med_1_bprhs_0, med1b)
    if "hmz_med_1_bprhs_0" in df_hmz_health_bprhs_0.columns and "med1b" in df_hmz_health_bprhs_0.columns:
        df_hmz_health_bprhs_0["hmz_med_1_bprhs_0"] = pd.to_numeric(df_hmz_health_bprhs_0["hmz_med_1_bprhs_0"], errors="coerce")
        df_hmz_health_bprhs_0.loc[df_hmz_health_bprhs_0["hmz_med_1_bprhs_0"].isna(), "med1b"] = np.nan
        df_hmz_health_bprhs_0.loc[df_hmz_health_bprhs_0["hmz_med_1_bprhs_0"] == 0, 'med1b'] = np.nan

    # bprhs v2 (hmz_med_1_bprhs_2, med1b_2yr)
    if "hmz_med_1_bprhs_2" in df_hmz_health_bprhs_2.columns and "med1b_2yr" in df_hmz_health_bprhs_2.columns:
        df_hmz_health_bprhs_2["hmz_med_1_bprhs_2"] = pd.to_numeric(df_hmz_health_bprhs_2["hmz_med_1_bprhs_2"], errors="coerce")
        df_hmz_health_bprhs_2.loc[df_hmz_health_bprhs_2["hmz_med_1_bprhs_2"].isna(), "med1b_2yr"] = np.nan
        df_hmz_health_bprhs_2.loc[df_hmz_health_bprhs_2["hmz_med_1_bprhs_2"] == 0, "med1b_2yr"] = np.nan


    # Renaming
    df_hmz_health_bprhs_0.rename(columns={'med1b': 'hmz_med_1_medication_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'med1b_2yr': 'hmz_med_1_medication_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'med1b_8yr': 'hmz_med_1_medication_bprhs_8'}, inplace=True)


    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)



    # --------------------------------------
    # PROSPECT
    # --------------------------------------

    # Renaming
    df_hmz_health_prospect.rename(columns={'med1a': 'hmz_med_1_medication_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)




    #  hmz_med_1_diagnosis_age
    # --------------------------------------
    # BPRHS
    # --------------------------------------
    #some of the answers in this variable are not in age
    # bprhs v3
    df_hmz_health_bprhs_5["studyid"] = df_hmz_health_bprhs_5["studyid"].astype(float).astype(int).astype(str)
    studyid_94664 = df_hmz_health_bprhs_5[df_hmz_health_bprhs_5["studyid"] == "94664"]

    if not studyid_94664.empty:
        print("vis3_dt_5yr:", studyid_94664["vis3_dt_5yr"].values[0])
        print("age_5yr:", studyid_94664["age_5yr"].values[0])
    else:
        print("not found")

    # subject 94664 was 59 when first diagnosed

    # bprhs_8
    df_hmz_health_bprhs_8["studyid"] = df_hmz_health_bprhs_8["studyid"].astype(float).astype(int).astype(str)
    studyid_36171 = df_hmz_health_bprhs_8[df_hmz_health_bprhs_8["studyid"] == "36171"]

    if not studyid_36171.empty:
        print("vis4_dt_8yr:", studyid_36171["vis4_dt_8yr"].values[0])
        print("age_8yr:", studyid_36171["age_8yr"].values[0])
    else:
        print("not found.")


    # subject 94895 was 31 when first diagnosed
    # subject 36171 was 67 when first diagnosed


    print(df_hmz_health_bprhs_8['vis4_dt_8yr'])
    print(df_hmz_health_bprhs_5['studyid'].head(20))


    # Function to convert values to integers if possible
    def safe_convert(x):
        if isinstance(x, str) and x.isdigit():  # Check if the string is a valid number
            return int(x)
        elif isinstance(x, (int, float)) and not np.isnan(x):  # Keep existing valid numbers
            return int(x)
        else:
            return np.nan  # Replace invalid values with NaN


    df_hmz_health_bprhs_5['med1age_5yr'] = df_hmz_health_bprhs_5['med1age_5yr'].apply(safe_convert)
    df_hmz_health_bprhs_5['med1g_5yr'] = df_hmz_health_bprhs_5['med1g_5yr'].apply(safe_convert)


    print(df_hmz_health_bprhs_5['med1age_5yr'].value_counts())  # New diagnosis
    print(df_hmz_health_bprhs_5['med1g_5yr'].value_counts())  # Old diagnosis
    print(df_hmz_health_bprhs_8['med1d_8yr'].value_counts())



    df_hmz_health_bprhs_5["hmz_med_1_age_bprhs_5"] = df_hmz_health_bprhs_5["med1age_5yr"].fillna(df_hmz_health_bprhs_5["med1g_5yr"])
    df_hmz_health_bprhs_5['hmz_med_1_age_bprhs_5'] = df_hmz_health_bprhs_5['hmz_med_1_age_bprhs_5'].replace({2009: 59})



    # Renaming
    df_hmz_health_bprhs_8.rename(columns={'med1d_8yr': 'hmz_med_1_age_bprhs_8'}, inplace=True)


    df_hmz_health_bprhs_8['hmz_med_1_age_bprhs_8'] = df_hmz_health_bprhs_8['hmz_med_1_age_bprhs_8'].replace({1986: 31})
    df_hmz_health_bprhs_8['hmz_med_1_age_bprhs_8'] = df_hmz_health_bprhs_8['hmz_med_1_age_bprhs_8'].replace({2003: 67})


    # Saving
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)


    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)




    # --------------------------------------
    # PROSPECT
    # --------------------------------------

    # Renaming the variable
    df_hmz_health_prospect.rename(columns={'age_calc': 'age_prospect'}, inplace=True)

    # Applying a ceiling function (function that converts decimal numbers into whole numbers) to hmz_age_prospect
    df_hmz_health_prospect['age_prospect'] = np.ceil(df_hmz_health_prospect['age_prospect'])

    # Saving 
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)


    # transforming the variable

    def calculate_diagnosis_age(row):
        try:
            # Convert to numeric, force errors to NaN
            med1b = pd.to_numeric(row["med1b"], errors='coerce')
            age_prospect = pd.to_numeric(row["age_prospect"], errors='coerce')
            med1c = pd.to_numeric(row["med1c"], errors='coerce')

            # If any of the critical values are NaN, return NaN
            if pd.isna(med1b) or pd.isna(med1c):
                return np.nan  

            # If med1b is a year (likely misentered), treat it as Year of Diagnosis
            if med1b > 1900:  
                med1c = 1  # Force Year of Diagnosis category

            # If med1b is an unrealistically high number, set to NaN
            if med1b > 150:
                return np.nan  

            if med1c == 2:  # Age at diagnosis directly provided
                return med1b

            elif med1c == 1:  # Year of diagnosis provided or corrected from above
                age_at_diagnosis = 2024 - med1b
                return age_at_diagnosis if 0 <= age_at_diagnosis <= 120 else np.nan  # Ensure realistic age

            elif med1c == 3:  # Years with diagnosis provided
                if pd.isna(age_prospect):
                    return np.nan  # Missing current age
                age_at_diagnosis = age_prospect - med1b
                return age_at_diagnosis if 0 <= age_at_diagnosis <= 120 else np.nan  # Ensure realistic age

        except Exception as e:
            print(f"Error processing row {row.name}: {e}")
            return np.nan  

    # Function to create the new variable
    df_hmz_health_prospect["hmz_med_1_age_prospect"] = df_hmz_health_prospect.apply(calculate_diagnosis_age, axis=1)

    # Saving 
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)





    # diabetes today
    # --------------------------------------
    # BPRHS
    # --------------------------------------

    # transformation
    # Apply transformation: if hmz_med_1 == 0 --> med1c is NaN; if hmz_med_1 == nan --> med1c is Nan
    # bprhs v1 (hmz_med_1_bprhs_0, med1c)
    if "hmz_med_1_bprhs_0" in df_hmz_health_bprhs_0.columns and "med1c" in df_hmz_health_bprhs_0.columns:
        df_hmz_health_bprhs_0["hmz_med_1_bprhs_0"] = pd.to_numeric(df_hmz_health_bprhs_0["hmz_med_1_bprhs_0"], errors="coerce")
        df_hmz_health_bprhs_0.loc[df_hmz_health_bprhs_0["hmz_med_1_bprhs_0"].isna(), "med1c"] = np.nan
        df_hmz_health_bprhs_0.loc[df_hmz_health_bprhs_0["hmz_med_1_bprhs_0"] == 0, 'med1c'] = np.nan

    # bprhs v2 (hmz_med_1_bprhs_2, med1c_2yr)
    if "hmz_med_1_bprhs_2" in df_hmz_health_bprhs_2.columns and "med1c_2yr" in df_hmz_health_bprhs_2.columns:
        df_hmz_health_bprhs_2["hmz_med_1_bprhs_2"] = pd.to_numeric(df_hmz_health_bprhs_2["hmz_med_1_bprhs_2"], errors="coerce")
        df_hmz_health_bprhs_2.loc[df_hmz_health_bprhs_2["hmz_med_1_bprhs_2"].isna(), "med1c_2yr"] = np.nan
        df_hmz_health_bprhs_2.loc[df_hmz_health_bprhs_2["hmz_med_1_bprhs_2"] == 0, "med1c_2yr"] = np.nan


    # Renaming
    df_hmz_health_bprhs_0.rename(columns={'med1c': 'hmz_med_1_today_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'med1c_2yr': 'hmz_med_1_today_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'med1c_8yr': 'hmz_med_1_today_bprhs_8'}, inplace=True)


    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)




    # --------------------------------------
    # PROSPECT
    # --------------------------------------
    # Renaming
    df_hmz_health_prospect.rename(columns={'med1d': 'hmz_med_1_today_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)





    # High blood pressure
    # --------------------------------------
    # BPRHS
    # --------------------------------------

    # Renaming
    df_hmz_health_bprhs_0.rename(columns={'med2': 'hmz_med_bp_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'med2x_2yr': 'hmz_med_bp_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'med2_8yr': 'hmz_med_bp_bprhs_8'}, inplace=True)


    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)





    # --------------------------------------
    # PROSPECT
    # --------------------------------------
    # 
    # Recoding  96, 97, 98 -> as NaN
    df_hmz_health_prospect['med3'] = df_hmz_health_prospect['med3'].replace({98: np.nan})



    # Checking the value counts after recoding
    print(df_hmz_health_prospect['med3'].value_counts(dropna=False).sort_index())

    # Renaming
    df_hmz_health_prospect.rename(columns={'med3': 'hmz_med_bp_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)


    print(df_hmz_health_prospect['hmz_med_bp_prospect'].value_counts(dropna=False).sort_index())






    # medication for high blood pressure
    # --------------------------------------
    # BPRHS
    # --------------------------------------
    base_variable = ["med2b"]

    # Dictionary with datasets and corresponding suffixes
    bprhs_datasets = {
        "Baseline": (df_hmz_health_bprhs_0, ""),
        "2-Year": (df_hmz_health_bprhs_2, "_2yr"),
        "5-Year": (df_hmz_health_bprhs_5, "_5yr"),
        "8-Year": (df_hmz_health_bprhs_8, "_8yr")
    }

    # Checking if the variables exist in all datasets
    # Looping through each dataset and count non-null values for specified variables with appropriate suffix
    for name, (df, suffix) in bprhs_datasets.items():
        print(f"\nCounts for {name} dataset:")
        for var in base_variable:
            variable_name = var + suffix  # Add the suffix to the base variable name
            if variable_name in df.columns:
                print(f"  {variable_name} count:", df[variable_name].count())
            else:
                print(f"  Column '{variable_name}' not found in {name}")  # Variable only exists in 0 , 2, and 8


    # checking pre transformation
    print(df_hmz_health_bprhs_0['med2b'].value_counts())
    print(df_hmz_health_bprhs_2['med2b_2yr'].value_counts())


    if "hmz_med_bp_bprhs_0" in df_hmz_health_bprhs_0.columns and "med2b" in df_hmz_health_bprhs_0.columns:
        df_hmz_health_bprhs_0["hmz_med_bp_bprhs_0"] = pd.to_numeric(df_hmz_health_bprhs_0["hmz_med_bp_bprhs_0"], errors="coerce")
        df_hmz_health_bprhs_0.loc[df_hmz_health_bprhs_0["hmz_med_bp_bprhs_0"].isna(), "med2b"] = np.nan
        df_hmz_health_bprhs_0.loc[df_hmz_health_bprhs_0["hmz_med_bp_bprhs_0"] == 0, "med2b"] = np.nan



    # 2-Year (hmz_med_bp_bprhs_2, med2b_2yr)
    if "hmz_med_bp_bprhs_2" in df_hmz_health_bprhs_2.columns and "med2b_2yr" in df_hmz_health_bprhs_2.columns:
        df_hmz_health_bprhs_2["hmz_med_bp_bprhs_2"] = pd.to_numeric(df_hmz_health_bprhs_2["hmz_med_bp_bprhs_2"], errors="coerce")
        df_hmz_health_bprhs_2.loc[df_hmz_health_bprhs_2["hmz_med_bp_bprhs_2"].isna(), "med2b_2yr"] = np.nan
        df_hmz_health_bprhs_2.loc[df_hmz_health_bprhs_2["hmz_med_bp_bprhs_2"] == 0, "med2b_2yr"] = np.nan



    # Renaming
    df_hmz_health_bprhs_0.rename(columns={'med2b': 'hmz_med_bp_medication_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'med2b_2yr': 'hmz_med_bp_medication_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'med2b_8yr': 'hmz_med_bp_medication_bprhs_8'}, inplace=True)



    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)





    # --------------------------------------
    # PROSPECT
    # --------------------------------------

    # Recoding
    df_hmz_health_prospect['med3a'] = df_hmz_health_prospect['med3a'].replace({96: np.nan})

    # Renaming
    df_hmz_health_prospect.rename(columns={'med3a': 'hmz_med_bp_medication_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)




    # high blood pressure condition today
    # --------------------------------------
    # BPRHS
    # --------------------------------------

    # transformation
    # Apply transformation: if hmz_med_bp == 0 --> med2c is NaN; if hmz_med_bp == nan --> med2c is Nan
    # bprhs v1 (hmz_med_bp_bprhs_0, med2c)
    if "hmz_med_bp_bprhs_0" in df_hmz_health_bprhs_0.columns and "med2c" in df_hmz_health_bprhs_0.columns:
        df_hmz_health_bprhs_0["hmz_med_bp_bprhs_0"] = pd.to_numeric(df_hmz_health_bprhs_0["hmz_med_bp_bprhs_0"], errors="coerce")
        df_hmz_health_bprhs_0.loc[df_hmz_health_bprhs_0["hmz_med_bp_bprhs_0"].isna(), "med2c"] = np.nan
        df_hmz_health_bprhs_0.loc[df_hmz_health_bprhs_0["hmz_med_bp_bprhs_0"] == 0, 'med2c'] = np.nan

    # bprhs v2 (hmz_med_bp_bprhs_2, med2c_2yr)
    if "hmz_med_bp_bprhs_2" in df_hmz_health_bprhs_2.columns and "med2c_2yr" in df_hmz_health_bprhs_2.columns:
        df_hmz_health_bprhs_2["hmz_med_bp_bprhs_2"] = pd.to_numeric(df_hmz_health_bprhs_2["hmz_med_bp_bprhs_2"], errors="coerce")
        df_hmz_health_bprhs_2.loc[df_hmz_health_bprhs_2["hmz_med_bp_bprhs_2"].isna(), "med2c_2yr"] = np.nan
        df_hmz_health_bprhs_2.loc[df_hmz_health_bprhs_2["hmz_med_bp_bprhs_2"] == 0, "med2c_2yr"] = np.nan


    # Renaming
    df_hmz_health_bprhs_0.rename(columns={'med2c': 'hmz_med_bp_today_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'med2c_2yr': 'hmz_med_bp_today_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'med2c_8yr': 'hmz_med_bp_today_bprhs_8'}, inplace=True)


    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)


    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)


    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)





    # --------------------------------------
    # PROSPECT
    # --------------------------------------

    # Recoding
    df_hmz_health_prospect['med3d'] = df_hmz_health_prospect['med3d'].replace({97: np.nan, 98: np.nan})

    # Renaming
    df_hmz_health_prospect.rename(columns={'med3d': 'hmz_med_bp_today_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)





    # overweight
    # --------------------------------------
    # BPRHS
    # --------------------------------------


    # Renaming
    df_hmz_health_bprhs_0.rename(columns={'med3': 'hmz_med_overweight_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'med3_2yr': 'hmz_med_overweight_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_5.rename(columns={'med3x_5yr': 'hmz_med_overweight_bprhs_5'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'med3_8yr': 'hmz_med_overweight_bprhs_8'}, inplace=True)


    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)





    # --------------------------------------
    # PROSPECT
    # --------------------------------------

    # 
    df_hmz_health_prospect['med4'] = df_hmz_health_prospect['med4'].replace({96: np.nan, 98: np.nan})

    # Renaming
    df_hmz_health_prospect.rename(columns={'med4': 'hmz_med_overweight_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)






    # medication overweight
    # --------------------------------------
    # BPRHS
    # --------------------------------------

    # transformation
    # Apply transformation: if hmz_med_overweight == 0 --> med3b is NaN; if hmz_med_overweight == nan --> med3b is Nan
    # bprhs v1 (hmz_med_overweight_bprhs_0, med3b)
    if "hmz_med_overweight_bprhs_0" in df_hmz_health_bprhs_0.columns and "med3b" in df_hmz_health_bprhs_0.columns:
        df_hmz_health_bprhs_0["hmz_med_overweight_bprhs_0"] = pd.to_numeric(df_hmz_health_bprhs_0["hmz_med_overweight_bprhs_0"], errors="coerce")
        df_hmz_health_bprhs_0.loc[df_hmz_health_bprhs_0["hmz_med_overweight_bprhs_0"].isna(), "med3b"] = np.nan
        df_hmz_health_bprhs_0.loc[df_hmz_health_bprhs_0["hmz_med_overweight_bprhs_0"] == 0, 'med3b'] = np.nan

    # bprhs v2 (hmz_med_overweight_bprhs_2, med3b_2yr)
    if "hmz_med_overweight_bprhs_2" in df_hmz_health_bprhs_2.columns and "med3b_2yr" in df_hmz_health_bprhs_2.columns:
        df_hmz_health_bprhs_2["hmz_med_overweight_bprhs_2"] = pd.to_numeric(df_hmz_health_bprhs_2["hmz_med_overweight_bprhs_2"], errors="coerce")
        df_hmz_health_bprhs_2.loc[df_hmz_health_bprhs_2["hmz_med_overweight_bprhs_2"].isna(), "med3b_2yr"] = np.nan
        df_hmz_health_bprhs_2.loc[df_hmz_health_bprhs_2["hmz_med_overweight_bprhs_2"] == 0, "med3b_2yr"] = np.nan


    # Renaming
    df_hmz_health_bprhs_0.rename(columns={'med3b': 'hmz_med_overweight_medication_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'med3b_2yr': 'hmz_med_overweight_medication_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'med3b_8yr': 'hmz_med_overweight_medication_bprhs_8'}, inplace=True)


    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)







    # --------------------------------------
    # PROSPECT
    # --------------------------------------
    # Renaming
    df_hmz_health_prospect.rename(columns={'med4a': 'hmz_med_overweight_medication_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)





    # condition (overweight)currently
    # --------------------------------------
    # BPRHS
    # --------------------------------------
    # transformation
    # Apply transformation: if hmz_med_overweight == 0 --> med3c is NaN; if hmz_med_overweight == nan --> med3c is Nan
    # bprhs v1 (hmz_med_overweight_bprhs_0, med3c)
    if "hmz_med_overweight_bprhs_0" in df_hmz_health_bprhs_0.columns and "med3c" in df_hmz_health_bprhs_0.columns:
        df_hmz_health_bprhs_0["hmz_med_overweight_bprhs_0"] = pd.to_numeric(df_hmz_health_bprhs_0["hmz_med_overweight_bprhs_0"], errors="coerce")
        df_hmz_health_bprhs_0.loc[df_hmz_health_bprhs_0["hmz_med_overweight_bprhs_0"].isna(), "med3c"] = np.nan
        df_hmz_health_bprhs_0.loc[df_hmz_health_bprhs_0["hmz_med_overweight_bprhs_0"] == 0, 'med3c'] = np.nan

    # bprhs v2 (hmz_med_overweight_bprhs_2, med3c_2yr)
    if "hmz_med_overweight_bprhs_2" in df_hmz_health_bprhs_2.columns and "med3c_2yr" in df_hmz_health_bprhs_2.columns:
        df_hmz_health_bprhs_2["hmz_med_overweight_bprhs_2"] = pd.to_numeric(df_hmz_health_bprhs_2["hmz_med_overweight_bprhs_2"], errors="coerce")
        df_hmz_health_bprhs_2.loc[df_hmz_health_bprhs_2["hmz_med_overweight_bprhs_2"].isna(), "med3c_2yr"] = np.nan
        df_hmz_health_bprhs_2.loc[df_hmz_health_bprhs_2["hmz_med_overweight_bprhs_2"] == 0, "med3c_2yr"] = np.nan


    # bprhs v3 (hmz_med_overweight_bprhs_5, med3c_5yr)
    if "hmz_med_overweight_bprhs_5" in df_hmz_health_bprhs_5.columns and "med3c_5yr" in df_hmz_health_bprhs_5.columns:
        df_hmz_health_bprhs_5["hmz_med_overweight_bprhs_5"] = pd.to_numeric(df_hmz_health_bprhs_5["hmz_med_overweight_bprhs_5"], errors="coerce")
        df_hmz_health_bprhs_5.loc[df_hmz_health_bprhs_5["hmz_med_overweight_bprhs_5"].isna(), "med3c_5yr"] = np.nan
        df_hmz_health_bprhs_5.loc[df_hmz_health_bprhs_5["hmz_med_overweight_bprhs_5"] == 0, "med3c_5yr"] = np.nan

    # Renaming
    df_hmz_health_bprhs_0.rename(columns={'med3c': 'hmz_med_overweight_today_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'med3c_2yr': 'hmz_med_overweight_today_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_5.rename(columns={'med3c_5yr': 'hmz_med_overweight_today_bprhs_5'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'med3c_8yr': 'hmz_med_overweight_today_bprhs_8'}, inplace=True)



    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)




    # --------------------------------------
    # PROSPECT
    # --------------------------------------

    # Recoding  96, 97, 98 -> as NaN
    df_hmz_health_prospect['med4d'] = df_hmz_health_prospect['med4d'].replace({96: np.nan, 98: np.nan})

    # Renaming
    df_hmz_health_prospect.rename(columns={'med4d': 'hmz_med_overweight_today_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)





    # angina
    # --------------------------------------
    # BPRHS
    # --------------------------------------

    # Renaming
    df_hmz_health_bprhs_8.rename(columns={'med7_2_8yr': 'hmz_med_angina_bprhs_8'}, inplace=True)

    # Saving
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)





    # --------------------------------------
    # PROSPECT
    # --------------------------------------

    # Recoding  96, 97, 98 -> as NaN
    df_hmz_health_prospect['med7'] = df_hmz_health_prospect['med7'].replace({97: np.nan, 98: np.nan})

    # Renaming
    df_hmz_health_prospect.rename(columns={'med7': 'hmz_med_angina_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)




    # medication for angina
    # --------------------------------------
    # BPRHS
    # --------------------------------------

    # Renaming
    df_hmz_health_bprhs_8.rename(columns={'med7_2b_8yr': 'hmz_med_angina_medication_bprhs_8'}, inplace=True)

    # Saving
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)




    # --------------------------------------
    # PROSPECT
    # --------------------------------------
    df_hmz_health_prospect['med7a'] = df_hmz_health_prospect['med7a'].replace({98: np.nan})

    # Renaming
    df_hmz_health_prospect.rename(columns={'med7a': 'hmz_med_angina_medication_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)




    # subject currently has angina
    # --------------------------------------
    # BPRHS
    # --------------------------------------

    # Renaming
    df_hmz_health_bprhs_8.rename(columns={'med7_2c_8yr': 'hmz_med_angina_today_bprhs_8'}, inplace=True)


    # Saving
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)





    # --------------------------------------
    # PROSPECT
    # --------------------------------------

    # Recoding  96, 97, 98 -> as NaN
    df_hmz_health_prospect['med7d'] = df_hmz_health_prospect['med7d'].replace({98: np.nan})

    # Renaming
    df_hmz_health_prospect.rename(columns={'med7d': 'hmz_med_angina_today_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)




    # heart attack
    # --------------------------------------
    # BPRHS
    # --------------------------------------

    # Renaming
    df_hmz_health_bprhs_0.rename(columns={'med6': 'hmz_med_heart_attack_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'med6x_2yr': 'hmz_med_heart_attack_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_5.rename(columns={'med6x_5yr': 'hmz_med_heart_attack_bprhs_5'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'med6_8yr': 'hmz_med_heart_attack_bprhs_8'}, inplace=True)


    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)




    # --------------------------------------
    # PROSPECT
    # --------------------------------------

    # Recoding  96, 97, 98 -> as NaN
    df_hmz_health_prospect['med8'] = df_hmz_health_prospect['med8'].replace({96: np.nan,97: np.nan, 98: np.nan})

    # Renaming
    df_hmz_health_prospect.rename(columns={'med8': 'hmz_med_heart_attack_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)






    # medication
    # --------------------------------------
    # BPRHS
    # -------------------------------------- 

    # transformation
    # Apply transformation: if hmz_med_heart_attack == 0 --> med6b is NaN; if hmz_med_heart_attack == nan --> med6b is Nan
    # bprhs v1 (hmz_med_heart_attack_bprhs_0, med6b)
    if "hmz_med_heart_attack_bprhs_0" in df_hmz_health_bprhs_0.columns and "med6b" in df_hmz_health_bprhs_0.columns:
        df_hmz_health_bprhs_0["hmz_med_heart_attack_bprhs_0"] = pd.to_numeric(df_hmz_health_bprhs_0["hmz_med_heart_attack_bprhs_0"], errors="coerce")
        df_hmz_health_bprhs_0.loc[df_hmz_health_bprhs_0["hmz_med_heart_attack_bprhs_0"].isna(), "med6b"] = np.nan
        df_hmz_health_bprhs_0.loc[df_hmz_health_bprhs_0["hmz_med_heart_attack_bprhs_0"] == 0, 'med6b'] = np.nan

    # bprhs v2 (hmz_med_heart_attack_bprhs_2, med6b_2yr)
    if "hmz_med_heart_attack_bprhs_2" in df_hmz_health_bprhs_2.columns and "med6b_2yr" in df_hmz_health_bprhs_2.columns:
        df_hmz_health_bprhs_2["hmz_med_heart_attack_bprhs_2"] = pd.to_numeric(df_hmz_health_bprhs_2["hmz_med_heart_attack_bprhs_2"], errors="coerce")
        df_hmz_health_bprhs_2.loc[df_hmz_health_bprhs_2["hmz_med_heart_attack_bprhs_2"].isna(), "med6b_2yr"] = np.nan
        df_hmz_health_bprhs_2.loc[df_hmz_health_bprhs_2["hmz_med_heart_attack_bprhs_2"] == 0, "med6b_2yr"] = np.nan



    # Renaming
    df_hmz_health_bprhs_0.rename(columns={'med6b': 'hmz_med_heart_attack_medication_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'med6b_2yr': 'hmz_med_heart_attack_medication_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'med6b_8yr': 'hmz_med_heart_attack_medication_bprhs_8'}, inplace=True)

    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)




    # --------------------------------------
    # PROSPECT
    # --------------------------------------

    # Renaming
    df_hmz_health_prospect.rename(columns={'med8a': 'hmz_med_heart_attack_medication_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)





    # condition (heart attack) currently
    # --------------------------------------
    # BPRHS
    # --------------------------------------

    # transformation
    # Apply transformation: if hmz_med_heart_attack == 0 --> med6c is NaN; if hmz_med_heart_attack == nan --> med6c is Nan
    # bprhs v1 (hmz_med_heart_attack_bprhs_0, med6c)
    if "hmz_med_heart_attack_bprhs_0" in df_hmz_health_bprhs_0.columns and "med6c" in df_hmz_health_bprhs_0.columns:
        df_hmz_health_bprhs_0["hmz_med_heart_attack_bprhs_0"] = pd.to_numeric(df_hmz_health_bprhs_0["hmz_med_heart_attack_bprhs_0"], errors="coerce")
        df_hmz_health_bprhs_0.loc[df_hmz_health_bprhs_0["hmz_med_heart_attack_bprhs_0"].isna(), "med6c"] = np.nan
        df_hmz_health_bprhs_0.loc[df_hmz_health_bprhs_0["hmz_med_heart_attack_bprhs_0"] == 0, 'med6c'] = np.nan

    # bprhs v2 (hmz_med_heart_attack_bprhs_2, med6c_2yr)
    if "hmz_med_heart_attack_bprhs_2" in df_hmz_health_bprhs_2.columns and "med6c_2yr" in df_hmz_health_bprhs_2.columns:
        df_hmz_health_bprhs_2["hmz_med_heart_attack_bprhs_2"] = pd.to_numeric(df_hmz_health_bprhs_2["hmz_med_heart_attack_bprhs_2"], errors="coerce")
        df_hmz_health_bprhs_2.loc[df_hmz_health_bprhs_2["hmz_med_heart_attack_bprhs_2"].isna(), "med6c_2yr"] = np.nan
        df_hmz_health_bprhs_2.loc[df_hmz_health_bprhs_2["hmz_med_heart_attack_bprhs_2"] == 0, "med6c_2yr"] = np.nan


    # bprhs v3 (hmz_med_heart_attack_bprhs_5, med6c_5yr)
    if "hmz_med_heart_attack_bprhs_5" in df_hmz_health_bprhs_5.columns and "med6c_5yr" in df_hmz_health_bprhs_5.columns:
        df_hmz_health_bprhs_5["hmz_med_heart_attack_bprhs_5"] = pd.to_numeric(df_hmz_health_bprhs_5["hmz_med_heart_attack_bprhs_5"], errors="coerce")
        df_hmz_health_bprhs_5.loc[df_hmz_health_bprhs_5["hmz_med_heart_attack_bprhs_5"].isna(), "med6c_5yr"] = np.nan
        df_hmz_health_bprhs_5.loc[df_hmz_health_bprhs_5["hmz_med_heart_attack_bprhs_5"] == 0, "med6c_5yr"] = np.nan


    # Renaming
    df_hmz_health_bprhs_0.rename(columns={'med6c': 'hmz_med_heart_attack_today_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'med6c_2yr': 'hmz_med_heart_attack_today_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_5.rename(columns={'med6c_5yr': 'hmz_med_heart_attack_today_bprhs_5'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'med6c_8yr': 'hmz_med_heart_attack_today_bprhs_8'}, inplace=True)

    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)



    # --------------------------------------
    # PROSPECT
    # --------------------------------------

    # Recoding  96, 97, 98 -> as NaN
    df_hmz_health_prospect['med8d'] = df_hmz_health_prospect['med8d'].replace({98: np.nan})

    # Renaming
    df_hmz_health_prospect.rename(columns={'med8d': 'hmz_med_heart_attack_today_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)




    # heart failure
    # --------------------------------------
    # BPRHS
    # --------------------------------------

    # Renaming
    df_hmz_health_bprhs_8.rename(columns={'med7_3_8yr': 'hmz_med_heart_failure_bprhs_8'}, inplace=True)

    # Saving
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)




    # --------------------------------------
    # PROSPECT
    # --------------------------------------
    # Recoding  96, 97, 98 -> as NaN
    df_hmz_health_prospect['med9'] = df_hmz_health_prospect['med9'].replace({97: np.nan, 98: np.nan})

    # Renaming
    df_hmz_health_prospect.rename(columns={'med9': 'hmz_med_heart_failure_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)






    # medication 
    # --------------------------------------
    # BPRHS
    # --------------------------------------

    # Renaming
    df_hmz_health_bprhs_8.rename(columns={'med7_3b_8yr': 'hmz_med_heart_failure_medication_bprhs_8'}, inplace=True)

    # Saving
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)




    # --------------------------------------
    # PROSPECT
    # --------------------------------------

    # Renaming
    df_hmz_health_prospect.rename(columns={'med9a': 'hmz_med_heart_failure_medication_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)





    # condition (heart attack) currently
    # --------------------------------------
    # BPRHS
    # --------------------------------------
    # Renaming
    df_hmz_health_bprhs_8.rename(columns={'med7_3c_8yr': 'hmz_med_heart_failure_today_bprhs_8'}, inplace=True)

    # Saving
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)




    # --------------------------------------
    # PROSPECT
    # --------------------------------------

    # Renaming
    df_hmz_health_prospect.rename(columns={'med9d': 'hmz_med_heart_failure_today_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)




    # heart disease
    # --------------------------------------
    # BPRHS
    # --------------------------------------

    # Renaming
    df_hmz_health_bprhs_0.rename(columns={'med7': 'hmz_med_heart_disease_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'med7x_2yr': 'hmz_med_heart_disease_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_5.rename(columns={'med7x_5yr': 'hmz_med_heart_disease_bprhs_5'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'med7_4_8yr': 'hmz_med_heart_disease_bprhs_8'}, inplace=True)


    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)




    # --------------------------------------
    # PROSPECT
    # --------------------------------------

    # Recoding  96, 97, 98 -> as NaN
    df_hmz_health_prospect['med12'] = df_hmz_health_prospect['med12'].replace({ 98: np.nan})

    # Renaming
    df_hmz_health_prospect.rename(columns={'med12': 'hmz_med_heart_disease_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)






    # medication overweight

    # --------------------------------------
    # BPRHS
    # --------------------------------------
    # transformation
    # Apply transformation: if hmz_med_heart_disease == 0 --> med7b is NaN; if hmz_med_heart_disease == nan --> med7b is Nan
    # bprhs v1 (hmz_med_heart_disease_bprhs_0, med7b)
    if "hmz_med_heart_disease_bprhs_0" in df_hmz_health_bprhs_0.columns and "med7b" in df_hmz_health_bprhs_0.columns:
        df_hmz_health_bprhs_0["hmz_med_heart_disease_bprhs_0"] = pd.to_numeric(df_hmz_health_bprhs_0["hmz_med_heart_disease_bprhs_0"], errors="coerce")
        df_hmz_health_bprhs_0.loc[df_hmz_health_bprhs_0["hmz_med_heart_disease_bprhs_0"].isna(), "med7b"] = np.nan
        df_hmz_health_bprhs_0.loc[df_hmz_health_bprhs_0["hmz_med_heart_disease_bprhs_0"] == 0, 'med7b'] = np.nan

    # bprhs v2 (hmz_med_heart_disease_bprhs_2, med7b_2yr)
    if "hmz_med_heart_disease_bprhs_2" in df_hmz_health_bprhs_2.columns and "med7b_2yr" in df_hmz_health_bprhs_2.columns:
        df_hmz_health_bprhs_2["hmz_med_heart_disease_bprhs_2"] = pd.to_numeric(df_hmz_health_bprhs_2["hmz_med_heart_disease_bprhs_2"], errors="coerce")
        df_hmz_health_bprhs_2.loc[df_hmz_health_bprhs_2["hmz_med_heart_disease_bprhs_2"].isna(), "med7b_2yr"] = np.nan
        df_hmz_health_bprhs_2.loc[df_hmz_health_bprhs_2["hmz_med_heart_disease_bprhs_2"] == 0, "med7b_2yr"] = np.nan


    # Renaming
    df_hmz_health_bprhs_0.rename(columns={'med7b': 'hmz_med_heart_disease_medication_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'med7b_2yr': 'hmz_med_heart_disease_medication_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'med7_4b_8yr': 'hmz_med_heart_disease_medication_bprhs_8'}, inplace=True)


    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)







    # --------------------------------------
    # PROSPECT
    # --------------------------------------
    # Renaming
    df_hmz_health_prospect.rename(columns={'med12a': 'hmz_med_heart_disease_medication_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)





    # condition (heart disease) currently
    # --------------------------------------
    # BPRHS
    # --------------------------------------


    # transformation
    # Apply transformation: if hmz_med_heart_disease == 0 --> med7c is NaN; if hmz_med_heart_disease == nan --> med7c is Nan
    # bprhs v1 (hmz_med_heart_disease_bprhs_0, med7c)
    if "hmz_med_heart_disease_bprhs_0" in df_hmz_health_bprhs_0.columns and "med7c" in df_hmz_health_bprhs_0.columns:
        df_hmz_health_bprhs_0["hmz_med_heart_disease_bprhs_0"] = pd.to_numeric(df_hmz_health_bprhs_0["hmz_med_heart_disease_bprhs_0"], errors="coerce")
        df_hmz_health_bprhs_0.loc[df_hmz_health_bprhs_0["hmz_med_heart_disease_bprhs_0"].isna(), "med7c"] = np.nan
        df_hmz_health_bprhs_0.loc[df_hmz_health_bprhs_0["hmz_med_heart_disease_bprhs_0"] == 0, 'med7c'] = np.nan

    # bprhs v2 (hmz_med_heart_disease_bprhs_2, med7c_2yr)
    if "hmz_med_heart_disease_bprhs_2" in df_hmz_health_bprhs_2.columns and "med7c_2yr" in df_hmz_health_bprhs_2.columns:
        df_hmz_health_bprhs_2["hmz_med_heart_disease_bprhs_2"] = pd.to_numeric(df_hmz_health_bprhs_2["hmz_med_heart_disease_bprhs_2"], errors="coerce")
        df_hmz_health_bprhs_2.loc[df_hmz_health_bprhs_2["hmz_med_heart_disease_bprhs_2"].isna(), "med7c_2yr"] = np.nan
        df_hmz_health_bprhs_2.loc[df_hmz_health_bprhs_2["hmz_med_heart_disease_bprhs_2"] == 0, "med7c_2yr"] = np.nan


    # bprhs v3 (hmz_med_heart_disease_bprhs_5, med7c_5yr)
    if "hmz_med_heart_disease_bprhs_5" in df_hmz_health_bprhs_5.columns and "med7c_5yr" in df_hmz_health_bprhs_5.columns:
        df_hmz_health_bprhs_5["hmz_med_heart_disease_bprhs_5"] = pd.to_numeric(df_hmz_health_bprhs_5["hmz_med_heart_disease_bprhs_5"], errors="coerce")
        df_hmz_health_bprhs_5.loc[df_hmz_health_bprhs_5["hmz_med_heart_disease_bprhs_5"].isna(), "med7c_5yr"] = np.nan
        df_hmz_health_bprhs_5.loc[df_hmz_health_bprhs_5["hmz_med_heart_disease_bprhs_5"] == 0, "med7c_5yr"] = np.nan


    # Renaming
    df_hmz_health_bprhs_0.rename(columns={'med7c': 'hmz_med_heart_disease_today_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'med7c_2yr': 'hmz_med_heart_disease_today_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_5.rename(columns={'med7c_5yr': 'hmz_med_heart_disease_today_bprhs_5'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'med7_4c_8yr': 'hmz_med_heart_disease_today_bprhs_8'}, inplace=True)


    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)




    # --------------------------------------
    # PROSPECT
    # --------------------------------------

    # Recoding  96, 97, 98 -> as NaN
    df_hmz_health_prospect['med12d'] = df_hmz_health_prospect['med12d'].replace({98: np.nan})

    # Renaming
    df_hmz_health_prospect.rename(columns={'med12d': 'hmz_med_heart_disease_today_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)



    # stroke
    # --------------------------------------
    # BPRHS
    # --------------------------------------


    # Renaming
    df_hmz_health_bprhs_0.rename(columns={'med8': 'hmz_med_stroke_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'med8x_2yr': 'hmz_med_stroke_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_5.rename(columns={'med8x_5yr': 'hmz_med_stroke_bprhs_5'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'med8_8yr': 'hmz_med_stroke_bprhs_8'}, inplace=True)


    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)






    # --------------------------------------
    # PROSPECT
    # --------------------------------------
    # Recoding  96, 97, 98 -> as NaN
    df_hmz_health_prospect['med14'] = df_hmz_health_prospect['med14'].replace({98: np.nan})

    # Renaming
    df_hmz_health_prospect.rename(columns={'med14': 'hmz_med_stroke_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)






    # medication 
    # --------------------------------------
    # BPRHS
    # --------------------------------------


    # transformation
    # Apply transformation: if hmz_med_stroke == 0 --> med8b is NaN; if hmz_med_stroke == nan --> med8b is Nan
    # baseline (hmz_med_stroke_bprhs_0, med8b)
    if "hmz_med_stroke_bprhs_0" in df_hmz_health_bprhs_0.columns and "med8b" in df_hmz_health_bprhs_0.columns:
        df_hmz_health_bprhs_0["hmz_med_stroke_bprhs_0"] = pd.to_numeric(df_hmz_health_bprhs_0["hmz_med_stroke_bprhs_0"], errors="coerce")
        df_hmz_health_bprhs_0.loc[df_hmz_health_bprhs_0["hmz_med_stroke_bprhs_0"].isna(), "med8b"] = np.nan
        df_hmz_health_bprhs_0.loc[df_hmz_health_bprhs_0["hmz_med_stroke_bprhs_0"] == 0, 'med8b'] = np.nan

    # 2-Year (hmz_med_stroke_bprhs_2, med8b_2yr)
    if "hmz_med_stroke_bprhs_2" in df_hmz_health_bprhs_2.columns and "med8b_2yr" in df_hmz_health_bprhs_2.columns:
        df_hmz_health_bprhs_2["hmz_med_stroke_bprhs_2"] = pd.to_numeric(df_hmz_health_bprhs_2["hmz_med_stroke_bprhs_2"], errors="coerce")
        df_hmz_health_bprhs_2.loc[df_hmz_health_bprhs_2["hmz_med_stroke_bprhs_2"].isna(), "med8b_2yr"] = np.nan
        df_hmz_health_bprhs_2.loc[df_hmz_health_bprhs_2["hmz_med_stroke_bprhs_2"] == 0, "med8b_2yr"] = np.nan


    # Renaming
    df_hmz_health_bprhs_0.rename(columns={'med8b': 'hmz_med_stroke_medication_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'med8b_2yr': 'hmz_med_stroke_medication_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'med8b_8yr': 'hmz_med_stroke_medication_bprhs_8'}, inplace=True)


    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)





    # --------------------------------------
    # PROSPECT
    # --------------------------------------

    # Renaming
    df_hmz_health_prospect.rename(columns={'med14a': 'hmz_med_stroke_medication_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)





    # condition (heart attack) currently

    # --------------------------------------
    # BPRHS
    # --------------------------------------

    # transformation
    # Apply transformation: if hmz_med_stroke == 0 --> med8c is NaN; if hmz_med_stroke == nan --> med8c is Nan
    # bprhs v1 (hmz_med_stroke_bprhs_0, med8c)
    if "hmz_med_stroke_bprhs_0" in df_hmz_health_bprhs_0.columns and "med8c" in df_hmz_health_bprhs_0.columns:
        df_hmz_health_bprhs_0["hmz_med_stroke_bprhs_0"] = pd.to_numeric(df_hmz_health_bprhs_0["hmz_med_stroke_bprhs_0"], errors="coerce")
        df_hmz_health_bprhs_0.loc[df_hmz_health_bprhs_0["hmz_med_stroke_bprhs_0"].isna(), "med8c"] = np.nan
        df_hmz_health_bprhs_0.loc[df_hmz_health_bprhs_0["hmz_med_stroke_bprhs_0"] == 0, 'med8c'] = np.nan

    # bprhs v2 (hmz_med_stroke_bprhs_2, med8c_2yr)
    if "hmz_med_stroke_bprhs_2" in df_hmz_health_bprhs_2.columns and "med8c_2yr" in df_hmz_health_bprhs_2.columns:
        df_hmz_health_bprhs_2["hmz_med_stroke_bprhs_2"] = pd.to_numeric(df_hmz_health_bprhs_2["hmz_med_stroke_bprhs_2"], errors="coerce")
        df_hmz_health_bprhs_2.loc[df_hmz_health_bprhs_2["hmz_med_stroke_bprhs_2"].isna(), "med8c_2yr"] = np.nan
        df_hmz_health_bprhs_2.loc[df_hmz_health_bprhs_2["hmz_med_stroke_bprhs_2"] == 0, "med8c_2yr"] = np.nan


    # bprhs v3 (hmz_med_stroke_bprhs_5, med8c_5yr)
    if "hmz_med_stroke_bprhs_5" in df_hmz_health_bprhs_5.columns and "med8c_5yr" in df_hmz_health_bprhs_5.columns:
        df_hmz_health_bprhs_5["hmz_med_stroke_bprhs_5"] = pd.to_numeric(df_hmz_health_bprhs_5["hmz_med_stroke_bprhs_5"], errors="coerce")
        df_hmz_health_bprhs_5.loc[df_hmz_health_bprhs_5["hmz_med_stroke_bprhs_5"].isna(), "med8c_5yr"] = np.nan
        df_hmz_health_bprhs_5.loc[df_hmz_health_bprhs_5["hmz_med_stroke_bprhs_5"] == 0, "med8c_5yr"] = np.nan



    # Renaming
    df_hmz_health_bprhs_0.rename(columns={'med8c': 'hmz_med_stroke_today_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'med8c_2yr': 'hmz_med_stroke_today_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_5.rename(columns={'med8c_5yr': 'hmz_med_stroke_today_bprhs_5'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'med8c_8yr': 'hmz_med_stroke_today_bprhs_8'}, inplace=True)

    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)




    # --------------------------------------
    # PROSPECT
    # --------------------------------------

    # Recoding  96, 97, 98 -> as NaN
    df_hmz_health_prospect['med14d'] = df_hmz_health_prospect['med14d'].replace({98: np.nan})

    # Renaming
    df_hmz_health_prospect.rename(columns={'med14d': 'hmz_med_stroke_today_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)





    # kidney disease

    # --------------------------------------
    # BPRHS
    # --------------------------------------


    # Renaming
    df_hmz_health_bprhs_0.rename(columns={'med11': 'hmz_med_kidney_disease_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'med11x_2yr': 'hmz_med_kidney_disease_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_5.rename(columns={'med11x_5yr': 'hmz_med_kidney_disease_bprhs_5'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'med11_8yr': 'hmz_med_kidney_disease_bprhs_8'}, inplace=True)


    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)





    # --------------------------------------
    # PROSPECT
    # --------------------------------------

    # Recoding  96, 97, 98 -> as NaN
    df_hmz_health_prospect['med19'] = df_hmz_health_prospect['med19'].replace({98: np.nan})

    # Renaming
    df_hmz_health_prospect.rename(columns={'med19': 'hmz_med_kidney_disease_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)






    # medication 
    # --------------------------------------
    # BPRHS
    # --------------------------------------


    # transformation
    # Apply transformation: if hmz_med_kidney_disease == 0 --> med11b is NaN; if hmz_med_kidney_disease == nan --> med11b is Nan
    # bprhs v1 (hmz_med_kidney_disease_bprhs_0, med11b)
    if "hmz_med_kidney_disease_bprhs_0" in df_hmz_health_bprhs_0.columns and "med11b" in df_hmz_health_bprhs_0.columns:
        df_hmz_health_bprhs_0["hmz_med_kidney_disease_bprhs_0"] = pd.to_numeric(df_hmz_health_bprhs_0["hmz_med_kidney_disease_bprhs_0"], errors="coerce")
        df_hmz_health_bprhs_0.loc[df_hmz_health_bprhs_0["hmz_med_kidney_disease_bprhs_0"].isna(), "med11b"] = np.nan
        df_hmz_health_bprhs_0.loc[df_hmz_health_bprhs_0["hmz_med_kidney_disease_bprhs_0"] == 0, 'med11b'] = np.nan

    # bprhs v2 (hmz_med_kidney_disease_bprhs_2, med11b_2yr)
    if "hmz_med_kidney_disease_bprhs_2" in df_hmz_health_bprhs_2.columns and "med11b_2yr" in df_hmz_health_bprhs_2.columns:
        df_hmz_health_bprhs_2["hmz_med_kidney_disease_bprhs_2"] = pd.to_numeric(df_hmz_health_bprhs_2["hmz_med_kidney_disease_bprhs_2"], errors="coerce")
        df_hmz_health_bprhs_2.loc[df_hmz_health_bprhs_2["hmz_med_kidney_disease_bprhs_2"].isna(), "med11b_2yr"] = np.nan
        df_hmz_health_bprhs_2.loc[df_hmz_health_bprhs_2["hmz_med_kidney_disease_bprhs_2"] == 0, "med11b_2yr"] = np.nan



    # Renaming
    df_hmz_health_bprhs_0.rename(columns={'med11b': 'hmz_med_kidney_disease_medication_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'med11b_2yr': 'hmz_med_kidney_disease_medication_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'med11b_8yr': 'hmz_med_kidney_disease_medication_bprhs_8'}, inplace=True)


    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)





    # --------------------------------------
    # PROSPECT
    # --------------------------------------

    # Renaming
    df_hmz_health_prospect.rename(columns={'med19a': 'hmz_med_kidney_disease_medication_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)





    # condition (heart attack) currently
    # --------------------------------------
    # BPRHS
    # --------------------------------------

    # transformation
    # Apply transformation: if hmz_med_kidney_disease == 0 --> med11c is NaN; if hmz_med_kidney_disease == nan --> med11c is Nan
    # bprhs v1 (hmz_med_kidney_disease_bprhs_0, med11c)
    if "hmz_med_kidney_disease_bprhs_0" in df_hmz_health_bprhs_0.columns and "med11c" in df_hmz_health_bprhs_0.columns:
        df_hmz_health_bprhs_0["hmz_med_kidney_disease_bprhs_0"] = pd.to_numeric(df_hmz_health_bprhs_0["hmz_med_kidney_disease_bprhs_0"], errors="coerce")
        df_hmz_health_bprhs_0.loc[df_hmz_health_bprhs_0["hmz_med_kidney_disease_bprhs_0"].isna(), "med11c"] = np.nan
        df_hmz_health_bprhs_0.loc[df_hmz_health_bprhs_0["hmz_med_kidney_disease_bprhs_0"] == 0, 'med11c'] = np.nan

    # bprhs v2 (hmz_med_kidney_disease_bprhs_2, med11c_2yr)
    if "hmz_med_kidney_disease_bprhs_2" in df_hmz_health_bprhs_2.columns and "med11c_2yr" in df_hmz_health_bprhs_2.columns:
        df_hmz_health_bprhs_2["hmz_med_kidney_disease_bprhs_2"] = pd.to_numeric(df_hmz_health_bprhs_2["hmz_med_kidney_disease_bprhs_2"], errors="coerce")
        df_hmz_health_bprhs_2.loc[df_hmz_health_bprhs_2["hmz_med_kidney_disease_bprhs_2"].isna(), "med11c_2yr"] = np.nan
        df_hmz_health_bprhs_2.loc[df_hmz_health_bprhs_2["hmz_med_kidney_disease_bprhs_2"] == 0, "med11c_2yr"] = np.nan


    # bprhs v3 (hmz_med_kidney_disease_bprhs_5, med11c_5yr)
    if "hmz_med_kidney_disease_bprhs_5" in df_hmz_health_bprhs_5.columns and "med11c_5yr" in df_hmz_health_bprhs_5.columns:
        df_hmz_health_bprhs_5["hmz_med_kidney_disease_bprhs_5"] = pd.to_numeric(df_hmz_health_bprhs_5["hmz_med_kidney_disease_bprhs_5"], errors="coerce")
        df_hmz_health_bprhs_5.loc[df_hmz_health_bprhs_5["hmz_med_kidney_disease_bprhs_5"].isna(), "med11c_5yr"] = np.nan
        df_hmz_health_bprhs_5.loc[df_hmz_health_bprhs_5["hmz_med_kidney_disease_bprhs_5"] == 0, "med11c_5yr"] = np.nan



    # Renaming
    df_hmz_health_bprhs_0.rename(columns={'med11c': 'hmz_med_kidney_disease_today_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'med11c_2yr': 'hmz_med_kidney_disease_today_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_5.rename(columns={'med11c_5yr': 'hmz_med_kidney_disease_today_bprhs_5'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'med11c_8yr': 'hmz_med_kidney_disease_today_bprhs_8'}, inplace=True)



    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)




    # --------------------------------------
    # PROSPECT
    # --------------------------------------

    # Recoding  96, 97, 98 -> as NaN
    df_hmz_health_prospect['med19d'] = df_hmz_health_prospect['med19d'].replace({98: np.nan})

    # Renaming
    df_hmz_health_prospect.rename(columns={'med19d': 'hmz_med_kidney_disease_today_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)





    # hepatitis
    # --------------------------------------
    # BPRHS
    # --------------------------------------


    # Renaming
    df_hmz_health_bprhs_0.rename(columns={'med21': 'hmz_med_hepatitis_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'med21x_2yr': 'hmz_med_hepatitis_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_5.rename(columns={'med21x_5yr': 'hmz_med_hepatitis_bprhs_5'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'med21_8yr': 'hmz_med_hepatitis_bprhs_8'}, inplace=True)


    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)






    # --------------------------------------
    # PROSPECT
    # --------------------------------------

    # Recoding  96, 97, 98 -> as NaN
    df_hmz_health_prospect['med21'] = df_hmz_health_prospect['med21'].replace({ 98: np.nan})

    # Renaming
    df_hmz_health_prospect.rename(columns={'med21': 'hmz_med_hepatitis_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)








    # Type of Hepatitis

    # --------------------------------------
    # BPRHS
    # --------------------------------------



    bprhs_datasets = {
        "Baseline": (df_hmz_health_bprhs_0, ""),
        "2-Year":   (df_hmz_health_bprhs_2, "_2yr"),
        "5-Year":   (df_hmz_health_bprhs_5, "_5yr"),
        "8-Year":   (df_hmz_health_bprhs_8, "_8yr")}

    # Recoding values in med21t_* variables
    for name, (df, suffix) in bprhs_datasets.items():
        var = 'med21t' + suffix
        if var in df.columns:
            # Recode A/B/C → 1/2/3
            df[var] = df[var].replace({'A': 1, 'B': 2, 'C': 3})

    # Renaming 
    df_hmz_health_bprhs_5.rename(columns={'med21t_5yr': 'hmz_med_hepatitis_type_bprhs_5'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'med21t_8yr': 'hmz_med_hepatitis_type_bprhs_8'}, inplace=True)
    print("Renaming complete.")

    # Saving
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)


    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)





    # --------------------------------------
    # PROSPECT
    # --------------------------------------

    # Ensuring consistent data types
    df_hmz_health_prospect[['med21e___1', 'med21e___2', 'med21e___3']] = df_hmz_health_prospect[
        ['med21e___1', 'med21e___2', 'med21e___3']
    ].astype(float)


    df_hmz_health_prospect['hmz_med_hepatitis_type_prospect'] = df_hmz_health_prospect.apply(
        lambda row: (
            1 if row['med21e___1'] == 1.0 else
            2 if row['med21e___2'] == 1.0 else
            3 if row['med21e___3'] == 1.0 else None
        ),
        axis=1
    )


    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)





    # medication for hepatitis

    # --------------------------------------
    # BPRHS
    # --------------------------------------

    # transformation
    # Apply transformation: if hmz_med_hepatitis == 0 --> med21b is NaN; if hmz_med_hepatitis == nan --> med21b is Nan
    # bprhs v1 (hmz_med_hepatitis_bprhs_0, med21b)
    if "hmz_med_hepatitis_bprhs_0" in df_hmz_health_bprhs_0.columns and "med21b" in df_hmz_health_bprhs_0.columns:
        df_hmz_health_bprhs_0["hmz_med_hepatitis_bprhs_0"] = pd.to_numeric(df_hmz_health_bprhs_0["hmz_med_hepatitis_bprhs_0"], errors="coerce")
        df_hmz_health_bprhs_0.loc[df_hmz_health_bprhs_0["hmz_med_hepatitis_bprhs_0"].isna(), "med21b"] = np.nan
        df_hmz_health_bprhs_0.loc[df_hmz_health_bprhs_0["hmz_med_hepatitis_bprhs_0"] == 0, 'med21b'] = np.nan

    # bprhs v2 (hmz_med_hepatitis_bprhs_2, med21b_2yr)
    if "hmz_med_hepatitis_bprhs_2" in df_hmz_health_bprhs_2.columns and "med21b_2yr" in df_hmz_health_bprhs_2.columns:
        df_hmz_health_bprhs_2["hmz_med_hepatitis_bprhs_2"] = pd.to_numeric(df_hmz_health_bprhs_2["hmz_med_hepatitis_bprhs_2"], errors="coerce")
        df_hmz_health_bprhs_2.loc[df_hmz_health_bprhs_2["hmz_med_hepatitis_bprhs_2"].isna(), "med21b_2yr"] = np.nan
        df_hmz_health_bprhs_2.loc[df_hmz_health_bprhs_2["hmz_med_hepatitis_bprhs_2"] == 0, "med21b_2yr"] = np.nan



    # Renaming
    df_hmz_health_bprhs_0.rename(columns={'med21b': 'hmz_med_hepatitis_medication_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'med21b_2yr': 'hmz_med_hepatitis_medication_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'med21b_8yr': 'hmz_med_hepatitis_medication_bprhs_8'}, inplace=True)


    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)





    # --------------------------------------
    # PROSPECT
    # --------------------------------------

    # Recoding  96, 97, 98 -> as NaN
    df_hmz_health_prospect['med21a'] = df_hmz_health_prospect['med21a'].replace({97: np.nan})

    # Renaming
    df_hmz_health_prospect.rename(columns={'med21a': 'hmz_med_hepatitis_medication_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)






    #subject has hepatitis currently
    # --------------------------------------
    # BPRHS
    # --------------------------------------

    # transformation
    # Apply transformation: if hmz_med_hepatitis == 0 --> med21c is NaN; if hmz_med_hepatitis == nan --> med21c is Nan
    # bprhs v1 (hmz_med_hepatitis_bprhs_0, med21c)
    if "hmz_med_hepatitis_bprhs_0" in df_hmz_health_bprhs_0.columns and "med21c" in df_hmz_health_bprhs_0.columns:
        df_hmz_health_bprhs_0["hmz_med_hepatitis_bprhs_0"] = pd.to_numeric(df_hmz_health_bprhs_0["hmz_med_hepatitis_bprhs_0"], errors="coerce")
        df_hmz_health_bprhs_0.loc[df_hmz_health_bprhs_0["hmz_med_hepatitis_bprhs_0"].isna(), "med21c"] = np.nan
        df_hmz_health_bprhs_0.loc[df_hmz_health_bprhs_0["hmz_med_hepatitis_bprhs_0"] == 0, 'med21c'] = np.nan

    # bprhs v2 (hmz_med_hepatitis_bprhs_2, med21c_2yr)
    if "hmz_med_hepatitis_bprhs_2" in df_hmz_health_bprhs_2.columns and "med21c_2yr" in df_hmz_health_bprhs_2.columns:
        df_hmz_health_bprhs_2["hmz_med_hepatitis_bprhs_2"] = pd.to_numeric(df_hmz_health_bprhs_2["hmz_med_hepatitis_bprhs_2"], errors="coerce")
        df_hmz_health_bprhs_2.loc[df_hmz_health_bprhs_2["hmz_med_hepatitis_bprhs_2"].isna(), "med21c_2yr"] = np.nan
        df_hmz_health_bprhs_2.loc[df_hmz_health_bprhs_2["hmz_med_hepatitis_bprhs_2"] == 0, "med21c_2yr"] = np.nan


    # bprhs v3 (hmz_med_hepatitis_bprhs_5, med21c_5yr)
    if "hmz_med_hepatitis_bprhs_5" in df_hmz_health_bprhs_5.columns and "med21c_5yr" in df_hmz_health_bprhs_5.columns:
        df_hmz_health_bprhs_5["hmz_med_hepatitis_bprhs_5"] = pd.to_numeric(df_hmz_health_bprhs_5["hmz_med_hepatitis_bprhs_5"], errors="coerce")
        df_hmz_health_bprhs_5.loc[df_hmz_health_bprhs_5["hmz_med_hepatitis_bprhs_5"].isna(), "med21c_5yr"] = np.nan
        df_hmz_health_bprhs_5.loc[df_hmz_health_bprhs_5["hmz_med_hepatitis_bprhs_5"] == 0, "med21c_5yr"] = np.nan

    # Renaming
    df_hmz_health_bprhs_0.rename(columns={'med21c': 'hmz_med_hepatitis_today_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'med21c_2yr': 'hmz_med_hepatitis_today_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'med21c_2yr': 'hmz_med_hepatitis_today_bprhs_5'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'med21c_8yr': 'hmz_med_hepatitis_today_bprhs_8'}, inplace=True)



    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)





    # --------------------------------------
    # PROSPECT
    # --------------------------------------
    # Recoding  96, 97, 98 -> as NaN
    df_hmz_health_prospect['med21d'] = df_hmz_health_prospect['med21d'].replace({98: np.nan})

    # Renaming
    df_hmz_health_prospect.rename(columns={'med21d': 'hmz_med_hepatitis_today_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)





    # Cancer
    # --------------------------------------
    # BPRHS
    # --------------------------------------
    # Renaming
    df_hmz_health_bprhs_0.rename(columns={'med15': 'hmz_med_cancer_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'med15x_2yr': 'hmz_med_cancer_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_5.rename(columns={'med15x_5yr': 'hmz_med_cancer_bprhs_5'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'med15_8yr': 'hmz_med_cancer_bprhs_8'}, inplace=True)



    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)




    # --------------------------------------
    # PROSPECT
    # --------------------------------------

    # Recoding  96, 97, 98 -> as NaN
    df_hmz_health_prospect['med26'] = df_hmz_health_prospect['med26'].replace({ 98: np.nan})

    # Renaming
    df_hmz_health_prospect.rename(columns={'med26': 'hmz_med_cancer_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)







    # Type of cancer
    # --------------------------------------
    # BPRHS
    # --------------------------------------

    cancer_mapping = {
        1: ["lung", "pulmon", "higado, pancreas, pulmon", "pulmonal", "lung cancer", "lung (misdiagnosis)", "pulmon cancer"],
        2: ["breast", "colon y senos", "breast/thyroid", "mama", "pecho",
        "tiene un quiste en el seno", "seno izquierdo y glandulas linfaticas",
        "en el seno izquierdo", "le quitaron el seno", "seno izquierdo",
        "seno, linfatico", "mamas", "de la mama",
        "cancer en el seno derecho.", "senos quistes",
        "breast colon", "breast cancer", "tiroide/seno", "seno, vaginal",
        "senos", "breast, liver", "de seno",
        "seno (derecho)", "seno ( izq)", "cancer en el seno",
     "en el seno derecho"],

        3: ["cervical", "cervix", "cell squamous","cervical cance4", "cervical cancer"],
        4: ["lymphoma", "linfatico", "blood", "leukemia", "leusemia","multiple myeloma"],
        5: [],
        6: [ "bones"],
        7: [],
        8: ["skin cancer", "cancer de piel"],
        9: [],
        10: ["stomach", "estomago", "en el estomago y pecho"],
        11: ["colon", "rectal", "tumor canceroso colon", "colon polipos", "colon cancer",
             "tumor conceroso un el colon", "colon carcer", "tumor canceroso en el colon"],
        12: ["Uterine","uterine", "utero", "cancer en el utero", "uterus","matriz", "uterine cancer", "maltris", "matris","en la matris","de la matriz","hysterectomy b/c of cancer"],
        13: ["prostate", "prostrate", "prostata", "cancer en la prostata", "prostate (empezando)", "en la prostata", "prostate cancer"],
        14: ["liver", "higado", "liver cancer"],
        15: ["other", "laringe", "adrenal gland cancer", "ovarian cancer",
             "cancer en el cuerpo", "ulcera" , "knee", "vulva", "dk", "carganta",
             "ulcera cancerosa", "had a cancerous tumor in his forehead", "throat", "thymoma",
             "tumor", "doesn't know name", "-", "lengua", "lupus related",
             "vejiga", ".", "eye", "lengua they cut part of it",
             "tuvo un tumor en el ojo izquierdo y lupus", "ovarian", "throat cancer",
             "lymph node between kidney and aorta", "rinon", "en los ovarios",
             "fiocrimositoma tumor in adrenal part of right kidney", "pelvic", "vaginal", "cancer en la cara",
             "ovarios"]
    }



    def categorize_cancer(text):
        if pd.isna(text) or text.strip() == "":
            return np.nan  

        text = text.lower().strip()  # Normalize text (remove spaces, convert to lowercase)

        for category, keywords in cancer_mapping.items():
            if text in keywords:  
                return category

    for name, (df, suffix) in bprhs_datasets.items():
        variable_name = "med15t" + suffix
        if variable_name in df.columns:
            df[variable_name] = df[variable_name].astype(str).str.strip()

    if 'med15t' in df_hmz_health_bprhs_0.columns:
        df_hmz_health_bprhs_0['med15t_bprhs_0'] = df_hmz_health_bprhs_0['med15t'].astype(str).apply(categorize_cancer)

    if 'med15t_2yr' in df_hmz_health_bprhs_2.columns:
        df_hmz_health_bprhs_2['med15t_bprhs_2'] = df_hmz_health_bprhs_2['med15t_2yr'].astype(str).apply(categorize_cancer)

    if 'med15t_5yr' in df_hmz_health_bprhs_5.columns:
        df_hmz_health_bprhs_5['med15t_bprhs_5'] = df_hmz_health_bprhs_5['med15t_5yr'].astype(str).apply(categorize_cancer)



    # Creating separate variables for each type of cancer (to harmonize with prospect)
    cancer_mapping = {
        1: "lung",
        2: "breast",
        3: "cervical",
        4: "blood",
        5: "testicular",
        6: "bone",
        7: "melanoma",
        8: "skin",
        9: "brain",
        10: "stomach",
        11: "colon",
        12: "uterine",
        13: "prostate",
        14: "liver",
        15: "other"
    }


    def transform_cancer_variables(df, suffix):
        for cancer_code, cancer_name in cancer_mapping.items():
            new_col = f"hmz_med_cancer_{cancer_name}_{suffix}"
            df[new_col] = np.where(df[f"med15t_{suffix}"] == cancer_code, 1, 0) 


    transform_cancer_variables(df_hmz_health_bprhs_0, "bprhs_0")
    transform_cancer_variables(df_hmz_health_bprhs_2, "bprhs_2")
    transform_cancer_variables(df_hmz_health_bprhs_5, "bprhs_5")



    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)






    # Renaming 
    df_hmz_health_bprhs_8.rename(columns={'med15t_8yr___16': 'hmz_med_cancer_lung_bprhs_8'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'med15t_8yr___4': 'hmz_med_cancer_breast_bprhs_8'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'med15t_8yr___5': 'hmz_med_cancer_cervical_bprhs_8'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'med15t_8yr___1': 'hmz_med_cancer_blood_bprhs_8'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'med15t_8yr___25': 'hmz_med_cancer_testicular_bprhs_8'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'med15t_8yr___2': 'hmz_med_cancer_bone_bprhs_8'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'med15t_8yr___18': 'hmz_med_cancer_melanoma_bprhs_8'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'med15t_8yr___19': 'hmz_med_cancer_skin_bprhs_8'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'med15t_8yr___3': 'hmz_med_cancer_brain_bprhs_8'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'med15t_8yr___14': 'hmz_med_cancer_stomach_bprhs_8'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'med15t_8yr___6': 'hmz_med_cancer_colon_bprhs_8'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'med15t_8yr___22': 'hmz_med_cancer_uterine_bprhs_8'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'med15t_8yr___24': 'hmz_med_cancer_prostate_bprhs_8'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'med15t_8yr___15': 'hmz_med_cancer_liver_bprhs_8'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'med15t_8yr___28': 'hmz_med_cancer_other_bprhs_8'}, inplace=True)

    # Updating 'other' with the list of cancers not included above
    cancer_vars = [
        'med15t_8yr___7',   # Rectum
        'med15t_8yr___8',   # Esophagus
        'med15t_8yr___9',   # Gallbladder
        'med15t_8yr___10',  # Kidney
        'med15t_8yr___11',  # Mouth/tongue/lip
        'med15t_8yr___12',  # Larynx-windpipe
        'med15t_8yr___13',  # Throat-pharynx
        'med15t_8yr___17',  # Lymphoma
        'med15t_8yr___20',  # Skin (Don't know what kind)
        'med15t_8yr___21',  # Ovary
        'med15t_8yr___23',  # Pancreas
        'med15t_8yr___26',  # Soft tissue (muscle or fat)
        'med15t_8yr___27',  # Thyroid
        'hmz_med_cancer_other_bprhs_8'  # Include existing 'other'
    ]


    # Harmonization Any 1 → 1 All NaN → NaN Else → 0
    def harmonize_cancer(row):
        if row[cancer_vars].isna().all():
            return np.nan
        elif (row[cancer_vars] == 1).any():
            return 1
        else:
            return 0


    df_hmz_health_bprhs_8['hmz_med_cancer_other_bprhs_8'] = df_hmz_health_bprhs_8.apply(harmonize_cancer, axis=1)

    # Saving
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)






    # --------------------------------------
    # PROSPECT
    # --------------------------------------
    # variables related to cancer - some studyids have more than one cancer so it was not possible to 
    # create one single hmz variable

    #renaming the variables
    df_hmz_health_prospect.rename(columns={'med26e___1': 'hmz_med_cancer_lung_prospect'}, inplace=True)
    df_hmz_health_prospect.rename(columns={'med26e___2': 'hmz_med_cancer_breast_prospect'}, inplace=True)
    df_hmz_health_prospect.rename(columns={'med26e___3': 'hmz_med_cancer_cervical_prospect'}, inplace=True)
    df_hmz_health_prospect.rename(columns={'med26e___4': 'hmz_med_cancer_blood_prospect'}, inplace=True)
    df_hmz_health_prospect.rename(columns={'med26e___5': 'hmz_med_cancer_testicular_prospect'}, inplace=True)
    df_hmz_health_prospect.rename(columns={'med26e___6': 'hmz_med_cancer_bone_prospect'}, inplace=True)
    df_hmz_health_prospect.rename(columns={'med26e___7': 'hmz_med_cancer_melanoma_prospect'}, inplace=True)
    df_hmz_health_prospect.rename(columns={'med26e___8': 'hmz_med_cancer_skin_prospect'}, inplace=True)
    df_hmz_health_prospect.rename(columns={'med26e___9': 'hmz_med_cancer_brain_prospect'}, inplace=True)
    df_hmz_health_prospect.rename(columns={'med26e___10': 'hmz_med_cancer_stomach_prospect'}, inplace=True)
    df_hmz_health_prospect.rename(columns={'med26e___11': 'hmz_med_cancer_colon_prospect'}, inplace=True)
    df_hmz_health_prospect.rename(columns={'med26e___12': 'hmz_med_cancer_uterine_prospect'}, inplace=True)
    df_hmz_health_prospect.rename(columns={'med26e___13': 'hmz_med_cancer_prostate_prospect'}, inplace=True)
    df_hmz_health_prospect.rename(columns={'med26e___14': 'hmz_med_cancer_liver_prospect'}, inplace=True)
    df_hmz_health_prospect.rename(columns={'med26e___15': 'hmz_med_cancer_other_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)




    # subject has the condition currently
    # --------------------------------------
    # BPRHS
    # --------------------------------------

    # transformation
    # Apply transformation: if hmz_med_cancer == 0 --> med15c is NaN; if hmz_med_cancer == nan --> med15c is Nan
    # bprhs v1 (hmz_med_cancer_bprhs_0, med15c)
    if "hmz_med_cancer_bprhs_0" in df_hmz_health_bprhs_0.columns and "med15c" in df_hmz_health_bprhs_0.columns:
        df_hmz_health_bprhs_0["hmz_med_cancer_bprhs_0"] = pd.to_numeric(df_hmz_health_bprhs_0["hmz_med_cancer_bprhs_0"], errors="coerce")
        df_hmz_health_bprhs_0.loc[df_hmz_health_bprhs_0["hmz_med_cancer_bprhs_0"].isna(), "med15c"] = np.nan
        df_hmz_health_bprhs_0.loc[df_hmz_health_bprhs_0["hmz_med_cancer_bprhs_0"] == 0, 'med15c'] = np.nan

    # bprhs v2 (hmz_med_cancer_bprhs_2, med15c_2yr)
    if "hmz_med_cancer_bprhs_2" in df_hmz_health_bprhs_2.columns and "med15c_2yr" in df_hmz_health_bprhs_2.columns:
        df_hmz_health_bprhs_2["hmz_med_cancer_bprhs_2"] = pd.to_numeric(df_hmz_health_bprhs_2["hmz_med_cancer_bprhs_2"], errors="coerce")
        df_hmz_health_bprhs_2.loc[df_hmz_health_bprhs_2["hmz_med_cancer_bprhs_2"].isna(), "med15c_2yr"] = np.nan
        df_hmz_health_bprhs_2.loc[df_hmz_health_bprhs_2["hmz_med_cancer_bprhs_2"] == 0, "med15c_2yr"] = np.nan


    # bprhs v3 (hmz_med_cancer_bprhs_5, med15c_5yr)
    if "hmz_med_cancer_bprhs_5" in df_hmz_health_bprhs_5.columns and "med15c_5yr" in df_hmz_health_bprhs_5.columns:
        df_hmz_health_bprhs_5["hmz_med_cancer_bprhs_5"] = pd.to_numeric(df_hmz_health_bprhs_5["hmz_med_cancer_bprhs_5"], errors="coerce")
        df_hmz_health_bprhs_5.loc[df_hmz_health_bprhs_5["hmz_med_cancer_bprhs_5"].isna(), "med15c_5yr"] = np.nan
        df_hmz_health_bprhs_5.loc[df_hmz_health_bprhs_5["hmz_med_cancer_bprhs_5"] == 0, "med15c_5yr"] = np.nan


    # Renaming
    df_hmz_health_bprhs_0.rename(columns={'med15c': 'hmz_med_cancer_today_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'med15c_2yr': 'hmz_med_cancer_today_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_5.rename(columns={'med15c_5yr': 'hmz_med_cancer_today_bprhs_5'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'med15c_8yr': 'hmz_med_cancer_today_bprhs_8'}, inplace=True)


    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)




    # --------------------------------------
    # PROSPECT
    # --------------------------------------

    # Recoding  96, 97, 98 -> as NaN
    df_hmz_health_prospect['med26d'] = df_hmz_health_prospect['med26d'].replace({ 98: np.nan})

    # Renaming
    df_hmz_health_prospect.rename(columns={'med26d': 'hmz_med_cancer_today_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)





    # medication cancer
    # --------------------------------------
    # BPRHS
    # --------------------------------------

    # transformation
    # Apply transformation: if hmz_med_cancer == 0 --> med15b is NaN; if hmz_med_cancer == nan --> med15b is Nan
    # bprhs v1 (hmz_med_cancer_bprhs_0, med15b)
    if "hmz_med_cancer_bprhs_0" in df_hmz_health_bprhs_0.columns and "med15b" in df_hmz_health_bprhs_0.columns:
        df_hmz_health_bprhs_0["hmz_med_cancer_bprhs_0"] = pd.to_numeric(df_hmz_health_bprhs_0["hmz_med_cancer_bprhs_0"], errors="coerce")
        df_hmz_health_bprhs_0.loc[df_hmz_health_bprhs_0["hmz_med_cancer_bprhs_0"].isna(), "med15b"] = np.nan
        df_hmz_health_bprhs_0.loc[df_hmz_health_bprhs_0["hmz_med_cancer_bprhs_0"] == 0, 'med15b'] = np.nan

    # bprhs v2 (hmz_med_cancer_bprhs_2, med15b_2yr)
    if "hmz_med_cancer_bprhs_2" in df_hmz_health_bprhs_2.columns and "med15b_2yr" in df_hmz_health_bprhs_2.columns:
        df_hmz_health_bprhs_2["hmz_med_cancer_bprhs_2"] = pd.to_numeric(df_hmz_health_bprhs_2["hmz_med_cancer_bprhs_2"], errors="coerce")
        df_hmz_health_bprhs_2.loc[df_hmz_health_bprhs_2["hmz_med_cancer_bprhs_2"].isna(), "med15b_2yr"] = np.nan
        df_hmz_health_bprhs_2.loc[df_hmz_health_bprhs_2["hmz_med_cancer_bprhs_2"] == 0, "med15b_2yr"] = np.nan



    # Renaming
    df_hmz_health_bprhs_0.rename(columns={'med15b': 'hmz_med_cancer_medication_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'med15b_2yr': 'hmz_med_cancer_medication_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'med15b_8yr': 'hmz_med_cancer_medication_bprhs_8'}, inplace=True)


    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)


    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)


    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)




    # --------------------------------------
    # PROSPECT
    # --------------------------------------

    # Renaming
    df_hmz_health_prospect.rename(columns={'med26a': 'hmz_med_cancer_medication_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)





    # stomach-intestine
    # --------------------------------------
    # BPRHS
    # --------------------------------------

    # Renaming
    df_hmz_health_bprhs_0.rename(columns={'med12': 'hmz_med_stomach_intestine_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'med12x_2yr': 'hmz_med_stomach_intestine_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_5.rename(columns={'med12x_5yr': 'hmz_med_stomach_intestine_bprhs_5'}, inplace=True)


    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)





    # Creating a variable about stomach problems for bprhs_12
    stomach_intestine_vars = ['med12_1_8yr', 'med12_2_8yr', 'med12_3_8yr', 'med12_4_8yr', 'med12_5_8yr', 'med12_6_8yr']

    # Creating the new variable: 1 if any column has 1, else 0
    df_hmz_health_bprhs_8['hmz_med_stomach_intestine_bprhs_8'] = df_hmz_health_bprhs_8[stomach_intestine_vars].apply(
        lambda row: np.nan if row.isna().all() else row.max(), axis=1
    )


    # Saving
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)





    # Type of stomach-intestine problem
    # --------------------------------------
    # BPRHS
    # --------------------------------------

    # For harmonization purposes, some of these variables need to be set to "other"
    stomach_vars = ["med12_2_8yr", "med12_3_8yr", "med12_6_8yr"]

    # Update med12_6_8yr 
    # If **all values** in med12_2_8yr, med12_3_8yr, med12_6_8yr are NaN → Keep **NaN**.
    # If **any value is 1** → Set to **1** (indicates presence of condition).
    # Else → Set to **0** (no condition reported).

    def harmonize_stomach(row):
        if row[stomach_vars].isna().all():
            return np.nan
        elif (row[stomach_vars] == 1).any():
            return 1
        else:
            return 0

    # 
    df_hmz_health_bprhs_8["med12_6_8yr"] = df_hmz_health_bprhs_8.apply(harmonize_stomach, axis=1)



    # Renaming
    df_hmz_health_bprhs_8.rename(columns={'med12_1_8yr': 'hmz_med_stomach_intestine_ulcer_bprhs_8', 
                                         # 'med12_2_8yr': 'hmz_med_stomach_intestine_ibs_bprhs_8',
                                          #'med12_3_8yr': 'hmz_med_stomach_intestine_ulcerative_colitis_bprhs_8',
                                          'med12_4_8yr': 'hmz_med_stomach_intestine_diverticular_bprhs_8',
                                          'med12_5_8yr': 'hmz_med_stomach_intestine_crohn_bprhs_8',
                                          'med12_6_8yr': 'hmz_med_stomach_intestine_other_bprhs_8' }, inplace=True)




    # Saving
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)




    # --------------------------------------
    # PROSPECT
    # --------------------------------------

    # For harmonization purposes, update 'other' based on specific stomach variables
    stomach_vars = ["med32e___1", "med32e___4", "med32e___5", "med32e___6", "med32e___8"]

    def harmonize_stomach_prospect(row):
        if row[stomach_vars].isna().all():
            return np.nan
        elif (row[stomach_vars] == 1).any():
            return 1
        else:
            return 0

    df_hmz_health_prospect["med32e___8"] = df_hmz_health_prospect.apply(harmonize_stomach_prospect, axis=1)


    # Renaming
    df_hmz_health_prospect.rename(columns={
        'med32e___2': 'hmz_med_stomach_intestine_crohn_prospect',
        'med32e___3': 'hmz_med_stomach_intestine_ulcer_prospect',
        'med32e___7': 'hmz_med_stomach_intestine_diverticular_prospect',
        'med32e___8': 'hmz_med_stomach_intestine_other_prospect'
    }, inplace=True)


    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)


    # Check result
    print(df_hmz_health_prospect['hmz_med_stomach_intestine_other_prospect'].value_counts(dropna=False))


    # medication for stomach intestine
    # --------------------------------------
    # BPRHS
    # --------------------------------------

    # bprhs v1
    if "hmz_med_stomach_intestine_bprhs_0" in df_hmz_health_bprhs_0.columns and "med12b" in df_hmz_health_bprhs_0.columns:
        df_hmz_health_bprhs_0["hmz_med_stomach_intestine_bprhs_0"] = pd.to_numeric(df_hmz_health_bprhs_0["hmz_med_stomach_intestine_bprhs_0"], errors="coerce")
        df_hmz_health_bprhs_0.loc[df_hmz_health_bprhs_0["hmz_med_stomach_intestine_bprhs_0"].isna(), "med12b"] = np.nan
        df_hmz_health_bprhs_0.loc[df_hmz_health_bprhs_0["hmz_med_stomach_intestine_bprhs_0"] == 0, "med12b"] = np.nan


    # bprhs v2
    if "hmz_med_stomach_intestine_bprhs_2" in df_hmz_health_bprhs_2.columns and "med12b_2yr" in df_hmz_health_bprhs_2.columns:
        df_hmz_health_bprhs_2["hmz_med_stomach_intestine_bprhs_2"] = pd.to_numeric(df_hmz_health_bprhs_2["hmz_med_stomach_intestine_bprhs_2"], errors="coerce")
        df_hmz_health_bprhs_2.loc[df_hmz_health_bprhs_2["hmz_med_stomach_intestine_bprhs_2"].isna(), "med12b_2yr"] = np.nan
        df_hmz_health_bprhs_2.loc[df_hmz_health_bprhs_2["hmz_med_stomach_intestine_bprhs_2"] == 0, "med12b_2yr"] = np.nan


    # Renaming
    df_hmz_health_bprhs_0.rename(columns={'med12b': 'hmz_med_stomach_intestine_medication_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'med12b_2yr': 'hmz_med_stomach_intestine_medication_bprhs_2'}, inplace=True)


    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)


    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)




    # creating a new variable for bprhs v4
    stomach_intestine_vars = ['med12_1b_8yr', 'med12_2b_8yr', 'med12_3b_8yr', 'med12_4b_8yr', 'med12_5b_8yr', 'med12_6b_8yr']

    # Creating the new variable: 1 if any column has 1, else 0
    df_hmz_health_bprhs_8['hmz_med_stomach_intestine_medication_bprhs_8'] = df_hmz_health_bprhs_8[stomach_intestine_vars].max(axis=1)


    # Saving
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)






    # stomach-intestine
    # --------------------------------------
    # PROSPECT
    # --------------------------------------
    # med32
    # Recoding
    df_hmz_health_prospect['med32'] = df_hmz_health_prospect['med32'].replace({98: np.nan})

    # Renaming
    df_hmz_health_prospect.rename(columns={'med32': 'hmz_med_stomach_intestine_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)



    #med32a
    # Recoding
    df_hmz_health_prospect['med32a'] = df_hmz_health_prospect['med32a'].replace({96: np.nan})

    # Renaming
    df_hmz_health_prospect.rename(columns={'med32a': 'hmz_med_stomach_intestine_medication_prospect'}, inplace=True)


    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)



    # respiratory condition today
    # --------------------------------------
    # BPRHS
    # --------------------------------------

    # transformation
    # Apply transformation: if hmz_med_stomach_intestine == 0 --> med12c is NaN; if hmz_med_stomach_intestine == nan --> med12c is Nan
    # bprhs v1 (hmz_med_stomach_intestine_bprhs_0, med12c)
    if "hmz_med_stomach_intestine_bprhs_0" in df_hmz_health_bprhs_0.columns and "med12c" in df_hmz_health_bprhs_0.columns:
        df_hmz_health_bprhs_0["hmz_med_stomach_intestine_bprhs_0"] = pd.to_numeric(df_hmz_health_bprhs_0["hmz_med_stomach_intestine_bprhs_0"], errors="coerce")
        df_hmz_health_bprhs_0.loc[df_hmz_health_bprhs_0["hmz_med_stomach_intestine_bprhs_0"].isna(), "med12c"] = np.nan
        df_hmz_health_bprhs_0.loc[df_hmz_health_bprhs_0["hmz_med_stomach_intestine_bprhs_0"] == 0, 'med12c'] = np.nan

    # bprhs v2 (hmz_med_stomach_intestine_bprhs_2, med12c_2yr)
    if "hmz_med_stomach_intestine_bprhs_2" in df_hmz_health_bprhs_2.columns and "med12c_2yr" in df_hmz_health_bprhs_2.columns:
        df_hmz_health_bprhs_2["hmz_med_stomach_intestine_bprhs_2"] = pd.to_numeric(df_hmz_health_bprhs_2["hmz_med_stomach_intestine_bprhs_2"], errors="coerce")
        df_hmz_health_bprhs_2.loc[df_hmz_health_bprhs_2["hmz_med_stomach_intestine_bprhs_2"].isna(), "med12c_2yr"] = np.nan
        df_hmz_health_bprhs_2.loc[df_hmz_health_bprhs_2["hmz_med_stomach_intestine_bprhs_2"] == 0, "med12c_2yr"] = np.nan

    # bprhs v3
    if "hmz_med_stomach_intestine_bprhs_5" in df_hmz_health_bprhs_5.columns and "med12c_5yr" in df_hmz_health_bprhs_5.columns:
        df_hmz_health_bprhs_5["hmz_med_stomach_intestine_bprhs_5"] = pd.to_numeric(df_hmz_health_bprhs_5["hmz_med_stomach_intestine_bprhs_5"], errors="coerce")
        df_hmz_health_bprhs_5.loc[df_hmz_health_bprhs_5["hmz_med_stomach_intestine_bprhs_5"].isna(), "med12c_5yr"] = np.nan
        df_hmz_health_bprhs_5.loc[df_hmz_health_bprhs_5["hmz_med_stomach_intestine_bprhs_5"] == 0, "med12c_5yr"] = np.nan


    # Renaming
    df_hmz_health_bprhs_0.rename(columns={'med12c': 'hmz_med_stomach_intestine_today_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'med12c_2yr': 'hmz_med_stomach_intestine_today_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_5.rename(columns={'med12c_5yr': 'hmz_med_stomach_intestine_today_bprhs_5'}, inplace=True)


    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)


    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)


    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)




    # Creating the variable for bprhs v4

    # creating a new variable for bprhs v4
    stomach_intestine_vars = ['med12_1c_8yr', 'med12_2c_8yr', 'med12_3c_8yr', 'med12_4c_8yr', 'med12_5c_8yr', 'med12_6c_8yr']

    # Creating the new variable: 1 if any column has 1, else 0
    df_hmz_health_bprhs_8['hmz_med_stomach_intestine_today_bprhs_8'] = df_hmz_health_bprhs_8[stomach_intestine_vars].max(axis=1)

    # Saving
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)




    # --------------------------------------
    # PROSPECT
    # --------------------------------------

    # Recoding
    df_hmz_health_prospect['med32d'] = df_hmz_health_prospect['med32d'].replace({98: np.nan})

    # Renaming
    df_hmz_health_prospect.rename(columns={'med32d': 'hmz_med_stomach_intestine_today_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)


    # anxiety
    # --------------------------------------
    # BPRHS
    # --------------------------------------


    # Renaming 
    # Renamingin all datasets
    df_hmz_health_bprhs_0.rename(columns={ "med17":"hmz_med_anxiety_bprhs_0" }, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={  "med17_2yr":"hmz_med_anxiety_bprhs_2"}, inplace=True)
    df_hmz_health_bprhs_5.rename(columns={ "med17x_5yr":"hmz_med_anxiety_bprhs_5"}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={ "med17_8yr":"hmz_med_anxiety_bprhs_8"}, inplace=True)


    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)


    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)


    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)


    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)





    # --------------------------------------
    # PROSPECT
    # --------------------------------------

    # Recoding  96, 97, 98 -> as NaN
    df_hmz_health_prospect['med34'] = df_hmz_health_prospect['med34'].replace({97: np.nan, 98: np.nan})

    # Renaming
    df_hmz_health_prospect.rename(columns={'med34': 'hmz_med_anxiety_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)




    # medication

    # --------------------------------------
    # BPRHS
    # --------------------------------------

    # bprhs v1
    if "hmz_med_anxiety_bprhs_0" in df_hmz_health_bprhs_0.columns and "med17b" in df_hmz_health_bprhs_0.columns:
        df_hmz_health_bprhs_0["hmz_med_anxiety_bprhs_0"] = pd.to_numeric(df_hmz_health_bprhs_0["hmz_med_anxiety_bprhs_0"], errors="coerce")
        df_hmz_health_bprhs_0.loc[df_hmz_health_bprhs_0["hmz_med_anxiety_bprhs_0"].isna(), "med17b"] = np.nan
        df_hmz_health_bprhs_0.loc[df_hmz_health_bprhs_0["hmz_med_anxiety_bprhs_0"] == 0, "med17b"] = np.nan

    # bprhs v2
    if "hmz_med_anxiety_bprhs_2" in df_hmz_health_bprhs_2.columns and "med17b_2yr" in df_hmz_health_bprhs_2.columns:
        df_hmz_health_bprhs_2["hmz_med_anxiety_bprhs_2"] = pd.to_numeric(df_hmz_health_bprhs_2["hmz_med_anxiety_bprhs_2"], errors="coerce")
        df_hmz_health_bprhs_2.loc[df_hmz_health_bprhs_2["hmz_med_anxiety_bprhs_2"].isna(), "med17b_2yr"] = np.nan
        df_hmz_health_bprhs_2.loc[df_hmz_health_bprhs_2["hmz_med_anxiety_bprhs_2"] == 0, "med17b_2yr"] = np.nan

    # bprhs v4
    if "med17b_8yr" in df_hmz_health_bprhs_8.columns:
        df_hmz_health_bprhs_8["med17b_8yr"] = df_hmz_health_bprhs_8["med17b_8yr"].replace({97: np.nan, 98: np.nan})

    # Renaming to harmonized variable names
    df_hmz_health_bprhs_0.rename(columns={'med17b': 'hmz_med_anxiety_medication_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'med17b_2yr': 'hmz_med_anxiety_medication_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'med17b_8yr': 'hmz_med_anxiety_medication_bprhs_8'}, inplace=True)

    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)


    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)


    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)




    # --------------------------------------
    # PROSPECT
    # --------------------------------------

    df_hmz_health_prospect['med34a'] = df_hmz_health_prospect['med34a'].replace({97: np.nan, 98: np.nan})
    print(df_hmz_health_prospect['med34a'].value_counts(dropna=False).sort_index())
    # Renaming
    df_hmz_health_prospect.rename(columns={'med34a': 'hmz_med_anxiety_medication_prospect'}, inplace=True)
    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)

    print(df_hmz_health_prospect['hmz_med_anxiety_medication_prospect'].value_counts())


    # --------------------------------------
    # BPRHS
    # --------------------------------------


    if "hmz_med_anxiety_bprhs_0" in df_hmz_health_bprhs_0.columns and "med17c" in df_hmz_health_bprhs_0.columns:
        df_hmz_health_bprhs_0["hmz_med_anxiety_bprhs_0"] = pd.to_numeric(df_hmz_health_bprhs_0["hmz_med_anxiety_bprhs_0"], errors="coerce")
        df_hmz_health_bprhs_0.loc[df_hmz_health_bprhs_0["hmz_med_anxiety_bprhs_0"].isna(), "med17c"] = np.nan
        df_hmz_health_bprhs_0.loc[df_hmz_health_bprhs_0["hmz_med_anxiety_bprhs_0"] == 0, "med17c"] = np.nan



    # bprhs v1 (hmz_med_anxiety_bprhs_2, med17c_2yr)
    if "hmz_med_anxiety_bprhs_2" in df_hmz_health_bprhs_2.columns and "med17c_2yr" in df_hmz_health_bprhs_2.columns:
        df_hmz_health_bprhs_2["hmz_med_anxiety_bprhs_2"] = pd.to_numeric(df_hmz_health_bprhs_2["hmz_med_anxiety_bprhs_2"], errors="coerce")
        df_hmz_health_bprhs_2.loc[df_hmz_health_bprhs_2["hmz_med_anxiety_bprhs_2"].isna(), "med17c_2yr"] = np.nan
        df_hmz_health_bprhs_2.loc[df_hmz_health_bprhs_2["hmz_med_anxiety_bprhs_2"] == 0, "med17c_2yr"] = np.nan

    # bprhs v3 (hmz_med_anxiety_bprhs_5, med17c_5yr)
    if "hmz_med_anxiety_bprhs_5" in df_hmz_health_bprhs_5.columns and "med17c_5yr" in df_hmz_health_bprhs_5.columns:
        df_hmz_health_bprhs_5["hmz_med_anxiety_bprhs_5"] = pd.to_numeric(df_hmz_health_bprhs_5["hmz_med_anxiety_bprhs_5"], errors="coerce")
        df_hmz_health_bprhs_5.loc[df_hmz_health_bprhs_5["hmz_med_anxiety_bprhs_5"].isna(), "med17c_5yr"] = np.nan
        df_hmz_health_bprhs_5.loc[df_hmz_health_bprhs_5["hmz_med_anxiety_bprhs_5"] == 0, "med17c_5yr"] = np.nan



    # Renaming
    df_hmz_health_bprhs_0.rename(columns={'med17c': 'hmz_med_anxiety_today_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'med17c_2yr': 'hmz_med_anxiety_today_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_5.rename(columns={'med17c_5yr': 'hmz_med_anxiety_today_bprhs_5'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'med17c_8yr': 'hmz_med_anxiety_today_bprhs_8'}, inplace=True)



    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)





    # --------------------------------------
    # PROSPECT
    # --------------------------------------

    #  creating variable anxiety today  for prospect using med34d__0 and med34d__1
    df_hmz_health_prospect["hmz_med_anxiety_today_prospect"] = df_hmz_health_prospect.apply(
        lambda row: 1 if row["med34d___1"] == 1 
        else 0 if row["med34d___0"] == 1 
        else pd.NA,
        axis=1)



    # depression
    # --------------------------------------
    # BPRHS
    # --------------------------------------


    # Renaming 

    df_hmz_health_bprhs_0.rename(columns={ "med18":"hmz_med_depression_bprhs_0" }, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={  "med18_2yr":"hmz_med_depression_bprhs_2"}, inplace=True)
    df_hmz_health_bprhs_5.rename(columns={ "med18x_5yr":"hmz_med_depression_bprhs_5"}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={ "med18_8yr":"hmz_med_depression_bprhs_8"}, inplace=True)


    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)





    # --------------------------------------
    # PROSPECT
    # --------------------------------------

    # Recoding  96, 97, 98 -> as NaN
    df_hmz_health_prospect['med35'] = df_hmz_health_prospect['med35'].replace({97: np.nan, 98: np.nan})

    # Renaming
    df_hmz_health_prospect.rename(columns={'med35': 'hmz_med_depression_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)




    # medication

    # --------------------------------------
    # BPRHS
    # --------------------------------------
    # bprhs v1
    if "hmz_med_depression_bprhs_0" in df_hmz_health_bprhs_0.columns and "med18b" in df_hmz_health_bprhs_0.columns:
        df_hmz_health_bprhs_0["hmz_med_depression_bprhs_0"] = pd.to_numeric(df_hmz_health_bprhs_0["hmz_med_depression_bprhs_0"], errors="coerce")
        df_hmz_health_bprhs_0.loc[df_hmz_health_bprhs_0["hmz_med_depression_bprhs_0"].isna(), "med18b"] = np.nan
        df_hmz_health_bprhs_0.loc[df_hmz_health_bprhs_0["hmz_med_depression_bprhs_0"] == 0, "med18b"] = np.nan



    # bprhs v2 (hmz_med_depression_bprhs_2, med18b_2yr)
    if "hmz_med_depression_bprhs_2" in df_hmz_health_bprhs_2.columns and "med18b_2yr" in df_hmz_health_bprhs_2.columns:
        df_hmz_health_bprhs_2["hmz_med_depression_bprhs_2"] = pd.to_numeric(df_hmz_health_bprhs_2["hmz_med_depression_bprhs_2"], errors="coerce")
        df_hmz_health_bprhs_2.loc[df_hmz_health_bprhs_2["hmz_med_depression_bprhs_2"].isna(), "med18b_2yr"] = np.nan
        df_hmz_health_bprhs_2.loc[df_hmz_health_bprhs_2["hmz_med_depression_bprhs_2"] == 0, "med18b_2yr"] = np.nan



    # Renaming
    df_hmz_health_bprhs_0.rename(columns={'med18b': 'hmz_med_depression_medication_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'med18b_2yr': 'hmz_med_depression_medication_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'med18b_8yr': 'hmz_med_depression_medication_bprhs_8'}, inplace=True)



    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)




    # --------------------------------------
    # PROSPECT
    # --------------------------------------
    # Checking variable
    print(df_hmz_health_prospect['med35a'].value_counts(dropna=False).sort_index())
    # Renaming
    df_hmz_health_prospect.rename(columns={'med35a': 'hmz_med_depression_medication_prospect'}, inplace=True)
    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)

    print(df_hmz_health_prospect['hmz_med_depression_medication_prospect'].value_counts())


    # --------------------------------------
    # BPRHS
    # --------------------------------------
    # bprhs v1
    if "hmz_med_depression_bprhs_0" in df_hmz_health_bprhs_0.columns and "med18c" in df_hmz_health_bprhs_0.columns:
        df_hmz_health_bprhs_0["hmz_med_depression_bprhs_0"] = pd.to_numeric(df_hmz_health_bprhs_0["hmz_med_depression_bprhs_0"], errors="coerce")
        df_hmz_health_bprhs_0.loc[df_hmz_health_bprhs_0["hmz_med_depression_bprhs_0"].isna(), "med18c"] = np.nan
        df_hmz_health_bprhs_0.loc[df_hmz_health_bprhs_0["hmz_med_depression_bprhs_0"] == 0, "med18c"] = np.nan



    # bprhs v2 (hmz_med_depression_bprhs_2, med18c_2yr)
    if "hmz_med_depression_bprhs_2" in df_hmz_health_bprhs_2.columns and "med18c_2yr" in df_hmz_health_bprhs_2.columns:
        df_hmz_health_bprhs_2["hmz_med_depression_bprhs_2"] = pd.to_numeric(df_hmz_health_bprhs_2["hmz_med_depression_bprhs_2"], errors="coerce")
        df_hmz_health_bprhs_2.loc[df_hmz_health_bprhs_2["hmz_med_depression_bprhs_2"].isna(), "med18c_2yr"] = np.nan
        df_hmz_health_bprhs_2.loc[df_hmz_health_bprhs_2["hmz_med_depression_bprhs_2"] == 0, "med18c_2yr"] = np.nan

    # bprhs v3 (hmz_med_depression_bprhs_5, med18c_5yr)
    if "hmz_med_depression_bprhs_5" in df_hmz_health_bprhs_5.columns and "med18c_5yr" in df_hmz_health_bprhs_5.columns:
        df_hmz_health_bprhs_5["hmz_med_depression_bprhs_5"] = pd.to_numeric(df_hmz_health_bprhs_5["hmz_med_depression_bprhs_5"], errors="coerce")
        df_hmz_health_bprhs_5.loc[df_hmz_health_bprhs_5["hmz_med_depression_bprhs_5"].isna(), "med18c_5yr"] = np.nan
        df_hmz_health_bprhs_5.loc[df_hmz_health_bprhs_5["hmz_med_depression_bprhs_5"] == 0, "med18c_5yr"] = np.nan


    # Renaming
    df_hmz_health_bprhs_0.rename(columns={'med18c': 'hmz_med_depression_today_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'med18c_2yr': 'hmz_med_depression_today_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_5.rename(columns={'med18c_5yr': 'hmz_med_depression_today_bprhs_5'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'med18c_8yr': 'hmz_med_depression_today_bprhs_8'}, inplace=True)



    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)





    # --------------------------------------
    # PROSPECT
    # --------------------------------------

    df_hmz_health_prospect['med35d'] = df_hmz_health_prospect['med35d'].replace({ 98: np.nan})
    # Renaming
    df_hmz_health_prospect.rename(columns={'med35d': 'hmz_med_depression_today_prospect'}, inplace=True)
    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)





    # eye disease
    # --------------------------------------
    # BPRHS
    # --------------------------------------

    # Renaming 
    # Renamingin all datasets
    df_hmz_health_bprhs_0.rename(columns={ "med16":"hmz_med_eye_bprhs_0" }, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={  "med16_2yr":"hmz_med_eye_bprhs_2"}, inplace=True)
    df_hmz_health_bprhs_5.rename(columns={ "med16x_5yr":"hmz_med_eye_bprhs_5"}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={ "med16_8yr":"hmz_med_eye_bprhs_8"}, inplace=True)

    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)





    # --------------------------------------
    # PROSPECT
    # --------------------------------------
    # creating a new variable because in prospect cataract and glaucoma are individual variables
    eye_vars = ['med33e___1', 'med33e___2']

    # Creating the new variable: NaN if both are missing, else take the max (1 if any condition is present)
    df_hmz_health_prospect['hmz_med_eye_prospect'] = df_hmz_health_prospect[eye_vars].apply(
        lambda row: np.nan if row.isna().all() else row.max(), axis=1
    )

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)




    # --------------------------------------
    # BPRHS
    # --------------------------------------

    # bprhs v1
    if "hmz_med_eye_bprhs_0" in df_hmz_health_bprhs_0.columns and "med16b" in df_hmz_health_bprhs_0.columns:
        df_hmz_health_bprhs_0["hmz_med_eye_bprhs_0"] = pd.to_numeric(df_hmz_health_bprhs_0["hmz_med_eye_bprhs_0"], errors="coerce")
        df_hmz_health_bprhs_0.loc[df_hmz_health_bprhs_0["hmz_med_eye_bprhs_0"].isna(), "med16b"] = np.nan
        df_hmz_health_bprhs_0.loc[df_hmz_health_bprhs_0["hmz_med_eye_bprhs_0"] == 0, "med16b"] = np.nan



    # bprhs v2 (hmz_med_eye_bprhs_2, med16b_2yr)
    if "hmz_med_eye_bprhs_2" in df_hmz_health_bprhs_2.columns and "med16b_2yr" in df_hmz_health_bprhs_2.columns:
        df_hmz_health_bprhs_2["hmz_med_eye_bprhs_2"] = pd.to_numeric(df_hmz_health_bprhs_2["hmz_med_eye_bprhs_2"], errors="coerce")
        df_hmz_health_bprhs_2.loc[df_hmz_health_bprhs_2["hmz_med_eye_bprhs_2"].isna(), "med16b_2yr"] = np.nan
        df_hmz_health_bprhs_2.loc[df_hmz_health_bprhs_2["hmz_med_eye_bprhs_2"] == 0, "med16b_2yr"] = np.nan


    # Renaming
    df_hmz_health_bprhs_0.rename(columns={'med16b': 'hmz_med_eye_medication_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'med16b_2yr': 'hmz_med_eye_medication_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'med16b_8yr': 'hmz_med_eye_medication_bprhs_8'}, inplace=True)


    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)




    # --------------------------------------
    # PROSPECT
    # --------------------------------------
    # Renaming
    df_hmz_health_prospect.rename(columns={'med33a': 'hmz_med_eye_medication_prospect'}, inplace=True)
    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)

    print(df_hmz_health_prospect['hmz_med_eye_medication_prospect'].value_counts())



    # --------------------------------------
    # BPRHS
    # --------------------------------------
    # bprhs v1
    if "hmz_med_eye_bprhs_0" in df_hmz_health_bprhs_0.columns and "med16c" in df_hmz_health_bprhs_0.columns:
        df_hmz_health_bprhs_0["hmz_med_eye_bprhs_0"] = pd.to_numeric(df_hmz_health_bprhs_0["hmz_med_eye_bprhs_0"], errors="coerce")
        df_hmz_health_bprhs_0.loc[df_hmz_health_bprhs_0["hmz_med_eye_bprhs_0"].isna(), "med16c"] = np.nan
        df_hmz_health_bprhs_0.loc[df_hmz_health_bprhs_0["hmz_med_eye_bprhs_0"] == 0, "med16c"] = np.nan



    # bprhs v2 (hmz_med_eye_bprhs_2, med16c_2yr)
    if "hmz_med_eye_bprhs_2" in df_hmz_health_bprhs_2.columns and "med16c_2yr" in df_hmz_health_bprhs_2.columns:
        df_hmz_health_bprhs_2["hmz_med_eye_bprhs_2"] = pd.to_numeric(df_hmz_health_bprhs_2["hmz_med_eye_bprhs_2"], errors="coerce")
        df_hmz_health_bprhs_2.loc[df_hmz_health_bprhs_2["hmz_med_eye_bprhs_2"].isna(), "med16c_2yr"] = np.nan
        df_hmz_health_bprhs_2.loc[df_hmz_health_bprhs_2["hmz_med_eye_bprhs_2"] == 0, "med16c_2yr"] = np.nan

    # bprhs v3 (hmz_med_eye_bprhs_5, med16c_5yr)
    if "hmz_med_eye_bprhs_5" in df_hmz_health_bprhs_5.columns and "med16c_5yr" in df_hmz_health_bprhs_5.columns:
        df_hmz_health_bprhs_5["hmz_med_eye_bprhs_5"] = pd.to_numeric(df_hmz_health_bprhs_5["hmz_med_eye_bprhs_5"], errors="coerce")
        df_hmz_health_bprhs_5.loc[df_hmz_health_bprhs_5["hmz_med_eye_bprhs_5"].isna(), "med16c_5yr"] = np.nan
        df_hmz_health_bprhs_5.loc[df_hmz_health_bprhs_5["hmz_med_eye_bprhs_5"] == 0, "med16c_5yr"] = np.nan


    # Renaming
    df_hmz_health_bprhs_0.rename(columns={'med16c': 'hmz_med_eye_today_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'med16c_2yr': 'hmz_med_eye_today_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_5.rename(columns={'med16c_5yr': 'hmz_med_eye_today_bprhs_5'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'med16c_8yr': 'hmz_med_eye_today_bprhs_8'}, inplace=True)



    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)





    # --------------------------------------
    # PROSPECT
    # --------------------------------------

    df_hmz_health_prospect['med33d'] = df_hmz_health_prospect['med33d'].replace({96: np.nan,98: np.nan})

    # Renaming
    df_hmz_health_prospect.rename(columns={'med33d': 'hmz_med_eye_today_prospect'}, inplace=True)
    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)





    #------------------------------------------------------------------------------------------------
    # Family History
    # -----------------------------------------------------------------------------------------------

    # Family history of diabetes
    # --------------------------------------
    # BPRHS
    # --------------------------------------
    # Creating the new variable 'hmz_fh_diabetes_bprhs_5'
    df_hmz_health_bprhs_5["hmz_fh_diabetes_bprhs_5"] = (
        df_hmz_health_bprhs_5[["fhx1a_5yr", "fhx1b_5yr", "fhx1c_5yr", "fhx1d_5yr"]].max(axis=1))

    # Saving
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)



    # --------------------------------------
    # PROSPECT
    # --------------------------------------

    # Recode values: 96, 97, 98 -> NaN
    if "fhi1" in df_hmz_health_prospect.columns:
        df_hmz_health_prospect["fhi1"] = df_hmz_health_prospect["fhi1"].replace({96: np.nan, 97: np.nan, 98: np.nan})
        print("Recode complete for: fhi1")

    # Renaming
    df_hmz_health_prospect.rename(columns={"fhi1": "hmz_fh_diabetes_prospect"}, inplace=True)

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)






    # Family history of hypertension
    # --------------------------------------
    # BPRHS
    # --------------------------------------

    # Creating the new variable 'hmz_fh_hypertension_bprhs_5'
    df_hmz_health_bprhs_5["hmz_fh_hypertension_bprhs_5"] = (
        df_hmz_health_bprhs_5[["fhx2a_5yr", "fhx2b_5yr", "fhx2c_5yr", "fhx2d_5yr"]].max(axis=1))

    # Saving
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)




    # --------------------------------------
    # PROSPECT
    # --------------------------------------
    # List of base variables to recode and rename
    base_variables = ["fhi2"]

    print(df_hmz_health_prospect["fhi2"].value_counts())


    # Recode  values: 96, 97, 98 -> NaN
    for var in base_variables:
        if var in df_hmz_health_prospect.columns:
            df_hmz_health_prospect[var] = df_hmz_health_prospect[var].replace({96: np.nan, 97: np.nan, 98: np.nan})


    # Mapping for Renaming
    rename_map = {"fhi2": "hmz_fh_hypertension_prospect"}

    # Renaming
    df_hmz_health_prospect.rename(columns=rename_map, inplace=True)


    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)






    # Family history of heart attack
    # --------------------------------------
    # BPRHS
    # --------------------------------------
    # Creating the new variable 'hmz_fh_heart_attack_bprhs_5'
    df_hmz_health_bprhs_5["hmz_fh_heart_attack_bprhs_5"] = (
        df_hmz_health_bprhs_5[["fhx4a_5yr", "fhx4b_5yr", "fhx4c_5yr", "fhx4d_5yr"]].max(axis=1))


    # Saving
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)





    # --------------------------------------
    # PROSPECT
    # --------------------------------------
    # Recode values: 96, 97, 98 -> NaN
    if "fhi5" in df_hmz_health_prospect.columns:
        df_hmz_health_prospect["fhi5"] = df_hmz_health_prospect["fhi5"].replace({96: np.nan, 97: np.nan, 98: np.nan})
        print("Recode complete for: fhi5")

    # Renaming
    df_hmz_health_prospect.rename(columns={"fhi5": "hmz_fh_heart_attack_prospect"}, inplace=True)


    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)







    # Family history of heart disease

    # --------------------------------------
    # BPRHS
    # --------------------------------------

    # Creating the new variable 'hmz_fh_heart_disease_bprhs_5'
    df_hmz_health_bprhs_5["hmz_fh_heart_disease_bprhs_5"] = (
        df_hmz_health_bprhs_5[["fhx5a_5yr", "fhx5b_5yr", "fhx5c_5yr", "fhx5d_5yr"]].max(axis=1))


    # Saving
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)





    # --------------------------------------
    # PROSPECT
    # --------------------------------------

    # Recode values: 96, 97, 98 -> NaN
    if "fhi6" in df_hmz_health_prospect.columns:
        df_hmz_health_prospect["fhi6"] = df_hmz_health_prospect["fhi6"].replace({96: np.nan, 97: np.nan, 98: np.nan})
        print("Recode complete for: fhi6")

    # Renaming
    df_hmz_health_prospect.rename(columns={"fhi6": "hmz_fh_heart_disease_prospect"}, inplace=True)

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)



    # Family history of stroke

    # --------------------------------------
    # BPRHS
    # --------------------------------------

    # Creating the new variable 'hmz_fh_stroke_bprhs_5'
    df_hmz_health_bprhs_5["hmz_fh_stroke_bprhs_5"] = (
        df_hmz_health_bprhs_5[["fhx6a_5yr", "fhx6b_5yr", "fhx6c_5yr", "fhx6d_5yr"]].max(axis=1))


    # Saving
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)



    # --------------------------------------
    # PROSPECT
    # --------------------------------------

    # Recode values: 96, 97, 98 -> NaN
    if "fhi7" in df_hmz_health_prospect.columns:
        df_hmz_health_prospect["fhi7"] = df_hmz_health_prospect["fhi7"].replace({96: np.nan, 97: np.nan, 98: np.nan})
        print("Recode complete for: fhi7")

    # Renaming
    df_hmz_health_prospect.rename(columns={"fhi7": "hmz_fh_stroke_prospect"}, inplace=True)



    #------------------------------------------------------------------------------------------------
    #  Health Behaviors: Tobacco
    # -----------------------------------------------------------------------------------------------


    # --------------------------------------
    # BPRHS
    # --------------------------------------
    # Using index 1, 2
    df_hmz_health_bprhs_5['tob3_5yr'] = df_hmz_health_bprhs_5['tob3_5yr'].replace({"Si": 1, "Yes": 1, "No": 0})

    # Saving
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)



    # Renaming 
    df_hmz_health_bprhs_0.rename(columns={"tob3":"hmz_hb_tob3_bprhs_0"}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={ "tob3x_2yr":"hmz_hb_tob3_bprhs_2" }, inplace=True)
    df_hmz_health_bprhs_5.rename(columns={ "tob3_5yr":"hmz_hb_tob3_bprhs_5" }, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={ "tob3_8yr":"hmz_hb_tob3_bprhs_8"}, inplace=True)

    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)




    # --------------------------------------
    # PROSPECT
    # --------------------------------------
    df_hmz_health_prospect.rename(columns={"tob3":"hmz_hb_tob3_prospect"}, inplace=True)
    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)


    # --------------------------------------
    # BPRHS
    # --------------------------------------
    #These variables exist in baseline but refer to other survey questions so they are not included here
    base_variables = ["tob5_1","tob5_2","tob5_3","tob5_4"]

    bprhs_datasets = {
        #"Baseline": (df_hmz_health_bprhs_0, ""),
       # "2-Year": (df_hmz_health_bprhs_2, "_2yr"),
        "5-Year": (df_hmz_health_bprhs_5, "_5yr"),
        "8-Year": (df_hmz_health_bprhs_8, "_8yr") }




    df_hmz_health_bprhs_5.rename(columns={ "tob5_1_5yr":"hmz_hb_tobacco_home_bprhs_5",
                  "tob5_2_5yr":"hmz_hb_tobacco_work_bprhs_5",
                  "tob5_3_5yr":"hmz_hb_tobacco_car_bprhs_5",
                  "tob5_4_5yr":"hmz_hb_tobacco_other_bprhs_5"}, inplace=True)


    df_hmz_health_bprhs_8.rename(columns={ "tob5_1_8yr":"hmz_hb_tobacco_home_bprhs_8",
                  "tob5_2_8yr":"hmz_hb_tobacco_work_bprhs_8",
                  "tob5_3_8yr":"hmz_hb_tobacco_car_bprhs_8",
                  "tob5_4_8yr":"hmz_hb_tobacco_other_bprhs_8"}, inplace=True)


    #Recode  values:  97, 98 -> NaN
    for var in base_variables:
      if var in df_hmz_health_bprhs_5.columns:
            df_hmz_health_bprhs_5[var] = df_hmz_health_bprhs_5[var].replace({97: np.nan, 98: np.nan, 99: np.nan})


    for var in base_variables:
      if var in df_hmz_health_bprhs_8.columns:
            df_hmz_health_bprhs_8[var] = df_hmz_health_bprhs_8[var].replace({97: np.nan, 98: np.nan, 99: np.nan})



    # Saving 
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)


    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)





    # --------------------------------------
    # PROSPECT
    # -------------------------------------- 

    base_variables = ["tob12","tob13","tob14","tob15"]

    #Recode  values: 96, 97, 98 -> NaN
    for var in base_variables:
      if var in df_hmz_health_prospect.columns:
            df_hmz_health_prospect[var] = df_hmz_health_prospect[var].replace({96: np.nan, 97: np.nan, 98: np.nan})



    # Mapping for Renaming
    rename_map = {"tob12": "hmz_hb_tobacco_home_prospect",
                  "tob13": "hmz_hb_tobacco_work_prospect",
                  "tob14": "hmz_hb_tobacco_car_prospect",
                  "tob15": "hmz_hb_tobacco_other_prospect",
                  }

    # Renaming
    df_hmz_health_prospect.rename(columns=rename_map, inplace=True)

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)




    #------------------------------------------------------------------------------------------------
    # Health Behavior: Alcohol
    # -----------------------------------------------------------------------------------------------


    # --------------------------------------
    # BPRHS
    # --------------------------------------
    # Fixing a formating issue in alc6_5yr
    # Convert to string, strip whitespace and invisible characters
    df_hmz_health_bprhs_5['alc6_5yr'] = (
        df_hmz_health_bprhs_5['alc6_5yr']
        .astype(str)
        .str.strip()
        .str.replace(r'[\u00A0\s]', '', regex=True)  # removes non-breaking spaces and regular spaces
        )

    #  Replace 'S' with NaN or empty string (choose one)
    df_hmz_health_bprhs_5['alc6_5yr'] = df_hmz_health_bprhs_5['alc6_5yr'].replace('S', np.nan)  # or use '' to just blank it
    df_hmz_health_bprhs_5['alc6_5yr'] = df_hmz_health_bprhs_5['alc6_5yr'].replace('nan', np.nan)

    # Saving
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)





    # Renaming 
    df_hmz_health_bprhs_0.rename(columns={ "alc3":"hmz_hb_alcohol_bprhs_0",
                  "alc4a":"hmz_hb_alc4a_bprhs_0",
                  "alc4b":"hmz_hb_alc4b_bprhs_0"

                                        }, inplace=True)



    df_hmz_health_bprhs_2.rename(columns={  "alc3_2yr":"hmz_hb_alcohol_bprhs_2",
                  "alc4a_2yr":"hmz_hb_alc4a_bprhs_2",
                  "alc4b_2yr":"hmz_hb_alc4b_bprhs_2"                                    
                                        }, inplace=True)


    df_hmz_health_bprhs_5.rename(columns={  "alc3_5yr":"hmz_hb_alcohol_bprhs_5",
                  "alc4a_5yr":"hmz_hb_alc4a_bprhs_5",
                  "alc4b_5yr":"hmz_hb_alc4b_bprhs_5"                                  
                                        }, inplace=True)


    df_hmz_health_bprhs_8.rename(columns={ "alc3_8yr":"hmz_hb_alcohol_bprhs_8",
                  "alc4a_8yr":"hmz_hb_alc4a_bprhs_8",
                  "alc4b_8yr":"hmz_hb_alc4b_bprhs_8"      }, inplace=True)




    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)




    # --------------------------------------
    # PROSPECT
    # --------------------------------------

    # List of base variables to recode and rename
    base_variables = ["alc3","alc4a","alc4b"]

    # Mapping for Renaming
    rename_map = {"alc3":"hmz_hb_alcohol",
                  "alc4a":"hmz_hb_alc4a",
                  "alc4b":"hmz_hb_alc4b",

    }

    # Recoding  values: 96, 97, 98 -> NaN
    for var in base_variables:
        if var in df_hmz_health_prospect.columns:
           df_hmz_health_prospect[var] = df_hmz_health_prospect[var].replace({96: np.nan, 97: np.nan, 98: np.nan})


    # Rename variables with `_prospect` suffix
    rename_with_suffix = {var: new_name + "_prospect" for var, new_name in rename_map.items()}
    df_hmz_health_prospect.rename(columns=rename_with_suffix, inplace=True)


    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)





    #-------------------------------------------------------------------

    #------------------------------------------------------------------------------------------------
    #  Health Behavior: Sleep
    # -----------------------------------------------------------------------------------------------


    # --------------------------------------
    # BPRHS
    # --------------------------------------


    base_variables = ["slp1", "slp2","slp2t","slp3a","slp3b","slp3c","slp3d","slp3e","slp4","slp5"]

    # decoding byte strings
    def clean_pmed1(value):
        if isinstance(value, str):  
            return value.strip().lower() 
        return np.nan  



    # Fixing some issues
    # removing some characters
    df_hmz_health_bprhs_5['slp2_5yr'] = df_hmz_health_bprhs_5['slp2_5yr'].replace({'11': '11:00', '10': '10:00','9': '9:00','12': '12:00','1': '1:00', 
                                                                                   '8': '8:00', '11;00': '11:00', '7': '7:00', '6:00pm': '6:00',
                                                                                 '2:00am': '2:00', 'todo el dia en la cama': np.nan,'2': '2:00'})


    # Saving
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)



    #changing am pm to 1 and 2
    df_hmz_health_bprhs_5['slp2t_5yr'] = df_hmz_health_bprhs_5['slp2t_5yr'].replace({'a.m.': 1, 'p.m.': 2})


    # Saving
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)



    # Renaming 
    # Renamingin 5yr dataset

    df_hmz_health_bprhs_5.rename(columns={  "slp1_5yr":"hmz_hb_slp1_bprhs_5",
                  "slp2_5yr":"hmz_hb_slp2_bprhs_5",
                  "slp2t_5yr":"hmz_hb_slp2t_ampm_bprhs_5",
                  "slp3a_5yr":"hmz_hb_slp_problem_i_bprhs_5",
                  "slp3b_5yr":"hmz_hb_slp_problem_ii_bprhs_5",
                  "slp3c_5yr":"hmz_hb_slp_problem_iii_bprhs_5",
                  "slp3d_5yr":"hmz_hb_slp_problem_iv_bprhs_5",
                  "slp3e_5yr":"hmz_hb_slp_problem_v_bprhs_5",
                  "slp4_5yr":"hmz_hb_slp_snore_bprhs_5",
                  "slp5_5yr":"hmz_hb_slp_snore_ii_bprhs_5"                                
                                        }, inplace=True)




    # Saving
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)




    # --------------------------------------
    # PROSPECT
    # --------------------------------------

    # Mapping for Renaming
    rename_map = {
        "slp1": "hmz_hb_slp1",
        "slp2": "hmz_hb_slp2",
        "slp2a": "hmz_hb_slp2t_ampm",
        "slp5": "hmz_hb_slp_problem_i",
        "slp6": "hmz_hb_slp_problem_ii",
        "slp7": "hmz_hb_slp_problem_iii",
        "slp8": "hmz_hb_slp_problem_iv",
        "slp9": "hmz_hb_slp_problem_v",
        "slp10a": "hmz_hb_slp_snore",
        "slp10b": "hmz_hb_slp_snore_ii"
    }

    # Define base variables for recoding
    base_variables = list(rename_map.keys())

    # Recode values: 96, 97, 98 -> NaN
    for var in base_variables:
        if var in df_hmz_health_prospect.columns:
            df_hmz_health_prospect[var] = df_hmz_health_prospect[var].replace({96: np.nan, 97: np.nan, 98: np.nan})

    # Rename variables with `_prospect` suffix
    rename_with_suffix = {var: new_name + "_prospect" for var, new_name in rename_map.items()}
    df_hmz_health_prospect.rename(columns=rename_with_suffix, inplace=True)

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)



    #------------------------------------------------------------------------------------------------
    #  Health Behavior: Perceived Stress
    # -----------------------------------------------------------------------------------------------

    # --------------------------------------
    # BPRHS
    # --------------------------------------

    # hmz_pss	"Perceived stress score
    # PSS1 + PSS2 + PSS3 + PSS4 + PSS5 + PSS6 + PSS7 + PSS8 + PSS9 + PSS10 + PSS11 + PSS12 + PSS 13 + PSS14;"


    # Transformation: reversing the order of some individual pss variables in bprhs v4
    # the variable pss does not exist in bprhs_8 but we can compute by adding the pss1 to pss14 variables
    # however, the pss individual variables in bprhs v4 do not follow the reversed order as some of the 
    # identical varibles in bprhs v1 and v2 so we first need to reverse the order of these variables
    pss_vars = ['pss1_8yr', 'pss2_8yr', 'pss3_8yr', 'pss4_8yr', 'pss5_8yr', 'pss6_8yr', 
                'pss7_8yr', 'pss8_8yr', 'pss9_8yr', 'pss10_8yr', 'pss11_8yr', 'pss12_8yr', 
                'pss13_8yr', 'pss14_8yr']


    # recoding 0 - 4, 1-3, 2-2,3-1, 4,0 
    subset_pss_variables = ['pss4_8yr', 'pss5_8yr', 'pss6_8yr', 'pss7_8yr', 'pss9_8yr', 'pss10_8yr', 'pss13_8yr']
    # transformation
    df_hmz_health_bprhs_8[subset_pss_variables] = df_hmz_health_bprhs_8[subset_pss_variables].replace({0:4, 1:3, 2:2, 3:1, 4:0})

    # Saving
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)




    # Creating the new variable pss in bprhs v4 by summing the variables pss1_8yr to pss_14 
    df_hmz_health_bprhs_8['hmz_pss_bprhs_8'] = df_hmz_health_bprhs_8[pss_vars].apply(
        lambda row: np.nan if row.isna().any() else row.sum(),
        axis=1
    )


    # Creating a new variable pss_a in bprhs v4 with imputed mean of pss1_8yr-pss14_8yr if 7 or less are missing
    subset_pss_a_variables = ['pss1_8yr', 'pss2_8yr', 'pss3_8yr', 'pss4_8yr', 'pss5_8yr', 'pss6_8yr', 
                              'pss7_8yr', 'pss8_8yr', 'pss9_8yr', 'pss10_8yr', 'pss11_8yr', 
                              'pss12_8yr', 'pss13_8yr', 'pss14_8yr']

    # Transformation: Impute mean if 7 or fewer are missing, else set NaN
    df_hmz_health_bprhs_8['hmz_pss_a_bprhs_8'] = df_hmz_health_bprhs_8[subset_pss_a_variables].apply(
        lambda row: np.nan if row.isna().sum() > 7 else row.fillna(row.mean()).sum(),
        axis=1
    )

    # Saving
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)




    # renaming the pss sum variable and pss_a in bprhs v1, v2, and v3 
    df_hmz_health_bprhs_0.rename(columns={"pss": "hmz_pss_bprhs_0"}, inplace=True)
    df_hmz_health_bprhs_0.rename(columns={"pss_a": "hmz_pss_a_bprhs_0"}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={"pss_2yr": "hmz_pss_bprhs_2"}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={"pss_a_2yr": "hmz_pss_a_bprhs_2"}, inplace=True)
    df_hmz_health_bprhs_5.rename(columns={"pss_5yr": "hmz_pss_bprhs_5"}, inplace=True)
    df_hmz_health_bprhs_5.rename(columns={"pss_a_5yr": "hmz_pss_a_bprhs_5"}, inplace=True)


    # renaming the individual pss variables
    # bprhs v1
    df_hmz_health_bprhs_0.rename(columns={'pss1': 'hmz_pss1_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_0.rename(columns={'pss2': 'hmz_pss2_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_0.rename(columns={'pss3': 'hmz_pss3_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_0.rename(columns={'pss4': 'hmz_pss4_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_0.rename(columns={'pss5': 'hmz_pss5_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_0.rename(columns={'pss6': 'hmz_pss6_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_0.rename(columns={'pss7': 'hmz_pss7_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_0.rename(columns={'pss8': 'hmz_pss8_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_0.rename(columns={'pss9': 'hmz_pss9_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_0.rename(columns={'pss10': 'hmz_pss10_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_0.rename(columns={'pss11': 'hmz_pss11_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_0.rename(columns={'pss12': 'hmz_pss12_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_0.rename(columns={'pss13': 'hmz_pss13_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_0.rename(columns={'pss14': 'hmz_pss14_bprhs_0'}, inplace=True)


    #bprhs v2
    df_hmz_health_bprhs_2.rename(columns={'pss1_2yr': 'hmz_pss1_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'pss2_2yr': 'hmz_pss2_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'pss3_2yr': 'hmz_pss3_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'pss4_2yr': 'hmz_pss4_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'pss5_2yr': 'hmz_pss5_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'pss6_2yr': 'hmz_pss6_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'pss7_2yr': 'hmz_pss7_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'pss8_2yr': 'hmz_pss8_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'pss9_2yr': 'hmz_pss9_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'pss10_2yr': 'hmz_pss10_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'pss11_2yr': 'hmz_pss11_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'pss12_2yr': 'hmz_pss12_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'pss13_2yr': 'hmz_pss13_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'pss14_2yr': 'hmz_pss14_bprhs_2'}, inplace=True)


    #bprhs v4

    df_hmz_health_bprhs_8.rename(columns={'pss1_8yr': 'hmz_pss1_bprhs_8'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'pss2_8yr': 'hmz_pss2_bprhs_8'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'pss3_8yr': 'hmz_pss3_bprhs_8'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'pss4_8yr': 'hmz_pss4_bprhs_8'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'pss5_8yr': 'hmz_pss5_bprhs_8'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'pss6_8yr': 'hmz_pss6_bprhs_8'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'pss7_8yr': 'hmz_pss7_bprhs_8'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'pss8_8yr': 'hmz_pss8_bprhs_8'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'pss9_8yr': 'hmz_pss9_bprhs_8'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'pss10_8yr': 'hmz_pss10_bprhs_8'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'pss11_8yr': 'hmz_pss11_bprhs_8'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'pss12_8yr': 'hmz_pss12_bprhs_8'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'pss13_8yr': 'hmz_pss13_bprhs_8'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'pss14_8yr': 'hmz_pss14_bprhs_8'}, inplace=True)


    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)


    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)


    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)


    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)




    # --------------------------------------
    # PROSPECT
    # --------------------------------------
    base_variables = ["pss1", "pss2","pss3","pss4","pss5","pss6","pss7","pss8","pss9","pss10","pss11","pss12","pss13","pss14"]


    #Recoding  values: 96, 97, 98 -> NaN
    for var in base_variables:
        if var in df_hmz_health_prospect.columns:
           df_hmz_health_prospect[var] = df_hmz_health_prospect[var].replace({96: np.nan, 97: np.nan, 98: np.nan})


    # Recoding to harmonize with corresponding bprhs pss variables       
    # Recoding 1 - 0, 2 - 1, 3 -2, 4 - 3, 5 - 4
    df_hmz_health_prospect[base_variables] = df_hmz_health_prospect[base_variables].replace({1:0 ,2 :1 ,3 :2 ,4 :3, 5:4 })

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)


    # Second recoding to harmonize with the pss variables in bprhs that have a reversed order
    # recoding 0 - 4, 1-3, 2-2,3-1, 4,0 
    subset_variables = ['pss4', 'pss5', 'pss6', 'pss7', 'pss9', 'pss10', 'pss13']
    # transformation
    df_hmz_health_prospect[subset_variables] = df_hmz_health_prospect[subset_variables].replace({0:4, 1:3, 2:2, 3:1, 4:0})         

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)


    # Creating the new variable pss in prospect by summing the variables pss1 to pss_14 
    df_hmz_health_prospect['hmz_pss_prospect'] = df_hmz_health_prospect[base_variables].apply(
        lambda row: np.nan if row.isna().any() else row.sum(),
        axis=1)

    # Saving
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)




    # Creating a new variable pss_a in prospect with imputed mean of pss1-pss14 if 7 or less are missing
    subset_pss_a_variables = ['pss1', 'pss2', 'pss3', 'pss4', 'pss5', 'pss6', 
                              'pss7', 'pss8', 'pss9', 'pss10', 'pss11', 
                              'pss12', 'pss13', 'pss14']

    # Transformation: Impute mean if 7 or fewer are missing, else set NaN
    df_hmz_health_prospect['hmz_pss_a_prospect'] = df_hmz_health_prospect[subset_pss_a_variables].apply(
        lambda row: np.nan if row.isna().sum() > 7 else row.fillna(row.mean()).sum(),
        axis=1)


    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)




    # renaming the individual pss variables
    df_hmz_health_prospect.rename(columns={'pss1': 'hmz_pss1_prospect'}, inplace=True)
    df_hmz_health_prospect.rename(columns={'pss2': 'hmz_pss2_prospect'}, inplace=True)
    df_hmz_health_prospect.rename(columns={'pss3': 'hmz_pss3_prospect'}, inplace=True)
    df_hmz_health_prospect.rename(columns={'pss4': 'hmz_pss4_prospect'}, inplace=True)
    df_hmz_health_prospect.rename(columns={'pss5': 'hmz_pss5_prospect'}, inplace=True)
    df_hmz_health_prospect.rename(columns={'pss6': 'hmz_pss6_prospect'}, inplace=True)
    df_hmz_health_prospect.rename(columns={'pss7': 'hmz_pss7_prospect'}, inplace=True)
    df_hmz_health_prospect.rename(columns={'pss8': 'hmz_pss8_prospect'}, inplace=True)
    df_hmz_health_prospect.rename(columns={'pss9': 'hmz_pss9_prospect'}, inplace=True)
    df_hmz_health_prospect.rename(columns={'pss10': 'hmz_pss10_prospect'}, inplace=True)
    df_hmz_health_prospect.rename(columns={'pss11': 'hmz_pss11_prospect'}, inplace=True)
    df_hmz_health_prospect.rename(columns={'pss12': 'hmz_pss12_prospect'}, inplace=True)
    df_hmz_health_prospect.rename(columns={'pss13': 'hmz_pss13_prospect'}, inplace=True)
    df_hmz_health_prospect.rename(columns={'pss14': 'hmz_pss14_prospect'}, inplace=True)


    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)




    #------------------------------------------------------------------------------------------------
    # Depression
    # -----------------------------------------------------------------------------------------------


    # --------------------------------------
    # BPRHS
    # --------------------------------------

    # hmz_dep_score: sum the dep variables ds1-ds20 in bprhs and dep1-dep20 in prospect

    # Transformation: reversing the order of some individual pss variables in bprhs v4
    # the variable cesd_score does not exist in bprhs_8 but we can compute by adding the ds1 to ds20 variables
    # however, the ds individual variables in bprhs v4 do not follow the reversed order as some of the 
    # identical varibles in bprhs v1 and v2 so we first need to reverse the order of these variables
    ds_vars = ["ds1_8yr", "ds2_8yr", "ds3_8yr", "ds4_8yr", "ds5_8yr", "ds6_8yr", "ds7_8yr", "ds8_8yr", 
                      "ds9_8yr", "ds10_8yr", "ds11_8yr", "ds12_8yr", "ds13_8yr", "ds14_8yr", "ds15_8yr", "ds16_8yr", "ds17_8yr", "ds18_8yr", "ds19_8yr", "ds20_8yr"]




    # Creating the new variable ds in bprhs v4 by summing the variables 
    df_hmz_health_bprhs_8['hmz_ds_bprhs_8'] = df_hmz_health_bprhs_8[ds_vars].apply(
        lambda row: np.nan if row.isna().any() else row.sum(),
        axis=1)


    # Saving
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)




    # Creating a new variable ds_a in bprhs v4 with imputed mean of ds1_8yr-ds20_8yr if 7 or less are missing
    subset_ds_a_variables = ["ds1_8yr", "ds2_8yr", "ds3_8yr", "ds4_8yr", "ds5_8yr", "ds6_8yr", "ds7_8yr", "ds8_8yr", 
                      "ds9_8yr", "ds10_8yr", "ds11_8yr", "ds12_8yr", "ds13_8yr", "ds14_8yr", "ds15_8yr", "ds16_8yr", "ds17_8yr", "ds18_8yr", "ds19_8yr", "ds20_8yr"]

    # Transformation: Impute mean if 10 or fewer are missing, else set NaN
    df_hmz_health_bprhs_8['hmz_ds_a_bprhs_8'] = df_hmz_health_bprhs_8[subset_ds_a_variables].apply(
        lambda row: np.nan if row.isna().sum() > 10 else row.fillna(row.mean()).sum(),
        axis=1)

    # Saving
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)




    # renaming
    df_hmz_health_bprhs_0.rename(columns={"cesd_score": "hmz_ds_bprhs_0"}, inplace=True)
    df_hmz_health_bprhs_0.rename(columns={"cesd_score_a": "hmz_ds_a_bprhs_0"}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={"cesd_score_2yr": "hmz_ds_bprhs_2"}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={"cesd_score_a_2yr": "hmz_ds_a_bprhs_2"}, inplace=True)
    df_hmz_health_bprhs_5.rename(columns={"cesd_score_5yr": "hmz_ds_bprhs_5"}, inplace=True)
    df_hmz_health_bprhs_5.rename(columns={"cesd_score_a_5yr": "hmz_ds_a_bprhs_5"}, inplace=True)

    # renaming the individual pss variables
    # bprhs v1
    df_hmz_health_bprhs_0.rename(columns={'ds1': 'hmz_ds1_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_0.rename(columns={'ds2': 'hmz_ds2_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_0.rename(columns={'ds3': 'hmz_ds3_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_0.rename(columns={'ds4': 'hmz_ds4_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_0.rename(columns={'ds5': 'hmz_ds5_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_0.rename(columns={'ds6': 'hmz_ds6_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_0.rename(columns={'ds7': 'hmz_ds7_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_0.rename(columns={'ds8': 'hmz_ds8_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_0.rename(columns={'ds9': 'hmz_ds9_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_0.rename(columns={'ds10': 'hmz_ds10_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_0.rename(columns={'ds11': 'hmz_ds11_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_0.rename(columns={'ds12': 'hmz_ds12_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_0.rename(columns={'ds13': 'hmz_ds13_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_0.rename(columns={'ds14': 'hmz_ds14_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_0.rename(columns={'ds15': 'hmz_ds15_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_0.rename(columns={'ds16': 'hmz_ds16_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_0.rename(columns={'ds17': 'hmz_ds17_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_0.rename(columns={'ds18': 'hmz_ds18_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_0.rename(columns={'ds19': 'hmz_ds19_bprhs_0'}, inplace=True)
    df_hmz_health_bprhs_0.rename(columns={'ds20': 'hmz_ds20_bprhs_0'}, inplace=True)



    #bprhs v2
    df_hmz_health_bprhs_2.rename(columns={'ds1_2yr': 'hmz_ds1_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'ds2_2yr': 'hmz_ds2_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'ds3_2yr': 'hmz_ds3_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'ds4_2yr': 'hmz_ds4_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'ds5_2yr': 'hmz_ds5_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'ds6_2yr': 'hmz_ds6_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'ds7_2yr': 'hmz_ds7_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'ds8_2yr': 'hmz_ds8_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'ds9_2yr': 'hmz_ds9_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'ds10_2yr': 'hmz_ds10_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'ds11_2yr': 'hmz_ds11_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'ds12_2yr': 'hmz_ds12_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'ds13_2yr': 'hmz_ds13_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'ds14_2yr': 'hmz_ds14_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'ds15_2yr': 'hmz_ds15_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'ds16_2yr': 'hmz_ds16_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'ds17_2yr': 'hmz_ds17_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'ds18_2yr': 'hmz_ds18_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'ds19_2yr': 'hmz_ds19_bprhs_2'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'ds20_2yr': 'hmz_ds20_bprhs_2'}, inplace=True)


    #bprhs v4
    df_hmz_health_bprhs_8.rename(columns={'ds1_8yr': 'hmz_ds1_bprhs_8'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'ds2_8yr': 'hmz_ds2_bprhs_8'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'ds3_8yr': 'hmz_ds3_bprhs_8'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'ds4_8yr': 'hmz_ds4_bprhs_8'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'ds5_8yr': 'hmz_ds5_bprhs_8'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'ds6_8yr': 'hmz_ds6_bprhs_8'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'ds7_8yr': 'hmz_ds7_bprhs_8'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'ds8_8yr': 'hmz_ds8_bprhs_8'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'ds9_8yr': 'hmz_ds9_bprhs_8'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'ds10_8yr': 'hmz_ds10_bprhs_8'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'ds11_8yr': 'hmz_ds11_bprhs_8'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'ds12_8yr': 'hmz_ds12_bprhs_8'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'ds13_8yr': 'hmz_ds13_bprhs_8'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'ds14_8yr': 'hmz_ds14_bprhs_8'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'ds15_8yr': 'hmz_ds15_bprhs_8'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'ds16_8yr': 'hmz_ds16_bprhs_8'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'ds17_8yr': 'hmz_ds17_bprhs_8'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'ds18_8yr': 'hmz_ds18_bprhs_8'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'ds19_8yr': 'hmz_ds19_bprhs_8'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'ds20_8yr': 'hmz_ds20_bprhs_8'}, inplace=True)



    # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)




    # --------------------------------------
    # PROSPECT
    # --------------------------------------

    base_variables = ["dep1", "dep2","dep3","dep4","dep5","dep6","dep7","dep8","dep9","dep10","dep11","dep12","dep13","dep14","dep15","dep16","dep17","dep18","dep19","dep20"]

    # Recoding  values: 96, 97, 98 -> NaN
    for var in base_variables:
        if var in df_hmz_health_prospect.columns:
           df_hmz_health_prospect[var] = df_hmz_health_prospect[var].replace({96: np.nan, 97: np.nan, 98: np.nan})


    # Recoding 1 - 0, 2 - 1, 3 -2, 4 - 3
    df_hmz_health_prospect[base_variables] = df_hmz_health_prospect[base_variables].replace({1:0 ,2 :1 ,3 :2 ,4 :3 })

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)


    # Second recoding to harmonize with the ds variables in bprhs that have a reversed order
    # recoding 0 - 3, 1-2, 2-1, 3-0
    subset_variables = ['dep4','dep8','dep12','dep16']
    # transformation
    df_hmz_health_prospect[subset_variables] = df_hmz_health_prospect[subset_variables].replace({0:3, 1:2, 2:1, 3:0})

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)



    # Creating the new variable ds in prospect by summing the variables pss1 to pss_14 
    df_hmz_health_prospect['hmz_ds_prospect'] = df_hmz_health_prospect[base_variables].apply(
        lambda row: np.nan if row.isna().any() else row.sum(),
        axis=1)

    # Saving
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)



    # Creating a new variable ds_a in prospect with imputed mean of ds1-ds20 if 7 or less are missing
    subset_ds_a_variables = ["dep1", "dep2","dep3","dep4","dep5","dep6","dep7","dep8","dep9","dep10","dep11","dep12","dep13","dep14","dep15","dep16","dep17","dep18","dep19","dep20"]

    # Transformation: Impute mean if 10 or fewer are missing, else set NaN
    df_hmz_health_prospect['hmz_ds_a_prospect'] = df_hmz_health_prospect[subset_ds_a_variables].apply(
        lambda row: np.nan if row.isna().sum() > 10 else row.fillna(row.mean()).sum(),
        axis=1)

    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)




    # Renaming the individual pss variables
    df_hmz_health_prospect.rename(columns={'dep1': 'hmz_ds1_prospect'}, inplace=True)
    df_hmz_health_prospect.rename(columns={'dep2': 'hmz_ds2_prospect'}, inplace=True)
    df_hmz_health_prospect.rename(columns={'dep3': 'hmz_ds3_prospect'}, inplace=True)
    df_hmz_health_prospect.rename(columns={'dep4': 'hmz_ds4_prospect'}, inplace=True)
    df_hmz_health_prospect.rename(columns={'dep5': 'hmz_ds5_prospect'}, inplace=True)
    df_hmz_health_prospect.rename(columns={'dep6': 'hmz_ds6_prospect'}, inplace=True)
    df_hmz_health_prospect.rename(columns={'dep7': 'hmz_ds7_prospect'}, inplace=True)
    df_hmz_health_prospect.rename(columns={'dep8': 'hmz_ds8_prospect'}, inplace=True)
    df_hmz_health_prospect.rename(columns={'dep9': 'hmz_ds9_prospect'}, inplace=True)
    df_hmz_health_prospect.rename(columns={'dep10': 'hmz_ds10_prospect'}, inplace=True)
    df_hmz_health_prospect.rename(columns={'dep11': 'hmz_ds11_prospect'}, inplace=True)
    df_hmz_health_prospect.rename(columns={'dep12': 'hmz_ds12_prospect'}, inplace=True)
    df_hmz_health_prospect.rename(columns={'dep13': 'hmz_ds13_prospect'}, inplace=True)
    df_hmz_health_prospect.rename(columns={'dep14': 'hmz_ds14_prospect'}, inplace=True)
    df_hmz_health_prospect.rename(columns={'dep15': 'hmz_ds15_prospect'}, inplace=True)
    df_hmz_health_prospect.rename(columns={'dep16': 'hmz_ds16_prospect'}, inplace=True)
    df_hmz_health_prospect.rename(columns={'dep17': 'hmz_ds17_prospect'}, inplace=True)
    df_hmz_health_prospect.rename(columns={'dep18': 'hmz_ds18_prospect'}, inplace=True)
    df_hmz_health_prospect.rename(columns={'dep19': 'hmz_ds19_prospect'}, inplace=True)
    df_hmz_health_prospect.rename(columns={'dep20': 'hmz_ds20_prospect'}, inplace=True)


    # Saving
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)

     #------------------------------------------------------------------------------------------------
     # Post-Processing - BPRHS and PROSPECT (Spanish) – health
     #------------------------------------------------------------------------------------------------

     # ------------------------------------------------------------------------------------------------------------
     #  Adding prefix 'hmz_health_' to variables starting with 'hmz_' 
     # ------------------------------------------------------------------------------------------------------------
    datasets_health = {
         "df_hmz_health_bprhs_0": df_hmz_health_bprhs_0,
         "df_hmz_health_bprhs_2": df_hmz_health_bprhs_2,
         "df_hmz_health_bprhs_5": df_hmz_health_bprhs_5,
         "df_hmz_health_bprhs_8": df_hmz_health_bprhs_8,
         "df_hmz_health_prospect": df_hmz_health_prospect}

    for name, df in datasets_health.items():
         df.columns = [f"hmz_health_{col[4:]}" if col.startswith('hmz_') else col for col in df.columns]
         df.to_csv(f"data/intermediate/{name}.csv", index=False)
         

     # ------------------------------------------------------------------------------------------------------------
     #  Adding visit column (bprhs)
     # ------------------------------------------------------------------------------------------------------------
    df_hmz_health_bprhs_0["hmz_visit_bprhs_0"] = df_hmz_health_bprhs_0["studyid"].notna().map({True: "v1", False: None})
    df_hmz_health_bprhs_2["hmz_visit_bprhs_2"] = df_hmz_health_bprhs_2["studyid"].notna().map({True: "v2", False: None})
    df_hmz_health_bprhs_5["hmz_visit_bprhs_5"] = df_hmz_health_bprhs_5["studyid"].notna().map({True: "v3", False: None})
    df_hmz_health_bprhs_8["hmz_visit_bprhs_8"] = df_hmz_health_bprhs_8["studyid"].notna().map({True: "v4", False: None})


     # Saving 
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)

     # ------------------------------------------------------------------------------------------------------------
     # Renaming redcap event --> hmz_visit (prospect)
     # ------------------------------------------------------------------------------------------------------------
    if "redcap_event_name" in df_hmz_health_prospect.columns:
         df_hmz_health_prospect["redcap_event_name"] = df_hmz_health_prospect["redcap_event_name"].replace({
             "baseline_arm_1": "v1",
             "visit_2_arm_1": "v2"})
         df_hmz_health_prospect.rename(columns={"redcap_event_name": "hmz_visit_prospect"}, inplace=True)
         df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)


     # ------------------------------------------------------------------------------------------------------------
     # Renaming record_id --> hmz_record_id (prospect)
     # ------------------------------------------------------------------------------------------------------------
    if "record_id" in df_hmz_health_prospect.columns:
         print(df_hmz_health_prospect["record_id"].value_counts())
         df_hmz_health_prospect.rename(columns={"record_id": "hmz_record_id_prospect"}, inplace=True)
         print(df_hmz_health_prospect["hmz_record_id_prospect"].value_counts())
         df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)


     # ------------------------------------------------------------------------------------------------------------ 
     # Keeping only studyid and 'hmz' variables
     # ------------------------------------------------------------------------------------------------------------
    df_hmz_health_bprhs_0 = df_hmz_health_bprhs_0.loc[:, df_hmz_health_bprhs_0.columns.str.startswith('hmz') | (df_hmz_health_bprhs_0.columns == 'studyid')]
    df_hmz_health_bprhs_2 = df_hmz_health_bprhs_2.loc[:, df_hmz_health_bprhs_2.columns.str.startswith('hmz') | (df_hmz_health_bprhs_2.columns == 'studyid')]
    df_hmz_health_bprhs_5 = df_hmz_health_bprhs_5.loc[:, df_hmz_health_bprhs_5.columns.str.startswith('hmz') | (df_hmz_health_bprhs_5.columns == 'studyid')]
    df_hmz_health_bprhs_8 = df_hmz_health_bprhs_8.loc[:, df_hmz_health_bprhs_8.columns.str.startswith('hmz') | (df_hmz_health_bprhs_8.columns == 'studyid')]
    df_hmz_health_prospect = df_hmz_health_prospect[[col for col in df_hmz_health_prospect.columns if col.startswith('hmz_') or col in ['studyid']]]
     
     # saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)
    df_hmz_health_prospect.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)



     # ------------------------------------------------------------------------------------------------------------
     # Creating PROSPECT visit-specific files
     # ------------------------------------------------------------------------------------------------------------
     # Filering not null studyids
    df_hmz_health_prospect = pd.read_csv("data/intermediate/df_hmz_health_prospect.csv")
    df_hmz_health_prospect = df_hmz_health_prospect[df_hmz_health_prospect["studyid"].notnull()]

     # Visit 1
    df_hmz_health_prospect_visit_1 = df_hmz_health_prospect[df_hmz_health_prospect["hmz_visit_prospect"] == "v1"].copy()
    df_hmz_health_prospect_visit_1.rename(columns={col: f"{col}_v1" for col in df_hmz_health_prospect_visit_1.columns if col != "studyid"}, inplace=True)
    df_hmz_health_prospect_visit_1.rename(columns={"hmz_visit_prospect_v1": "visit"}, inplace=True)
    df_hmz_health_prospect_visit_1.to_csv("data/intermediate/df_hmz_health_prospect_visit_1.csv", index=False)

     # Visit 2
    df_hmz_health_prospect_visit_2 = df_hmz_health_prospect[df_hmz_health_prospect["hmz_visit_prospect"] == "v2"].copy()
    df_hmz_health_prospect_visit_2.rename(columns={col: f"{col}_v2" for col in df_hmz_health_prospect_visit_2.columns if col != "studyid"}, inplace=True)
    df_hmz_health_prospect_visit_2.rename(columns={"hmz_visit_prospect_v2": "visit"}, inplace=True)
    df_hmz_health_prospect_visit_2.to_csv("data/intermediate/df_hmz_health_prospect_visit_2.csv", index=False)

    # ------------------------------------------------------------------------------------------------------------
    # Renaming hmz visit --> visit
    # ------------------------------------------------------------------------------------------------------------

    df_hmz_health_bprhs_0.rename(columns={'hmz_visit_bprhs_0': 'visit'}, inplace=True)
    df_hmz_health_bprhs_2.rename(columns={'hmz_visit_bprhs_2': 'visit'}, inplace=True)
    df_hmz_health_bprhs_5.rename(columns={'hmz_visit_bprhs_5': 'visit'}, inplace=True)
    df_hmz_health_bprhs_8.rename(columns={'hmz_visit_bprhs_8': 'visit'}, inplace=True)
    df_hmz_health_prospect_visit_1.rename(columns={'hmz_visit_prospect_v1': 'visit'}, inplace=True)
    df_hmz_health_prospect_visit_2.rename(columns={'hmz_visit_prospect_v2': 'visit'}, inplace=True)


  
     # Saving
    df_hmz_health_bprhs_0.to_csv('data/intermediate/df_hmz_health_bprhs_0.csv', index=False)
    df_hmz_health_bprhs_2.to_csv('data/intermediate/df_hmz_health_bprhs_2.csv', index=False)
    df_hmz_health_bprhs_5.to_csv('data/intermediate/df_hmz_health_bprhs_5.csv', index=False)
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)
    df_hmz_health_prospect_visit_1.to_csv("data/intermediate/df_hmz_health_prospect_visit_1.csv", index=False)
    df_hmz_health_prospect_visit_2.to_csv("data/intermediate/df_hmz_health_prospect_visit_2.csv", index=False)

 

    ##%%
    #---------------------------------------------------------------------------------------
    # loading the data: english (only PROSPECT)
    from harmonization_scripts.load.loader_health import load_health_english_data
    data = load_health_english_data(config)
    df_hmz_health_prospect_english = data['prospect_english']
    #--------------------------------------------------------------------------------------------

    #------------------------------------------------------------------------------------------------
    # Lab 
    # -----------------------------------------------------------------------------------------------
    # blood

    # Recoding 96, 97, 98 as NaN
    if "bld2" in df_hmz_health_prospect_english.columns:
        df_hmz_health_prospect_english["bld2"] = df_hmz_health_prospect_english["bld2"].replace({96: np.nan, 97: np.nan, 98: np.nan})

    # Renaming
    df_hmz_health_prospect_english.rename(columns={"bld2": "hmz_lab_bld_prospect"}, inplace=True)

    # Saving
    df_hmz_health_prospect_english.to_csv('data/intermediate/df_hmz_health_prospect_english.csv', index=False)


    # blood pressure

    # Renaming
    df_hmz_health_prospect_english.rename(columns={'bpsys_avg': 'hmz_ant_bp_sys_prospect','bpdias_avg': 'hmz_ant_bp_dias_prospect' }, inplace=True)
    # Saving
    df_hmz_health_prospect_english.to_csv("data/intermediate/df_hmz_health_prospect_english.csv", index=False)



    # weight

    # Renaming
    df_hmz_health_prospect_english.rename(columns={'wt_avg': 'hmz_ant_wt_avg_prospect'}, inplace=True)
    # Saving
    df_hmz_health_prospect_english.to_csv('data/intermediate/df_hmz_health_prospect_english.csv', index=False)


    # bmi
    # Renaming
    df_hmz_health_prospect_english.rename(columns={'bmi': 'hmz_ant_bmi_prospect'}, inplace=True)
    # Saving
    df_hmz_health_prospect_english.to_csv('data/intermediate/df_hmz_health_prospect_english.csv', index=False)



    #  hip circumference
    # Renaming
    df_hmz_health_prospect_english.rename(columns={'hc_avg': 'hmz_ant_hip_prospect'}, inplace=True)
    # Saving
    df_hmz_health_prospect_english.to_csv('data/intermediate/df_hmz_health_prospect_english.csv', index=False)



    # cholesterol
    # Renaming
    df_hmz_health_prospect_english.rename(columns={'lab1': 'hmz_lab_chol_prospect'}, inplace=True)
    # Saving
    df_hmz_health_prospect_english.to_csv('data/intermediate/df_hmz_health_prospect_english.csv', index=False)



    # ldl
    # Renaming
    df_hmz_health_prospect_english.rename(columns={'lab2': 'hmz_lab_ldl_prospect'}, inplace=True)
    # Saving
    df_hmz_health_prospect_english.to_csv('data/intermediate/df_hmz_health_prospect_english.csv', index=False)


    # hdl
    # Renaming
    df_hmz_health_prospect_english.rename(columns={'lab3': 'hmz_lab_hdl_prospect'}, inplace=True)
    # Saving
    df_hmz_health_prospect_english.to_csv('data/intermediate/df_hmz_health_prospect_english.csv', index=False)



    # trig
    # Renaming
    df_hmz_health_prospect_english.rename(columns={'lab4': 'hmz_lab_trig_prospect'}, inplace=True)
    # Saving
    df_hmz_health_prospect_english.to_csv('data/intermediate/df_hmz_health_prospect_english.csv', index=False)


    # gluc
    # Renaming
    df_hmz_health_prospect_english.rename(columns={'lab5': 'hmz_lab_gluc_prospect'}, inplace=True)
    # Saving
    df_hmz_health_prospect_english.to_csv('data/intermediate/df_hmz_health_prospect_english.csv', index=False)


    # a1c
    # Renaming
    df_hmz_health_prospect_english.rename(columns={'lab6': 'hmz_lab_a1c_prospect'}, inplace=True)
    # Saving
    df_hmz_health_prospect_english.to_csv('data/intermediate/df_hmz_health_prospect_english.csv', index=False)




    # bun creat
    # Renaming
    df_hmz_health_prospect_english.rename(columns={'lab19': 'hmz_lab_bun_creat_prospect'}, inplace=True)
    # Saving
    df_hmz_health_prospect_english.to_csv('data/intermediate/df_hmz_health_prospect_english.csv', index=False)



    # bun
    # Renaming
    df_hmz_health_prospect_english.rename(columns={'lab17': 'hmz_lab_bun_prospect'}, inplace=True)
    # Saving
    df_hmz_health_prospect_english.to_csv('data/intermediate/df_hmz_health_prospect_english.csv', index=False)



    # creat
    # Renaming
    df_hmz_health_prospect_english.rename(columns={'lab18': 'hmz_lab_creat_prospect'}, inplace=True)
    # Saving
    df_hmz_health_prospect_english.to_csv('data/intermediate/df_hmz_health_prospect_english.csv', index=False)


    # alb
    # Renaming
    df_hmz_health_prospect_english.rename(columns={'lab28': 'hmz_lab_alb_prospect'}, inplace=True)
    # Saving
    df_hmz_health_prospect_english.to_csv('data/intermediate/df_hmz_health_prospect_english.csv', index=False)



    # chol hdl
    # Renaming
    df_hmz_health_prospect_english.rename(columns={'lab37': 'hmz_lab_chol_hdl_prospect'}, inplace=True)
    # Saving
    df_hmz_health_prospect_english.to_csv('data/intermediate/df_hmz_health_prospect_english.csv', index=False)



    # ldl hdl
    # Renaming
    df_hmz_health_prospect_english.rename(columns={'lab38': 'hmz_lab_ldl_hdl_prospect'}, inplace=True)
    # Saving
    df_hmz_health_prospect_english.to_csv('data/intermediate/df_hmz_health_prospect_english.csv', index=False)


    # insulin
    # Renaming
    df_hmz_health_prospect_english.rename(columns={'lab12': 'hmz_lab_insulin_prospect'}, inplace=True)
    # Saving
    df_hmz_health_prospect_english.to_csv('data/intermediate/df_hmz_health_prospect_english.csv', index=False)




    # crp
    # Convert CRP-High Sensitivity from mg/dL to mg/L
    df_hmz_health_prospect_english["lab14"] = df_hmz_health_prospect_english["lab14"] * 10
    # Renaming
    df_hmz_health_prospect_english.rename(columns={'lab14': 'hmz_lab_crp_prospect'}, inplace=True)
    # Saving
    df_hmz_health_prospect_english.to_csv('data/intermediate/df_hmz_health_prospect_english.csv', index=False)



    # platelet
    # Renaming
    df_hmz_health_prospect_english.rename(columns={'lab11': 'hmz_lab_platelet_prospect'}, inplace=True)
    # Saving
    df_hmz_health_prospect_english.to_csv('data/intermediate/df_hmz_health_prospect_english.csv', index=False)



    #------------------------------------------------------------------------------------------------
    # Anthropometric measurements
    # -----------------------------------------------------------------------------------------------
    # pounds i

    # renaming
    df_hmz_health_prospect_english.rename(columns={'ant3a': 'hmz_ant_pounds_i_prospect'}, inplace=True)
    # Renaming
    df_hmz_health_prospect_english.to_csv('data/intermediate/df_hmz_health_prospect_english.csv', index=False)
    # Saving
    df_hmz_health_prospect_english.to_csv('data/intermediate/df_hmz_health_prospect_english.csv', index=False)

    # pounds ii

    # recoding 
    df_hmz_health_prospect_english["ant3b"] = df_hmz_health_prospect_english["ant3b"].replace({96: np.nan, 97: np.nan, 98: np.nan})
    # renaming
    df_hmz_health_prospect_english.rename(columns={'ant3b': 'hmz_ant_pounds_ii_prospect'}, inplace=True)
    # Saving
    df_hmz_health_prospect_english.to_csv('data/intermediate/df_hmz_health_prospect_english.csv', index=False)


    # pounds iii

    # recoding 98 to nan
    df_hmz_health_prospect_english["ant3c"] = df_hmz_health_prospect_english["ant3c"].replace({96: np.nan, 97: np.nan, 98: np.nan})
    # Renaming
    df_hmz_health_prospect_english.rename(columns={'ant3c': 'hmz_ant_pounds_iii_prospect'}, inplace=True)
    # Saving
    df_hmz_health_prospect_english.to_csv('data/intermediate/df_hmz_health_prospect_english.csv', index=False)


    # height

    # Renaming
    df_hmz_health_prospect_english.rename(columns={'ht_avg': 'hmz_ant_ht_prospect'}, inplace=True)
    # Saving
    df_hmz_health_prospect_english.to_csv('data/intermediate/df_hmz_health_prospect_english.csv', index=False)


    # weight
    # Renaming
    df_hmz_health_prospect_english.rename(columns={'wc_avg': 'hmz_ant_avg_waist_prospect'}, inplace=True)
    # Saving
    df_hmz_health_prospect_english.to_csv('data/intermediate/df_hmz_health_prospect_english.csv', index=False)



    #------------------------------------------------------------------------------------------------
    # Medical Diagnosis
    # -----------------------------------------------------------------------------------------------


    # List of tuples: (column name, recode values, new name)
    variables = [
        ("med29",   {96: np.nan, 98: np.nan}, "hmz_med_arthritis_prospect"),
        ("med29a",  {98: np.nan},             "hmz_med_arthritis_medication_prospect"),
        ("med29d",  {96: np.nan, 98: np.nan}, "hmz_med_arthritis_today_prospect"),
        ("med30",   {97: np.nan, 98: np.nan}, "hmz_med_osteoporosis_prospect"),
        ("med30a",  {98: np.nan},             "hmz_med_osteoporosis_medication_prospect"),
        ("med30d",  {96: np.nan},             "hmz_med_osteoporosis_today_prospect"),
        ("med31",   {97: np.nan, 98: np.nan}, "hmz_med_respiratory_prospect"),
        ("med31a",  None,                     "hmz_med_respiratory_medication_prospect"),
        ("med31d",  {98: np.nan},             "hmz_med_respiratory_today_prospect"),
    ]

    for column, recode_values, renamed_column in variables:
        if column in df_hmz_health_prospect_english.columns:
            if recode_values:
                df_hmz_health_prospect_english[column] = df_hmz_health_prospect_english[column].replace(recode_values)
            df_hmz_health_prospect_english.rename(columns={column: renamed_column}, inplace=True)



    # Saving
    df_hmz_health_prospect_english.to_csv('data/intermediate/df_hmz_health_prospect_english.csv', index=False)


    # respiratory conditions
    # Renaming
    df_hmz_health_prospect_english.rename(columns={'med31e___1': 'hmz_med_respiratory_emphysema_prospect',
                                           'med31e___2': 'hmz_med_respiratory_chronic_bronchitis_prospect',
                                           'med31e___3': 'hmz_med_respiratory_asthma_prospect',
                                           'med31e___4': 'hmz_med_respiratory_copd_prospect',
                                           'med31e___5': 'hmz_med_respiratory_other_prospect'  }, inplace=True)

    # Saving
    df_hmz_health_prospect_english.to_csv('data/intermediate/df_hmz_health_prospect_english.csv', index=False)



    # diabetes

    # Recoding  96, 97, 98 -> as NaN
    df_hmz_health_prospect_english['med1'] = df_hmz_health_prospect_english['med1'].replace({96: np.nan, 97: np.nan, 98: np.nan})

    # Renaming
    df_hmz_health_prospect_english.rename(columns={'med1': 'hmz_med_1_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect_english.to_csv('data/intermediate/df_hmz_health_prospect_english.csv', index=False)




    # diabetes medication

    # Renaming
    df_hmz_health_prospect_english.rename(columns={'med1a': 'hmz_med_1_medication_prospect'}, inplace=True)
    # Saving
    df_hmz_health_prospect_english.to_csv('data/intermediate/df_hmz_health_prospect_english.csv', index=False)




    # diagnosis age
    df_hmz_health_prospect_english.rename(columns={'age_calc': 'age_prospect'}, inplace=True)

    # Applying a ceiling function (function that converts decimal numbers into whole numbers) to hmz_age_prospect
    df_hmz_health_prospect_english['age_prospect'] = np.ceil(df_hmz_health_prospect_english['age_prospect'])

    # Saving 
    df_hmz_health_prospect_english.to_csv('data/intermediate/df_hmz_health_prospect_english.csv', index=False)

    # transforming the variable

    def calculate_diagnosis_age(row):
        try:
            # Convert to numeric, force errors to NaN
            med1b = pd.to_numeric(row["med1b"], errors='coerce')
            age_prospect = pd.to_numeric(row["age_prospect"], errors='coerce')
            med1c = pd.to_numeric(row["med1c"], errors='coerce')

            # If any of the critical values are NaN, return NaN
            if pd.isna(med1b) or pd.isna(med1c):
                return np.nan  

            # If med1b is a year (likely misentered), treat it as Year of Diagnosis
            if med1b > 1900:  
                med1c = 1  # Force Year of Diagnosis category

            # If med1b is an unrealistically high number, set to NaN
            if med1b > 150:
                return np.nan  

            if med1c == 2:  # Age at diagnosis directly provided
                return med1b

            elif med1c == 1:  # Year of diagnosis provided or corrected from above
                age_at_diagnosis = 2024 - med1b
                return age_at_diagnosis if 0 <= age_at_diagnosis <= 120 else np.nan  # Ensure realistic age

            elif med1c == 3:  # Years with diagnosis provided
                if pd.isna(age_prospect):
                    return np.nan  # Missing current age
                age_at_diagnosis = age_prospect - med1b
                return age_at_diagnosis if 0 <= age_at_diagnosis <= 120 else np.nan  # Ensure realistic age

        except Exception as e:
            print(f"Error processing row {row.name}: {e}")
            return np.nan  

    # Apply the function to create the new variable
    df_hmz_health_prospect_english["hmz_med_1_age_prospect"] = df_hmz_health_prospect_english.apply(calculate_diagnosis_age, axis=1)


    # Saving
    df_hmz_health_prospect_english.to_csv('data/intermediate/df_hmz_health_prospect_english.csv', index=False)



    # diabetes condition today

    # Renaming
    df_hmz_health_prospect_english.rename(columns={'med1d': 'hmz_med_1_today_prospect'}, inplace=True)
    # Saving
    df_hmz_health_prospect_english.to_csv('data/intermediate/df_hmz_health_prospect_english.csv', index=False)





    transformations = [
        ("med3",   {98: np.nan},                          "hmz_med_bp_prospect"),
        ("med3a",  {96: np.nan},                          "hmz_med_bp_medication_prospect"),
        ("med3d",  {97: np.nan, 98: np.nan},              "hmz_med_bp_today_prospect"),
        ("med4",   {96: np.nan, 98: np.nan},              "hmz_med_overweight_prospect"),
        ("med4a",  None,                                  "hmz_med_overweight_medication_prospect"),
        ("med4d",  {96: np.nan, 98: np.nan},              "hmz_med_overweight_today_prospect"),
        ("med7",   {97: np.nan, 98: np.nan},              "hmz_med_angina_prospect"),
        ("med7a",  {98: np.nan},                          "hmz_med_angina_medication_prospect"),
        ("med7d",  {98: np.nan},                          "hmz_med_angina_today_prospect"),
        ("med8",   {96: np.nan, 97: np.nan, 98: np.nan},  "hmz_med_heart_attack_prospect"),
        ("med8a",  None,                                  "hmz_med_heart_attack_medication_prospect"),
        ("med8d",  {98: np.nan},                          "hmz_med_heart_attack_today_prospect"),
        ("med9",   {97: np.nan, 98: np.nan},              "hmz_med_heart_failure_prospect"),
        ("med9a",  None,                                  "hmz_med_heart_failure_medication_prospect"),
        ("med9d",  None,                                  "hmz_med_heart_failure_today_prospect"),
        ("med12",  {98: np.nan},                          "hmz_med_heart_disease_prospect"),
        ("med12a", None,                                  "hmz_med_heart_disease_medication_prospect"),
        ("med12d", {98: np.nan},                          "hmz_med_heart_disease_today_prospect"),
        ("med14",  {98: np.nan},                          "hmz_med_stroke_prospect"),
        ("med14a", None,                                  "hmz_med_stroke_medication_prospect"),
        ("med14d", {98: np.nan},                          "hmz_med_stroke_today_prospect"),
        ("med19",  {98: np.nan},                          "hmz_med_kidney_disease_prospect"),
        ("med19a", None,                                  "hmz_med_kidney_disease_medication_prospect"),
        ("med19d", {98: np.nan},                          "hmz_med_kidney_disease_today_prospect")
    ]


    for col, recodes, new_name in transformations:
        if col in df_hmz_health_prospect_english.columns:
            if recodes:
                df_hmz_health_prospect_english[col] = df_hmz_health_prospect_english[col].replace(recodes)
            df_hmz_health_prospect_english.rename(columns={col: new_name}, inplace=True)

    # Saving
    df_hmz_health_prospect_english.to_csv('data/intermediate/df_hmz_health_prospect_english.csv', index=False)








    # hepatitis 
    # Recoding  96, 97, 98 -> as NaN
    df_hmz_health_prospect_english['med21'] = df_hmz_health_prospect_english['med21'].replace({ 98: np.nan})

    # Renaming
    df_hmz_health_prospect_english.rename(columns={'med21': 'hmz_med_hepatitis_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect_english.to_csv('data/intermediate/df_hmz_health_prospect_english.csv', index=False)




    # types of hepatitis 


    df_hmz_health_prospect_english[['med21e___1', 'med21e___2', 'med21e___3']] = df_hmz_health_prospect_english[
        ['med21e___1', 'med21e___2', 'med21e___3']
    ].astype(float)


    df_hmz_health_prospect_english['hmz_med_hepatitis_type_prospect'] = df_hmz_health_prospect_english.apply(
        lambda row: (
            1 if row['med21e___1'] == 1.0 else
            2 if row['med21e___2'] == 1.0 else
            3 if row['med21e___3'] == 1.0 else None
        ),
        axis=1)



    # Saving
    df_hmz_health_prospect_english.to_csv('data/intermediate/df_hmz_health_prospect_english.csv', index=False)



    # hepatitis medication
    # Recoding  96, 97, 98 -> as NaN
    df_hmz_health_prospect_english['med21a'] = df_hmz_health_prospect_english['med21a'].replace({97: np.nan})

    # Renaming
    df_hmz_health_prospect_english.rename(columns={'med21a': 'hmz_med_hepatitis_medication_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect_english.to_csv('data/intermediate/df_hmz_health_prospect_english.csv', index=False)



    # hepatitis today

    # Recoding  96, 97, 98 -> as NaN
    df_hmz_health_prospect_english['med21d'] = df_hmz_health_prospect_english['med21d'].replace({98: np.nan})

    # Renaming
    df_hmz_health_prospect_english.rename(columns={'med21d': 'hmz_med_hepatitis_today_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect_english.to_csv('data/intermediate/df_hmz_health_prospect_english.csv', index=False)



    # cancer

    # 
    # Recoding  96, 97, 98 -> as NaN
    df_hmz_health_prospect_english['med26'] = df_hmz_health_prospect_english['med26'].replace({ 98: np.nan})

    # Renaming
    df_hmz_health_prospect_english.rename(columns={'med26': 'hmz_med_cancer_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect_english.to_csv('data/intermediate/df_hmz_health_prospect_english.csv', index=False)



    # types of cancer
    # variables related to cancer - some studyids have more than one cancer so it was not possible to 
    # create one single hmz variable

    print(df_hmz_health_prospect_english['med26e___8'].value_counts())

    #renaming the variables
    df_hmz_health_prospect_english.rename(columns={'med26e___1': 'hmz_med_cancer_lung_prospect'}, inplace=True)
    df_hmz_health_prospect_english.rename(columns={'med26e___2': 'hmz_med_cancer_breast_prospect'}, inplace=True)
    df_hmz_health_prospect_english.rename(columns={'med26e___3': 'hmz_med_cancer_cervical_prospect'}, inplace=True)
    df_hmz_health_prospect_english.rename(columns={'med26e___4': 'hmz_med_cancer_blood_prospect'}, inplace=True)
    df_hmz_health_prospect_english.rename(columns={'med26e___5': 'hmz_med_cancer_testicular_prospect'}, inplace=True)
    df_hmz_health_prospect_english.rename(columns={'med26e___6': 'hmz_med_cancer_bone_prospect'}, inplace=True)
    df_hmz_health_prospect_english.rename(columns={'med26e___7': 'hmz_med_cancer_melanoma_prospect'}, inplace=True)
    df_hmz_health_prospect_english.rename(columns={'med26e___8': 'hmz_med_cancer_skin_prospect'}, inplace=True)
    df_hmz_health_prospect_english.rename(columns={'med26e___9': 'hmz_med_cancer_brain_prospect'}, inplace=True)
    df_hmz_health_prospect_english.rename(columns={'med26e___10': 'hmz_med_cancer_stomach_prospect'}, inplace=True)
    df_hmz_health_prospect_english.rename(columns={'med26e___11': 'hmz_med_cancer_colon_prospect'}, inplace=True)
    df_hmz_health_prospect_english.rename(columns={'med26e___12': 'hmz_med_cancer_uterine_prospect'}, inplace=True)
    df_hmz_health_prospect_english.rename(columns={'med26e___13': 'hmz_med_cancer_prostate_prospect'}, inplace=True)
    df_hmz_health_prospect_english.rename(columns={'med26e___14': 'hmz_med_cancer_liver_prospect'}, inplace=True)
    df_hmz_health_prospect_english.rename(columns={'med26e___15': 'hmz_med_cancer_other_prospect'}, inplace=True)


    # Saving 
    df_hmz_health_prospect_english.to_csv('data/intermediate/df_hmz_health_prospect_english.csv', index=False)


    # condition (cancer) today


    # Recoding  96, 97, 98 -> as NaN
    df_hmz_health_prospect_english['med26d'] = df_hmz_health_prospect_english['med26d'].replace({ 98: np.nan})
    # Renaming
    df_hmz_health_prospect_english.rename(columns={'med26d': 'hmz_med_cancer_today_prospect'}, inplace=True)
    # Saving
    df_hmz_health_prospect_english.to_csv('data/intermediate/df_hmz_health_prospect_english.csv', index=False)






    # medication cancer
    # Renaming
    df_hmz_health_prospect_english.rename(columns={'med26a': 'hmz_med_cancer_medication_prospect'}, inplace=True)
    # Saving
    df_hmz_health_prospect_english.to_csv('data/intermediate/df_hmz_health_prospect_english.csv', index=False)


    # stomach-intestine
    # Renaming
    df_hmz_health_prospect_english.rename(columns={'med32': 'hmz_med_stomach_intestine_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect_english.to_csv('data/intermediate/df_hmz_health_prospect.csv', index=False)

    # types of stomach intestine conditions

    base_variable = ["med32e___1", "med32e___2", "med32e___3", "med32e___4", 
                     "med32e___5", "med32e___6", "med32e___7", "med32e___8"]

    for var in base_variable:
        print(f"Value counts for {var}:")
        print(df_hmz_health_prospect_english[var].value_counts(dropna=False), "\n")




    # For harmonization purposes, update 'other' based on specific stomach variables
    stomach_vars = ["med32e___1", "med32e___4", "med32e___5", "med32e___6", "med32e___8"]

    def harmonize_stomach_prospect(row):
        if row[stomach_vars].isna().all():
            return np.nan
        elif (row[stomach_vars] == 1).any():
            return 1
        else:
            return 0

    df_hmz_health_prospect_english["med32e___8"] = df_hmz_health_prospect_english.apply(harmonize_stomach_prospect, axis=1)


    # Renaming
    df_hmz_health_prospect_english.rename(columns={
        'med32e___2': 'hmz_med_stomach_intestine_crohn_prospect',
        'med32e___3': 'hmz_med_stomach_intestine_ulcer_prospect',
        'med32e___7': 'hmz_med_stomach_intestine_diverticular_prospect',
        'med32e___8': 'hmz_med_stomach_intestine_other_prospect'
    }, inplace=True)


    # Saving
    df_hmz_health_prospect_english.to_csv('data/intermediate/df_hmz_health_prospect_english.csv', index=False)



    # medication for stomach intestine

    # Recoding
    df_hmz_health_prospect_english['med32a'] = df_hmz_health_prospect_english['med32a'].replace({96: np.nan})

    # Renaming
    df_hmz_health_prospect_english.rename(columns={'med32a': 'hmz_med_stomach_intestine_medication_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect_english.to_csv('data/intermediate/df_hmz_health_prospect_english.csv', index=False)


    # stomach-intestine condition today


    # Recoding
    df_hmz_health_prospect_english['med32d'] = df_hmz_health_prospect_english['med32d'].replace({98: np.nan})

    # Renaming
    df_hmz_health_prospect_english.rename(columns={'med32d': 'hmz_med_stomach_intestine_today_prospect'}, inplace=True)

    df_hmz_health_prospect_english.to_csv('data/intermediate/df_hmz_health_prospect_english.csv', index=False)



    # anxiety

    # Recoding  96, 97, 98 -> as NaN
    df_hmz_health_prospect_english['med34'] = df_hmz_health_prospect_english['med34'].replace({97: np.nan, 98: np.nan})

    # Renaming
    df_hmz_health_prospect_english.rename(columns={'med34': 'hmz_med_anxiety_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect_english.to_csv('data/intermediate/df_hmz_health_prospect_english.csv', index=False)



    # medication


    df_hmz_health_prospect_english['med34a'] = df_hmz_health_prospect_english['med34a'].replace({97: np.nan, 98: np.nan})
    # Renaming
    df_hmz_health_prospect_english.rename(columns={'med34a': 'hmz_med_anxiety_medication_prospect'}, inplace=True)
    # Saving
    df_hmz_health_prospect_english.to_csv('data/intermediate/df_hmz_health_prospect_english.csv', index=False)



    # anxiety

    #  creating variable anxiety today  for prospect using med34d__0 and med34d__1


    df_hmz_health_prospect_english["hmz_med_anxiety_today_prospect"] = df_hmz_health_prospect_english.apply(
        lambda row: 1 if row["med34d___1"] == 1 
        else 0 if row["med34d___0"] == 1 
        else pd.NA,
        axis=1)



    # depression

    # Recoding  96, 97, 98 -> as NaN
    df_hmz_health_prospect_english['med35'] = df_hmz_health_prospect_english['med35'].replace({97: np.nan, 98: np.nan})

    # Renaming
    df_hmz_health_prospect_english.rename(columns={'med35': 'hmz_med_depression_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect_english.to_csv('data/intermediate/df_hmz_health_prospect_english.csv', index=False)



    # medication

    # Renaming
    df_hmz_health_prospect_english.rename(columns={'med35a': 'hmz_med_depression_medication_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect_english.to_csv('data/intermediate/df_hmz_health_prospect_english.csv', index=False)



    # condition (depression) today
    df_hmz_health_prospect_english['med35d'] = df_hmz_health_prospect_english['med35d'].replace({ 98: np.nan})

    # Renaming
    df_hmz_health_prospect_english.rename(columns={'med35d': 'hmz_med_depression_today_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect_english.to_csv('data/intermediate/df_hmz_health_prospect_english.csv', index=False)




    # eye disease

    # creating a new variable because in prospect cataract and glaucoma are individual variables
    eye_vars = ['med33e___1', 'med33e___2']

    # Creating the new variable: NaN if both are missing, else take the max (1 if any condition is present)
    df_hmz_health_prospect_english['hmz_med_eye_prospect'] = df_hmz_health_prospect_english[eye_vars].apply(
        lambda row: np.nan if row.isna().all() else row.max(), axis=1)


    # Saving
    df_hmz_health_prospect_english.to_csv('data/intermediate/df_hmz_health_prospect_english.csv', index=False)


    # eye medication
    # Renaming
    df_hmz_health_prospect_english.rename(columns={'med33a': 'hmz_med_eye_medication_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect_english.to_csv('data/intermediate/df_hmz_health_prospect_english.csv', index=False)


    # condition (eye disease) today
    df_hmz_health_prospect_english['med33d'] = df_hmz_health_prospect_english['med33d'].replace({96: np.nan,98: np.nan})

    # Renaming
    df_hmz_health_prospect_english.rename(columns={'med33d': 'hmz_med_eye_today_prospect'}, inplace=True)

    # Saving
    df_hmz_health_prospect_english.to_csv('data/intermediate/df_hmz_health_prospect_english.csv', index=False)





    #------------------------------------------------------------------------------------------------
    # Family History
    # -----------------------------------------------------------------------------------------------


    fh_variables = [
        ("fhi1", "hmz_fh_diabetes_prospect"),
        ("fhi2", "hmz_fh_hypertension_prospect"),
        ("fhi5", "hmz_fh_heart_attack_prospect"),
        ("fhi6", "hmz_fh_heart_disease_prospect"),
        ("fhi7", "hmz_fh_stroke_prospect")
    ]

    # Recoding and renaming
    for col, new_col in fh_variables:
        if col in df_hmz_health_prospect_english.columns:
            df_hmz_health_prospect_english[col] = df_hmz_health_prospect_english[col].replace({96: np.nan, 97: np.nan, 98: np.nan})
            df_hmz_health_prospect_english.rename(columns={col: new_col}, inplace=True)

    # Saving
    df_hmz_health_prospect_english.to_csv('data/intermediate/df_hmz_health_prospect_english.csv', index=False)




    #------------------------------------------------------------------------------------------------
    # Health behavior: Tobacco
    # -----------------------------------------------------------------------------------------------

    # Renaming tob3 
    df_hmz_health_prospect_english.rename(columns={"tob3": "hmz_hb_tob3_prospect"}, inplace=True)

    # Recoding and renaming other tobacco-related variables
    tobacco_vars = {
        "tob12": "hmz_hb_tobacco_home_prospect",
        "tob13": "hmz_hb_tobacco_work_prospect",
        "tob14": "hmz_hb_tobacco_car_prospect",
        "tob15": "hmz_hb_tobacco_other_prospect"
    }

    for old, new in tobacco_vars.items():
        if old in df_hmz_health_prospect_english.columns:
            df_hmz_health_prospect_english[old] = df_hmz_health_prospect_english[old].replace({96: np.nan, 97: np.nan, 98: np.nan})
            df_hmz_health_prospect_english.rename(columns={old: new}, inplace=True)

    # Saving
    df_hmz_health_prospect_english.to_csv('data/intermediate/df_hmz_health_prospect_english.csv', index=False)






    #------------------------------------------------------------------------------------------------
    # Health behavior: Alcohol
    # -----------------------------------------------------------------------------------------------



    # Alcohol-related variables
    alcohol_vars = {
        "alc3": "hmz_hb_alcohol_prospect",
        "alc4a": "hmz_hb_alc4a_prospect",
        "alc4b": "hmz_hb_alc4b_prospect"}

    # Recoding and renaming
    for old, new in alcohol_vars.items():
        if old in df_hmz_health_prospect_english.columns:
            df_hmz_health_prospect_english[old] = df_hmz_health_prospect_english[old].replace({96: np.nan, 97: np.nan, 98: np.nan})
            df_hmz_health_prospect_english.rename(columns={old: new}, inplace=True)

    # Saving
    df_hmz_health_prospect_english.to_csv('data/intermediate/df_hmz_health_prospect_english.csv', index=False)




    #------------------------------------------------------------------------------------------------
    # Health behavior: Sleep
    # -----------------------------------------------------------------------------------------------

    # Mapping for renaming
    sleep_vars = {
        "slp1": "hmz_hb_slp1_prospect",
        "slp2": "hmz_hb_slp2_prospect",
        "slp2a": "hmz_hb_slp2t_ampm_prospect",
        "slp5": "hmz_hb_slp_problem_i_prospect",
        "slp6": "hmz_hb_slp_problem_ii_prospect",
        "slp7": "hmz_hb_slp_problem_iii_prospect",
        "slp8": "hmz_hb_slp_problem_iv_prospect",
        "slp9": "hmz_hb_slp_problem_v_prospect",
        "slp10a": "hmz_hb_slp_snore_prospect",
        "slp10b": "hmz_hb_slp_snore_ii_prospect"
    }

    # Defining base variables for recoding
    base_variables = list(sleep_vars.keys())

    # Recoding values: 96, 97, 98 -> NaN
    for var in base_variables:
        if var in df_hmz_health_prospect_english.columns:
            df_hmz_health_prospect_english[var] = df_hmz_health_prospect_english[var].replace({96: np.nan, 97: np.nan, 98: np.nan})

    # Renaming columns all at once
    df_hmz_health_prospect_english.rename(columns=sleep_vars, inplace=True)

    # Saving
    df_hmz_health_prospect_english.to_csv('data/intermediate/df_hmz_health_prospect_english.csv', index=False)

    #------------------------------------------------------------------------------------------------
    # Health behavior: Perceived Stress
    # -----------------------------------------------------------------------------------------------


    # hmz_pss	"Perceived stress score
    # PSS1 + PSS2 + PSS3 + PSS4 + PSS5 + PSS6 + PSS7 + PSS8 + PSS9 + PSS10 + PSS11 + PSS12 + PSS 13 + PSS14;"
    # variables need to be created


    base_variables = ["pss1", "pss2","pss3","pss4","pss5","pss6","pss7","pss8","pss9","pss10","pss11","pss12","pss13","pss14"]


    #Recoding  values: 96, 97, 98 -> NaN
    for var in base_variables:
        if var in df_hmz_health_prospect_english.columns:
           df_hmz_health_prospect_english[var] = df_hmz_health_prospect_english[var].replace({96: np.nan, 97: np.nan, 98: np.nan})


    # Recoding to harmonize with corresponding bprhs pss variables       
    # Recoding 1 - 0, 2 - 1, 3 -2, 4 - 3, 5 - 4
    df_hmz_health_prospect_english[base_variables] = df_hmz_health_prospect_english[base_variables].replace({1:0 ,2 :1 ,3 :2 ,4 :3, 5:4 })

    # Saving
    df_hmz_health_prospect_english.to_csv('data/intermediate/df_hmz_health_prospect_english.csv', index=False)

    # Second recoding to harmonize with the pss variables in bprhs that have a reversed order
    # recoding 0 - 4, 1-3, 2-2,3-1, 4,0 
    subset_variables = ['pss4', 'pss5', 'pss6', 'pss7', 'pss9', 'pss10', 'pss13']
    # transformation
    df_hmz_health_prospect_english[subset_variables] = df_hmz_health_prospect_english[subset_variables].replace({0:4, 1:3, 2:2, 3:1, 4:0})


    # Saving
    df_hmz_health_prospect_english.to_csv('data/intermediate/df_hmz_health_prospect_english.csv', index=False)


    # Creating the new variable pss in prospect by summing the variables pss1 to pss_14 
    df_hmz_health_prospect_english['hmz_pss_prospect'] = df_hmz_health_prospect_english[base_variables].apply(
        lambda row: np.nan if row.isna().any() else row.sum(),
        axis=1)


    # Saving
    df_hmz_health_bprhs_8.to_csv('data/intermediate/df_hmz_health_bprhs_8.csv', index=False)




    # Creating a new variable pss_a in prospect with imputed mean of pss1-pss14 if 7 or less are missing
    subset_pss_a_variables = ['pss1', 'pss2', 'pss3', 'pss4', 'pss5', 'pss6', 
                              'pss7', 'pss8', 'pss9', 'pss10', 'pss11', 
                              'pss12', 'pss13', 'pss14']

    # Transformation: Impute mean if 7 or fewer are missing, else set NaN
    df_hmz_health_prospect_english['hmz_pss_a_prospect'] = df_hmz_health_prospect_english[subset_pss_a_variables].apply(
        lambda row: np.nan if row.isna().sum() > 7 else row.fillna(row.mean()).sum(),
        axis=1)


    # Saving
    df_hmz_health_prospect_english.to_csv('data/intermediate/df_hmz_health_prospect_english.csv', index=False)



    # renaming the individual pss variables
    df_hmz_health_prospect_english.rename(columns={'pss1': 'hmz_pss1_prospect'}, inplace=True)
    df_hmz_health_prospect_english.rename(columns={'pss2': 'hmz_pss2_prospect'}, inplace=True)
    df_hmz_health_prospect_english.rename(columns={'pss3': 'hmz_pss3_prospect'}, inplace=True)
    df_hmz_health_prospect_english.rename(columns={'pss4': 'hmz_pss4_prospect'}, inplace=True)
    df_hmz_health_prospect_english.rename(columns={'pss5': 'hmz_pss5_prospect'}, inplace=True)
    df_hmz_health_prospect_english.rename(columns={'pss6': 'hmz_pss6_prospect'}, inplace=True)
    df_hmz_health_prospect_english.rename(columns={'pss7': 'hmz_pss7_prospect'}, inplace=True)
    df_hmz_health_prospect_english.rename(columns={'pss8': 'hmz_pss8_prospect'}, inplace=True)
    df_hmz_health_prospect_english.rename(columns={'pss9': 'hmz_pss9_prospect'}, inplace=True)
    df_hmz_health_prospect_english.rename(columns={'pss10': 'hmz_pss10_prospect'}, inplace=True)
    df_hmz_health_prospect_english.rename(columns={'pss11': 'hmz_pss11_prospect'}, inplace=True)
    df_hmz_health_prospect_english.rename(columns={'pss12': 'hmz_pss12_prospect'}, inplace=True)
    df_hmz_health_prospect_english.rename(columns={'pss13': 'hmz_pss13_prospect'}, inplace=True)
    df_hmz_health_prospect_english.rename(columns={'pss14': 'hmz_pss14_prospect'}, inplace=True)


    # Saving
    df_hmz_health_prospect_english.to_csv('data/intermediate/df_hmz_health_prospect_english.csv', index=False)


    #------------------------------------------------------------------------------------------------
    # Depression
    # -----------------------------------------------------------------------------------------------

    # hmz_dep_score: sum the dep variables ds1-ds20 in bprhs and dep1-dep20 in prospect


    base_variables = ["dep1", "dep2","dep3","dep4","dep5","dep6","dep7","dep8","dep9","dep10","dep11","dep12","dep13","dep14","dep15","dep16","dep17","dep18","dep19","dep20"]

    # Recoding  values: 96, 97, 98 -> NaN
    for var in base_variables:
        if var in df_hmz_health_prospect_english.columns:
           df_hmz_health_prospect_english[var] = df_hmz_health_prospect_english[var].replace({96: np.nan, 97: np.nan, 98: np.nan})

    # Recoding 1 - 0, 2 - 1, 3 -2, 4 - 3
    df_hmz_health_prospect_english[base_variables] = df_hmz_health_prospect_english[base_variables].replace({1:0 ,2 :1 ,3 :2 ,4 :3 })

    # Saving
    df_hmz_health_prospect_english.to_csv('data/intermediate/df_hmz_health_prospect_english.csv', index=False)

    # Second recoding to harmonize with the ds variables in bprhs that have a reversed order
    # recoding 0 - 3, 1-2, 2-1, 3-0
    subset_variables = ['dep4','dep8','dep12','dep16']
    # transformation
    df_hmz_health_prospect_english[subset_variables] = df_hmz_health_prospect_english[subset_variables].replace({0:3, 1:2, 2:1, 3:0})


    # Saving
    df_hmz_health_prospect_english.to_csv('data/intermediate/df_hmz_health_prospect_english.csv', index=False)


    # Creating the new variable ds in prospect by summing the variables pss1 to pss_14 
    df_hmz_health_prospect_english['hmz_ds_prospect'] = df_hmz_health_prospect_english[base_variables].apply(
        lambda row: np.nan if row.isna().any() else row.sum(),
        axis=1)


    # Creating a new variable ds_a in prospect with imputed mean of ds1-ds20 if 7 or less are missing
    subset_ds_a_variables = ["dep1", "dep2","dep3","dep4","dep5","dep6","dep7","dep8","dep9","dep10","dep11","dep12","dep13","dep14","dep15","dep16","dep17","dep18","dep19","dep20"]

    # Transformation: Impute mean if 10 or fewer are missing, else set NaN
    df_hmz_health_prospect_english['hmz_ds_a_prospect'] = df_hmz_health_prospect_english[subset_ds_a_variables].apply(
        lambda row: np.nan if row.isna().sum() > 10 else row.fillna(row.mean()).sum(),
        axis=1
    )

    # Saving
    df_hmz_health_prospect_english.to_csv('data/intermediate/df_hmz_health_prospect_english.csv', index=False)



    # renaming the individual ds variables
    df_hmz_health_prospect_english.rename(columns={'dep1': 'hmz_ds1_prospect'}, inplace=True)
    df_hmz_health_prospect_english.rename(columns={'dep2': 'hmz_ds2_prospect'}, inplace=True)
    df_hmz_health_prospect_english.rename(columns={'dep3': 'hmz_ds3_prospect'}, inplace=True)
    df_hmz_health_prospect_english.rename(columns={'dep4': 'hmz_ds4_prospect'}, inplace=True)
    df_hmz_health_prospect_english.rename(columns={'dep5': 'hmz_ds5_prospect'}, inplace=True)
    df_hmz_health_prospect_english.rename(columns={'dep6': 'hmz_ds6_prospect'}, inplace=True)
    df_hmz_health_prospect_english.rename(columns={'dep7': 'hmz_ds7_prospect'}, inplace=True)
    df_hmz_health_prospect_english.rename(columns={'dep8': 'hmz_ds8_prospect'}, inplace=True)
    df_hmz_health_prospect_english.rename(columns={'dep9': 'hmz_ds9_prospect'}, inplace=True)
    df_hmz_health_prospect_english.rename(columns={'dep10': 'hmz_ds10_prospect'}, inplace=True)
    df_hmz_health_prospect_english.rename(columns={'dep11': 'hmz_ds11_prospect'}, inplace=True)
    df_hmz_health_prospect_english.rename(columns={'dep12': 'hmz_ds12_prospect'}, inplace=True)
    df_hmz_health_prospect_english.rename(columns={'dep13': 'hmz_ds13_prospect'}, inplace=True)
    df_hmz_health_prospect_english.rename(columns={'dep14': 'hmz_ds14_prospect'}, inplace=True)
    df_hmz_health_prospect_english.rename(columns={'dep15': 'hmz_ds15_prospect'}, inplace=True)
    df_hmz_health_prospect_english.rename(columns={'dep16': 'hmz_ds16_prospect'}, inplace=True)
    df_hmz_health_prospect_english.rename(columns={'dep17': 'hmz_ds17_prospect'}, inplace=True)
    df_hmz_health_prospect_english.rename(columns={'dep18': 'hmz_ds18_prospect'}, inplace=True)
    df_hmz_health_prospect_english.rename(columns={'dep19': 'hmz_ds19_prospect'}, inplace=True)
    df_hmz_health_prospect_english.rename(columns={'dep20': 'hmz_ds20_prospect'}, inplace=True)


    # Saving
    df_hmz_health_prospect_english.to_csv('data/intermediate/df_hmz_health_prospect_english.csv', index=False)


    # -------------------------------------------------------------------------------------------------
    # Post-Processing  – PROSPECT English  health
    # -------------------------------------------------------------------------------------------------

    # --------------------------
    # Adding “health” prefix to every variable that starts with “hmz_”
    # --------------------------
    df_hmz_health_prospect_english.columns = [
        f"hmz_health_{c[4:]}" if c.startswith("hmz_") else c
        for c in df_hmz_health_prospect_english.columns]
    df_hmz_health_prospect_english.to_csv('data/intermediate/df_hmz_health_prospect_english.csv', index=False)


    # --------------------------
    #  Renaming REDCap event variable --> hmz_visit
    # --------------------------
    if "redcap_event_name" in df_hmz_health_prospect_english.columns:
        df_hmz_health_prospect_english["redcap_event_name"] = (
            df_hmz_health_prospect_english["redcap_event_name"]
            .replace({"baseline_arm_1": "v1", "visit_2_arm_1": "v2"}) )
        df_hmz_health_prospect_english.rename(
            columns={"redcap_event_name": "hmz_visit_prospect"}, inplace=True )
      
    df_hmz_health_prospect_english.to_csv('data/intermediate/df_hmz_health_prospect_english.csv', index=False)

    # --------------------------
    # Renaming record_id → hmz_record_id_prospect
    # --------------------------
    if "record_id" in df_hmz_health_prospect_english.columns:
        df_hmz_health_prospect_english.rename(
            columns={"record_id": "hmz_record_id_prospect"}, inplace=True)
        
    df_hmz_health_prospect_english.to_csv('data/intermediate/df_hmz_health_prospect_english.csv', index=False)


    # --------------------------
    # Keeping only studyid and hmz variables
    # --------------------------
    df_hmz_health_prospect_english = df_hmz_health_prospect_english[[col for col in df_hmz_health_prospect_english.columns if col.startswith('hmz_') or col in ['studyid']]]   
    df_hmz_health_prospect_english.to_csv('data/intermediate/df_hmz_health_prospect_english.csv', index=False)



    
    # ------------------------------------------------------------------------------------------------------------
    # Creating PROSPECT visit-specific files
    # ------------------------------------------------------------------------------------------------------------

    df_hmz_health_prospect_english = pd.read_csv("data/intermediate/df_hmz_health_prospect_english.csv")
    df_hmz_health_prospect_english = df_hmz_health_prospect_english[df_hmz_health_prospect_english["studyid"].notnull() ]

    # --------------------------
    # Splitting into Visit-1 and Visit-2 files
    # --------------------------
    # Visit 1
    df_hmz_health_prospect_english_visit_1 = df_hmz_health_prospect_english[df_hmz_health_prospect_english["hmz_visit_prospect"] == "v1"].copy()
    df_hmz_health_prospect_english_visit_1.rename(columns={col: f"{col}_v1" for col in df_hmz_health_prospect_english_visit_1.columns if col != "studyid"}, inplace=True)
    df_hmz_health_prospect_english_visit_1.rename(columns={"hmz_visit_prospect_v1": "visit"}, inplace=True)
    df_hmz_health_prospect_english_visit_1.to_csv("data/intermediate/df_hmz_health_prospect_english_visit_1.csv", index=False)

    # Visit 2
    df_hmz_health_prospect_english_visit_2 = df_hmz_health_prospect_english[df_hmz_health_prospect_english["hmz_visit_prospect"] == "v2"].copy()
    df_hmz_health_prospect_english_visit_2.rename(columns={col: f"{col}_v2" for col in df_hmz_health_prospect_english_visit_2.columns if col != "studyid"}, inplace=True)
    df_hmz_health_prospect_english_visit_2.rename(columns={"hmz_visit_prospect_v2": "visit"}, inplace=True)
    df_hmz_health_prospect_english_visit_2.to_csv("data/intermediate/df_hmz_health_prospect_english_visit_2.csv", index=False)


    # ------------------------------------------------------------------------------------------------------------
    # Renaming hmz visit --> visit
    # ------------------------------------------------------------------------------------------------------------
   
    df_hmz_health_prospect_english_visit_1.rename(columns={'hmz_visit_prospect_english_v1': 'visit'}, inplace=True)
    df_hmz_health_prospect_english_visit_2.rename(columns={'hmz_visit_prospect_english_v2': 'visit'}, inplace=True)
   
   # Saving
    df_hmz_health_prospect_english_visit_1.to_csv("data/intermediate/df_hmz_health_prospect_english_visit_1.csv", index=False)
    df_hmz_health_prospect_english_visit_2.to_csv("data/intermediate/df_hmz_health_prospect_english_visit_2.csv", index=False)


    
    return {"df_hmz_health_prospect_visit_1": df_hmz_health_prospect_visit_1,
            "df_hmz_health_prospect_visit_2": df_hmz_health_prospect_visit_2,
            "df_hmz_health_prospect_english_visit_1": df_hmz_health_prospect_english_visit_1,
            "df_hmz_health_prospect_english_visit_2": df_hmz_health_prospect_english_visit_2,
            "df_hmz_health_bprhs_0": df_hmz_health_bprhs_0,  
            "df_hmz_health_bprhs_2": df_hmz_health_bprhs_2,  
            "df_hmz_health_bprhs_5": df_hmz_health_bprhs_5, 
            "df_hmz_health_bprhs_8": df_hmz_health_bprhs_8  }
