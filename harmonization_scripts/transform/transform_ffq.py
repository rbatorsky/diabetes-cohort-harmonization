
def transform_ffq(config):


    import pandas as pd
    import numpy as np
    import os
   
    #------------------------------------------------------------------------------------------------
    # Loading the data: Spanish
    # -----------------------------------------------------------------------------------------------


    from harmonization_scripts.load.loader_ffq import load_ffq_spanish_data

    data = load_ffq_spanish_data(config)
    df_hmz_ffq_bprhs_0 = data['bprhs_0']
    df_hmz_ffq_bprhs_2 = data['bprhs_2']
    df_hmz_ffq_bprhs_5 = data['bprhs_5']
    df_hmz_ffq_bprhs_8 = data['bprhs_8']
    df_hmz_ffq_prospect = data['prospect']
    df_ffq_nutrients_prospect = pd.read_csv(config["ffq_prospect_perday_full"], encoding='latin1')

   


    #------------------------------------------------------------------------------------------------
    # Diet, Meal Place, Supplements
    # -----------------------------------------------------------------------------------------------


    # --------------------------------------
    # BPRHS
    # --------------------------------------

    # Diet type

    df_hmz_ffq_bprhs_0["diet_type"] = df_hmz_ffq_bprhs_0["diet_type"].replace({
        'Rx': 4,
        'Weight reduction': 3,
        'Vegetarian': 2,
        'Kosher': 1,
        'N/A': np.nan})

    # Saving
    df_hmz_ffq_bprhs_0.to_csv('data/intermediate/df_hmz_ffq_bprhs_0.csv', index=False)




    # Meal place

    meal_vars = ["meal_place_brk", "meal_place_lun", "meal_place_din"]


    replacements = {
        'Home': 1,
        'Work': 2,
        'Cafeteria': 3,
        'Fast food': 4,
        'Restaurant': 5,
        'N/A': np.nan,
        'MM': np.nan}

    for var in meal_vars:
        df_hmz_ffq_bprhs_0[var] = df_hmz_ffq_bprhs_0[var].replace(replacements)

    # Saving
    df_hmz_ffq_bprhs_0.to_csv('data/intermediate/df_hmz_ffq_bprhs_0.csv', index=False)


    # Supplements

    # removing option 0 in bprhs v0
    df_hmz_ffq_bprhs_0[[
        "supdur_1", "supdur_2", "supdur_3", "supdur_4", "supdur_5", "supdur_6",
        "supdur_7", "supdur_8", "supdur_9", "supdur_10", "supdur_11", "supdur_12", "supdur_13",
        "supdur_14", "supdur_15", "supdur_16", "supdur_17", "supdur_18"
    ]] = df_hmz_ffq_bprhs_0[[
        "supdur_1", "supdur_2", "supdur_3", "supdur_4", "supdur_5", "supdur_6",
        "supdur_7", "supdur_8", "supdur_9", "supdur_10", "supdur_11", "supdur_12", "supdur_13",
        "supdur_14", "supdur_15", "supdur_16", "supdur_17", "supdur_18"
    ]].replace({0: np.nan})


    # Saving
    df_hmz_ffq_bprhs_0.to_csv('data/intermediate/df_hmz_ffq_bprhs_0.csv', index=False)

    # Renaming 
    df_hmz_ffq_bprhs_0.rename(columns={
        "diet_type": "hmz_diet_type_bprhs_0",
        "meal_place_brk": "hmz_meal_place_breakfast_bprhs_0",
        "meal_place_lun": "hmz_meal_place_lunch_bprhs_0",
        "meal_place_din": "hmz_meal_place_dinner_bprhs_0",
        #"eat_out_frq_week": "hmz_eat_out_bprhs_0",
        "supp_use": "hmz_sup_use_bprhs_0",
        "supdur_1": "hmz_sup_dur_1_bprhs_0",
        "supdur_2": "hmz_sup_dur_2_bprhs_0",
        "supdur_3": "hmz_sup_dur_3_bprhs_0",
        "supdur_4": "hmz_sup_dur_4_bprhs_0",
        "supdur_5": "hmz_sup_dur_5_bprhs_0",
        "supdur_6": "hmz_sup_dur_6_bprhs_0",
        "supdur_7": "hmz_sup_dur_7_bprhs_0",
        "supdur_8": "hmz_sup_dur_8_bprhs_0",
        "supdur_9": "hmz_sup_dur_9_bprhs_0",
        "supdur_10": "hmz_sup_dur_10_bprhs_0",
        "supdur_11": "hmz_sup_dur_11_bprhs_0",
        "supdur_12": "hmz_sup_dur_12_bprhs_0",
        "supdur_13": "hmz_sup_dur_13_bprhs_0",
        "supdur_14": "hmz_sup_dur_14_bprhs_0",
        "supdur_15": "hmz_sup_dur_15_bprhs_0",
        "supdur_16": "hmz_sup_dur_16_bprhs_0",
        "supdur_17": "hmz_sup_dur_17_bprhs_0",
        "supdur_18": "hmz_sup_dur_18_bprhs_0"    }, inplace=True)


    # Saving 
    df_hmz_ffq_bprhs_0.to_csv('data/intermediate/df_hmz_ffq_bprhs_0.csv', index=False)






    # --------------------------------------
    # PROSPECT
    # --------------------------------------

    # summary variables

    summary_vars = ['summary18', 'summary19', 'summary20']

    # Recording value 6 with NaN
    df_hmz_ffq_prospect[summary_vars] = df_hmz_ffq_prospect[summary_vars].replace(6, np.nan)

    # Saving 
    df_hmz_ffq_prospect.to_csv('data/intermediate/df_hmz_ffq_prospect.csv', index=False)



    # Renaming
    df_hmz_ffq_prospect.rename(columns={
    "summary17": "hmz_diet_type_prospect",
    "summary18": "hmz_meal_place_breakfast_prospect",
    "summary19": "hmz_meal_place_lunch_prospect",
    "summary20": "hmz_meal_place_dinner_prospect",
    #"summary16": "hmz_eat_out_prospect",
    "supyn": "hmz_sup_use_prospect",
    "supdur1": "hmz_sup_dur_1_prospect",
    "supdur2": "hmz_sup_dur_2_prospect",
    "supdur3": "hmz_sup_dur_3_prospect",
    "supdur4": "hmz_sup_dur_4_prospect",
    "supdur5": "hmz_sup_dur_5_prospect",
    "supdur6": "hmz_sup_dur_6_prospect",
    "supdur7": "hmz_sup_dur_7_prospect",
    "supdur8": "hmz_sup_dur_8_prospect",
    "supdur9": "hmz_sup_dur_9_prospect",
    "supdur10": "hmz_sup_dur_10_prospect",
    "supdur11": "hmz_sup_dur_11_prospect",
    "supdur12": "hmz_sup_dur_12_prospect",
    "supdur13": "hmz_sup_dur_13_prospect",
    "supdur14": "hmz_sup_dur_14_prospect",
    "supdur15": "hmz_sup_dur_15_prospect",
    "supdur16": "hmz_sup_dur_16_prospect",
    "supdur17": "hmz_sup_dur_17_prospect",
    "supdur18": "hmz_sup_dur_18_prospect"}, inplace=True)


    # Saving 
    df_hmz_ffq_prospect.to_csv('data/intermediate/df_hmz_ffq_prospect.csv', index=False)



# Nutrients (calculated from food reports)


    # --------------------------------------
    # BPRHS
    # --------------------------------------


    df_hmz_ffq_bprhs_0.rename(columns={
    "gramamt_f": "hmz_gramamt_bprhs_0",
    "kcal_f": "hmz_kcal_bprhs_0",
    "kj_f": "hmz_kj_bprhs_0",
    "tcho_f": "hmz_tcho_bprhs_0",
    "fat_f": "hmz_fat_bprhs_0",
    "pro_f": "hmz_pro_bprhs_0",
    "vpro_f": "hmz_vpro_bprhs_0",
    "apro_f": "hmz_apro_bprhs_0",
    "alc_f": "hmz_alc_bprhs_0",
    "chol_f": "hmz_chol_bprhs_0",
    "sfa_f": "hmz_sfa_bprhs_0",
    "mfa_f": "hmz_mfa_bprhs_0",
    "pfa_f": "hmz_pfa_bprhs_0",
    "fruc_f": "hmz_fruc_bprhs_0",
    "gala_f": "hmz_gala_bprhs_0",
    "gluc_f": "hmz_gluc_bprhs_0",
    "lact_f": "hmz_lact_bprhs_0",
    "malt_f": "hmz_malt_bprhs_0",
    "sucr_f": "hmz_sucr_bprhs_0",
    "star_f": "hmz_star_bprhs_0",
    "tsugar_f": "hmz_tsugar_bprhs_0",
    "dfib_f": "hmz_dfib_bprhs_0",
    "wsdf_f": "hmz_wsdf_bprhs_0",
    "ifib_f": "hmz_ifib_bprhs_0",
    "pect_f": "hmz_pect_bprhs_0",
    "va_f": "hmz_va_bprhs_0",
    "acar_f": "hmz_acar_bprhs_0",
    "bceq_f": "hmz_bceq_bprhs_0",
    "bcar_f": "hmz_bcar_bprhs_0",
    "rl_f": "hmz_rl_bprhs_0",
    "varae_f": "hmz_varae_bprhs_0",
    "vare_f": "hmz_vare_bprhs_0",
    "bcry_f": "hmz_bcry_bprhs_0",
    "lyco_f": "hmz_lyco_bprhs_0",
    "lz_f": "hmz_lz_bprhs_0",
    "vb6_f": "hmz_vb6_bprhs_0",
    "vb12_f": "hmz_vb12_bprhs_0",
    "fol_f": "hmz_fol_bprhs_0",
    "dfe_f": "hmz_dfe_bprhs_0",
    "nfol_f": "hmz_nfol_bprhs_0",
    "sfol_f": "hmz_sfol_bprhs_0",
    "nia_f": "hmz_nia_bprhs_0",
    "niaeq_f": "hmz_niaeq_bprhs_0",
    "pant_f": "hmz_pant_bprhs_0",
    "thi_f": "hmz_thi_bprhs_0",
    "rib_f": "hmz_rib_bprhs_0",
    "choline_f": "hmz_choline_bprhs_0",
    "ttc_f": "hmz_ttc_bprhs_0",
    "atc_f": "hmz_atc_bprhs_0",
    "natatoc_f": "hmz_natatoc_bprhs_0",
    "synatoc_f": "hmz_synatoc_bprhs_0",
    "btc_f": "hmz_btc_bprhs_0",
    "dtc_f": "hmz_dtc_bprhs_0",
    "gtc_f": "hmz_gtc_bprhs_0",
    "vc_f": "hmz_vc_bprhs_0",
    "vd_f": "hmz_vd_bprhs_0",
    "vite_f": "hmz_vite_bprhs_0",
    "vk_f": "hmz_vk_bprhs_0",
    "ca_f": "hmz_ca_bprhs_0",
    "cu_f": "hmz_cu_bprhs_0",
    "fe_f": "hmz_fe_bprhs_0",
    "k_f": "hmz_k_bprhs_0",
    "na_f": "hmz_na_bprhs_0",
    "mg_f": "hmz_mg_bprhs_0",
    "mn_f": "hmz_mn_bprhs_0",
    "se_f": "hmz_se_bprhs_0",
    "zn_f": "hmz_zn_bprhs_0",
    "p_f": "hmz_p_bprhs_0",
    "s04_0_f": "hmz_s04_0_bprhs_0",
    "s06_0_f": "hmz_s06_0_bprhs_0",
    "s08_0_f": "hmz_s08_0_bprhs_0",
    "s10_0_f": "hmz_s10_0_bprhs_0",
    "s12_0_f": "hmz_s12_0_bprhs_0",
    "s14_0_f": "hmz_s14_0_bprhs_0",
    "s16_0_f": "hmz_s16_0_bprhs_0",
    "s17_0_f": "hmz_s17_0_bprhs_0",
    "s18_0_f": "hmz_s18_0_bprhs_0",
    "s20_0_f": "hmz_s20_0_bprhs_0",
    "s22_0_f": "hmz_s22_0_bprhs_0",
    "m14_1_f": "hmz_m14_1_bprhs_0",
    "m16_1_f": "hmz_m16_1_bprhs_0",
    "m18_1_f": "hmz_m18_1_bprhs_0",
    "m20_1_f": "hmz_m20_1_bprhs_0",
    "m22_1_f": "hmz_m22_1_bprhs_0",
    "p18_2_f": "hmz_p18_2_bprhs_0",
    "p18_3_f": "hmz_p18_3_bprhs_0",
    "p18_4_f": "hmz_p18_4_bprhs_0",
    "p20_4_f": "hmz_p20_4_bprhs_0",
    "p20_5_f": "hmz_p20_5_bprhs_0",
    "p22_5_f": "hmz_p22_5_bprhs_0",
    "p22_6_f": "hmz_p22_6_bprhs_0",
    "f161t_f": "hmz_f161t_bprhs_0",
    "f181t_f": "hmz_f181t_bprhs_0",
    "f182t_f": "hmz_f182t_bprhs_0",
    "ttfa_f": "hmz_ttfa_bprhs_0",
    "omega3_f": "hmz_omega3_bprhs_0",
    "cyst_f": "hmz_cyst_bprhs_0",
    "glut_f": "hmz_glut_bprhs_0",
    "glyc_f": "hmz_glyc_bprhs_0",
    "isol_f": "hmz_isol_bprhs_0",
    "hist_f": "hmz_hist_bprhs_0",
    "leuc_f": "hmz_leuc_bprhs_0",
    "lysi_f": "hmz_lysi_bprhs_0",
    "meth_f": "hmz_meth_bprhs_0",
    "phen_f": "hmz_phen_bprhs_0",
    "prol_f": "hmz_prol_bprhs_0",
    "seri_f": "hmz_seri_bprhs_0",
    "thre_f": "hmz_thre_bprhs_0",
    "tryp_f": "hmz_tryp_bprhs_0",
    "alan_f": "hmz_alan_bprhs_0",
    "argi_f": "hmz_argi_bprhs_0",
    "aspa_f": "hmz_aspa_bprhs_0",
    "tyro_f": "hmz_tyro_bprhs_0",
    "vali_f": "hmz_vali_bprhs_0",
    "mh3_f": "hmz_mh3_bprhs_0",
    "aspt_f": "hmz_aspt_bprhs_0",
    "glyt_f": "hmz_glyt_bprhs_0",
    "coum_f": "hmz_coum_bprhs_0",
    "daid_f": "hmz_daid_bprhs_0",
    "betaine_f": "hmz_betaine_bprhs_0",
    "bioa_f": "hmz_bioa_bprhs_0",
    "formon_f": "hmz_formon_bprhs_0",
    "geni_f": "hmz_geni_bprhs_0",
    "eryth_f": "hmz_eryth_bprhs_0",
    "mani_f": "hmz_mani_bprhs_0",
    "inos_f": "hmz_inos_bprhs_0",
    "lactl_f": "hmz_lactl_bprhs_0",
    "pini_f": "hmz_pini_bprhs_0",
    "sorb_f": "hmz_sorb_bprhs_0",
    "xyli_f": "hmz_xyli_bprhs_0",
    "acho_f": "hmz_acho_bprhs_0",
    "asugar_f": "hmz_asugar_bprhs_0",
    "sucl_f": "hmz_sucl_bprhs_0",
    "acesk_f": "hmz_acesk_bprhs_0",
    "oxal_f": "hmz_oxal_bprhs_0",
    "phyt_f": "hmz_phyt_bprhs_0",
    "sp_f": "hmz_sp_bprhs_0",
    "caf_f": "hmz_caf_bprhs_0",
    "ash_f": "hmz_ash_bprhs_0",
    "w_f": "hmz_w_bprhs_0",
    "nitrogen_f": "hmz_nitrogen_bprhs_0"}, inplace=True)

   # Saving 
    df_hmz_ffq_bprhs_0.to_csv('data/intermediate/df_hmz_ffq_bprhs_0.csv', index=False)



    df_hmz_ffq_bprhs_2.rename(columns={
    "gramamt_f_w2": "hmz_gramamt_bprhs_2",
    "kcal_f_w2": "hmz_kcal_bprhs_2",
    "kj_f_w2": "hmz_kj_bprhs_2",
    "tcho_f_w2": "hmz_tcho_bprhs_2",
    "fat_f_w2": "hmz_fat_bprhs_2",
    "pro_f_w2": "hmz_pro_bprhs_2",
    "vpro_f_w2": "hmz_vpro_bprhs_2",
    "apro_f_w2": "hmz_apro_bprhs_2",
    "alc_f_w2": "hmz_alc_bprhs_2",
    "chol_f_w2": "hmz_chol_bprhs_2",
    "sfa_f_w2": "hmz_sfa_bprhs_2",
    "mfa_f_w2": "hmz_mfa_bprhs_2",
    "pfa_f_w2": "hmz_pfa_bprhs_2",
    "fruc_f_w2": "hmz_fruc_bprhs_2",
    "gala_f_w2": "hmz_gala_bprhs_2",
    "gluc_f_w2": "hmz_gluc_bprhs_2",
    "lact_f_w2": "hmz_lact_bprhs_2",
    "malt_f_w2": "hmz_malt_bprhs_2",
    "sucr_f_w2": "hmz_sucr_bprhs_2",
    "star_f_w2": "hmz_star_bprhs_2",
    "tsugar_f_w2": "hmz_tsugar_bprhs_2",
    "dfib_f_w2": "hmz_dfib_bprhs_2",
    "wsdf_f_w2": "hmz_wsdf_bprhs_2",
    "ifib_f_w2": "hmz_ifib_bprhs_2",
    "pect_f_w2": "hmz_pect_bprhs_2",
    "va_f_w2": "hmz_va_bprhs_2",
    "acar_f_w2": "hmz_acar_bprhs_2",
    "bceq_f_w2": "hmz_bceq_bprhs_2",
    "bcar_f_w2": "hmz_bcar_bprhs_2",
    "rl_f_w2": "hmz_rl_bprhs_2",
    "varae_f_w2": "hmz_varae_bprhs_2",
    "vare_f_w2": "hmz_vare_bprhs_2",
    "bcry_f_w2": "hmz_bcry_bprhs_2",
    "lyco_f_w2": "hmz_lyco_bprhs_2",
    "lz_f_w2": "hmz_lz_bprhs_2",
    "vb6_f_w2": "hmz_vb6_bprhs_2",
    "vb12_f_w2": "hmz_vb12_bprhs_2",
    "fol_f_w2": "hmz_fol_bprhs_2",
    "dfe_f_w2": "hmz_dfe_bprhs_2",
    "nfol_f_w2": "hmz_nfol_bprhs_2",
    "sfol_f_w2": "hmz_sfol_bprhs_2",
    "nia_f_w2": "hmz_nia_bprhs_2",
    "niaeq_f_w2": "hmz_niaeq_bprhs_2",
    "pant_f_w2": "hmz_pant_bprhs_2",
    "thi_f_w2": "hmz_thi_bprhs_2",
    "rib_f_w2": "hmz_rib_bprhs_2",
    "choline_f_w2": "hmz_choline_bprhs_2",
    "ttc_f_w2": "hmz_ttc_bprhs_2",
    "atc_f_w2": "hmz_atc_bprhs_2",
    "natatoc_f_w2": "hmz_natatoc_bprhs_2",
    "synatoc_f_w2": "hmz_synatoc_bprhs_2",
    "btc_f_w2": "hmz_btc_bprhs_2",
    "dtc_f_w2": "hmz_dtc_bprhs_2",
    "gtc_f_w2": "hmz_gtc_bprhs_2",
    "vc_f_w2": "hmz_vc_bprhs_2",
    "vd_f_w2": "hmz_vd_bprhs_2",
    "vite_f_w2": "hmz_vite_bprhs_2",
    "vk_f_w2": "hmz_vk_bprhs_2",
    "ca_f_w2": "hmz_ca_bprhs_2",
    "cu_f_w2": "hmz_cu_bprhs_2",
    "fe_f_w2": "hmz_fe_bprhs_2",
    "k_f_w2": "hmz_k_bprhs_2",
    "na_f_w2": "hmz_na_bprhs_2",
    "mg_f_w2": "hmz_mg_bprhs_2",
    "mn_f_w2": "hmz_mn_bprhs_2",
    "se_f_w2": "hmz_se_bprhs_2",
    "zn_f_w2": "hmz_zn_bprhs_2",
    "p_f_w2": "hmz_p_bprhs_2",
    "s04_0_f_w2": "hmz_s04_0_bprhs_2",
    "s06_0_f_w2": "hmz_s06_0_bprhs_2",
    "s08_0_f_w2": "hmz_s08_0_bprhs_2",
    "s10_0_f_w2": "hmz_s10_0_bprhs_2",
    "s12_0_f_w2": "hmz_s12_0_bprhs_2",
    "s14_0_f_w2": "hmz_s14_0_bprhs_2",
    "s16_0_f_w2": "hmz_s16_0_bprhs_2",
    "s17_0_f_w2": "hmz_s17_0_bprhs_2",
    "s18_0_f_w2": "hmz_s18_0_bprhs_2",
    "s20_0_f_w2": "hmz_s20_0_bprhs_2",
    "s22_0_f_w2": "hmz_s22_0_bprhs_2",
    "m14_1_f_w2": "hmz_m14_1_bprhs_2",
    "m16_1_f_w2": "hmz_m16_1_bprhs_2",
    "m18_1_f_w2": "hmz_m18_1_bprhs_2",
    "m20_1_f_w2": "hmz_m20_1_bprhs_2",
    "m22_1_f_w2": "hmz_m22_1_bprhs_2",
    "p18_2_f_w2": "hmz_p18_2_bprhs_2",
    "p18_3_f_w2": "hmz_p18_3_bprhs_2",
    "p18_4_f_w2": "hmz_p18_4_bprhs_2",
    "p20_4_f_w2": "hmz_p20_4_bprhs_2",
    "p20_5_f_w2": "hmz_p20_5_bprhs_2",
    "p22_5_f_w2": "hmz_p22_5_bprhs_2",
    "p22_6_f_w2": "hmz_p22_6_bprhs_2",
    "f161t_f_w2": "hmz_f161t_bprhs_2",
    "f181t_f_w2": "hmz_f181t_bprhs_2",
    "f182t_f_w2": "hmz_f182t_bprhs_2",
    "ttfa_f_w2": "hmz_ttfa_bprhs_2",
    "omega3_f_w2": "hmz_omega3_bprhs_2",
    "cyst_f_w2": "hmz_cyst_bprhs_2",
    "glut_f_w2": "hmz_glut_bprhs_2",
    "glyc_f_w2": "hmz_glyc_bprhs_2",
    "isol_f_w2": "hmz_isol_bprhs_2",
    "hist_f_w2": "hmz_hist_bprhs_2",
    "leuc_f_w2": "hmz_leuc_bprhs_2",
    "lysi_f_w2": "hmz_lysi_bprhs_2",
    "meth_f_w2": "hmz_meth_bprhs_2",
    "phen_f_w2": "hmz_phen_bprhs_2",
    "prol_f_w2": "hmz_prol_bprhs_2",
    "seri_f_w2": "hmz_seri_bprhs_2",
    "thre_f_w2": "hmz_thre_bprhs_2",
    "tryp_f_w2": "hmz_tryp_bprhs_2",
    "alan_f_w2": "hmz_alan_bprhs_2",
    "argi_f_w2": "hmz_argi_bprhs_2",
    "aspa_f_w2": "hmz_aspa_bprhs_2",
    "tyro_f_w2": "hmz_tyro_bprhs_2",
    "vali_f_w2": "hmz_vali_bprhs_2",
    "mh3_f_w2": "hmz_mh3_bprhs_2",
    "aspt_f_w2": "hmz_aspt_bprhs_2",
    "glyt_f_w2": "hmz_glyt_bprhs_2",
    "coum_f_w2": "hmz_coum_bprhs_2",
    "daid_f_w2": "hmz_daid_bprhs_2",
    "betaine_f_w2": "hmz_betaine_bprhs_2",
    "bioa_f_w2": "hmz_bioa_bprhs_2",
    "formon_f_w2": "hmz_formon_bprhs_2",
    "geni_f_w2": "hmz_geni_bprhs_2",
    "eryth_f_w2": "hmz_eryth_bprhs_2",
    "mani_f_w2": "hmz_mani_bprhs_2",
    "inos_f_w2": "hmz_inos_bprhs_2",
    "lactl_f_w2": "hmz_lactl_bprhs_2",
    "pini_f_w2": "hmz_pini_bprhs_2",
    "sorb_f_w2": "hmz_sorb_bprhs_2",
    "xyli_f_w2": "hmz_xyli_bprhs_2",
    "acho_f_w2": "hmz_acho_bprhs_2",
    "asugar_f_w2": "hmz_asugar_bprhs_2",
    "sucl_f_w2": "hmz_sucl_bprhs_2",
    "acesk_f_w2": "hmz_acesk_bprhs_2",
    "oxal_f_w2": "hmz_oxal_bprhs_2",
    "phyt_f_w2": "hmz_phyt_bprhs_2",
    "sp_f_w2": "hmz_sp_bprhs_2",
    "caf_f_w2": "hmz_caf_bprhs_2",
    "ash_f_w2": "hmz_ash_bprhs_2",
    "w_f_w2": "hmz_w_bprhs_2",
    "nitrogen_f_w2": "hmz_nitrogen_bprhs_2"}, inplace=True)

   # Saving 
    df_hmz_ffq_bprhs_2.to_csv('data/intermediate/df_hmz_ffq_bprhs_2.csv', index=False)



    df_hmz_ffq_bprhs_5.rename(columns={
    "gramamt_f_w3": "hmz_gramamt_bprhs_5",
    "kcal_f_w3": "hmz_kcal_bprhs_5",
    "kj_f_w3": "hmz_kj_bprhs_5",
    "tcho_f_w3": "hmz_tcho_bprhs_5",
    "fat_f_w3": "hmz_fat_bprhs_5",
    "pro_f_w3": "hmz_pro_bprhs_5",
    "vpro_f_w3": "hmz_vpro_bprhs_5",
    "apro_f_w3": "hmz_apro_bprhs_5",
    "alc_f_w3": "hmz_alc_bprhs_5",
    "chol_f_w3": "hmz_chol_bprhs_5",
    "sfa_f_w3": "hmz_sfa_bprhs_5",
    "mfa_f_w3": "hmz_mfa_bprhs_5",
    "pfa_f_w3": "hmz_pfa_bprhs_5",
    "fruc_f_w3": "hmz_fruc_bprhs_5",
    "gala_f_w3": "hmz_gala_bprhs_5",
    "gluc_f_w3": "hmz_gluc_bprhs_5",
    "lact_f_w3": "hmz_lact_bprhs_5",
    "malt_f_w3": "hmz_malt_bprhs_5",
    "sucr_f_w3": "hmz_sucr_bprhs_5",
    "star_f_w3": "hmz_star_bprhs_5",
    "tsugar_f_w3": "hmz_tsugar_bprhs_5",
    "dfib_f_w3": "hmz_dfib_bprhs_5",
    "wsdf_f_w3": "hmz_wsdf_bprhs_5",
    "ifib_f_w3": "hmz_ifib_bprhs_5",
    "pect_f_w3": "hmz_pect_bprhs_5",
    "va_f_w3": "hmz_va_bprhs_5",
    "acar_f_w3": "hmz_acar_bprhs_5",
    "bceq_f_w3": "hmz_bceq_bprhs_5",
    "bcar_f_w3": "hmz_bcar_bprhs_5",
    "rl_f_w3": "hmz_rl_bprhs_5",
    "varae_f_w3": "hmz_varae_bprhs_5",
    "vare_f_w3": "hmz_vare_bprhs_5",
    "bcry_f_w3": "hmz_bcry_bprhs_5",
    "lyco_f_w3": "hmz_lyco_bprhs_5",
    "lz_f_w3": "hmz_lz_bprhs_5",
    "vb6_f_w3": "hmz_vb6_bprhs_5",
    "vb12_f_w3": "hmz_vb12_bprhs_5",
    "fol_f_w3": "hmz_fol_bprhs_5",
    "dfe_f_w3": "hmz_dfe_bprhs_5",
    "nfol_f_w3": "hmz_nfol_bprhs_5",
    "sfol_f_w3": "hmz_sfol_bprhs_5",
    "nia_f_w3": "hmz_nia_bprhs_5",
    "niaeq_f_w3": "hmz_niaeq_bprhs_5",
    "pant_f_w3": "hmz_pant_bprhs_5",
    "thi_f_w3": "hmz_thi_bprhs_5",
    "rib_f_w3": "hmz_rib_bprhs_5",
    "choline_f_w3": "hmz_choline_bprhs_5",
    "ttc_f_w3": "hmz_ttc_bprhs_5",
    "atc_f_w3": "hmz_atc_bprhs_5",
    "natatoc_f_w3": "hmz_natatoc_bprhs_5",
    "synatoc_f_w3": "hmz_synatoc_bprhs_5",
    "btc_f_w3": "hmz_btc_bprhs_5",
    "dtc_f_w3": "hmz_dtc_bprhs_5",
    "gtc_f_w3": "hmz_gtc_bprhs_5",
    "vc_f_w3": "hmz_vc_bprhs_5",
    "vd_f_w3": "hmz_vd_bprhs_5",
    "vite_f_w3": "hmz_vite_bprhs_5",
    "vk_f_w3": "hmz_vk_bprhs_5",
    "ca_f_w3": "hmz_ca_bprhs_5",
    "cu_f_w3": "hmz_cu_bprhs_5",
    "fe_f_w3": "hmz_fe_bprhs_5",
    "k_f_w3": "hmz_k_bprhs_5",
    "na_f_w3": "hmz_na_bprhs_5",
    "mg_f_w3": "hmz_mg_bprhs_5",
    "mn_f_w3": "hmz_mn_bprhs_5",
    "se_f_w3": "hmz_se_bprhs_5",
    "zn_f_w3": "hmz_zn_bprhs_5",
    "p_f_w3": "hmz_p_bprhs_5",
    "s04_0_f_w3": "hmz_s04_0_bprhs_5",
    "s06_0_f_w3": "hmz_s06_0_bprhs_5",
    "s08_0_f_w3": "hmz_s08_0_bprhs_5",
    "s10_0_f_w3": "hmz_s10_0_bprhs_5",
    "s12_0_f_w3": "hmz_s12_0_bprhs_5",
    "s14_0_f_w3": "hmz_s14_0_bprhs_5",
    "s16_0_f_w3": "hmz_s16_0_bprhs_5",
    "s17_0_f_w3": "hmz_s17_0_bprhs_5",
    "s18_0_f_w3": "hmz_s18_0_bprhs_5",
    "s20_0_f_w3": "hmz_s20_0_bprhs_5",
    "s22_0_f_w3": "hmz_s22_0_bprhs_5",
    "m14_1_f_w3": "hmz_m14_1_bprhs_5",
    "m16_1_f_w3": "hmz_m16_1_bprhs_5",
    "m18_1_f_w3": "hmz_m18_1_bprhs_5",
    "m20_1_f_w3": "hmz_m20_1_bprhs_5",
    "m22_1_f_w3": "hmz_m22_1_bprhs_5",
    "p18_2_f_w3": "hmz_p18_2_bprhs_5",
    "p18_3_f_w3": "hmz_p18_3_bprhs_5",
    "p18_4_f_w3": "hmz_p18_4_bprhs_5",
    "p20_4_f_w3": "hmz_p20_4_bprhs_5",
    "p20_5_f_w3": "hmz_p20_5_bprhs_5",
    "p22_5_f_w3": "hmz_p22_5_bprhs_5",
    "p22_6_f_w3": "hmz_p22_6_bprhs_5",
    "f161t_f_w3": "hmz_f161t_bprhs_5",
    "f181t_f_w3": "hmz_f181t_bprhs_5",
    "f182t_f_w3": "hmz_f182t_bprhs_5",
    "ttfa_f_w3": "hmz_ttfa_bprhs_5",
    "omega3_f_w3": "hmz_omega3_bprhs_5",
    "cyst_f_w3": "hmz_cyst_bprhs_5",
    "glut_f_w3": "hmz_glut_bprhs_5",
    "glyc_f_w3": "hmz_glyc_bprhs_5",
    "isol_f_w3": "hmz_isol_bprhs_5",
    "hist_f_w3": "hmz_hist_bprhs_5",
    "leuc_f_w3": "hmz_leuc_bprhs_5",
    "lysi_f_w3": "hmz_lysi_bprhs_5",
    "meth_f_w3": "hmz_meth_bprhs_5",
    "phen_f_w3": "hmz_phen_bprhs_5",
    "prol_f_w3": "hmz_prol_bprhs_5",
    "seri_f_w3": "hmz_seri_bprhs_5",
    "thre_f_w3": "hmz_thre_bprhs_5",
    "tryp_f_w3": "hmz_tryp_bprhs_5",
    "alan_f_w3": "hmz_alan_bprhs_5",
    "argi_f_w3": "hmz_argi_bprhs_5",
    "aspa_f_w3": "hmz_aspa_bprhs_5",
    "tyro_f_w3": "hmz_tyro_bprhs_5",
    "vali_f_w3": "hmz_vali_bprhs_5",
    "mh3_f_w3": "hmz_mh3_bprhs_5",
    "aspt_f_w3": "hmz_aspt_bprhs_5",
    "glyt_f_w3": "hmz_glyt_bprhs_5",
    "coum_f_w3": "hmz_coum_bprhs_5",
    "daid_f_w3": "hmz_daid_bprhs_5",
    "betaine_f_w3": "hmz_betaine_bprhs_5",
    "bioa_f_w3": "hmz_bioa_bprhs_5",
    "formon_f_w3": "hmz_formon_bprhs_5",
    "geni_f_w3": "hmz_geni_bprhs_5",
    "eryth_f_w3": "hmz_eryth_bprhs_5",
    "mani_f_w3": "hmz_mani_bprhs_5",
    "inos_f_w3": "hmz_inos_bprhs_5",
    "lactl_f_w3": "hmz_lactl_bprhs_5",
    "pini_f_w3": "hmz_pini_bprhs_5",
    "sorb_f_w3": "hmz_sorb_bprhs_5",
    "xyli_f_w3": "hmz_xyli_bprhs_5",
    "acho_f_w3": "hmz_acho_bprhs_5",
    "asugar_f_w3": "hmz_asugar_bprhs_5",
    "sucl_f_w3": "hmz_sucl_bprhs_5",
    "acesk_f_w3": "hmz_acesk_bprhs_5",
    "oxal_f_w3": "hmz_oxal_bprhs_5",
    "phyt_f_w3": "hmz_phyt_bprhs_5",
    "sp_f_w3": "hmz_sp_bprhs_5",
    "caf_f_w3": "hmz_caf_bprhs_5",
    "ash_f_w3": "hmz_ash_bprhs_5",
    "w_f_w3": "hmz_w_bprhs_5",
    "nitrogen_f_w3": "hmz_nitrogen_bprhs_5"}, inplace=True)

   # Saving 
    df_hmz_ffq_bprhs_5.to_csv('data/intermediate/df_hmz_ffq_bprhs_5.csv', index=False)


    df_hmz_ffq_bprhs_8.rename(columns={
 "gramamt": "hmz_gramamt_bprhs_8",
"rfkcal": "hmz_kcal_bprhs_8",
"rfkj": "hmz_kj_bprhs_8",
"rftcho": "hmz_tcho_bprhs_8",
"rffat": "hmz_fat_bprhs_8",
"rfpro": "hmz_pro_bprhs_8",
"rfvpro": "hmz_vpro_bprhs_8",
"rfapro": "hmz_apro_bprhs_8",
"rfalc": "hmz_alc_bprhs_8",
"rfchol": "hmz_chol_bprhs_8",
"rfsfa": "hmz_sfa_bprhs_8",
"rfmfa": "hmz_mfa_bprhs_8",
"rfpfa": "hmz_pfa_bprhs_8",
"rffruc": "hmz_fruc_bprhs_8",
"rfgala": "hmz_gala_bprhs_8",
"rfgluc": "hmz_gluc_bprhs_8",
"rflact": "hmz_lact_bprhs_8",
"rfmalt": "hmz_malt_bprhs_8",
"rfsucr": "hmz_sucr_bprhs_8",
"rfstar": "hmz_star_bprhs_8",
"rftsugar": "hmz_tsugar_bprhs_8",
"rfdfib": "hmz_dfib_bprhs_8",
"rfwsdf": "hmz_wsdf_bprhs_8",
"rfifib": "hmz_ifib_bprhs_8",
"rfpect": "hmz_pect_bprhs_8",
"rfva": "hmz_va_bprhs_8",
"rfacar": "hmz_acar_bprhs_8",
"rfbceq": "hmz_bceq_bprhs_8",
"rfbcar": "hmz_bcar_bprhs_8",
"rfrl": "hmz_rl_bprhs_8",
"rfvarae": "hmz_varae_bprhs_8",
"rfvare": "hmz_vare_bprhs_8",
"rfbcry": "hmz_bcry_bprhs_8",
"rflyco": "hmz_lyco_bprhs_8",
"rflz": "hmz_lz_bprhs_8",
"rfvb6": "hmz_vb6_bprhs_8",
"rfvb12": "hmz_vb12_bprhs_8",
"rffol": "hmz_fol_bprhs_8",
"rfdfe": "hmz_dfe_bprhs_8",
"rfnfol": "hmz_nfol_bprhs_8",
"rfsfol": "hmz_sfol_bprhs_8",
"rfnia": "hmz_nia_bprhs_8",
"rfniaeq": "hmz_niaeq_bprhs_8",
"rfpant": "hmz_pant_bprhs_8",
"rfthi": "hmz_thi_bprhs_8",
"rfrib": "hmz_rib_bprhs_8",
"rfcholine": "hmz_choline_bprhs_8",
"rfttc": "hmz_ttc_bprhs_8",
"rfatc": "hmz_atc_bprhs_8",
"rfnatatoc": "hmz_natatoc_bprhs_8",
"rfsynatoc": "hmz_synatoc_bprhs_8",
"rfbtc": "hmz_btc_bprhs_8",
"rfdtc": "hmz_dtc_bprhs_8",
"rfgtc": "hmz_gtc_bprhs_8",
"rfvc": "hmz_vc_bprhs_8",
"rfvd": "hmz_vd_bprhs_8",
"rfvite": "hmz_vite_bprhs_8",
"rfvk": "hmz_vk_bprhs_8",
"rfca": "hmz_ca_bprhs_8",
"rfcu": "hmz_cu_bprhs_8",
"rffe": "hmz_fe_bprhs_8",
"rfk": "hmz_k_bprhs_8",
"rfna": "hmz_na_bprhs_8",
"rfmg": "hmz_mg_bprhs_8",
"rfmn": "hmz_mn_bprhs_8",
"rfse": "hmz_se_bprhs_8",
"rfzn": "hmz_zn_bprhs_8",
"rfp": "hmz_p_bprhs_8",
"rfs04_0": "hmz_s04_0_bprhs_8",
"rfs06_0": "hmz_s06_0_bprhs_8",
"rfs08_0": "hmz_s08_0_bprhs_8",
"rfs10_0": "hmz_s10_0_bprhs_8",
"rfs12_0": "hmz_s12_0_bprhs_8",
"rfs14_0": "hmz_s14_0_bprhs_8",
"rfs16_0": "hmz_s16_0_bprhs_8",
"rfs17_0": "hmz_s17_0_bprhs_8",
"rfs18_0": "hmz_s18_0_bprhs_8",
"rfs20_0": "hmz_s20_0_bprhs_8",
"rfs22_0": "hmz_s22_0_bprhs_8",
"rfm14_1": "hmz_m14_1_bprhs_8",
"rfm16_1": "hmz_m16_1_bprhs_8",
"rfm18_1": "hmz_m18_1_bprhs_8",
"rfm20_1": "hmz_m20_1_bprhs_8",
"rfm22_1": "hmz_m22_1_bprhs_8",
"rfp18_2": "hmz_p18_2_bprhs_8",
"rfp18_3": "hmz_p18_3_bprhs_8",
"rfp18_4": "hmz_p18_4_bprhs_8",
"rfp20_4": "hmz_p20_4_bprhs_8",
"rfp20_5": "hmz_p20_5_bprhs_8",
"rfp22_5": "hmz_p22_5_bprhs_8",
"rfp22_6": "hmz_p22_6_bprhs_8",
"rff161t": "hmz_f161t_bprhs_8",
"rff181t": "hmz_f181t_bprhs_8",
"rff182t": "hmz_f182t_bprhs_8",
"rfttfa": "hmz_ttfa_bprhs_8",
"rfomega3": "hmz_omega3_bprhs_8",
"rfcyst": "hmz_cyst_bprhs_8",
"rfglut": "hmz_glut_bprhs_8",
"rfglyc": "hmz_glyc_bprhs_8",
"rfisol": "hmz_isol_bprhs_8",
"rfhist": "hmz_hist_bprhs_8",
"rfleuc": "hmz_leuc_bprhs_8",
"rflysi": "hmz_lysi_bprhs_8",
"rfmeth": "hmz_meth_bprhs_8",
"rfphen": "hmz_phen_bprhs_8",
"rfprol": "hmz_prol_bprhs_8",
"rfseri": "hmz_seri_bprhs_8",
"rfthre": "hmz_thre_bprhs_8",
"rftryp": "hmz_tryp_bprhs_8",
"rfalan": "hmz_alan_bprhs_8",
"rfargi": "hmz_argi_bprhs_8",
"rfaspa": "hmz_aspa_bprhs_8",
"rftyro": "hmz_tyro_bprhs_8",
"rfvali": "hmz_vali_bprhs_8",
"rfmh3": "hmz_mh3_bprhs_8",
"rfaspt": "hmz_aspt_bprhs_8",
"rfglyt": "hmz_glyt_bprhs_8",
"rfcoum": "hmz_coum_bprhs_8",
"rfdaid": "hmz_daid_bprhs_8",
"rfbetaine": "hmz_betaine_bprhs_8",
"rfbioa": "hmz_bioa_bprhs_8",
"rfformon": "hmz_formon_bprhs_8",
"rfgeni": "hmz_geni_bprhs_8",
"rferyth": "hmz_eryth_bprhs_8",
"rfmani": "hmz_mani_bprhs_8",
"rfinos": "hmz_inos_bprhs_8",
"rflactl": "hmz_lactl_bprhs_8",
"rfpini": "hmz_pini_bprhs_8",
"rfsorb": "hmz_sorb_bprhs_8",
"rfxyli": "hmz_xyli_bprhs_8",
"rfacho": "hmz_acho_bprhs_8",
"rfasugar": "hmz_asugar_bprhs_8",
"rfsucl": "hmz_sucl_bprhs_8",
"rfacesk": "hmz_acesk_bprhs_8",
"rfoxal": "hmz_oxal_bprhs_8",
"rfphyt": "hmz_phyt_bprhs_8",
"rfsp": "hmz_sp_bprhs_8",
"rfcaf": "hmz_caf_bprhs_8",
"rfash": "hmz_ash_bprhs_8",
"rfw": "hmz_w_bprhs_8",
"rfnitrogen": "hmz_nitrogen_bprhs_8"}, inplace=True)

    df_hmz_ffq_bprhs_8.to_csv('data/intermediate/df_hmz_ffq_bprhs_8.csv', index=False)



    # --------------------------------------
    # PROSPECT
    # --------------------------------------

    # adjusting visit column
    df_ffq_nutrients_prospect["visit"] = df_ffq_nutrients_prospect["visit"].astype(str).str.strip().replace({"1": "v1", "2": "v2"})

 # Saving 
    df_ffq_nutrients_prospect.to_csv('data/intermediate/df_ffq_nutrients_prospect.csv', index=False)



    df_ffq_nutrients_prospect.rename(columns={
 "gramamt": "hmz_gramamt_prospect",
 "rfkcal": "hmz_kcal_prospect",
 "rfkj": "hmz_kj_prospect",
 "rftcho": "hmz_tcho_prospect",
 "rffat": "hmz_fat_prospect",
 "rfpro": "hmz_pro_prospect",
 "rfvpro": "hmz_vpro_prospect",
 "rfapro": "hmz_apro_prospect",
 "rfalc": "hmz_alc_prospect",
 "rfchol": "hmz_chol_prospect",
 "rfsfa": "hmz_sfa_prospect",
 "rfmfa": "hmz_mfa_prospect",
 "rfpfa": "hmz_pfa_prospect",
 "rffruc": "hmz_fruc_prospect",
 "rfgala": "hmz_gala_prospect",
 "rfgluc": "hmz_gluc_prospect",
 "rflact": "hmz_lact_prospect",
 "rfmalt": "hmz_malt_prospect",
 "rfsucr": "hmz_sucr_prospect",
 "rfstar": "hmz_star_prospect",
 "rftsugar": "hmz_tsugar_prospect",
 "rfdfib": "hmz_dfib_prospect",
 "rfwsdf": "hmz_wsdf_prospect",
 "rfifib": "hmz_ifib_prospect",
 "rfpect": "hmz_pect_prospect",
 "rfva": "hmz_va_prospect",
 "rfacar": "hmz_acar_prospect",
 "rfbceq": "hmz_bceq_prospect",
 "rfbcar": "hmz_bcar_prospect",
 "rfrl": "hmz_rl_prospect",
 "rfvarae": "hmz_varae_prospect",
 "rfvare": "hmz_vare_prospect",
 "rfbcry": "hmz_bcry_prospect",
 "rflyco": "hmz_lyco_prospect",
 "rflz": "hmz_lz_prospect",
 "rfvb6": "hmz_vb6_prospect",
 "rfvb12": "hmz_vb12_prospect",
 "rffol": "hmz_fol_prospect",
 "rfdfe": "hmz_dfe_prospect",
 "rfnfol": "hmz_nfol_prospect",
 "rfsfol": "hmz_sfol_prospect",
 "rfnia": "hmz_nia_prospect",
 "rfniaeq": "hmz_niaeq_prospect",
 "rfpant": "hmz_pant_prospect",
 "rfthi": "hmz_thi_prospect",
 "rfrib": "hmz_rib_prospect",
 "rfcholine": "hmz_choline_prospect",
 "rfttc": "hmz_ttc_prospect",
 "rfatc": "hmz_atc_prospect",
 "rfnatatoc": "hmz_natatoc_prospect",
 "rfsynatoc": "hmz_synatoc_prospect",
 "rfbtc": "hmz_btc_prospect",
 "rfdtc": "hmz_dtc_prospect",
 "rfgtc": "hmz_gtc_prospect",
 "rfvc": "hmz_vc_prospect",
 "rfvd": "hmz_vd_prospect",
 "rfvite": "hmz_vite_prospect",
 "rfvk": "hmz_vk_prospect",
 "rfca": "hmz_ca_prospect",
 "rfcu": "hmz_cu_prospect",
 "rffe": "hmz_fe_prospect",
 "rfk": "hmz_k_prospect",
 "rfna": "hmz_na_prospect",
 "rfmg": "hmz_mg_prospect",
 "rfmn": "hmz_mn_prospect",
 "rfse": "hmz_se_prospect",
 "rfzn": "hmz_zn_prospect",
 "rfp": "hmz_p_prospect",
 "rfs04_0": "hmz_s04_0_prospect",
 "rfs06_0": "hmz_s06_0_prospect",
 "rfs08_0": "hmz_s08_0_prospect",
 "rfs10_0": "hmz_s10_0_prospect",
 "rfs12_0": "hmz_s12_0_prospect",
 "rfs14_0": "hmz_s14_0_prospect",
 "rfs16_0": "hmz_s16_0_prospect",
 "rfs17_0": "hmz_s17_0_prospect",
 "rfs18_0": "hmz_s18_0_prospect",
 "rfs20_0": "hmz_s20_0_prospect",
 "rfs22_0": "hmz_s22_0_prospect",
 "rfm14_1": "hmz_m14_1_prospect",
 "rfm16_1": "hmz_m16_1_prospect",
 "rfm18_1": "hmz_m18_1_prospect",
 "rfm20_1": "hmz_m20_1_prospect",
 "rfm22_1": "hmz_m22_1_prospect",
 "rfp18_2": "hmz_p18_2_prospect",
 "rfp18_3": "hmz_p18_3_prospect",
 "rfp18_4": "hmz_p18_4_prospect",
 "rfp20_4": "hmz_p20_4_prospect",
 "rfp20_5": "hmz_p20_5_prospect",
 "rfp22_5": "hmz_p22_5_prospect",
 "rfp22_6": "hmz_p22_6_prospect",
 "rff161t": "hmz_f161t_prospect",
 "rff181t": "hmz_f181t_prospect",
 "rff182t": "hmz_f182t_prospect",
 "rfttfa": "hmz_ttfa_prospect",
 "rfomega3": "hmz_omega3_prospect",
 "rfcyst": "hmz_cyst_prospect",
 "rfglut": "hmz_glut_prospect",
 "rfglyc": "hmz_glyc_prospect",
 "rfisol": "hmz_isol_prospect",
 "rfhist": "hmz_hist_prospect",
 "rfleuc": "hmz_leuc_prospect",
 "rflysi": "hmz_lysi_prospect",
 "rfmeth": "hmz_meth_prospect",
 "rfphen": "hmz_phen_prospect",
 "rfprol": "hmz_prol_prospect",
 "rfseri": "hmz_seri_prospect",
 "rfthre": "hmz_thre_prospect",
 "rftryp": "hmz_tryp_prospect",
 "rfalan": "hmz_alan_prospect",
 "rfargi": "hmz_argi_prospect",
 "rfaspa": "hmz_aspa_prospect",
 "rftyro": "hmz_tyro_prospect",
 "rfvali": "hmz_vali_prospect",
 "rfmh3": "hmz_mh3_prospect",
 "rfaspt": "hmz_aspt_prospect",
 "rfglyt": "hmz_glyt_prospect",
 "rfcoum": "hmz_coum_prospect",
 "rfdaid": "hmz_daid_prospect",
 "rfbetaine": "hmz_betaine_prospect",
 "rfbioa": "hmz_bioa_prospect",
 "rfformon": "hmz_formon_prospect",
 "rfgeni": "hmz_geni_prospect",
 "rferyth": "hmz_eryth_prospect",
 "rfmani": "hmz_mani_prospect",
 "rfinos": "hmz_inos_prospect",
 "rflactl": "hmz_lactl_prospect",
 "rfpini": "hmz_pini_prospect",
 "rfsorb": "hmz_sorb_prospect",
 "rfxyli": "hmz_xyli_prospect",
 "rfacho": "hmz_acho_prospect",
 "rfasugar": "hmz_asugar_prospect",
 "rfsucl": "hmz_sucl_prospect",
 "rfacesk": "hmz_acesk_prospect",
 "rfoxal": "hmz_oxal_prospect",
 "rfphyt": "hmz_phyt_prospect",
 "rfsp": "hmz_sp_prospect",
 "rfcaf": "hmz_caf_prospect",
 "rfash": "hmz_ash_prospect",
 "rfw": "hmz_w_prospect",
 "rfnitrogen": "hmz_nitrogen_prospect"}, inplace=True)
    
 # Saving 
    df_ffq_nutrients_prospect.to_csv('data/intermediate/df_ffq_nutrients_prospect.csv', index=False)


    
    #------------------------------------------------------------------------------------------------
    # Post-Processing - BPRHS and PROSPECT (Spanish) – ffq
    #------------------------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------------------------------------
    #  Adding prefix 'hmz_ffq_' to variables starting with 'hmz_' 
    # ------------------------------------------------------------------------------------------------------------
    datasets_ffq = {
             "df_hmz_ffq_bprhs_0": df_hmz_ffq_bprhs_0,
             "df_hmz_ffq_bprhs_2": df_hmz_ffq_bprhs_2,
             "df_hmz_ffq_bprhs_5": df_hmz_ffq_bprhs_5,
             "df_hmz_ffq_bprhs_8": df_hmz_ffq_bprhs_8,
             "df_hmz_ffq_prospect": df_hmz_ffq_prospect}

    for name, df in datasets_ffq.items():
             df.columns = [f"hmz_ffq_{col[4:]}" if col.startswith('hmz_') else col for col in df.columns]
             df.to_csv(f"data/intermediate/{name}.csv", index=False)
             

        # ------------------------------------------------------------------------------------------------------------
        #  Adding visit column (bprhs)
        # ------------------------------------------------------------------------------------------------------------
    df_hmz_ffq_bprhs_0["hmz_visit_bprhs_0"] = df_hmz_ffq_bprhs_0["studyid"].notna().map({True: "v1", False: None})
    df_hmz_ffq_bprhs_2["hmz_visit_bprhs_2"] = df_hmz_ffq_bprhs_2["studyid"].notna().map({True: "v2", False: None})
    df_hmz_ffq_bprhs_5["hmz_visit_bprhs_5"] = df_hmz_ffq_bprhs_5["studyid"].notna().map({True: "v3", False: None})
    df_hmz_ffq_bprhs_8["hmz_visit_bprhs_8"] = df_hmz_ffq_bprhs_8["studyid"].notna().map({True: "v4", False: None})


         # Saving 
    df_hmz_ffq_bprhs_0.to_csv('data/intermediate/df_hmz_ffq_bprhs_0.csv', index=False)
    df_hmz_ffq_bprhs_2.to_csv('data/intermediate/df_hmz_ffq_bprhs_2.csv', index=False)
    df_hmz_ffq_bprhs_5.to_csv('data/intermediate/df_hmz_ffq_bprhs_5.csv', index=False)
    df_hmz_ffq_bprhs_8.to_csv('data/intermediate/df_hmz_ffq_bprhs_8.csv', index=False)
    df_hmz_ffq_prospect.to_csv('data/intermediate/df_hmz_ffq_prospect.csv', index=False)

        # ------------------------------------------------------------------------------------------------------------
        # Renaming redcap event --> hmz_visit (prospect)
        # ------------------------------------------------------------------------------------------------------------
    if "redcap_event_name" in df_hmz_ffq_prospect.columns:
             df_hmz_ffq_prospect["redcap_event_name"] = df_hmz_ffq_prospect["redcap_event_name"].replace({
                 "visit_1_arm_1": "v1",
                 "visit_2_arm_1": "v2"})
             df_hmz_ffq_prospect.rename(columns={"redcap_event_name": "hmz_visit_prospect"}, inplace=True)
             df_hmz_ffq_prospect.to_csv('data/intermediate/df_hmz_ffq_prospect.csv', index=False)


        # ------------------------------------------------------------------------------------------------------------
        # Renaming visit (for nutrients data) --> hmz_visit (prospect)
        # ------------------------------------------------------------------------------------------------------------
    if "visit" in df_hmz_ffq_prospect.columns:
             df_hmz_ffq_prospect["visit"] = df_hmz_ffq_prospect["visit"].replace({
                 1: "v1",
                 2: "v2"})
             df_hmz_ffq_prospect.rename(columns={"visit": "hmz_visit_prospect"}, inplace=True)
             df_hmz_ffq_prospect.to_csv('data/intermediate/df_hmz_ffq_prospect.csv', index=False)



        # ------------------------------------------------------------------------------------------------------------
        # Renaming record_id --> hmz_record_id (prospect)
        # ------------------------------------------------------------------------------------------------------------
    if "record_id" in df_hmz_ffq_prospect.columns:
             print(df_hmz_ffq_prospect["record_id"].value_counts())
             df_hmz_ffq_prospect.rename(columns={"record_id": "hmz_record_id_prospect"}, inplace=True)
             print(df_hmz_ffq_prospect["hmz_record_id_prospect"].value_counts())
             df_hmz_ffq_prospect.to_csv('data/intermediate/df_hmz_ffq_prospect.csv', index=False)


        # ------------------------------------------------------------------------------------------------------------ 
        # Keeping only studyid and 'hmz' variables
        # ------------------------------------------------------------------------------------------------------------
    df_hmz_ffq_bprhs_0 = df_hmz_ffq_bprhs_0.loc[:, df_hmz_ffq_bprhs_0.columns.str.startswith('hmz') | (df_hmz_ffq_bprhs_0.columns == 'studyid')]
    df_hmz_ffq_bprhs_2 = df_hmz_ffq_bprhs_2.loc[:, df_hmz_ffq_bprhs_2.columns.str.startswith('hmz') | (df_hmz_ffq_bprhs_2.columns == 'studyid')]
    df_hmz_ffq_bprhs_5 = df_hmz_ffq_bprhs_5.loc[:, df_hmz_ffq_bprhs_5.columns.str.startswith('hmz') | (df_hmz_ffq_bprhs_5.columns == 'studyid')]
    df_hmz_ffq_bprhs_8 = df_hmz_ffq_bprhs_8.loc[:, df_hmz_ffq_bprhs_8.columns.str.startswith('hmz') | (df_hmz_ffq_bprhs_8.columns == 'studyid')]
    df_hmz_ffq_prospect = df_hmz_ffq_prospect[[col for col in df_hmz_ffq_prospect.columns if col.startswith('hmz_') or col in ['studyid']]]
         
         # saving
    df_hmz_ffq_bprhs_0.to_csv('data/intermediate/df_hmz_ffq_bprhs_0.csv', index=False)
    df_hmz_ffq_bprhs_2.to_csv('data/intermediate/df_hmz_ffq_bprhs_2.csv', index=False)
    df_hmz_ffq_bprhs_5.to_csv('data/intermediate/df_hmz_ffq_bprhs_5.csv', index=False)
    df_hmz_ffq_bprhs_8.to_csv('data/intermediate/df_hmz_ffq_bprhs_8.csv', index=False)
    df_hmz_ffq_prospect.to_csv('data/intermediate/df_hmz_ffq_prospect.csv', index=False)



        # ------------------------------------------------------------------------------------------------------------
        # Creating PROSPECT visit-specific files
        # ------------------------------------------------------------------------------------------------------------
         # Filering not null studyids
    df_hmz_ffq_prospect = pd.read_csv("data/intermediate/df_hmz_ffq_prospect.csv")
    df_hmz_ffq_prospect = df_hmz_ffq_prospect[df_hmz_ffq_prospect["studyid"].notnull()]

         # Visit 1
    df_hmz_ffq_prospect_visit_1 = df_hmz_ffq_prospect[df_hmz_ffq_prospect["hmz_visit_prospect"] == "v1"].copy()
    df_hmz_ffq_prospect_visit_1.rename(columns={col: f"{col}_v1" for col in df_hmz_ffq_prospect_visit_1.columns if col != "studyid"}, inplace=True)
    df_hmz_ffq_prospect_visit_1.rename(columns={"hmz_visit_prospect_v1": "visit"}, inplace=True)
    df_hmz_ffq_prospect_visit_1.to_csv("data/intermediate/df_hmz_ffq_prospect_visit_1.csv", index=False)

         # Visit 2
    df_hmz_ffq_prospect_visit_2 = df_hmz_ffq_prospect[df_hmz_ffq_prospect["hmz_visit_prospect"] == "v2"].copy()
    df_hmz_ffq_prospect_visit_2.rename(columns={col: f"{col}_v2" for col in df_hmz_ffq_prospect_visit_2.columns if col != "studyid"}, inplace=True)
    df_hmz_ffq_prospect_visit_2.rename(columns={"hmz_visit_prospect_v2": "visit"}, inplace=True)
    df_hmz_ffq_prospect_visit_2.to_csv("data/intermediate/df_hmz_ffq_prospect_visit_2.csv", index=False)

        # ------------------------------------------------------------------------------------------------------------
        # Renaming hmz visit --> visit
        # ------------------------------------------------------------------------------------------------------------

    df_hmz_ffq_bprhs_0.rename(columns={'hmz_visit_bprhs_0': 'visit'}, inplace=True)
    df_hmz_ffq_bprhs_2.rename(columns={'hmz_visit_bprhs_2': 'visit'}, inplace=True)
    df_hmz_ffq_bprhs_5.rename(columns={'hmz_visit_bprhs_5': 'visit'}, inplace=True)
    df_hmz_ffq_bprhs_8.rename(columns={'hmz_visit_bprhs_8': 'visit'}, inplace=True)
    df_hmz_ffq_prospect_visit_1.rename(columns={'hmz_visit_prospect_v1': 'visit'}, inplace=True)
    df_hmz_ffq_prospect_visit_2.rename(columns={'hmz_visit_prospect_v2': 'visit'}, inplace=True)



         # Saving
    df_hmz_ffq_bprhs_0.to_csv('data/intermediate/df_hmz_ffq_bprhs_0.csv', index=False)
    df_hmz_ffq_bprhs_2.to_csv('data/intermediate/df_hmz_ffq_bprhs_2.csv', index=False)
    df_hmz_ffq_bprhs_5.to_csv('data/intermediate/df_hmz_ffq_bprhs_5.csv', index=False)
    df_hmz_ffq_bprhs_8.to_csv('data/intermediate/df_hmz_ffq_bprhs_8.csv', index=False)
    df_hmz_ffq_prospect_visit_1.to_csv("data/intermediate/df_hmz_ffq_prospect_visit_1.csv", index=False)
    df_hmz_ffq_prospect_visit_2.to_csv("data/intermediate/df_hmz_ffq_prospect_visit_2.csv", index=False)


    
    #-----------------------------------------------------------------------------------------


    #------------------------------------------------------------------------------------------------
    # loading the data: English (only PROSPECT)
    # -----------------------------------------------------------------------------------------------

    # loading the data: English (only PROSPECT)
    from harmonization_scripts. load.loader_ffq import load_ffq_english_data
    data = load_ffq_english_data(config)
    df_hmz_ffq_prospect_english = data['prospect_english']


    # Transformation: remove option six from prospect data
    # Checking the variables in prospect
    variables = ['summary18', 'summary19', 'summary20']

    for var in variables:
        if var in df_hmz_ffq_prospect_english.columns:  
            df_hmz_ffq_prospect_english[var] = df_hmz_ffq_prospect_english[var].replace(6, np.nan)
    # Saving
    df_hmz_ffq_prospect_english.to_csv('data/intermediate/df_hmz_ffq_prospect_english.csv', index=False)


    # Renaming

    # Renaming columns directly in the prospect df
    df_hmz_ffq_prospect_english.rename(columns={
    "summary17": "hmz_diet_type_prospect",
    "summary18": "hmz_meal_place_breakfast_prospect",
    "summary19": "hmz_meal_place_lunch_prospect",
    "summary20": "hmz_meal_place_dinner_prospect",
    #"summary16": "hmz_eat_out_prospect",
    "supyn": "hmz_sup_use_prospect",
    "supdur1": "hmz_sup_dur_1_prospect",
    "supdur2": "hmz_sup_dur_2_prospect",
    "supdur3": "hmz_sup_dur_3_prospect",
    "supdur4": "hmz_sup_dur_4_prospect",
    "supdur5": "hmz_sup_dur_5_prospect",
    "supdur6": "hmz_sup_dur_6_prospect",
    "supdur7": "hmz_sup_dur_7_prospect",
    "supdur8": "hmz_sup_dur_8_prospect",
    "supdur9": "hmz_sup_dur_9_prospect",
    "supdur10": "hmz_sup_dur_10_prospect",
    "supdur11": "hmz_sup_dur_11_prospect",
    "supdur12": "hmz_sup_dur_12_prospect",
    "supdur13": "hmz_sup_dur_13_prospect",
    "supdur14": "hmz_sup_dur_14_prospect",
    "supdur15": "hmz_sup_dur_15_prospect",
    "supdur16": "hmz_sup_dur_16_prospect",
    "supdur17": "hmz_sup_dur_17_prospect",
    "supdur18": "hmz_sup_dur_18_prospect"}, inplace=True)


    # Saving 
    df_hmz_ffq_prospect_english.to_csv('data/intermediate/df_hmz_ffq_prospect_english.csv', index=False)


    #------------------------------------------------------------------------------------------------
    # Post-processing Prospect English
    # -----------------------------------------------------------------------------------------------

    # --------------------------
    # Adding “ffq” prefix to every variable that starts with “hmz_”
    # --------------------------
    df_hmz_ffq_prospect_english.columns = [
        f"hmz_ffq_{c[4:]}" if c.startswith("hmz_") else c
        for c in df_hmz_ffq_prospect_english.columns]
    df_hmz_ffq_prospect_english.to_csv('data/intermediate/df_hmz_ffq_prospect_english.csv', index=False)


    # --------------------------
    #  Renaming REDCap event variable --> hmz_visit
    # --------------------------
    if "redcap_event_name" in df_hmz_ffq_prospect_english.columns:
        df_hmz_ffq_prospect_english["redcap_event_name"] = df_hmz_ffq_prospect_english["redcap_event_name"].replace({
            "event_1_arm_1": "v1"})
        df_hmz_ffq_prospect_english.rename(columns={"redcap_event_name": "hmz_visit_prospect"}, inplace=True)

    df_hmz_ffq_prospect_english.to_csv('data/intermediate/df_hmz_ffq_prospect_english.csv', index=False)

    # --------------------------
    # Renaming record_id → hmz_record_id_prospect
    # --------------------------
    if "record_id" in df_hmz_ffq_prospect_english.columns:
        df_hmz_ffq_prospect_english.rename(
            columns={"record_id": "hmz_record_id_prospect"}, inplace=True)
        
    df_hmz_ffq_prospect_english.to_csv('data/intermediate/df_hmz_ffq_prospect_english.csv', index=False)


    # --------------------------
    # Keeping only studyid and hmz variables
    # --------------------------
    df_hmz_ffq_prospect_english = df_hmz_ffq_prospect_english[[col for col in df_hmz_ffq_prospect_english.columns if col.startswith('hmz_') or col in ['studyid']]]   
    df_hmz_ffq_prospect_english.to_csv('data/intermediate/df_hmz_ffq_prospect_english.csv', index=False)



    
    # ------------------------------------------------------------------------------------------------------------
    # Creating PROSPECT visit-specific files
    # ------------------------------------------------------------------------------------------------------------

    df_hmz_ffq_prospect_english = pd.read_csv("data/intermediate/df_hmz_ffq_prospect_english.csv")
    df_hmz_ffq_prospect_english = df_hmz_ffq_prospect_english[df_hmz_ffq_prospect_english["studyid"].notnull() ]

    # --------------------------
    # Splitting into Visit-1 and Visit-2 files
    # --------------------------
    # Visit 1
    df_hmz_ffq_prospect_english_visit_1 = df_hmz_ffq_prospect_english[df_hmz_ffq_prospect_english["hmz_visit_prospect"] == "v1"].copy()
    df_hmz_ffq_prospect_english_visit_1.rename(columns={col: f"{col}_v1" for col in df_hmz_ffq_prospect_english_visit_1.columns if col != "studyid"}, inplace=True)
    df_hmz_ffq_prospect_english_visit_1.rename(columns={"hmz_visit_prospect_v1": "visit"}, inplace=True)
    df_hmz_ffq_prospect_english_visit_1.to_csv("data/intermediate/df_hmz_ffq_prospect_english_visit_1.csv", index=False)

    # Visit 2
    df_hmz_ffq_prospect_english_visit_2 = df_hmz_ffq_prospect_english[df_hmz_ffq_prospect_english["hmz_visit_prospect"] == "v2"].copy()
    df_hmz_ffq_prospect_english_visit_2.rename(columns={col: f"{col}_v2" for col in df_hmz_ffq_prospect_english_visit_2.columns if col != "studyid"}, inplace=True)
    df_hmz_ffq_prospect_english_visit_2.rename(columns={"hmz_visit_prospect_v2": "visit"}, inplace=True)
    df_hmz_ffq_prospect_english_visit_2.to_csv("data/intermediate/df_hmz_ffq_prospect_english_visit_2.csv", index=False)


    # ------------------------------------------------------------------------------------------------------------
    # Renaming hmz visit --> visit
    # ------------------------------------------------------------------------------------------------------------
   
    df_hmz_ffq_prospect_english_visit_1.rename(columns={'hmz_visit_prospect_english_v1': 'visit'}, inplace=True)
    df_hmz_ffq_prospect_english_visit_2.rename(columns={'hmz_visit_prospect_english_v2': 'visit'}, inplace=True)
   
  
   # Saving
    df_hmz_ffq_prospect_english_visit_1.to_csv("data/intermediate/df_hmz_ffq_prospect_english_visit_1.csv", index=False)
    df_hmz_ffq_prospect_english_visit_2.to_csv("data/intermediate/df_hmz_ffq_prospect_english_visit_2.csv", index=False)
    

    # ------------------------------------------------------------------------------------------------------------
    # Merging nutrients data (Tufts) into each PROSPECT visit
    # ------------------------------------------------------------------------------------------------------------


    #  Adding prefix 'hmz_ffq_' to variables starting with 'hmz_'      
    df_ffq_nutrients_prospect.columns = [
    f"hmz_ffq_{col[4:]}" if col.startswith("hmz_") else col 
    for col in df_ffq_nutrients_prospect.columns]
   
    # Saving
    df_ffq_nutrients_prospect.to_csv("data/intermediate/df_ffq_nutrients_prospect.csv", index=False)

    # Normalizing visit before filtering 
    df_ffq_nutrients_prospect["visit"] = df_ffq_nutrients_prospect["visit"].astype(str).str.lower().str.strip()    

    # Keeping only v1 and v2 visits
    df_ffq_nutrients_prospect = df_ffq_nutrients_prospect[df_ffq_nutrients_prospect["visit"].isin(["v1", "v2"])]
    
    # Saving
    df_ffq_nutrients_prospect.to_csv("data/intermediate/df_ffq_nutrients_prospect.csv", index=False)

    # Keeping only studyid, visit, and hmz_ variables
    df_ffq_nutrients_prospect = df_ffq_nutrients_prospect.loc[
        :, df_ffq_nutrients_prospect.columns.str.startswith("hmz_") |
        df_ffq_nutrients_prospect.columns.isin(["studyid", "visit"])]

    # Saving
    df_ffq_nutrients_prospect.to_csv("data/intermediate/df_ffq_nutrients_prospect.csv", index=False)

    # --------------------------------
    # Visit 1
    # --------------------------------
    df_hmz_ffq_prospect_visit_1 = pd.read_csv("data/intermediate/df_hmz_ffq_prospect_visit_1.csv")
    df_ffq_nutrients_v1 = df_ffq_nutrients_prospect[df_ffq_nutrients_prospect["visit"] == "v1"].copy()

    df_ffq_nutrients_v1 = (
        df_ffq_nutrients_v1.drop(columns="visit")
        .groupby("studyid", as_index=False)
        .sum(numeric_only=True))
    df_ffq_nutrients_v1["visit"] = "v1"

    df_ffq_nutrients_v1 = df_ffq_nutrients_v1.rename(columns={
        col: f"{col}_v1" for col in df_ffq_nutrients_v1.columns if col not in ["studyid", "visit"]
        })

    # Standardizing studyid
    df_ffq_nutrients_v1["studyid"] = df_ffq_nutrients_v1["studyid"].astype(str).str.replace(r"\.0$", "", regex=True)
    df_hmz_ffq_prospect_visit_1["studyid"] = df_hmz_ffq_prospect_visit_1["studyid"].astype(str).str.replace(r"\.0$", "", regex=True)

    # Dropping duplicates
    df_ffq_nutrients_v1 = df_ffq_nutrients_v1.drop_duplicates(subset=["studyid", "visit"])
    df_hmz_ffq_prospect_visit_1 = df_hmz_ffq_prospect_visit_1.drop_duplicates(subset=["studyid", "visit"])

    df_merged_v1 = pd.merge(
        df_hmz_ffq_prospect_visit_1,
        df_ffq_nutrients_v1,
        on=["studyid", "visit"],
        how="left")
    
    df_merged_v1.to_csv("data/intermediate/df_hmz_ffq_prospect_visit_1.csv", index=False)

# --------------------------------
# Visit 2
# --------------------------------
    df_hmz_ffq_prospect_visit_2 = pd.read_csv("data/intermediate/df_hmz_ffq_prospect_visit_2.csv")
    df_ffq_nutrients_v2 = df_ffq_nutrients_prospect[df_ffq_nutrients_prospect["visit"] == "v2"].copy()

    df_ffq_nutrients_v2 = (
        df_ffq_nutrients_v2.drop(columns="visit")
        .groupby("studyid", as_index=False)
        .sum(numeric_only=True))
    df_ffq_nutrients_v2["visit"] = "v2"

    df_ffq_nutrients_v2 = df_ffq_nutrients_v2.rename(columns={
        col: f"{col}_v2" for col in df_ffq_nutrients_v2.columns if col not in ["studyid", "visit"]})

    df_ffq_nutrients_v2["studyid"] = df_ffq_nutrients_v2["studyid"].astype(str).str.replace(r"\.0$", "", regex=True)
    df_hmz_ffq_prospect_visit_2["studyid"] = df_hmz_ffq_prospect_visit_2["studyid"].astype(str).str.replace(r"\.0$", "", regex=True)

    df_ffq_nutrients_v2 = df_ffq_nutrients_v2.drop_duplicates(subset=["studyid", "visit"])
    df_hmz_ffq_prospect_visit_2 = df_hmz_ffq_prospect_visit_2.drop_duplicates(subset=["studyid", "visit"])

    df_merged_v2 = pd.merge(
        df_hmz_ffq_prospect_visit_2,
        df_ffq_nutrients_v2,
        on=["studyid", "visit"],
        how="outer")
    
    df_merged_v2.to_csv("data/intermediate/df_hmz_ffq_prospect_visit_2.csv", index=False)

    return {
    "df_hmz_ffq_bprhs_0": df_hmz_ffq_bprhs_0,
    "df_hmz_ffq_bprhs_2": df_hmz_ffq_bprhs_2,
    "df_hmz_ffq_bprhs_5": df_hmz_ffq_bprhs_5,
    "df_hmz_ffq_bprhs_8": df_hmz_ffq_bprhs_8,
    "df_hmz_ffq_prospect_visit_1": df_merged_v1,
    "df_hmz_ffq_prospect_visit_2": df_merged_v2,
    "df_hmz_ffq_prospect_english_visit_1": df_hmz_ffq_prospect_english_visit_1,
    #"df_hmz_ffq_prospect_english_visit_2": df_hmz_ffq_prospect_english_visit_2 # no data
    }


