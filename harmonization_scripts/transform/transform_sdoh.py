

def transform_sdoh(config):

    
    import pandas as pd
    import numpy as np
   
  

    # ------------------------------------------------------------------------------------------------
    # Loading the data: spanish
    # ------------------------------------------------------------------------------------------------


    from scripts.load.loader_sdoh import load_sdoh_spanish_data

    data = load_sdoh_spanish_data(config)

    df_hmz_sdoh_bprhs_0 = data['bprhs_0']
    df_hmz_sdoh_bprhs_2 = data['bprhs_2']
    df_hmz_sdoh_bprhs_5 = data['bprhs_5']
    df_hmz_sdoh_bprhs_8 = data['bprhs_8']
    df_hmz_sdoh_prospect = data['prospect']
                            
    # ============================================================================================
    #  Gender
    # ============================================================================================

    # --------------------------------------
    # BPRHS
    # --------------------------------------
    # Renaming the variables
    for df, col, suffix in [(df_hmz_sdoh_bprhs_0, 'female', 'bprhs_0'),
                            (df_hmz_sdoh_bprhs_2, 'female', 'bprhs_2'),
                            (df_hmz_sdoh_bprhs_5, 'female', 'bprhs_5'),
                            (df_hmz_sdoh_bprhs_8, 'female_8yr', 'bprhs_8')]:
        df.rename(columns={col: f'hmz_gender_{suffix}'}, inplace=True)
        df.to_csv(f'data/intermediate/df_hmz_sdoh_{suffix}.csv', index=False)


    # --------------------------------------
    # PROSPECT
    # --------------------------------------
    # Renaming the variables
    df_hmz_sdoh_prospect.rename(columns={'dem3': 'hmz_gender_prospect'}, inplace=True)
    df_hmz_sdoh_prospect.to_csv('data/intermediate/df_hmz_sdoh_prospect.csv', index=False)
    # ============================================================================================
    #  Age
    # ============================================================================================

    # --------------------------------------
    # BPRHS
    # --------------------------------------
    # Renaming the variables
    for df, col, suffix in [(df_hmz_sdoh_bprhs_0, 'age', 'bprhs_0'),
        (df_hmz_sdoh_bprhs_2, 'age_2yr', 'bprhs_2'),
        (df_hmz_sdoh_bprhs_5, 'age_5yr', 'bprhs_5'),
        (df_hmz_sdoh_bprhs_8, 'age_8yr', 'bprhs_8'),]:
        df.rename(columns={col: f'hmz_age_{suffix}'}, inplace=True)
        df.to_csv(f'data/intermediate/df_hmz_sdoh_{suffix}.csv', index=False)

    # --------------------------------------
    # PROSPECT
    # --------------------------------------
    # Renaming and using ceil function to round up numbers
    df_hmz_sdoh_prospect.rename(columns={'age_calc': 'hmz_age_prospect'}, inplace=True)
    df_hmz_sdoh_prospect['hmz_age_prospect'] = np.ceil(df_hmz_sdoh_prospect['hmz_age_prospect'])
    df_hmz_sdoh_prospect.to_csv('data/intermediate/df_hmz_sdoh_prospect.csv', index=False)



    # -------------------------------------------------------------------------------------------------
    # Neighborhood Features and Access 
    # -------------------------------------------------------------------------------------------------

    # --------------------------------------
    # BPRHS
    # --------------------------------------
    # Transformation 1: Recoding  don't know/not sure and refused as nan ---------------------------
    base_variables = [
        "nfa8r", "nfa8s", "nfa9a", "nfa9b", "nfa9c", "nfa9d", "nfa8q", "nfa8p",
        "nfa4a", "nfa4b", "nfa4c", "nfa4d", "nfa4e", "nfa4f", "nfa4g", "nfa4h", "nfa4i", "nfa4j", "nfa4k"
    ]

    for var in base_variables:
        var_with_suffix = var + "_5yr"
        if var_with_suffix in df_hmz_sdoh_bprhs_5.columns:
            df_hmz_sdoh_bprhs_5[var_with_suffix] = df_hmz_sdoh_bprhs_5[var_with_suffix].apply(
                lambda x: int(x.strip()) if isinstance(x, str) and x.strip().isdigit() else x
            )
            df_hmz_sdoh_bprhs_5[var_with_suffix] = df_hmz_sdoh_bprhs_5[var_with_suffix].replace({97: np.nan, 98: np.nan})

    # Renaming 
    df_hmz_sdoh_bprhs_5.rename(columns={
        'nfa8r_5yr': 'hmz_nfa_violence_bprhs_5', 
        'nfa8s_5yr': 'hmz_nfa_safety_bprhs_5', 
        'nfa9a_5yr': 'hmz_nfa_weapon_bprhs_5', 
        'nfa9b_5yr': 'hmz_nfa_gang_fights_bprhs_5',
        'nfa9c_5yr': 'hmz_nfa_assault_bprhs_5',
        'nfa9d_5yr': 'hmz_nfa_rob_bprhs_5',
        'nfa8h_5yr': 'hmz_nfa_exercise_bprhs_5',    
        'nfa8q_5yr': 'hmz_nfa_safety_walk_bprhs_5',
        'nfa4a_5yr': 'hmz_nfa_fruits_vegetables_i_bprhs_5',
        'nfa4b_5yr': 'hmz_nfa_fruits_vegetables_ii_bprhs_5',
        'nfa4c_5yr': 'hmz_nfa_fruits_vegetables_iii_bprhs_5',
        'nfa4d_5yr': 'hmz_nfa_lowfat_i_bprhs_5',
        'nfa4e_5yr': 'hmz_nfa_lowfat_ii_bprhs_5',
        'nfa4f_5yr': 'hmz_nfa_lowfat_iii_bprhs_5',
        'nfa4g_5yr': 'hmz_nfa_wholegrain_i_bprhs_5',
        'nfa4h_5yr': 'hmz_nfa_wholegrain_ii_bprhs_5',
        'nfa4i_5yr': 'hmz_nfa_wholegrain_iii_bprhs_5',
        'nfa4j_5yr': 'hmz_nfa_fish_bprhs_5',
        'nfa4k_5yr': 'hmz_nfa_fastfood_bprhs_5'
    }, inplace=True)

    # Saving
    df_hmz_sdoh_bprhs_5.to_csv('data/intermediate/df_hmz_sdoh_bprhs_5.csv', index=False)


    # Transformation 2: options 1,2,3,4, are recoded as 3,2,1,0 -------------------------------------
    variables_to_recode = [  
        'hmz_nfa_weapon_bprhs_5', 
        'hmz_nfa_gang_fights_bprhs_5', 
        'hmz_nfa_assault_bprhs_5', 
        'hmz_nfa_rob_bprhs_5']

    # recoding dictionary
    recode_map = {1: 3, 2: 2, 3: 1, 4: 0}


    for var in variables_to_recode:
        if var in df_hmz_sdoh_bprhs_5.columns:
            df_hmz_sdoh_bprhs_5[var] = df_hmz_sdoh_bprhs_5[var].replace(recode_map)


    # Saving
    df_hmz_sdoh_bprhs_5.to_csv('data/intermediate/df_hmz_sdoh_bprhs_5.csv', index=False)



    # Transformation 3:  options 1,2,4, 5 are recoded as 5, 4,2, 1 ---------------------------------

    # recoding dictionary
    recode_map_2 = {1: 5, 2: 4, 4: 2, 5: 1}

    df_hmz_sdoh_bprhs_5['hmz_nfa_violence_bprhs_5'] = df_hmz_sdoh_bprhs_5['hmz_nfa_violence_bprhs_5'].replace(recode_map_2)

    # Saving
    df_hmz_sdoh_bprhs_5.to_csv('data/intermediate/df_hmz_sdoh_bprhs_5.csv', index=False)


    # Transformation 4: Recoding  don't know/not sure and refused as nan -----------------------------
    base_variables = ["nfa7h", "nfa8l", "nfa8m", "nfa8n", "nfa8o", "nfa8i", "nfa8k"]

    # Cleaning function for inconsistent formats
    def clean_value(value):
        if isinstance(value, str):
            return value.strip()
        return value

    # Cleaning function 
    for col in df_hmz_sdoh_bprhs_5.columns:
        if col.startswith("nfa"):  
            df_hmz_sdoh_bprhs_5[col] = df_hmz_sdoh_bprhs_5[col].apply(clean_value)

    # Recoding 
    for var in base_variables:
        var_with_suffix = var + "_5yr"
        if var_with_suffix in df_hmz_sdoh_bprhs_5.columns:
            # Converting to numeric
            df_hmz_sdoh_bprhs_5[var_with_suffix] = pd.to_numeric(df_hmz_sdoh_bprhs_5[var_with_suffix], errors='coerce')
            # Recoding 97 and 98 to NaN
            df_hmz_sdoh_bprhs_5[var_with_suffix] = df_hmz_sdoh_bprhs_5[var_with_suffix].replace({97: np.nan, 98: np.nan})


    # Renaming 
    df_hmz_sdoh_bprhs_5.rename(columns={
        'nfa7h_5yr': 'hmz_nfa_sidewalks_bprhs_5', 
        'nfa8l_5yr': 'hmz_nfa_roads_bprhs_5', 
        'nfa8m_5yr': 'hmz_nfa_walk_bprhs_5', 
        'nfa8n_5yr': 'hmz_nfa_stores_bprhs_5',
        'nfa8o_5yr': 'hmz_nfa_people_walk_bprhs_5',
        'nfa8i_5yr': 'hmz_nfa_pleasant_walk_bprhs_5',
        'nfa8k_5yr': 'hmz_nfa_traffic_bprhs_5'}, inplace=True)


    # Saving 
    df_hmz_sdoh_bprhs_5.to_csv('data/intermediate/df_hmz_sdoh_bprhs_5.csv', index=False)



    # Transformation 5: Removing option "Don't know" and recoding other options 
    # nfa1
    if 'nfa1_5yr' in df_hmz_sdoh_bprhs_5.columns:
        # Recoding values
        df_hmz_sdoh_bprhs_5['nfa1_5yr'] = df_hmz_sdoh_bprhs_5['nfa1_5yr'].replace({
            "Half mile or less (1 mile is about 12 block or a 20 minute walk)": 1,
            "More than half mile but less than 1 mile": 2,
            "More than 1 mile but less than 5 miles": 3,
            "5-10 miles": 4,
            "More than 10 miles": 5,
            "Don't know": None})

        # Renaming the column
        df_hmz_sdoh_bprhs_5.rename(columns={'nfa1_5yr': 'hmz_nfa_shopping_distance_bprhs_5'}, inplace=True)

    # Saving 
    df_hmz_sdoh_bprhs_5.to_csv('data/intermediate/df_hmz_sdoh_bprhs_5.csv', index=False)

    #nfa2
    if 'nfa2_5yr' in df_hmz_sdoh_bprhs_5.columns:
        # Recoding values
        df_hmz_sdoh_bprhs_5['nfa2_5yr'] = df_hmz_sdoh_bprhs_5['nfa2_5yr'].replace({
            "All or almost all of it": 4,
            "Most of it": 3,
            "About half of it": 2,
            "Some of it": 1,
            "None or almost none of it": 0,
            "Don't know": None
        })

        # Renaming
        df_hmz_sdoh_bprhs_5.rename(columns={'nfa2_5yr': 'hmz_nfa_shopping_food_bprhs_5'}, inplace=True)


    # Saving 
    df_hmz_sdoh_bprhs_5.to_csv('data/intermediate/df_hmz_sdoh_bprhs_5.csv', index=False)



    # --------------------------------------
    # PROSPECT
    # --------------------------------------
    # Transformation 1: options  refused to answer, do not remember, and  do not know are recoded as nan-----------------
    variables_to_recode = [
        "nss33", "nss34", "nss40", "nss41", "nss42", "nss43", "nss32",
        "nss56", "nss14", "nss15", "nss16", "nss17", "nss11", "nss1", "nss2", "nss13",
        "nss19", "nss20", "nss21", "nss22", "nss23", "nss24", "nss25", "nss26", "nss27", "nss28", "nss31"
    ]

    rename_map = {
        "nss33": "hmz_nfa_violence_prospect",
        "nss34": "hmz_nfa_safety_prospect",
        "nss40": "hmz_nfa_weapon_prospect",
        "nss41": "hmz_nfa_gang_fights_prospect",
        "nss42": "hmz_nfa_assault_prospect",
        "nss43": "hmz_nfa_rob_prospect",
        "nss32": "hmz_nfa_safety_walk_prospect",
        "nss56": "hmz_nfa_sidewalks_prospect",
        "nss14": "hmz_nfa_roads_prospect",
        "nss15": "hmz_nfa_walk_prospect",
        "nss16": "hmz_nfa_stores_prospect",
        "nss17": "hmz_nfa_people_walk_prospect",
        "nss11": "hmz_nfa_pleasant_walk_prospect",
        "nss1":  "hmz_nfa_shopping_distance_prospect",
        "nss2":  "hmz_nfa_shopping_food_prospect",
        "nss13": "hmz_nfa_traffic_prospect",
        "nss19": "hmz_nfa_fruits_vegetables_i_prospect",
        "nss20": "hmz_nfa_fruits_vegetables_ii_prospect",
        "nss21": "hmz_nfa_fruits_vegetables_iii_prospect",
        "nss22": "hmz_nfa_lowfat_i_prospect",
        "nss23": "hmz_nfa_lowfat_ii_prospect",
        "nss24": "hmz_nfa_lowfat_iii_prospect",
        "nss25": "hmz_nfa_wholegrain_i_prospect",
        "nss26": "hmz_nfa_wholegrain_ii_prospect",
        "nss27": "hmz_nfa_wholegrain_iii_prospect",
        "nss28": "hmz_nfa_fish_prospect",
        "nss31": "hmz_nfa_fastfood_prospect"
    }

    # Recoding and transforming
    for var in variables_to_recode:
        if var in df_hmz_sdoh_prospect.columns:
            df_hmz_sdoh_prospect[var] = pd.to_numeric(df_hmz_sdoh_prospect[var], errors='coerce')
            df_hmz_sdoh_prospect[var] = df_hmz_sdoh_prospect[var].replace({96: np.nan, 97: np.nan, 98: np.nan})

    # Renaming
    df_hmz_sdoh_prospect.rename(columns=rename_map, inplace=True)

    # Saving
    df_hmz_sdoh_prospect.to_csv('data/intermediate/df_hmz_sdoh_prospect.csv', index=False)



    #------------------------------------------------------------------------------------------------
    # Household Composition
    # -----------------------------------------------------------------------------------------------

    # --------------------------------------
    # BPRHS
    # --------------------------------------

    # Checking variables
    base_variables = ["hc1", "hc1b", "hc1c", "hc8"]
    suffixes = {
        "bprhs_0": (df_hmz_sdoh_bprhs_0, ""),
        "bprhs_2": (df_hmz_sdoh_bprhs_2, "_2yr"),
        "bprhs_5": (df_hmz_sdoh_bprhs_5, "_5yr"),
        "bprhs_8": (df_hmz_sdoh_bprhs_8, "_8yr")
    }

    # Recoding value 2 → NaN for 'hc8'
    for _, (df, suffix) in suffixes.items():
        colname = f"hc8{suffix}"
        if colname in df.columns:
            df[colname] = df[colname].replace({2: np.nan})

    # Renaming variables
    for key, (df, suffix) in suffixes.items():
        rename_map = {
            f"hc1{suffix}": f"hmz_hc_{key}",
            f"hc1b{suffix}": f"hmz_hc_0_5_{key}",
            f"hc1c{suffix}": f"hmz_hc_6_12_{key}",
            f"hc8{suffix}": f"hmz_hc_marital_{key}"
        }
        df.rename(columns=rename_map, inplace=True)
        df.to_csv(f"data/intermediate/df_hmz_sdoh_{key}.csv", index=False)

    # Saving
    df_hmz_sdoh_bprhs_8.to_csv('data/intermediate/df_hmz_sdoh_bprhs_8.csv', index=False)





    # --------------------------------------
    # PROSPECT
    # --------------------------------------

    # Variables to recode
    variables_to_recode = ["hem1", "hem2a", "hem2b", "hem4"]

    # Recoding specific values in 'hem4'
    df_hmz_sdoh_prospect["hem4"] = df_hmz_sdoh_prospect["hem4"].replace({
        96: np.nan, 2: 1, 4: 3, 5: 4, 6: 5
    })

    # Renaming variables
    df_hmz_sdoh_prospect.rename(columns={
        "hem1": "hmz_hc_prospect",
        "hem2a": "hmz_hc_0_5_prospect",
        "hem2b": "hmz_hc_6_12_prospect",
        "hem4": "hmz_hc_marital_prospect"
    }, inplace=True)

    # Saving
    df_hmz_sdoh_prospect.to_csv('data/intermediate/df_hmz_sdoh_prospect.csv', index=False)



    #------------------------------------------------------------------------------------------------
    # Education
    # -----------------------------------------------------------------------------------------------


    # --------------------------------------
    # BPRHS
    # --------------------------------------

    # Renaming the variable
    for df, suffix in [
        (df_hmz_sdoh_bprhs_0, "bprhs_0"),
        (df_hmz_sdoh_bprhs_2, "bprhs_2"),
        (df_hmz_sdoh_bprhs_5, "bprhs_5")]:
        df.rename(columns={"educ3": f"hmz_hc_educ_{suffix}"}, inplace=True)
        df.to_csv(f'data/intermediate/df_hmz_sdoh_{suffix}.csv', index=False)


    # --------------------------------------
    # PROSPECT
    # --------------------------------------

    df_hmz_sdoh_prospect["hem3"] = df_hmz_sdoh_prospect["hem3"].replace({
        96: np.nan, 97: np.nan, 98: np.nan,
        1: 1, 2: 1,
        3: 2, 4: 2,
        5: 3, 6: 3, 7: 3, 8: 3, 9: 3,
        10: 4, 11: 4, 12: 4, 13: 4,
        14: 5, 15: 5, 16: 5})

    # Renaming
    df_hmz_sdoh_prospect.rename(columns={'hem3': 'hmz_hc_educ_prospect'}, inplace=True)

    # Saving
    df_hmz_sdoh_prospect.to_csv('data/intermediate/df_hmz_sdoh_prospect.csv', index=False)





    #----------------------------------------------------------------------------------------------
    # Work History and Income
    # ---------------------------------------------------------------------------------------------


    # --------------------------------------
    # BPRHS
    # --------------------------------------

    # Recoding 96, 97, 98 to NaN and renaming for 'wh6ac' and 'wh6ac_2yr'
    df_hmz_sdoh_bprhs_0['wh6ac'] = df_hmz_sdoh_bprhs_0['wh6ac'].replace({96: np.nan, 97: np.nan, 98: np.nan})
    df_hmz_sdoh_bprhs_2['wh6ac_2yr'] = df_hmz_sdoh_bprhs_2['wh6ac_2yr'].replace({96: np.nan, 97: np.nan, 98: np.nan})

    # Renaming 
    df_hmz_sdoh_bprhs_0.rename(columns={'wh6ac': 'hmz_whi_occupation_bprhs_0'}, inplace=True)
    df_hmz_sdoh_bprhs_2.rename(columns={'wh6ac_2yr': 'hmz_whi_occupation_bprhs_2'}, inplace=True)

    # Saving 
    df_hmz_sdoh_bprhs_0.to_csv('data/intermediate/df_hmz_sdoh_bprhs_0.csv', index=False)
    df_hmz_sdoh_bprhs_2.to_csv('data/intermediate/df_hmz_sdoh_bprhs_2.csv', index=False)


    # --------------------------------------
    # PROSPECT
    # --------------------------------------


    occupations = {
        1: ["Administrador", "Administradora", "Gerente", "Director", "Directora", "Coordinador", "Coordinadora",
            "Secretaria", "Asistente administrativo", "Analista de presupuesto"],
        2: ["Funcionario ejecutivo", "Policia", "Sargento", "Inspectora de contribuciones", "Oficial administrativo",
            "Catedratico", "Profesor universitario", "Educador en salud", "Abogada", "Abogado"],
        3: ["Enfermera", "Médico", "Farmaceutica", "Doctor", "Tecnologa Medica", "Terapista fisica", "Terapista Respiratoria",
            "Psicologa", "Trabajadora social", "Consejera", "Nutricionista", "Paramédico", "Tecnica oftalmica"],
        4: ["Maestro", "Maestra", "Profesor", "Profesora", "Tutor", "Tutora", "Asistente de maestra", "Educador",
            "Facilitadora Docente", "Trabajadora Social Escolar"],
        5: ["Técnico automotriz", "Técnico de refrigeración", "Electricista", "Tecnico de permisos", "Tecnólogo Médico",
            "Técnica de biblioteca", "Técnico el reparación"],
        6: ["Vendedor", "Ventas", "Cajera", "Call Center", "Servicio al cliente", "Consultora", "Representante de ventas",
            "Agente de Seguros", "Tienda comercial", "Mercadeo"],
        7: ["Empleada doméstica", "Ama de llaves", "Housekeeping", "Cuidadora de envejecientes", "Cuida ancianos",
            "Niñera", "Cuidadora"],
        8: [],  # Armed Services 
        9: ["Agricultura", "Agronomo", "Farming", "Forestry"],
        10: ["Handyman", "Mantenimiento", "Carpinteria", "Plomero", "Pintor", "Mecanico", "Contratista"],
        11: ["Operador de equipo pesado", "Operador de manufactura", "Operador Multitrabajo", "Encargado de almacén"],
        12: ["Chofer", "Transporte", "Uber", "Delivery", "Conductor"],
        13: ["Limpieza", "Recolección de basura", "Trabajador general", "Auxiliar", "Mantenimiento de hogares"],
        14: ["Artesana", "Artista", "Barbero", "Estilista", "Cocinero", "Reposteria", "Chef", "Dueño de negocio"]
    }



    # Function to categorize occupation
    def categorize_occupation(text):
        if pd.isna(text) or text.strip() == "":
            return np.nan  
        text = text.lower()
        for category, keywords in occupations.items():  # Using 'occupations' dictionary
            if any(keyword.lower() in text for keyword in keywords):
                return category
        return np.nan  

    # Function to transform the dataset
    def transform_occupation(df, suffix):
        col_name = f"whi7"  
        df[f"hmz_whi_occupation_{suffix}"] = df[col_name].apply(categorize_occupation)  

    # Applying transformation to df_hmz_sdoh_prospect
    transform_occupation(df_hmz_sdoh_prospect, "prospect")

    # Saving the transformed DataFrame
    df_hmz_sdoh_prospect.to_csv('data/intermediate/df_hmz_sdoh_prospect.csv', index=False)




    #------------------------------------------------------------------------------------------------
    # Social and Community Support & Assistance
    # -----------------------------------------------------------------------------------------------


    # --------------------------------------
    # BPRHS
    # --------------------------------------
    # Transformation 1: Cleaning some variables
    # soc2a_5yr 
    df_hmz_sdoh_bprhs_5['soc2a_5yr'] = df_hmz_sdoh_bprhs_5['soc2a_5yr'].replace([-98, -99, 'No sabe'], np.nan)

    # soc2a_8yr 
    df_hmz_sdoh_bprhs_8['soc2a_8yr'] = df_hmz_sdoh_bprhs_8['soc2a_8yr'].replace([-98, -99, '1:30', '1:15'], np.nan)

    # soc2b_5yr
    cleanup_map = {
        'Minutos': 1,
        'Minutes': 1,
        'Horas': 2,
        'Hours': 2,
        'Dias': 3}


    df_hmz_sdoh_bprhs_5['soc2b_5yr'] = df_hmz_sdoh_bprhs_5['soc2b_5yr'].replace(cleanup_map)



    # soc3b
    soc3b_5yr_map = {
        'Less than once a year/never': 1,
        'Menos de una vez al ano': 1,
        'Yearly': 2,
        'Al ano': 2,
        'Monthly': 3,
        'Al mes': 3,
        'Weekly': 4,
        'A la semana': 4,
        'Daily': 5,
        'Al dia': 5}

    df_hmz_sdoh_bprhs_5['soc3b_5yr'] = df_hmz_sdoh_bprhs_5['soc3b_5yr'].replace(soc3b_5yr_map)


    # soc4b_5yr 
    soc4b_5yr_map = {
        'Less than once a year/never': 1,  # In case this label appears
        'Menos de una vez al ano': 1,
        'Yearly': 2,
        'Al ano': 2,
        'Monthly': 3,
        'Al mes': 3,
        'Weekly': 4,
        'A la semana': 4,
        'Daily': 5,
        'Al dia': 5}


    df_hmz_sdoh_bprhs_5['soc4b_5yr'] = df_hmz_sdoh_bprhs_5['soc4b_5yr'].replace(soc4b_5yr_map)

    df_hmz_sdoh_bprhs_5.to_csv('data/intermediate/df_hmz_sdoh_bprhs_5.csv', index=False)



    #  soc5b_5yr
    soc5b_5yr_map = {
        'Less than once a year/never': 1,
        'Menos de una vez al ano': 1,
        'Yearly': 2,
        'Al ano': 2,
        'Monthly': 3,
        'Al mes': 3,
        'Weekly': 4,
        'A la semana': 4,
        'Daily': 5,
        'Al dia': 5}


    df_hmz_sdoh_bprhs_5['soc5b_5yr'] = df_hmz_sdoh_bprhs_5['soc5b_5yr'].replace(soc5b_5yr_map)


    # soc29_5yr
    soc29_5yr_map = {
        'About enough': 1,
        'Suficiente': 1,
        'Too much': 2,
        'Demasiadas': 2,
        'Would like to do more': 3,
        'Gustaria envolvere en mas': 3}


    df_hmz_sdoh_bprhs_5['soc29_5yr'] = df_hmz_sdoh_bprhs_5['soc29_5yr'].replace(soc29_5yr_map)



    # saving
    df_hmz_sdoh_bprhs_5.to_csv('data/intermediate/df_hmz_sdoh_bprhs_5.csv', index=False)
    df_hmz_sdoh_bprhs_8.to_csv('data/intermediate/df_hmz_sdoh_bprhs_8.csv', index=False)




    # Transformation 2: Recoding

    variables_to_transform = ['soc3b', 'soc4b', 'soc5b']

    transformation_map = {1: 5, 2: 4, 4: 2, 9: 1}


    for var in variables_to_transform:
        df_hmz_sdoh_bprhs_0[var] = df_hmz_sdoh_bprhs_0[var].replace(transformation_map)
        # Check value counts after transformation
        print(f"\nValue counts after transformation for {var}:")
        print(df_hmz_sdoh_bprhs_0[var].value_counts(dropna=False))


    # renaming
    df_hmz_sdoh_bprhs_0.rename(columns={
        'soc1': 'hmz_soc1_bprhs_0',
        'soc2a': 'hmz_soc2a_bprhs_0',
        'soc2b': 'hmz_soc2b_bprhs_0',
        'soc3a': 'hmz_soc3a_bprhs_0',
        'soc3b': 'hmz_soc3b_bprhs_0',
        'soc4a': 'hmz_soc4a_bprhs_0',
        'soc4b': 'hmz_soc4b_bprhs_0',
        'soc5a': 'hmz_soc5a_bprhs_0',
        'soc5b': 'hmz_soc5b_bprhs_0',
        'soc6': 'hmz_soc6_bprhs_0',
        'soc29': 'hmz_soc_activities_feel_bprhs_0'
    }, inplace=True)

    df_hmz_sdoh_bprhs_2.rename(columns={
        'soc1_2yr': 'hmz_soc1_bprhs_2',
        'soc2a_2yr': 'hmz_soc2a_bprhs_2',
        'soc2b_2yr': 'hmz_soc2b_bprhs_2',
        'soc3a_2yr': 'hmz_soc3a_bprhs_2',
        'soc3b_2yr': 'hmz_soc3b_bprhs_2',
        'soc4a_2yr': 'hmz_soc4a_bprhs_2',
        'soc4b_2yr': 'hmz_soc4b_bprhs_2',
        'soc5a_2yr': 'hmz_soc5a_bprhs_2',
        'soc5b_2yr': 'hmz_soc5b_bprhs_2',
        'soc6_2yr': 'hmz_soc6_bprhs_2',
        'soc29_2yr': 'hmz_soc_activities_feel_bprhs_2'
    }, inplace=True)


    df_hmz_sdoh_bprhs_5.rename(columns={
        'soc1_5yr': 'hmz_soc1_bprhs_5',
        'soc2a_5yr': 'hmz_soc2a_bprhs_5',
        'soc2b_5yr': 'hmz_soc2b_bprhs_5',
        'soc3a_5yr': 'hmz_soc3a_bprhs_5',
        'soc3b_5yr': 'hmz_soc3b_bprhs_5',
        'soc4a_5yr': 'hmz_soc4a_bprhs_5',
        'soc4b_5yr': 'hmz_soc4b_bprhs_5',
        'soc5a_5yr': 'hmz_soc5a_bprhs_5',
        'soc5b_5yr': 'hmz_soc5b_bprhs_5',
        'soc6_5yr': 'hmz_soc6_bprhs_5',
        'soc29_5yr': 'hmz_soc_activities_feel_bprhs_5'
    }, inplace=True)

    df_hmz_sdoh_bprhs_8.rename(columns={
        'soc1_8yr': 'hmz_soc1_bprhs_8',
        'soc2a_8yr': 'hmz_soc2a_bprhs_8',
        'soc2b_8yr': 'hmz_soc2b_bprhs_8',
        'soc3a_8yr': 'hmz_soc3a_bprhs_8',
        'soc3b_8yr': 'hmz_soc3b_bprhs_8',
        'soc4a_8yr': 'hmz_soc4a_bprhs_8',
        'soc4b_8yr': 'hmz_soc4b_bprhs_8',
        'soc5a_8yr': 'hmz_soc5a_bprhs_8',
        'soc5b_8yr': 'hmz_soc5b_bprhs_8',
        'soc6_8yr': 'hmz_soc6_bprhs_8',
        'soc29_8yr': 'hmz_soc_activities_feel_bprhs_8'
    }, inplace=True)



    # Saving
    df_hmz_sdoh_bprhs_0.to_csv('data/intermediate/df_hmz_sdoh_bprhs_0.csv', index=False)
    df_hmz_sdoh_bprhs_2.to_csv("data/intermediate/df_hmz_sdoh_bprhs_0.csv", index=False)
    df_hmz_sdoh_bprhs_5.to_csv("data/intermediate/df_hmz_sdoh_bprhs_0.csv", index=False)
    df_hmz_sdoh_bprhs_8.to_csv("data/intermediate/df_hmz_sdoh_bprhs_0.csv", index=False)



    # Transformation 3: Creating variable soc activities
    # this variable corresponds to the sum of several variables (soc16-soc28)
    # renaming the variable in bprhs v1
    df_hmz_sdoh_bprhs_0.rename(columns={'soc_activities': 'hmz_soc_activities_bprhs_0'}, inplace=True)
            
    # variables to sum for creating soc_activities for bprhs v3 and v4
    variables_to_sum = ["soc16", "soc17","soc172_962" , "soc18", "soc20", "soc21",
        "soc22", "soc23", "soc24", "soc25", "soc26", "soc27", "soc28"]


    # bprhs v3
    variables_to_recode_5 = [   "soc16_5yr", "soc17_5yr", "soc172_962_5yr", "soc18_5yr", "soc20_5yr", "soc21_5yr",
        "soc22_5yr", "soc23_5yr", "soc24_5yr", "soc25_5yr", "soc26_5yr", "soc27_5yr", "soc28_5yr"]

    for var in variables_to_recode_5:
        if var in df_hmz_sdoh_bprhs_5.columns:
            df_hmz_sdoh_bprhs_5[var] = pd.to_numeric(df_hmz_sdoh_bprhs_5[var], errors='coerce')
            df_hmz_sdoh_bprhs_5[var] = df_hmz_sdoh_bprhs_5[var].replace({-96: np.nan, 96: np.nan, 97: np.nan, 98: np.nan})


    # recoding as numeric
    # convert columns to numeric, forcing errors='coerce' to replace non-numeric values with NaN
    df_hmz_sdoh_bprhs_5[variables_to_recode_5] = df_hmz_sdoh_bprhs_5[variables_to_recode_5].apply(pd.to_numeric, errors='coerce')
    print(df_hmz_sdoh_bprhs_5[variables_to_recode_5].dtypes)

    # creating a new variable
    # Lambda function that filters non-NaN and non-zero values, assigning NaN if the entire row is NaN
    df_hmz_sdoh_bprhs_5["hmz_soc_activities_bprhs_5"] = (
        df_hmz_sdoh_bprhs_5[variables_to_recode_5]
        .apply(lambda row: np.nan if row.isna().all() else row[(row.notna()) & (row != 0)].count(), axis=1)
    )

    # Saving
    df_hmz_sdoh_bprhs_5.to_csv('data/intermediate/df_hmz_sdoh_bprhs_5.csv', index=False)

    # bprhs v4
    variables_to_recode_8 = [    "soc16_8yr", "soc17_8yr", "soc172_962_8yr", "soc18_8yr", "soc20_8yr", "soc21_8yr",
        "soc22_8yr", "soc23_8yr", "soc24_8yr", "soc25_8yr", "soc26_8yr", "soc27_8yr", "soc28_8yr"]
    for var in variables_to_recode_8:
        if var in df_hmz_sdoh_bprhs_8.columns:
            df_hmz_sdoh_bprhs_8[var] = pd.to_numeric(df_hmz_sdoh_bprhs_8[var], errors='coerce')
            df_hmz_sdoh_bprhs_8[var] = df_hmz_sdoh_bprhs_8[var].replace({96: np.nan, 97: np.nan, 98: np.nan})




    # recoding as numeric
    # convert columns to numeric, forcing errors='coerce' to replace non-numeric values with NaN
    df_hmz_sdoh_bprhs_8[variables_to_recode_8] = df_hmz_sdoh_bprhs_8[variables_to_recode_8].apply(pd.to_numeric, errors='coerce')
    print(df_hmz_sdoh_bprhs_8[variables_to_recode_8].dtypes)

    # creating a new variable
    # Lambda function that filters non-NaN and non-zero values, assigning NaN if the entire row is NaN
    df_hmz_sdoh_bprhs_8["hmz_soc_activities_bprhs_8"] = (
        df_hmz_sdoh_bprhs_8[variables_to_recode_8]
        .apply(lambda row: np.nan if row.isna().all() else row[(row.notna()) & (row != 0)].count(), axis=1)
    )


    # Saving
    df_hmz_sdoh_bprhs_8.to_csv('data/intermediate/df_hmz_sdoh_bprhs_8.csv', index=False)






    # Renaming columns for social activities (soc16 to soc28) in bprhs v1, v3 and v4
    df_hmz_sdoh_bprhs_0.rename(columns={
        'soc16': 'hmz_soc_get_together_i_bprhs_0',
        'soc17': 'hmz_soc_volunteer_bprhs_0',
        'soc18': 'hmz_soc_phone_i_bprhs_0',
        'soc19': 'hmz_soc_get_together_ii_bprhs_0',
        'soc20': 'hmz_soc_phone_ii_bprhs_0',
        'soc21': 'hmz_soc_church_bprhs_0',
        'soc22': 'hmz_soc_event_bprhs_0',
        'soc23': 'hmz_soc_sports_bprhs_0',
        'soc24': 'hmz_soc_read_bprhs_0',
        'soc25': 'hmz_soc_hobbies_bprhs_0',
        'soc26': 'hmz_soc_repairs_bprhs_0',
        'soc27': 'hmz_soc_care_relative_bprhs_0',
        'soc28': 'hmz_soc_help_bprhs_0'
    }, inplace=True)


    df_hmz_sdoh_bprhs_5.rename(columns={
        'soc16_5yr': 'hmz_soc_get_together_i_bprhs_5',
        'soc17_5yr': 'hmz_soc_volunteer_bprhs_5',
        'soc172_962_5yr': 'hmz_soc_phone_i_bprhs_5',
        'soc18_5yr': 'hmz_soc_get_together_ii_bprhs_5', 
        'soc20_5yr': 'hmz_soc_phone_ii_bprhs_5',
        'soc21_5yr': 'hmz_soc_church_bprhs_5',
        'soc22_5yr': 'hmz_soc_event_bprhs_5',
        'soc23_5yr': 'hmz_soc_sports_bprhs_5',
        'soc24_5yr': 'hmz_soc_read_bprhs_5',
        'soc25_5yr': 'hmz_soc_hobbies_bprhs_5',
        'soc26_5yr': 'hmz_soc_repairs_bprhs_5',
        'soc27_5yr': 'hmz_soc_care_relative_bprhs_5',
        'soc28_5yr': 'hmz_soc_help_bprhs_5'
    }, inplace=True)

    df_hmz_sdoh_bprhs_8.rename(columns={
        'soc16_8yr': 'hmz_soc_get_together_i_bprhs_8',
        'soc17_8yr': 'hmz_soc_volunteer_bprhs_8',
        'soc172_962_8yr': 'hmz_soc_phone_i_bprhs_8',
       'soc18_8yr': 'hmz_soc_get_together_ii_bprhs_8', 
        'soc20_8yr': 'hmz_soc_phone_ii_bprhs_8',
        'soc21_8yr': 'hmz_soc_church_bprhs_8',
        'soc22_8yr': 'hmz_soc_event_bprhs_8',
        'soc23_8yr': 'hmz_soc_sports_bprhs_8',
        'soc24_8yr': 'hmz_soc_read_bprhs_8',
        'soc25_8yr': 'hmz_soc_hobbies_bprhs_8',
        'soc26_8yr': 'hmz_soc_repairs_bprhs_8',
        'soc27_8yr': 'hmz_soc_care_relative_bprhs_8',
        'soc28_8yr': 'hmz_soc_help_bprhs_8'
    }, inplace=True)

    # Saving 
    df_hmz_sdoh_bprhs_0.to_csv('data/intermediate/df_hmz_sdoh_bprhs_0.csv', index=False)
    df_hmz_sdoh_bprhs_2.to_csv('data/intermediate/df_hmz_sdoh_bprhs_2.csv', index=False)
    df_hmz_sdoh_bprhs_5.to_csv('data/intermediate/df_hmz_sdoh_bprhs_5.csv', index=False)
    df_hmz_sdoh_bprhs_8.to_csv('data/intermediate/df_hmz_sdoh_bprhs_8.csv', index=False)



    # Transformation 4: Creating new variable
    # **hmz_soc_support_i**: number of people who provide personal support for the subjec or persons who are important to the subject
    # hmz_soc_support_i_bprhs: count the number of people provided in the social support variables pn1a-pn16a  bprhs (10 people)
    base_variables = ["pn1a","pn2a","pn3a","pn4a","pn5a","pn6a","pn7a","pn8a","pn9a","pn10a","pn11a","pn12a","pn13a","pn14a","pn15a","pn16a"]

        

    # Creating new variable
    # bprhs v1
    df_hmz_sdoh_bprhs_0.columns = df_hmz_sdoh_bprhs_0.columns.str.lower().str.strip()
    valid_columns_0 = [var for var in base_variables if var in df_hmz_sdoh_bprhs_0.columns]
    if valid_columns_0:
        df_hmz_sdoh_bprhs_0["hmz_soc_support_i_bprhs_0"] = df_hmz_sdoh_bprhs_0[valid_columns_0].apply(
            lambda row: np.nan if row.isna().all() else row.notna().sum(), axis=1
        )
        print("Created `hmz_soc_support_i_bprhs_0` in Baseline")

    # bprhs v2
    df_hmz_sdoh_bprhs_2.columns = df_hmz_sdoh_bprhs_2.columns.str.lower().str.strip()
    valid_columns_2 = [var + "_2yr" for var in base_variables if (var + "_2yr") in df_hmz_sdoh_bprhs_2.columns]
    if valid_columns_2:
        df_hmz_sdoh_bprhs_2["hmz_soc_support_i_bprhs_2"] = df_hmz_sdoh_bprhs_2[valid_columns_2].apply(
            lambda row: np.nan if row.isna().all() else row.notna().sum(), axis=1
        )
        print("Created `hmz_soc_support_i_bprhs_2` in 2-Year")

    # bprhs v4
    df_hmz_sdoh_bprhs_8.columns = df_hmz_sdoh_bprhs_8.columns.str.lower().str.strip()
    valid_columns_8 = [var + "_8yr" for var in base_variables if (var + "_8yr") in df_hmz_sdoh_bprhs_8.columns]
    if valid_columns_8:
        df_hmz_sdoh_bprhs_8["hmz_soc_support_i_bprhs_8"] = df_hmz_sdoh_bprhs_8[valid_columns_8].apply(
            lambda row: np.nan if row.isna().all() else row.notna().sum(), axis=1
        )
        print("Created `hmz_soc_support_i_bprhs_8` in 8-Year")


    # Saving 
    df_hmz_sdoh_bprhs_0.to_csv('data/intermediate/df_hmz_sdoh_bprhs_0.csv', index=False)
    df_hmz_sdoh_bprhs_2.to_csv('data/intermediate/df_hmz_sdoh_bprhs_2.csv', index=False)
    df_hmz_sdoh_bprhs_8.to_csv('data/intermediate/df_hmz_sdoh_bprhs_8.csv', index=False)





    # Transformation 5 
    # hmz_soc_support_ii
    # Assigning categories from prospect to bprhs relationship with person that provides support (n=10) 

    base_variables = ["pn1b", "pn2b", "pn3b", "pn4b", "pn5b", "pn6b", "pn7b", "pn8b", "pn9b", "pn10b"]


    bprhs_datasets = {
        "Baseline": (df_hmz_sdoh_bprhs_0, ""),
        "2-Year": (df_hmz_sdoh_bprhs_2, "_2yr"),
        "8-Year": (df_hmz_sdoh_bprhs_8, "_8yr")
    }


    for _, (df, _) in bprhs_datasets.items():
        df.columns = df.columns.str.lower().str.strip()

    # Mapping of text values to standardized codes
    mapping = {
        "wife": "1", "wife/girlfriend/partner": "1", "boyfriend": "1", "girlfriend": "1", "esposa": "1", "esposo": "1", "ex-esposo": "1",
        "yerna": "2", "yerno": "2", "ahijado": "2", "amadre": "2", "aunt": "2", "aunt of her grandson": "2", "visnieta": "2",
        "brother": "2", "brother in law": "2", "ahijada": "2", "bisnieto": "2", "tia": "2", "cunada": "2", "cunado ": "2",
        "daughter": "2", "daughter's mother in law": "2", "granddaughter": "2", "grandson": "2", "hermana": "2", "hermano": "2",
        "hija": "2", "hija de juana": "2", "hijastra": "2", "hijo": "2", "mama": "2", "nephew": "2", "nieta": "2", "nieto": "2",
        "otra prima de su nene": "2", "padre": "2", "papa": "2", "prima": "2", "primo": "2", "sister": "2", "sobrina": "2",
        "sobrino": "2", "sobrinos": "2", "son": "2", "son in law": "2", "suegra": "2", "grandaughter ": "2", "hijastro": "2",
        "daughter in law": "2", "father": "2", "mother-in-law": "2", "niece": "2", "nuera": "2", "siblings": "2", "daugher": "2",
        "daught": "2", "daughter in laws": "2", "daughters": "2", "gradchildren": "2", "grandchildren": "2", "grandmother": "2",
        "great children": "2", "greatchildren": "2", "nice": "2", "children": "2", "sons": "2", "sobrinas": "2",
        "amiga": "3", "amiga (friend)": "3", "comay (friend)": "3", "amigo": "3", "best-friend": "3", "amigos": "3",
        "amiga/ comadre": "3", "friend": "3", "amigas": "3", "amiga (child)": "3", "godmother": "3", "friends": "3",
        "amiga (pastora)": "3", "hermana de la iglesia": "3", "amiga y hermana en la fe": "3",
        "boss": "4", "companeres de trabajo": "4", "co-worker": "4", "companera de trabajo": "4",
        "amiga/vecina": "5", "vecina pr": "5", "vecino": "5", "vecina (americana)": "5", "neighbor": "5",
        "doctor": "6",
        "consejera": "7", "consejero": "7", "psychologist": "7",
        "assoc pastor": "8", "pastor": "8", "priest": "8", "sacerdote": "8", "pastors": "8",
        "advocate": "9", "amiga/case manager": "9", "alianza": "9", "wife of building manager": "9", "case manager de case iris": "9",
        "boyfriend's mother": "9", "works in the building": "9", "case manager": "9", "home care aide": "9", "homemaker": "9",
        "interprete": "9", "secretary": "9", "wife of pastor": "9", "manager": "9", "pareja": "9", "trabajador social": "9",
        "alvarado": "9", "jose": "9", "guzman": "9", "natalia": "9", "neibord": "9", "albert": "9", "colon": "9", "dog": "9",
        "jorge": "9", "princess": "9", "taino": "9", "felicita": "9"
    }


    for _, (df, suffix) in bprhs_datasets.items():
        for var in base_variables:
            variable_name = var + suffix
            if variable_name in df.columns:
                df[variable_name] = (
                    df[variable_name]
                    .astype(str)
                    .str.lower()
                    .str.strip()
                    .replace(mapping)
                    .apply(lambda x: x if x in set(mapping.values()) else np.nan)
                )

    # Renaming variables
    df_hmz_sdoh_bprhs_0.rename(columns={f'pn{i}b': f'hmz_soc_support_ii_{i}_bprhs_0' for i in range(1, 11)}, inplace=True)
    df_hmz_sdoh_bprhs_2.rename(columns={f'pn{i}b_2yr': f'hmz_soc_support_ii_{i}_bprhs_2' for i in range(1, 11)}, inplace=True)
    df_hmz_sdoh_bprhs_8.rename(columns={f'pn{i}b_8yr': f'hmz_soc_support_ii_{i}_bprhs_8' for i in range(1, 11)}, inplace=True)

    # Saving
    df_hmz_sdoh_bprhs_0.to_csv('data/intermediate/df_hmz_sdoh_bprhs_0.csv', index=False)
    df_hmz_sdoh_bprhs_2.to_csv('data/intermediate/df_hmz_sdoh_bprhs_2.csv', index=False)
    df_hmz_sdoh_bprhs_8.to_csv('data/intermediate/df_hmz_sdoh_bprhs_8.csv', index=False)




    # Transformation 6
    # hmz_love_support
    # Assigning categories from prospect to BPRHS relationship with person that provides support (n=10)

    base_variables = ["emo1", "emo2", "emo3", "emo4", "emosup", "emo1_1", "emo1_2", "emo1_3", "emo1_4", "emo1_5", "emo1_6", "emo1_7", "emo1_8", "emo1_9", "emo1_10"]

    bprhs_datasets = {
        "Baseline": (df_hmz_sdoh_bprhs_0, ""),
        "2-Year": (df_hmz_sdoh_bprhs_2, "_2yr"),
        "5-Year": (df_hmz_sdoh_bprhs_5, "_5yr"),
        "8-Year": (df_hmz_sdoh_bprhs_8, "_8yr"),
    }

    for dataset_name, (df, _) in bprhs_datasets.items():
        df.columns = df.columns.str.lower().str.strip()

    # Creating the new variables avg emo1–emo4 by dividing by 16
    df_hmz_sdoh_bprhs_0['hmz_soc_emo1_avg_bprhs_0'] = df_hmz_sdoh_bprhs_0['emo1'].apply(
        lambda x: np.nan if pd.isna(x) else (x / 16 if x != 0 else 0)
    )

    df_hmz_sdoh_bprhs_0['hmz_soc_emo2_avg_bprhs_0'] = df_hmz_sdoh_bprhs_0['emo2'].apply(
        lambda x: np.nan if pd.isna(x) else (x / 16 if x != 0 else 0)
    )

    df_hmz_sdoh_bprhs_0['hmz_soc_emo3_avg_bprhs_0'] = df_hmz_sdoh_bprhs_0['emo3'].apply(
        lambda x: np.nan if pd.isna(x) else (x / 16 if x != 0 else 0)
    )

    df_hmz_sdoh_bprhs_0['hmz_soc_emo4_avg_bprhs_0'] = df_hmz_sdoh_bprhs_0['emo4'].apply(
        lambda x: np.nan if pd.isna(x) else (x / 16 if x != 0 else 0)
    )

    df_hmz_sdoh_bprhs_2['hmz_soc_emo1_avg_bprhs_2'] = df_hmz_sdoh_bprhs_2['emo1_2yr'].apply(
        lambda x: np.nan if pd.isna(x) else (x / 16 if x != 0 else 0)
    )

    df_hmz_sdoh_bprhs_2['hmz_soc_emo2_avg_bprhs_2'] = df_hmz_sdoh_bprhs_2['emo2_2yr'].apply(
        lambda x: np.nan if pd.isna(x) else (x / 16 if x != 0 else 0)
    )

    df_hmz_sdoh_bprhs_2['hmz_soc_emo3_avg_bprhs_2'] = df_hmz_sdoh_bprhs_2['emo3_2yr'].apply(
        lambda x: np.nan if pd.isna(x) else (x / 16 if x != 0 else 0)
    )

    df_hmz_sdoh_bprhs_2['hmz_soc_emo4_avg_bprhs_2'] = df_hmz_sdoh_bprhs_2['emo4_2yr'].apply(
        lambda x: np.nan if pd.isna(x) else (x / 16 if x != 0 else 0)
    )

    # Creating new variable hmz_soc_emosup_avg
    df_hmz_sdoh_bprhs_0['hmz_soc_emosup_avg_bprhs_0'] = (
        df_hmz_sdoh_bprhs_0['hmz_soc_emo1_avg_bprhs_0'] +
        df_hmz_sdoh_bprhs_0['hmz_soc_emo2_avg_bprhs_0'] +
        df_hmz_sdoh_bprhs_0['hmz_soc_emo3_avg_bprhs_0'] +
        df_hmz_sdoh_bprhs_0['hmz_soc_emo4_avg_bprhs_0']
    )

    df_hmz_sdoh_bprhs_2['hmz_soc_emosup_avg_bprhs_2'] = (
        df_hmz_sdoh_bprhs_2['hmz_soc_emo1_avg_bprhs_2'] +
        df_hmz_sdoh_bprhs_2['hmz_soc_emo2_avg_bprhs_2'] +
        df_hmz_sdoh_bprhs_2['hmz_soc_emo3_avg_bprhs_2'] +
        df_hmz_sdoh_bprhs_2['hmz_soc_emo4_avg_bprhs_2']
    )

    # Renaming
    df_hmz_sdoh_bprhs_0.rename(columns={
        'emo1_1': 'hmz_soc_emo1_1_bprhs_0',
        'emo1_2': 'hmz_soc_emo1_2_bprhs_0',
        'emo1_3': 'hmz_soc_emo1_3_bprhs_0',
        'emo1_4': 'hmz_soc_emo1_4_bprhs_0',
        'emo1_5': 'hmz_soc_emo1_5_bprhs_0',
        'emo1_6': 'hmz_soc_emo1_6_bprhs_0',
        'emo1_7': 'hmz_soc_emo1_7_bprhs_0',
        'emo1_8': 'hmz_soc_emo1_8_bprhs_0',
        'emo1_9': 'hmz_soc_emo1_9_bprhs_0',
        'emo1_10': 'hmz_soc_emo1_10_bprhs_0'
    }, inplace=True)

    df_hmz_sdoh_bprhs_2.rename(columns={
        'emo1_1_2yr': 'hmz_soc_emo1_1_bprhs_2',
        'emo1_2_2yr': 'hmz_soc_emo1_2_bprhs_2',
        'emo1_3_2yr': 'hmz_soc_emo1_3_bprhs_2',
        'emo1_4_2yr': 'hmz_soc_emo1_4_bprhs_2',
        'emo1_5_2yr': 'hmz_soc_emo1_5_bprhs_2',
        'emo1_6_2yr': 'hmz_soc_emo1_6_bprhs_2',
        'emo1_7_2yr': 'hmz_soc_emo1_7_bprhs_2',
        'emo1_8_2yr': 'hmz_soc_emo1_8_bprhs_2',
        'emo1_9_2yr': 'hmz_soc_emo1_9_bprhs_2',
        'emo1_10_2yr': 'hmz_soc_emo1_10_bprhs_2'
    }, inplace=True)


    # Saving
    df_hmz_sdoh_bprhs_0.to_csv('data/intermediate/df_hmz_sdoh_bprhs_0.csv', index=False)
    df_hmz_sdoh_bprhs_2.to_csv('data/intermediate/df_hmz_sdoh_bprhs_2.csv', index=False)





    # Transformation 7
    # hmz_respect_support
    # Assigning categories from prospect to BPRHS relationship with person that provides support (n=10)
    base_variables = ["emo2_1", "emo2_2", "emo2_3", "emo2_4", "emo2_5", "emo2_6", "emo2_7", "emo2_8", "emo2_9", "emo2_10"] # variables only exist in baseline and two year

    bprhs_datasets = {
        "Baseline": (df_hmz_sdoh_bprhs_0, ""),
        "2-Year": (df_hmz_sdoh_bprhs_2, "_2yr")}


    for dataset_name, (df, _) in bprhs_datasets.items():
        df.columns = df.columns.str.lower().str.strip()


    # Renaming columns 
    df_hmz_sdoh_bprhs_0.rename(columns={'emo2_1': 'hmz_soc_emo2_1_bprhs_0',
                                        'emo2_2': 'hmz_soc_emo2_2_bprhs_0',
                                        'emo2_3': 'hmz_soc_emo2_3_bprhs_0',
                                        'emo2_4': 'hmz_soc_emo2_4_bprhs_0',
                                        'emo2_5': 'hmz_soc_emo2_5_bprhs_0',
                                        'emo2_6': 'hmz_soc_emo2_6_bprhs_0',
                                        'emo2_7': 'hmz_soc_emo2_7_bprhs_0',
                                        'emo2_8': 'hmz_soc_emo2_8_bprhs_0',
                                        'emo2_9': 'hmz_soc_emo2_9_bprhs_0',
                                        'emo2_10':'hmz_soc_emo2_10_bprhs_0'}, inplace=True)



    df_hmz_sdoh_bprhs_2.rename(columns={'emo2_1_2yr': 'hmz_soc_emo2_1_bprhs_2',
                                        'emo2_2_2yr': 'hmz_soc_emo2_2_bprhs_2',
                                        'emo2_3_2yr': 'hmz_soc_emo2_3_bprhs_2',
                                        'emo2_4_2yr': 'hmz_soc_emo2_4_bprhs_2',
                                        'emo2_5_2yr': 'hmz_soc_emo2_5_bprhs_2',
                                        'emo2_6_2yr': 'hmz_soc_emo2_6_bprhs_2',
                                        'emo2_7_2yr': 'hmz_soc_emo2_7_bprhs_2',
                                        'emo2_8_2yr': 'hmz_soc_emo2_8_bprhs_2',
                                        'emo2_9_2yr': 'hmz_soc_emo2_9_bprhs_2',
                                        'emo2_10_2yr': 'hmz_soc_emo2_10_bprhs_2'}, inplace=True)




    # Saving 
    df_hmz_sdoh_bprhs_0.to_csv('data/intermediate/df_hmz_sdoh_bprhs_0.csv', index=False)
    df_hmz_sdoh_bprhs_2.to_csv('data/intermediate/df_hmz_sdoh_bprhs_2.csv', index=False)


    # Transformation 8
    # hmz_respect_support
    # Assigning categories from prospect to BPRHS relationship with person that provides support (n=10)
    base_variables = ["emo3_1", "emo3_2", "emo3_3", "emo3_4", "emo3_5", "emo3_6", "emo3_7", "emo3_8", "emo3_9", "emo3_10"]


    bprhs_datasets = {
        "Baseline": (df_hmz_sdoh_bprhs_0, ""),
        "2-Year": (df_hmz_sdoh_bprhs_2, "_2yr")}

    for dataset_name, (df, _) in bprhs_datasets.items():
        df.columns = df.columns.str.lower().str.strip()



    # Renaming  
    df_hmz_sdoh_bprhs_0.rename(columns={'emo3_1': 'hmz_soc_emo3_1_bprhs_0',
                                        'emo3_2': 'hmz_soc_emo3_2_bprhs_0',
                                        'emo3_3': 'hmz_soc_emo3_3_bprhs_0',
                                        'emo3_4': 'hmz_soc_emo3_4_bprhs_0',
                                        'emo3_5': 'hmz_soc_emo3_5_bprhs_0',
                                        'emo3_6': 'hmz_soc_emo3_6_bprhs_0',
                                        'emo3_7': 'hmz_soc_emo3_7_bprhs_0',
                                        'emo3_8': 'hmz_soc_emo3_8_bprhs_0',
                                        'emo3_9': 'hmz_soc_emo3_9_bprhs_0',
                                        'emo3_10': 'hmz_soc_emo3_10_bprhs_0'}, inplace=True)



    df_hmz_sdoh_bprhs_2.rename(columns={'emo3_1_2yr': 'hmz_soc_emo3_1_bprhs_2',
                                        'emo3_2_2yr': 'hmz_soc_emo3_2_bprhs_2',
                                        'emo3_3_2yr': 'hmz_soc_emo3_3_bprhs_2',
                                        'emo3_4_2yr': 'hmz_soc_emo3_4_bprhs_2',
                                        'emo3_5_2yr': 'hmz_soc_emo3_5_bprhs_2',
                                        'emo3_6_2yr': 'hmz_soc_emo3_6_bprhs_2',
                                        'emo3_7_2yr': 'hmz_soc_emo3_7_bprhs_2',
                                        'emo3_8_2yr': 'hmz_soc_emo3_8_bprhs_2',
                                        'emo3_9_2yr': 'hmz_soc_emo3_9_bprhs_2',
                                        'emo3_10_2yr': 'hmz_soc_emo3_10_bprhs_2'}, inplace=True)



    # Saving the datasets after transformation and renaming
    df_hmz_sdoh_bprhs_0.to_csv('data/intermediate/df_hmz_sdoh_bprhs_0.csv', index=False)
    df_hmz_sdoh_bprhs_2.to_csv('data/intermediate/df_hmz_sdoh_bprhs_2.csv', index=False)



    # Transformation 9
    # hmz_actions_thoughts_support
    # Assigning categories from prospect to BPRHS relationship with person that provides support (n=10)
    base_variables = ["emo4_1", "emo4_2", "emo4_3", "emo4_4", "emo4_5", "emo4_6", "emo4_7", "emo4_8", "emo4_9", "emo4_10"]


    bprhs_datasets = {
        "Baseline": (df_hmz_sdoh_bprhs_0, ""),
        "2-Year": (df_hmz_sdoh_bprhs_2, "_2yr")}

    for dataset_name, (df, _) in bprhs_datasets.items():
        df.columns = df.columns.str.lower().str.strip()


    #  Renaming
    df_hmz_sdoh_bprhs_0.rename(columns={'emo4_1': 'hmz_soc_emo4_1_bprhs_0',
                                        'emo4_2': 'hmz_soc_emo4_2_bprhs_0',
                                        'emo4_3': 'hmz_soc_emo4_3_bprhs_0',
                                        'emo4_4': 'hmz_soc_emo4_4_bprhs_0',
                                        'emo4_5': 'hmz_soc_emo4_5_bprhs_0',
                                        'emo4_6': 'hmz_soc_emo4_6_bprhs_0',
                                        'emo4_7': 'hmz_soc_emo4_7_bprhs_0',
                                        'emo4_8': 'hmz_soc_emo4_8_bprhs_0',
                                        'emo4_9': 'hmz_soc_emo4_9_bprhs_0',
                                        'emo4_10': 'hmz_soc_emo4_10_bprhs_0'}, inplace=True)



    df_hmz_sdoh_bprhs_2.rename(columns={'emo4_1_2yr': 'hmz_soc_emo4_1_bprhs_2',
                                        'emo4_2_2yr': 'hmz_soc_emo4_2_bprhs_2',
                                        'emo4_3_2yr': 'hmz_soc_emo4_3_bprhs_2',
                                        'emo4_4_2yr': 'hmz_soc_emo4_4_bprhs_2',
                                        'emo4_5_2yr': 'hmz_soc_emo4_5_bprhs_2',
                                        'emo4_6_2yr': 'hmz_soc_emo4_6_bprhs_2',
                                        'emo4_7_2yr': 'hmz_soc_emo4_7_bprhs_2',
                                        'emo4_8_2yr': 'hmz_soc_emo4_8_bprhs_2',
                                        'emo4_9_2yr': 'hmz_soc_emo4_9_bprhs_2',
                                        'emo4_10_2yr': 'hmz_soc_emo4_10_bprhs_2' }, inplace=True)




    # Saving 
    df_hmz_sdoh_bprhs_0.to_csv('data/intermediate/df_hmz_sdoh_bprhs_0.csv', index=False)
    df_hmz_sdoh_bprhs_2.to_csv('data/intermediate/df_hmz_sdoh_bprhs_2.csv', index=False)
    print("\nDatasets saved successfully.")

    # Transformation 10
    # hmz_soc_help_support
    # Assigning categories from prospect to BPRHS relationship with person that provides support (n=10)
    base_variables = ["aid5_1", "aid5_2", "aid5_3", "aid5_4", "aid5_5", "aid5_6", "aid5_7", "aid5_8", "aid5_9", "aid5_10", "aid5_11","aid5_12","aid5_13","aid5_14","aid5_15","aid5_16" ]


    bprhs_datasets = {
        "Baseline": (df_hmz_sdoh_bprhs_0, ""),
        "2-Year": (df_hmz_sdoh_bprhs_2, "_2yr")}


    # Transformation 11
    # Creating the new variables avg aid by dividing by 16
    # bprhs v1
    # aid5

    # Creating 'hmz_soc_aid5_avg' 
    df_hmz_sdoh_bprhs_0['hmz_soc_aid5_avg_bprhs_0'] = df_hmz_sdoh_bprhs_0['aid5'].apply(
        lambda x: np.nan if pd.isna(x) else (x / 16 if x != 0 else 0))


    # aid6
    # Creating 'hmz_soc_aid6_avg' 
    df_hmz_sdoh_bprhs_0['hmz_soc_aid6_avg_bprhs_0'] = df_hmz_sdoh_bprhs_0['aid6'].apply(
        lambda x: np.nan if pd.isna(x) else (x / 16 if x != 0 else 0))


    # bprhs v2
    # aid5
    # Creating 'hmz_soc_aid5_avg' 
    df_hmz_sdoh_bprhs_2['hmz_soc_aid5_avg_bprhs_2'] = df_hmz_sdoh_bprhs_2['aid5_2yr'].apply(
        lambda x: np.nan if pd.isna(x) else (x / 16 if x != 0 else 0))

    #aid6
    # Creating 'hmz_soc_aid6_avg' 
    df_hmz_sdoh_bprhs_2['hmz_soc_aid6_avg_bprhs_2'] = df_hmz_sdoh_bprhs_2['aid6_2yr'].apply(
        lambda x: np.nan if pd.isna(x) else (x / 16 if x != 0 else 0))

    # Saving
    df_hmz_sdoh_bprhs_0.to_csv('data/intermediate/df_hmz_sdoh_bprhs_0.csv', index=False)
    df_hmz_sdoh_bprhs_2.to_csv('data/intermediate/df_hmz_sdoh_bprhs_2.csv', index=False)



    # creating new variable hmz_soc_aid_avg
    # bprhs v1
    df_hmz_sdoh_bprhs_0['hmz_soc_aid_avg_bprhs_0'] = (
        df_hmz_sdoh_bprhs_0['hmz_soc_aid5_avg_bprhs_0'] +
        df_hmz_sdoh_bprhs_0['hmz_soc_aid6_avg_bprhs_0'] 
    )




    #bprhs v2
    df_hmz_sdoh_bprhs_2['hmz_soc_aid_avg_bprhs_2'] = (
        df_hmz_sdoh_bprhs_2['hmz_soc_aid5_avg_bprhs_2'] +
        df_hmz_sdoh_bprhs_2['hmz_soc_aid6_avg_bprhs_2'] 
    )




    #  Renaming
    df_hmz_sdoh_bprhs_0.rename(columns={'aid5_1': 'hmz_soc_aid5_1_bprhs_0',
                                        'aid5_2': 'hmz_soc_aid5_2_bprhs_0',
                                        'aid5_3': 'hmz_soc_aid5_3_bprhs_0',
                                        'aid5_4': 'hmz_soc_aid5_4_bprhs_0',
                                        'aid5_5': 'hmz_soc_aid5_5_bprhs_0',
                                        'aid5_6': 'hmz_soc_aid5_6_bprhs_0',
                                        'aid5_7': 'hmz_soc_aid5_7_bprhs_0',
                                        'aid5_8': 'hmz_soc_aid5_8_bprhs_0',
                                        'aid5_9': 'hmz_soc_aid5_9_bprhs_0',
                                        'aid5_10': 'hmz_soc_aid5_10_bprhs_0'
                                                                      
                                        }, inplace=True)

    df_hmz_sdoh_bprhs_0.rename(columns={'aid6_1': 'hmz_soc_aid6_1_bprhs_0',
                                        'aid6_2': 'hmz_soc_aid6_2_bprhs_0',
                                        'aid6_3': 'hmz_soc_aid6_3_bprhs_0',
                                        'aid6_4': 'hmz_soc_aid6_4_bprhs_0',
                                        'aid6_5': 'hmz_soc_aid6_5_bprhs_0',
                                        'aid6_6': 'hmz_soc_aid6_6_bprhs_0',
                                        'aid6_7': 'hmz_soc_aid6_7_bprhs_0',
                                        'aid6_8': 'hmz_soc_aid6_8_bprhs_0',
                                        'aid6_9': 'hmz_soc_aid6_9_bprhs_0',
                                        'aid6_10': 'hmz_soc_aid6_10_bprhs_0'
                                                                      
                                        }, inplace=True)



    df_hmz_sdoh_bprhs_2.rename(columns={'aid5_1_2yr': 'hmz_soc_aid5_1_bprhs_2',
                                        'aid5_2_2yr': 'hmz_soc_aid5_2_bprhs_2',
                                        'aid5_3_2yr': 'hmz_soc_aid5_3_bprhs_2',
                                        'aid5_4_2yr': 'hmz_soc_aid5_4_bprhs_2',
                                        'aid5_5_2yr': 'hmz_soc_aid5_5_bprhs_2',
                                        'aid5_6_2yr': 'hmz_soc_aid5_6_bprhs_2',
                                        'aid5_7_2yr': 'hmz_soc_aid5_7_bprhs_2',
                                        'aid5_8_2yr': 'hmz_soc_aid5_8_bprhs_2',
                                        'aid5_9_2yr': 'hmz_soc_aid5_9_bprhs_2',
                                        'aid5_10_2yr': 'hmz_soc_aid5_10_bprhs_2'
                                    
                                        }, inplace=True)

    df_hmz_sdoh_bprhs_2.rename(columns={'aid6_1_2yr': 'hmz_soc_aid6_1_bprhs_2',
                                        'aid6_2_2yr': 'hmz_soc_aid6_2_bprhs_2',
                                        'aid6_3_2yr': 'hmz_soc_aid6_3_bprhs_2',
                                        'aid6_4_2yr': 'hmz_soc_aid6_4_bprhs_2',
                                        'aid6_5_2yr': 'hmz_soc_aid6_5_bprhs_2',
                                        'aid6_6_2yr': 'hmz_soc_aid6_6_bprhs_2',
                                        'aid6_7_2yr': 'hmz_soc_aid6_7_bprhs_2',
                                        'aid6_8_2yr': 'hmz_soc_aid6_8_bprhs_2',
                                        'aid6_9_2yr': 'hmz_soc_aid6_9_bprhs_2',
                                        'aid6_10_2yr': 'hmz_soc_aid6_10_bprhs_2'
                                    
                                        }, inplace=True)



    # Saving 
    df_hmz_sdoh_bprhs_0.to_csv('data/intermediate/df_hmz_sdoh_bprhs_0.csv', index=False)
    df_hmz_sdoh_bprhs_2.to_csv('data/intermediate/df_hmz_sdoh_bprhs_2.csv', index=False)






    # Transformation 12
    # hmz_soc_aid6
    # Assigning categories from prospect to BPRHS relationship with person that provides support (n=10)
    base_variables = ["aid6_1", "aid6_2", "aid6_3", "aid6_4", "aid6_5", "aid6_6", "aid6_7", "aid6_8", "aid6_9", "aid6_10"]

    bprhs_datasets = {
        "Baseline": (df_hmz_sdoh_bprhs_0, ""),
        "2-Year": (df_hmz_sdoh_bprhs_2, "_2yr"),
    }

    # Normalizing column names in all datasets
    for dataset_name, (df, _) in bprhs_datasets.items():
        df.columns = df.columns.str.lower().str.strip()

    # Renaming  
    df_hmz_sdoh_bprhs_0.rename(columns={'aid6_1': 'hmz_soc_aid6_1_bprhs_0',
                                        'aid6_2': 'hmz_soc_aid6_2_bprhs_0',
                                        'aid6_3': 'hmz_soc_aid6_3_bprhs_0',
                                        'aid6_4': 'hmz_soc_aid6_4_bprhs_0',
                                        'aid6_5': 'hmz_soc_aid6_5_bprhs_0',
                                        'aid6_6': 'hmz_soc_aid6_6_bprhs_0',
                                        'aid6_7': 'hmz_soc_aid6_7_bprhs_0',
                                        'aid6_8': 'hmz_soc_aid6_8_bprhs_0',
                                        'aid6_9': 'hmz_soc_aid6_9_bprhs_0',
                                        'aid6_10': 'hmz_soc_aid6_10_bprhs_0'
                                                                      
                                        }, inplace=True)



    df_hmz_sdoh_bprhs_2.rename(columns={'aid6_1_2yr': 'hmz_soc_aid6_1_bprhs_2',
                                        'aid6_2_2yr': 'hmz_soc_aid6_2_bprhs_2',
                                        'aid6_3_2yr': 'hmz_soc_aid6_3_bprhs_2',
                                        'aid6_4_2yr': 'hmz_soc_aid6_4_bprhs_2',
                                        'aid6_5_2yr': 'hmz_soc_aid6_5_bprhs_2',
                                        'aid6_6_2yr': 'hmz_soc_aid6_6_bprhs_2',
                                        'aid6_7_2yr': 'hmz_soc_aid6_7_bprhs_2',
                                        'aid6_8_2yr': 'hmz_soc_aid6_8_bprhs_2',
                                        'aid6_9_2yr': 'hmz_soc_aid6_9_bprhs_2',
                                        'aid6_10_2yr': 'hmz_soc_aid6_10_bprhs_2'
                                
                                        }, inplace=True)



    # Saving the datasets 
    df_hmz_sdoh_bprhs_0.to_csv('data/intermediate/df_hmz_sdoh_bprhs_0.csv', index=False)
    df_hmz_sdoh_bprhs_2.to_csv('data/intermediate/df_hmz_sdoh_bprhs_2.csv', index=False)


    # --------------------------------------
    # PROSPECT
    # --------------------------------------


    # Transformation 1: recoding 96, 97, 98 as nan
    recode_rename_map = {
        # General social support
        "soc1": "hmz_soc1_prospect",
        "soc2a": "hmz_soc2a_prospect",
        "soc2b": "hmz_soc2b_prospect",
        "soc3a": "hmz_soc3a_prospect",
        "soc3b": "hmz_soc3b_prospect",
        "soc4a": "hmz_soc4a_prospect",
        "soc4b": "hmz_soc4b_prospect",
        "soc5a": "hmz_soc5a_prospect",
        "soc5b": "hmz_soc5b_prospect",
        "soc6": "hmz_soc6_prospect",
        "soc20": "hmz_soc_activities_feel_prospect",
    
        # Instrumental support
        "nor1a": "hmz_soc_support_ii_1_prospect",
        "nor2a": "hmz_soc_support_ii_2_prospect",
        "nor3a": "hmz_soc_support_ii_3_prospect",
        "nor4a": "hmz_soc_support_ii_4_prospect",
        "nor5a": "hmz_soc_support_ii_5_prospect",
        "nor6a": "hmz_soc_support_ii_6_prospect",
        "nor7a": "hmz_soc_support_ii_7_prospect",
        "nor8a": "hmz_soc_support_ii_8_prospect",
        "nor9a": "hmz_soc_support_ii_9_prospect",
        "nor10a": "hmz_soc_support_ii_10_prospect",

        # Emotional closeness
        "nor1c": "hmz_soc_emo1_1_prospect",
        "nor2c": "hmz_soc_emo1_2_prospect",
        "nor3c": "hmz_soc_emo1_3_prospect",
        "nor4c": "hmz_soc_emo1_4_prospect",
        "nor5c": "hmz_soc_emo1_5_prospect",
        "nor6c": "hmz_soc_emo1_6_prospect",
        "nor7c": "hmz_soc_emo1_7_prospect",
        "nor8c": "hmz_soc_emo1_8_prospect",
        "nor9c": "hmz_soc_emo1_9_prospect",
        "nor10c": "hmz_soc_emo1_10_prospect",

        # Respect/support
        "nor1d": "hmz_soc_emo2_1_prospect",
        "nor2d": "hmz_soc_emo2_2_prospect",
        "nor3d": "hmz_soc_emo2_3_prospect",
        "nor4d": "hmz_soc_emo2_4_prospect",
        "nor5d": "hmz_soc_emo2_5_prospect",
        "nor6d": "hmz_soc_emo2_6_prospect",
        "nor7d": "hmz_soc_emo2_7_prospect",
        "nor8d": "hmz_soc_emo2_8_prospect",
        "nor9d": "hmz_soc_emo2_9_prospect",
        "nor10d": "hmz_soc_emo2_10_prospect",

        # Confide
        "nor1e": "hmz_soc_emo3_1_prospect",
        "nor2e": "hmz_soc_emo3_2_prospect",
        "nor3e": "hmz_soc_emo3_3_prospect",
        "nor4e": "hmz_soc_emo3_4_prospect",
        "nor5e": "hmz_soc_emo3_5_prospect",
        "nor6e": "hmz_soc_emo3_6_prospect",
        "nor7e": "hmz_soc_emo3_7_prospect",
        "nor8e": "hmz_soc_emo3_8_prospect",
        "nor9e": "hmz_soc_emo3_9_prospect",
        "nor10e": "hmz_soc_emo3_10_prospect",

        # Actions/thoughts
        "nor1f": "hmz_soc_emo4_1_prospect",
        "nor2f": "hmz_soc_emo4_2_prospect",
        "nor3f": "hmz_soc_emo4_3_prospect",
        "nor4f": "hmz_soc_emo4_4_prospect",
        "nor5f": "hmz_soc_emo4_5_prospect",
        "nor6f": "hmz_soc_emo4_6_prospect",
        "nor7f": "hmz_soc_emo4_7_prospect",
        "nor8f": "hmz_soc_emo4_8_prospect",
        "nor9f": "hmz_soc_emo4_9_prospect",
        "nor10f": "hmz_soc_emo4_10_prospect",

        # Aid 5
        "nor1g": "hmz_soc_aid5_1_prospect",
        "nor2g": "hmz_soc_aid5_2_prospect",
        "nor3g": "hmz_soc_aid5_3_prospect",
        "nor4g": "hmz_soc_aid5_4_prospect",
        "nor5g": "hmz_soc_aid5_5_prospect",
        "nor6g": "hmz_soc_aid5_6_prospect",
        "nor7g": "hmz_soc_aid5_7_prospect",
        "nor8g": "hmz_soc_aid5_8_prospect",
        "nor9g": "hmz_soc_aid5_9_prospect",
        "nor10g": "hmz_soc_aid5_10_prospect",

        # Aid 6
        "nor1h": "hmz_soc_aid6_1_prospect",
        "nor2h": "hmz_soc_aid6_2_prospect",
        "nor3h": "hmz_soc_aid6_3_prospect",
        "nor4h": "hmz_soc_aid6_4_prospect",
        "nor5h": "hmz_soc_aid6_5_prospect",
        "nor6h": "hmz_soc_aid6_6_prospect",
        "nor7h": "hmz_soc_aid6_7_prospect",
        "nor8h": "hmz_soc_aid6_8_prospect",
        "nor9h": "hmz_soc_aid6_9_prospect",
        "nor10h": "hmz_soc_aid6_10_prospect"
    }

    # Recode and rename
    for original_var, renamed_var in recode_rename_map.items():
        if original_var in df_hmz_sdoh_prospect.columns:
            df_hmz_sdoh_prospect[original_var] = df_hmz_sdoh_prospect[original_var].replace({96: np.nan, 97: np.nan, 98: np.nan})

    df_hmz_sdoh_prospect.rename(columns=recode_rename_map, inplace=True)

    # Saving
    df_hmz_sdoh_prospect.to_csv('data/intermediate/df_hmz_sdoh_prospect.csv', index=False)

    # Transformation 2: creating variable soc_activities
    # Variables to sum for creating soc_activities
    variables_prospect = [
        "soc7", "soc8", "soc9", "soc10", "soc11",
        "soc12", "soc13", "soc14", "soc15", "soc16", "soc17", "soc18", "soc19"]



    for var in variables_prospect:
        if var in df_hmz_sdoh_prospect.columns:
            df_hmz_sdoh_prospect[var] = pd.to_numeric(df_hmz_sdoh_prospect[var], errors='coerce')
            df_hmz_sdoh_prospect[var] = df_hmz_sdoh_prospect[var].replace({96: np.nan, 97: np.nan, 98: np.nan})



    # Creating the new variable
    # Lambda function that filters non-NaN and non-zero values, assigning NaN if the entire row is NaN
    df_hmz_sdoh_prospect["hmz_soc_activities_prospect"] = (
        df_hmz_sdoh_prospect[variables_prospect]
        .apply(lambda row: np.nan if row.isna().all() else row[(row.notna()) & (row != 0)].count(), axis=1))

    # saving
    df_hmz_sdoh_prospect.to_csv('data/intermediate/df_hmz_sdoh_prospect.csv', index=False)

    # Renaming variables
    df_hmz_sdoh_prospect.rename(columns={
        "soc7": "hmz_soc_get_together_i_prospect",
        "soc8": "hmz_soc_volunteer_prospect",
        "soc9": "hmz_soc_phone_i_prospect",
        "soc10": "hmz_soc_get_together_ii_prospect",
        "soc11": "hmz_soc_phone_ii_prospect",
        "soc12": "hmz_soc_church_prospect",
        "soc13": "hmz_soc_event_prospect",
        "soc14": "hmz_soc_sports_prospect",
        "soc15": "hmz_soc_read_prospect",
        "soc16": "hmz_soc_hobbies_prospect",
        "soc17": "hmz_soc_repairs_prospect",
        "soc18": "hmz_soc_care_relative_prospect",
        "soc19": "hmz_soc_help_prospect"
    }, inplace=True)


    # Saving 
    df_hmz_sdoh_prospect.to_csv('data/intermediate/df_hmz_sdoh_prospect.csv', index=False)

    # Transformation 3: creating a dictionary to handle the non-numeric answers
    people = {
        7: ["Andrea, Millie, ALexa, Alondra, Cesar, Jesius, Edgar"],
        11: ["Benjamin, Daisy, Amarilys, Migdalia, Eva, Ive, Cristina, Carlos, Abigail, Emanuel, Nadia      1"],
        6: ["Wilda, Wanda, Irma, Eileen, Jimmy, Jaqueline", 
            "Marinet, Gilberto, Sauda, Ivelisse, Alnery, Edwin", 
            "Roselyn, Rosangely, Wilmerie, Iris, Hermanos, Santos", 
            "Esposa, hermana, sobrinos, amistades (no menciono nombres), perritos"],
        5: ["Hijos, nietos, esposo"],  # assuming hijos = 2, nietos = 2 and esposo = 1
        'no sabe': np.nan,
        "El participante no puede determinar el número de personas.": np.nan,
        2: ["JSS, LG"],
        3: ["Luz Rosado Guillet"]}

    # Function to categorize people
    def categorize_people(value):
        # Handle missing values or empty strings
        if pd.isna(value) or (isinstance(value, str) and value.strip() == ""):
            return np.nan  

        # Trying to convert numeric strings
        try:
            return float(value)
        except:
            pass

        value_stripped = value.strip()

        # Check for exact match in dictionary keys
        if value_stripped in people:
            return people[value_stripped]

        # Convert to lowercase for text comparison
        value_lower = value_stripped.lower()

        # Check if the text matches any predefined category (substring match)
        for category, keywords in people.items():
            if isinstance(keywords, list):
                if any(isinstance(keyword, str) and keyword.lower() in value_lower for keyword in keywords):
                    return category

        return np.nan  # Default to NaN if no match is found

    # Function to transform the dataset
    def transform_people(df, suffix):
        col_name = "nor0"  # Column to transform
        if col_name in df.columns:
            df[f"hmz_soc_support_i_{suffix}"] = df[col_name].apply(categorize_people)

    transform_people(df_hmz_sdoh_prospect, "prospect")

    # Saving
    df_hmz_sdoh_prospect.to_csv('data/intermediate/df_hmz_sdoh_prospect.csv', index=False)


    # Transformation 4: Creating derived variables
    # hmz_soc_emo1_avg
    emo1_vars_prospect = [
        "hmz_soc_emo1_1_prospect", "hmz_soc_emo1_2_prospect", "hmz_soc_emo1_3_prospect", 
        "hmz_soc_emo1_4_prospect", "hmz_soc_emo1_5_prospect", "hmz_soc_emo1_6_prospect", 
        "hmz_soc_emo1_7_prospect", "hmz_soc_emo1_8_prospect", "hmz_soc_emo1_9_prospect", 
        "hmz_soc_emo1_10_prospect"]


    def calculate_avg_with_nans_and_zeros(row):
        if row.isna().all():
            return np.nan  # All values are NaN, keep as NaN
        return row.sum() / 10  # Include zeros, divide by 10

    df_hmz_sdoh_prospect['hmz_soc_emo1_avg_prospect'] = df_hmz_sdoh_prospect[emo1_vars_prospect].apply(
        calculate_avg_with_nans_and_zeros, axis=1
    )


    # hmz_soc_emo2_avg

    emo2_vars_prospect = [
        "hmz_soc_emo2_1_prospect", "hmz_soc_emo2_2_prospect", "hmz_soc_emo2_3_prospect", 
        "hmz_soc_emo2_4_prospect", "hmz_soc_emo2_5_prospect", "hmz_soc_emo2_6_prospect", 
        "hmz_soc_emo2_7_prospect", "hmz_soc_emo2_8_prospect", "hmz_soc_emo2_9_prospect", 
        "hmz_soc_emo2_10_prospect"]



    def calculate_avg_with_nans_and_zeros(row):
        if row.isna().all():
            return np.nan  # All values are NaN, keep as NaN
        return row.sum() / 10  # Include zeros, divide by 10

    df_hmz_sdoh_prospect['hmz_soc_emo2_avg_prospect'] = df_hmz_sdoh_prospect[emo2_vars_prospect].apply(
        calculate_avg_with_nans_and_zeros, axis=1
    )


    # hmz_soc_emo3_avg
    emo3_vars_prospect = [
        "hmz_soc_emo3_1_prospect", "hmz_soc_emo3_2_prospect", "hmz_soc_emo3_3_prospect", 
        "hmz_soc_emo3_4_prospect", "hmz_soc_emo3_5_prospect", "hmz_soc_emo3_6_prospect", 
        "hmz_soc_emo3_7_prospect", "hmz_soc_emo3_8_prospect", "hmz_soc_emo3_9_prospect", 
        "hmz_soc_emo3_10_prospect"]


    def calculate_avg_with_nans_and_zeros(row):
        if row.isna().all():
            return np.nan  # All values are NaN, keep as NaN
        return row.sum() / 10  # Include zeros, divide by 10

    df_hmz_sdoh_prospect['hmz_soc_emo3_avg_prospect'] = df_hmz_sdoh_prospect[emo3_vars_prospect].apply(
        calculate_avg_with_nans_and_zeros, axis=1)



    # hmz_soc_emo4_avg
    emo4_vars_prospect = [
        "hmz_soc_emo4_1_prospect", "hmz_soc_emo4_2_prospect", "hmz_soc_emo4_3_prospect", 
        "hmz_soc_emo4_4_prospect", "hmz_soc_emo4_5_prospect", "hmz_soc_emo4_6_prospect", 
        "hmz_soc_emo4_7_prospect", "hmz_soc_emo4_8_prospect", "hmz_soc_emo4_9_prospect", 
        "hmz_soc_emo4_10_prospect"]


    def calculate_avg_with_nans_and_zeros(row):
        if row.isna().all():
            return np.nan  # All values are NaN, keep as NaN
        return row.sum() / 10  # Include zeros, divide by 10

    df_hmz_sdoh_prospect['hmz_soc_emo4_avg_prospect'] = df_hmz_sdoh_prospect[emo4_vars_prospect].apply(
        calculate_avg_with_nans_and_zeros, axis=1
    )

    # Saving 
    df_hmz_sdoh_prospect.to_csv('data/intermediate/df_hmz_sdoh_prospect.csv', index=False)

    # Creating the new emosup variable
    # Create 'hmz_soc_emosup_avg_prospect' as the sum of the four averages
    df_hmz_sdoh_prospect['hmz_soc_emosup_avg_prospect'] = (
        df_hmz_sdoh_prospect['hmz_soc_emo1_avg_prospect'] +
        df_hmz_sdoh_prospect['hmz_soc_emo2_avg_prospect'] +
        df_hmz_sdoh_prospect['hmz_soc_emo3_avg_prospect'] +
        df_hmz_sdoh_prospect['hmz_soc_emo4_avg_prospect'])



    # Saving 
    df_hmz_sdoh_prospect.to_csv('data/intermediate/df_hmz_sdoh_prospect.csv', index=False)


    # Transformation 5: aid5
    # hmz_soc_aid5_avg
    aid5_vars_prospect = [
        "hmz_soc_aid5_1_prospect", "hmz_soc_aid5_2_prospect", "hmz_soc_aid5_3_prospect", 
        "hmz_soc_aid5_4_prospect", "hmz_soc_aid5_5_prospect", "hmz_soc_aid5_6_prospect", 
        "hmz_soc_aid5_7_prospect", "hmz_soc_aid5_8_prospect", "hmz_soc_aid5_9_prospect", 
        "hmz_soc_aid5_10_prospect"]


    def calculate_avg_with_nans_and_zeros(row):
        if row.isna().all():
            return np.nan  # All values are NaN, keep as NaN
        return row.sum() / 10  # Include zeros, divide by 10

    df_hmz_sdoh_prospect['hmz_soc_aid5_avg_prospect'] = df_hmz_sdoh_prospect[aid5_vars_prospect].apply(
        calculate_avg_with_nans_and_zeros, axis=1)




    # Transformation 6: aid6
    # hmz_soc_aid6_avg
    aid6_vars_prospect = [
        "hmz_soc_aid6_1_prospect", "hmz_soc_aid6_2_prospect", "hmz_soc_aid6_3_prospect", 
        "hmz_soc_aid6_4_prospect", "hmz_soc_aid6_5_prospect", "hmz_soc_aid6_6_prospect", 
        "hmz_soc_aid6_7_prospect", "hmz_soc_aid6_8_prospect", "hmz_soc_aid6_9_prospect", 
        "hmz_soc_aid6_10_prospect"]

    def calculate_avg_with_nans_and_zeros(row):
        if row.isna().all():
            return np.nan  # All values are NaN, keep as NaN
        return row.sum() / 10  # Include zeros, divide by 10

    df_hmz_sdoh_prospect['hmz_soc_aid6_avg_prospect'] = df_hmz_sdoh_prospect[aid6_vars_prospect].apply(
        calculate_avg_with_nans_and_zeros, axis=1)

    # Saving
    df_hmz_sdoh_prospect.to_csv('data/intermediate/df_hmz_sdoh_prospect.csv', index=False)



    # Creating new variable aid_avg
    # Create 'hmz_soc_aid_avg_prospect' as the sum of the four averages
    df_hmz_sdoh_prospect['hmz_soc_aid_avg_prospect'] = (
        df_hmz_sdoh_prospect['hmz_soc_aid5_avg_prospect'] +
        df_hmz_sdoh_prospect['hmz_soc_aid6_avg_prospect'] )


    # Saving 
    df_hmz_sdoh_prospect.to_csv('data/intermediate/df_hmz_sdoh_prospect.csv', index=False)



    #------------------------------------------------------------------------------------------------
    # Access to Health Services
    # -----------------------------------------------------------------------------------------------


    # --------------------------------------
    # BPRHS
    # --------------------------------------

    base_variables = ["ins1", "ins1x", "ins2_1", "ins2_2", "ins2_3", "ins2_4", "ins2_5", "ins2_6", "ins2_7", "ins2_8", "ins2_9", "ins3"]

    bprhs_datasets = {
        "Baseline": (df_hmz_sdoh_bprhs_0, ""),
        "2-Year": (df_hmz_sdoh_bprhs_2, "_2yr"),
        "5-Year": (df_hmz_sdoh_bprhs_5, "_5yr")
    }

    # Recoding values 97 and 98 to np.nan and cleaning strings
    for df, suffix in bprhs_datasets.values():
        for var in base_variables:
            var_name = var + suffix
            if var_name in df.columns:
                df[var_name] = df[var_name].apply(lambda x: int(x.strip()) if isinstance(x, str) and x.strip().isdigit() else x)
                df[var_name] = df[var_name].replace({97: np.nan, 98: np.nan})

    # Public Insurance Variables
    # Baseline
    if all(var in df_hmz_sdoh_bprhs_0.columns for var in ["ins2_1", "ins2_2"]):
        df_hmz_sdoh_bprhs_0['hmz_public_insurance_bprhs_0'] = df_hmz_sdoh_bprhs_0[["ins2_1", "ins2_2"]].max(axis=1)
        print("Variable hmz_public_insurance_bprhs_0 created successfully.")
    else:
        print("One or both of the variables 'ins2_1' or 'ins2_2' not found in baseline.")

    # 2-Year
    if all(var in df_hmz_sdoh_bprhs_2.columns for var in ["ins2_1_2yr", "ins2_2_2yr"]):
        df_hmz_sdoh_bprhs_2['hmz_public_insurance_bprhs_2'] = df_hmz_sdoh_bprhs_2[["ins2_1_2yr", "ins2_2_2yr"]].max(axis=1)
        print("Variable hmz_public_insurance_bprhs_2 created successfully.")
    else:
        print("One or both of the variables 'ins2_1_2yr' or 'ins2_2_2yr' not found in 2-Year dataset.")


    # Private Insurance Variables
    # Baseline
    private_vars_0 = ["ins2_3", "ins2_4", "ins2_5", "ins2_6", "ins2_7", "ins2_8", "ins2_9"]
    if all(var in df_hmz_sdoh_bprhs_0.columns for var in private_vars_0):
        df_hmz_sdoh_bprhs_0['hmz_private_insurance_bprhs_0'] = df_hmz_sdoh_bprhs_0[private_vars_0].max(axis=1)
        print("Variable hmz_private_insurance_bprhs_0 created successfully.")
    else:
        print("Some private insurance variables not found in baseline dataset.")

    # 2-Year
    private_vars_2yr = [var + "_2yr" for var in private_vars_0]
    if all(var in df_hmz_sdoh_bprhs_2.columns for var in private_vars_2yr):
        df_hmz_sdoh_bprhs_2['hmz_private_insurance_bprhs_2'] = df_hmz_sdoh_bprhs_2[private_vars_2yr].max(axis=1)
        print("Variable hmz_private_insurance_bprhs_2 created successfully.")
    else:
        print("Some private insurance variables not found in 2-Year dataset.")


    # RenamingVariables
    df_hmz_sdoh_bprhs_0.rename(columns={'ins1': 'hmz_insurance_bprhs_0'}, inplace=True)
    df_hmz_sdoh_bprhs_2.rename(columns={'ins1x_2yr': 'hmz_insurance_bprhs_2'}, inplace=True)
    df_hmz_sdoh_bprhs_5.rename(columns={'ins1_5yr': 'hmz_insurance_bprhs_5'}, inplace=True)

    # Recoding hmz_no_insurance_bprhs_0 to be in the same categories as in prospect:
    # 1. Less than 1 year  2. Between 1 year and 5 years  3. More than 5 years but less than 10  4. More than 10 years

    # Function to convert ins3a and ins3a2 into years
    def convert_to_years(row):
        if pd.isna(row['ins3a']) or pd.isna(row['ins3a2']):
            return np.nan
        if row['ins3a2'] == 1:   # Years
            return row['ins3a']
        elif row['ins3a2'] == 2: # Months
            return row['ins3a'] / 12
        elif row['ins3a2'] == 3: # Weeks
            return row['ins3a'] / 52
        else:
            return np.nan

    # Applying the conversion directly and storing in a temporary variable
    df_hmz_sdoh_bprhs_0['ins3a_converted'] = df_hmz_sdoh_bprhs_0.apply(convert_to_years, axis=1)

    # Recode into categories
    def recode_no_insurance(years):
        if pd.isna(years):
            return np.nan
        elif years < 1:
            return 1
        elif 1 <= years <= 5:
            return 2
        elif 5 < years < 10:
            return 3
        else:
            return 4

    # Apply recoding
    df_hmz_sdoh_bprhs_0['hmz_no_insurance_bprhs_0'] = df_hmz_sdoh_bprhs_0['ins3a_converted'].apply(recode_no_insurance)

    # Droping the temporary variable
    df_hmz_sdoh_bprhs_0.drop(columns=['ins3a_converted'], inplace=True)

    # Saving
    df_hmz_sdoh_bprhs_0.to_csv('data/intermediate/df_hmz_sdoh_bprhs_0.csv', index=False)
    print("Baseline dataset saved to 'df_hmz_sdoh_bprhs_0.csv'.")


    # --------------------------------------
    # PROSPECT
    # --------------------------------------

    variables_to_recode = [
        "hhc5", "hhc5b1", "hhc5b2", "hhc5b13", "hhc5b15", "hhc5b3", "hhc5b4",
        "hhc5b5", "hhc5b6", "hhc5b7", "hhc5b8", "hhc5b9", "hhc5b10", "hhc5b11",
        "hhc5b12", "hhc5b14", "hhc5b16", "hhc5b17", "hhc5a"
    ]

    for var in variables_to_recode:
        df_hmz_sdoh_prospect[var] = df_hmz_sdoh_prospect[var].replace({96: np.nan, 97: np.nan, 98: np.nan})




    # Recoding public insurance
    # Creating a new variable hmz_public_insurance_prospect
    if all(var in df_hmz_sdoh_prospect.columns for var in ['hhc5b1', 'hhc5b2', 'hhc5b13', 'hhc5b15']):
        df_hmz_sdoh_prospect['hmz_public_insurance_prospect'] = df_hmz_sdoh_prospect[['hhc5b1', 'hhc5b2', 'hhc5b13', 'hhc5b15']].max(axis=1)
        print("Variable hmz_public_insurance_prospect created successfully.")
    else:
        print("Some variables required for hmz_public_insurance_prospect are missing from the dataset.")



    # Recoding private insurance
    # Creating a new variable hmz_private_insurance_prospect
    if all(var in df_hmz_sdoh_prospect.columns for var in ["hhc5b3", "hhc5b4", "hhc5b5", "hhc5b6", "hhc5b7", "hhc5b8",
                                                           "hhc5b9", "hhc5b10", "hhc5b11", "hhc5b12", "hhc5b14", "hhc5b16", "hhc5b17"]):
        df_hmz_sdoh_prospect['hmz_private_insurance_prospect'] = df_hmz_sdoh_prospect[
            ["hhc5b3", "hhc5b4", "hhc5b5", "hhc5b6", "hhc5b7", "hhc5b8", "hhc5b9", "hhc5b10",
             "hhc5b11", "hhc5b12", "hhc5b14", "hhc5b16", "hhc5b17"]].max(axis=1)
        print("Variable hmz_private_insurance_prospect created successfully.")
    else:
        print("Some variables required for hmz_private_insurance_prospect are missing from the dataset.")


    # Renaming 
    df_hmz_sdoh_prospect.rename(columns={'hhc5': 'hmz_insurance_prospect', 'hhc5a': 'hmz_no_insurance_prospect'}, inplace=True)



    # Saving
    df_hmz_sdoh_prospect.to_csv('data/intermediate/df_hmz_sdoh_prospect.csv', index=False)

    #------------------------------------------------------------------------------------------------
    # Perceived Discrimination
    # -----------------------------------------------------------------------------------------------

    # --------------------------------------
    # BPRHS
    # --------------------------------------
    # Transformation 1: recoding no answer and renaming variables

    # Variables to recode
    base_variables = [
        "pdq_1a", "pdq_1b", "pdq_1c", "pdq_1d", "pdq_1e", "pdq_1f", "pdq_1g", "pdq_1h",
        "pdq_2a", "pdq_2b", "pdq_2c", "pdq_2d", "pdq_2e", "pdq_2f", "pdq_2g", "pdq_2h",
        "pdq_2ht", "pdq_3a", "pdq_3b", "pdq_3c", "pdq_3d", "pdq_3e",
        "pdq_4a", "pdq_4b", "pdq_4c", "pdq_4d", "pdq_4e", "pdq_4f", "pdq_4g", "pdq_4h",
        "pdq_4i", "pdq_4it", "pdq_2i", "pdq_2it", "pdq_2j", "pdq_4j"
    ]

    # Recode 97 and 98 as 99 in 5-Year dataset
    for var in base_variables:
        var_with_suffix = var + "_5yr"
        if var_with_suffix in df_hmz_sdoh_bprhs_5.columns:
            df_hmz_sdoh_bprhs_5[var_with_suffix] = df_hmz_sdoh_bprhs_5[var_with_suffix].astype(str).str.strip()
            df_hmz_sdoh_bprhs_5[var_with_suffix] = df_hmz_sdoh_bprhs_5[var_with_suffix].apply(
                lambda x: 99 if x in ['97', '98'] else x
            )

    # Recode options in 'pdq_2j_5yr': 1→0, 2→1, 3→2, 4→3
    df_hmz_sdoh_bprhs_5['pdq_2j_5yr'] = df_hmz_sdoh_bprhs_5['pdq_2j_5yr'].replace({
        1: 0, 2: 1, 3: 2, 4: 3
    })

    # Recode options in 'pdq_4j_5yr': 1→0, 2→1, 3→2, 4→3
    df_hmz_sdoh_bprhs_5['pdq_4j_5yr'] = df_hmz_sdoh_bprhs_5['pdq_4j_5yr'].replace({
        1: 0, 2: 1, 3: 2, 4: 3
    })

    # Save the transformed DataFrame
    df_hmz_sdoh_bprhs_5.to_csv('data/intermediate/df_hmz_sdoh_bprhs_5.csv', index=False)



    # Transformation 2: Categorizing the text variables

    #pdq_4it_5yr

    discrimination_reasons = {
        'Physical or Health-Related Conditions': [
            'Debido a que sufre de Epilepcia', 'serious vision problems', 'debido a que usaba la mano izquierda',
            'Por problemas con la audicion.', 'Se burlaban de ella por su nombre.',
            'Era mas grande que los otros ninos de la escuela y se burlaban de el.',
            'por que era la mas alta en la escuela y se burlaban de ella', 'se burlaban por su empedimento en la pierna'
        ],
    
        'Bullying & Harassment': [
            'Bulling', 'Los ninos en la escuela le ponian sobrenombres', 'Los ninos de la escuela la maltrataban',
            'Era pesado con ella.', 'Acoso sexual en el trabajo', 
            'her teacher in school was mean and abusive to all of the children', 
            'her husband treated her badly because she wasn\'t smart and didn\'t go to school',
            'Fue golpeada por otros ninos.', 'Pensaba que ella era tonta, pero ella enseno su caracter.',
            'in school the girls were jealous of her about boys', 'people were jealous of her at school'
        ],
    
        'Work-Related Issues': [
            'miscommunication at work', 'Por bruta (no seguia instrucciones)', 'Por preferencia a otras personas.',
            'por cambio de posicion en el trabajo.', 'work related problems',
            'Por que aveces los jefes quiere que las personas trabajen a su manera.', 'Por abusadores, trabajaba mas que los otros.',
            'Abuso de poder del jefe.', 'Los maestro tenian preferencia.', 'Miedo Profesional.',
            'Por favoritismo', 'Tuvo una companera que era envidiosa.', 'Dudaron de su capacidad como maestra',
            'porque no se llevaba con su companero de trabajo'
        ],
    
        'Social & Personal Conflicts': [
            'people think that they know more or are smarter than her', 'people thinking they are better than her and want to take advantage',
            'Por enviadias', 'Por que la gente hablaba cosas malas de ella.', 'porque no aprendia rapido las clases.',
            'por que tienen mala actitud con la Sra.', 'Por ignorancia', 'Por que era pobre y por su apariencia.',
            'confrontational and attitude', 'Por la actitud.', 'personal reasons within relationships',
            'strong character started fights', 'Por el caracter de ella, siempre callada.', 'Por la mala actitud de la gente.',
            'Por la forma de hablar en alta voz y ser.', 'Por inmadurez de las personas.', 'ella dice que la gente piensa que esta loca'
        ],
    
        'Family & Domestic Issues': [
            'Su padre lo maltratada y no estaba bien en la escuela.', 'She was sexually and physically abused by her father',
            'because of my parents marital situation', 'her husband treated her badly because she wasn\'t smart and didn\'t go to school',
            'Violencia Domestica'
        ],
    
        'Legal & Authority-Related Issues': [
            'debido a que la conderanaron siendo inocente en un accidente', 'Record legal', 'Por el record.',
            'lo trataron injustamente porque el director de la escuela le djio que perdia el tiempo'
        ],
    
        'Religious or Cultural Beliefs': [
            'Religious Views'
        ],
    
        'Doesn\'t Know / No Specific Reason': [
            'no sabe', 'doesn\'t know', 'Ninguno de los anteriores', 'Fue casualidad que le ocurienron estos eventos.',
            'Nada importante', 'does not know'
        ]
    }

    # Flattening the dictionary for lookup
    discrimination_map = {reason.lower().strip(): category 
                          for category, reasons in discrimination_reasons.items() 
                          for reason in reasons}

    # Function to replace reasons with categories in a DataFrame column
    def map_discrimination_to_category(df, column_name):
        df[column_name] = df[column_name].astype(str).str.lower().str.strip().map(discrimination_map)
        return df

    df_hmz_sdoh_bprhs_5 = map_discrimination_to_category(df_hmz_sdoh_bprhs_5, 'pdq_4it_5yr')


    # Saving
    df_hmz_sdoh_bprhs_5.to_csv('data/intermediate/df_hmz_sdoh_bprhs_5.csv', index=False)

    #pdq_2it_5yr


    discrimination_reasons_2 = {
        'Physical or Health-Related Conditions': [
            'discrimination because she is hiv positive', 'because of her health problem',
            'her health condition'
        ],
    
        'Bullying & Harassment': [
            'people are afraid of getting in trouble of her what will happen to them',
            'Coworker thinks she knows best and everything is her way'
        ],
    
        'Work-Related Issues': [
            'problems with a worker at an establishment'
        ],
    
        'Social & Personal Conflicts': [
            'Subestimacion', 'Subrtimacion', 'jealousy, trying to put others down', 'envy', 
            'por envidia', 'envidia', 'por que es buena gente.', 'the way he speaks and people thinking he is less intelligent',
            'la han menospreciado', 'debido a criticas sobre su manera de ser', 'people are insincere', 
            'Por el caracter', 'Por su caracter.', 'Por la forma de ser, es muy sincera',
            'Por la manera que ella es, en el caracter', 'Por la desconfianza', 'Por ignorancias.',
            'Por la educacion.', 'Por la forma de actual.', 'Por la forma de hablar, la gente pueden pensar que ella dice cosas para ofender.',
            'because people have more education than her', 'because he talks loud and it bothers people',
            'Por que ellos tienen mejores cosas que ella.', 'Mala educacion', 'Malos entendidos'
        ],
    
        'Family & Domestic Issues': [
            'ella dice que su marido le trata injustamente', 'ella dice porque estorbaba en su casa',
            'family matters', 'personal relationship problems', 'Por preferencias familiares',
            'la sujeta no sabe el por que la nieta la a tratado asi'
        ],
    
        'Legal & Authority-Related Issues': [
            'Discriminated by source of income'
        ],
    
        'Religious or Cultural Beliefs': [
            'difference of opinions', 'diferencias en ideas o forma de pensar'
        ],
    
        'Economic or Financial Issues': [
            'Por la situacion economica', 'por lo economico', 'Discriminated by source of income'
        ],
    
        'Doesn\'t Know / No Specific Reason': [
            "doesn't know", "doesnot know", "doesnt know", "No sabe", "no sabe", "don't know", 
            "does now know", "Sin razon especifica", "Ninguna de las anteriores", 
            "Ninguno de los anteriores", "Ninguno de los anteriores aplica", "doesnow't kn"
        ]
    }

    # Flattening the dictionary for lookup
    discrimination_map = {reason.lower().strip(): category 
                          for category, reasons in discrimination_reasons_2.items() 
                          for reason in reasons}

    # Function to replace reasons with categories in a DataFrame column
    def map_discrimination_to_category(df, column_name):
        df[column_name] = df[column_name].astype(str).str.lower().str.strip().map(discrimination_map)
        return df

    df_hmz_sdoh_bprhs_5 = map_discrimination_to_category(df_hmz_sdoh_bprhs_5, 'pdq_2it_5yr')


    df_hmz_sdoh_bprhs_5.to_csv('data/intermediate/df_hmz_sdoh_bprhs_5.csv', index=False)

    # pdq_2ht_5yr

    discrimination_reasons_3 = { 
        'Physical or Health-Related Conditions': [
            'discrimination because she is hiv positive', 'because of her health problem',
            'her health condition'
        ],

        'Bullying & Harassment': [
            'people are afraid of getting in trouble of her what will happen to them',
            'sus hijas la trataban mal'
        ],

        'Work-Related Issues': [
            'Por la posicion del trabajo que tienen.',
            'problems with a worker at an establishment'
        ],

        'Social & Personal Conflicts': [
            'conflicto personal', 'jealousy', 'stressful daily routine make people very tense',
            'way of dress', 'Por que le dice a la gente las cosas en su cara.', 
            'Por ser callada y timida.', 'Por la apariencia.', 'Por la forma que ella mira y como se ve.',
            'family matters', 'because he talks loud and it bothers people',
            'people are insincere', 'difference of opinions', 'personality differences',
            'Por envidia.', 'Por la estatuta.', 'Por que la quiere manipular.',
            'overall problems in relationships with people', 'Por que ellos tienen mejores cosas que ella.',
            'Por que no tuvo mucha educacion.', 'Por que creen que saben mas que el.',
            'personal relationship problems', 'Por que son personas que no saben tratar a la gente.',
            'Por la manera que ella es, en el caracter.', 'Por la desconfianza.',
            'Por que no le presto dinero.', 'Por que tienen mas dinero que el.',
            'Por que la gente se cree superiores a otros.', 'su nieta le a tratado con menos respeto',
            'Por su personalidad', 'Por la manera de hablar, la gente pueden pensar que ella dice cosas para ofender.',
            'La gente son imprudente, dice las cosas por decirlas.'
        ],

        'Economic or Financial Issues': [
            'Por la situacion economica', 'Por lo economico', 'Because she depends on public assitense'
        ],

        'Family & Domestic Issues': [
            'Por preferencias familiares'
        ],

        'Religious or Cultural Beliefs': [
            'Por la crencias religiosas.'
        ],

        'Education & Knowledge-Related Issues': [
            'Por que no tuvo mucha educacion.', 'because people have more education than her',
            'because of your education'
        ],

        'Doesn\'t Know / No Specific Reason': [
            "doesn't know", 'doesnot know', "doesnt know", "No sabe", "no sabe.", "don't know", "does not know"
        ]
    }
    

    # Flattening the dictionary for lookup
    discrimination_map = {reason.lower().strip(): category 
                          for category, reasons in discrimination_reasons_3.items() 
                          for reason in reasons}

    # Function to replace reasons with categories in a DataFrame column
    def map_discrimination_to_category(df, column_name):
        df[column_name] = df[column_name].astype(str).str.lower().str.strip().map(discrimination_map)
        return df

    df_hmz_sdoh_bprhs_5 = map_discrimination_to_category(df_hmz_sdoh_bprhs_5, 'pdq_2ht_5yr')



    # Renaming 
    df_hmz_sdoh_bprhs_5.rename(columns={
        'pdq_1a_5yr': 'hmz_pdq_1a_bprhs_5',
        'pdq_1b_5yr': 'hmz_pdq_1b_bprhs_5',
        'pdq_1c_5yr': 'hmz_pdq_1c_bprhs_5',
        'pdq_1d_5yr': 'hmz_pdq_1d_bprhs_5',
        'pdq_1e_5yr': 'hmz_pdq_1e_bprhs_5',
        'pdq_1f_5yr': 'hmz_pdq_1f_bprhs_5',
        'pdq_1g_5yr': 'hmz_pdq_1g_bprhs_5',
        'pdq_1h_5yr': 'hmz_pdq_1h_bprhs_5',
        'pdq_2a_5yr': 'hmz_pdq_2a_bprhs_5',
        'pdq_2b_5yr': 'hmz_pdq_2b_bprhs_5',
        'pdq_2c_5yr': 'hmz_pdq_2c_bprhs_5',
        'pdq_2d_5yr': 'hmz_pdq_2d_bprhs_5',
        'pdq_2e_5yr': 'hmz_pdq_2e_bprhs_5',
        'pdq_2f_5yr': 'hmz_pdq_2f_bprhs_5',
        'pdq_2g_5yr': 'hmz_pdq_2g_bprhs_5',
        'pdq_2h_5yr': 'hmz_pdq_2h_bprhs_5',
        'pdq_2ht_5yr': 'hmz_pdq_2h_other_bprhs_5',
        'pdq_3a_5yr': 'hmz_pdq_3a_bprhs_5',
        'pdq_3b_5yr': 'hmz_pdq_3b_bprhs_5',
        'pdq_3c_5yr': 'hmz_pdq_3c_bprhs_5',
        'pdq_3d_5yr': 'hmz_pdq_3d_bprhs_5',
        'pdq_3e_5yr': 'hmz_pdq_3e_bprhs_5',
        'pdq_4a_5yr': 'hmz_pdq_4a_bprhs_5',
        'pdq_4b_5yr': 'hmz_pdq_4b_bprhs_5',
        'pdq_4c_5yr': 'hmz_pdq_4c_bprhs_5',
        'pdq_4d_5yr': 'hmz_pdq_4d_bprhs_5',
        'pdq_4e_5yr': 'hmz_pdq_4e_bprhs_5',
        'pdq_4f_5yr': 'hmz_pdq_4f_bprhs_5',
        'pdq_4g_5yr': 'hmz_pdq_4g_bprhs_5',
        'pdq_4h_5yr': 'hmz_pdq_4h_bprhs_5',
        'pdq_4i_5yr': 'hmz_pdq_4i_bprhs_5',
        'pdq_4it_5yr': 'hmz_pdq_4i_other_bprhs_5',
        'pdq_2i_5yr': 'hmz_pdq_2i_bprhs_5',
        'pdq_2it_5yr': 'hmz_pdq_2i_other_bprhs_5',
        'pdq_2j_5yr': 'hmz_pdq_2j_bprhs_5',   
        'pdq_4j_5yr': 'hmz_pdq_4j_bprhs_5'
    }, inplace=True)




    # Saving 
    df_hmz_sdoh_bprhs_5.to_csv('data/intermediate/df_hmz_sdoh_bprhs_5.csv', index=False)


    # --------------------------------------
    # PROSPECT
    # --------------------------------------

    # List of variables to check, recode, and rename
    variables_to_recode = [
        "pdq1a", "pdq1b", "pdq1c", "pdq1d", "pdq1e", "pdq1f", "pdq1g", "pdq1h",
        "pdq2a", "pdq2b", "pdq2c", "pdq2d", "pdq2e", "pdq2f", "pdq2g", "pdq2h",
        "pdq2h1", "pdq3a", "pdq3b", "pdq3c", "pdq3d", "pdq3e", "pdq4a", "pdq4b",
        "pdq4c", "pdq4d", "pdq4e", "pdq4f", "pdq4g", "pdq4h", "pdq4i", "pdq4h1",
        "pdq2i","pdq2j", "pdq4i1", "pdq4j"
    ]

        
    for var in variables_to_recode:
        if var in df_hmz_sdoh_prospect.columns:
            df_hmz_sdoh_prospect[var] = df_hmz_sdoh_prospect[var].replace({96: np.nan, 97: np.nan, 98: np.nan})

      # Saving
    df_hmz_sdoh_prospect.to_csv('data/intermediate/df_hmz_sdoh_prospect.csv', index=False)

        
    # Categorizing
    # pdq4h1

    discrimination_reasons_4 = {'Physical or Health-Related Conditions': [
            'por el vih', 'hiv', 'por ser hiv', 'por ser HIV.', 'the participant is HIV positive',
            'nepotismo y dado su aflicion de HIV', 'por tener espejuelos', 'problema de salud mental',
            'condicion de salud mental', 'condicion fisica', 'por discapacidad', 'impedimento',
            'impedimento.', 'por condición médica', 'por condición medica.', 'por condición medica, favoritismo, por falta de empatía',
            'por condición de salud mental', 'porque los niños la molestaban sin razón', 'condiciones medicas',
            'por su problema de audición.', 'problemas con la autoridad o con seguir ordenes dadas',
            'problemas de salud-depresion', 'condición médica', 'diagnóstico medico', 'razones de salud',
            'health issues', 'situación de salud', 'problemas de salud', 'condición socioeconómica y salud',
            'debido a su diagnóstico de VIH', 'condición de salud en el trabajo'
        ],
    
        'Bullying & Harassment': [
            'bullying', 'bullying y prepotencia', 'bullying en la escuela', 'bullying de niños',
            'bullying y problemas laborales', 'bullying y envidia', 'bullying y tacticas de abogados',
            'bullying en la escuela', 'bulling en la escuela', 'bullying, diferencias laborales',
            'sobrenombres', 'acoso', 'acoso en la escuela por ser estudiosa.', 'acoso de niño',
            'preferencia de maestros a estudiantes', 'abuso de poder (gerente)', 'abuso de poder',
            'tratan de minimizar a la participante', 'celos academicos'
        ],

        'Work-Related Issues': [
            'work issues', 'nepotismo en su área de trabajo.', 'hostigamiento, más trabajo por igual paga',
            'trabajo: personas malintencionadas', 'laboral conditions', 'malas condiciones laborales.',
            'trabajo de ventas.', 'problemas laborales con situaciones interinas', 'maltrato en el sistema de salud',
            'explotacion laboral', 'conflicto en el trabajo', 'puesto de trabajo y política', 
            'competencia laboral; agencias gubernamentales la trataron como si fuera deshonesta y negligente..',
            'su actitud.', 'conflicto en el trabajo como directora en empleo anterior',
            'en el empleo, por excederse en sus responsabilidades.', 'condición de salud en el trabajo',
            'presión social por parte de amistades', 'por su posicion en el trabajo', 'injusticias en proceso de vivienda',
            'supervisora queria que hicieran las cosas tal y como ella decia', 'los demás se creían mejores. que la participante.'
        ],

        'Social & Personal Conflicts': [
            'subestimacion', 'subrtimacion', 'por envidia', 'envidia', 'celos profesionales', 'celos profesionales en el trabajo',
            'competencia', 'inteligencia percibida en la escuela(competencia) participante tiene un gemela',
            'porque te ven como competencia', 'su actitud.', 'por la manera de ser', 'actitud general', 
            'por su carácter.', 'problemas personales.', 'por probatoria', 'por su problema de audición.',
            'actitudes', 'actitud.', 'personalidad jovial.', 'falta de madurez', 'presión social',
            'envidia y celos', 'celos profesionales, religion.', 'diferencias en la sociedad', 'competencia entre profesionales',
            'porque decian que era nerd', 'envy', 'competencia profesional', 'personalidad, chisme del trabajo',
            'en el parto no dejaron que se pegara a su bebé.', 'envidia profesional.', 'falta de madurez (trabajo)/ medico (trato no profesional)'
        ],

        'Family & Domestic Issues': [
            'familiares', 'personal relationship problems', 'problemas familiares', 'por su desesperacion',
            'familiares', 'situaciones familiares', 'su prioridad son sus hijos y no le respetaban por eso',
            'porque no le dieron oportunidad de vivir en un apartamento', 'porque no le dieron oportunidad de vivir en un apartamento'
        ],

        'Legal & Authority-Related Issues': [
            'personal issues with police men', 'burocracia gubernamental.', 'burocracia del departamento de educacion',
            'el patrono obstaculizó sus visitas al fondo de seguro del estado por lesión en el empleo',
            'discriminado en el tribunal por problema en trabajo', 'injusticia', 'situaciones políticas',
            'problemas con abogado de la otra parte', 'razones políticas.', 'razones de salud',
            'injusticia familiar', 'secuestro infantil', 'impericia medica', 'despido injustificado',
            'injusticias en proceso de vivienda', 'razones políticas.', 'razones politicas.', 'razones políticas.',
            'presión social por parte de amistades'
        ],

        'Religious or Cultural Beliefs': [
            'religion', 'religion y apariencia fisica', 'religious views', 'creencias religiosas', 
            'afiliaciones religiosas', 'religión'
        ],

        'Economic or Financial Issues': [
            'por la situación económica', 'por lo económico', 'estatus socioeconómico', 'status social',
            'discriminado por el ingreso', 'estatus socioeconómico.', 'por ingresos', 'situaciones económicas y condiciones de salud',
            'nivel económico, condiciones médicas', 'discriminacion por estatus socioeconomico'
        ],

        'Political Beliefs & Affiliations': [
            'politica', 'política', 'situación política', 'por razones politicas', 'political affiliations',
            'political differences', 'diferencias politicas', 'afiliación política', 'posturas politicas',
            'motivos ideológicos.', 'afiliaciones políticas'
        ],

        'Doesn\'t Know / No Specific Reason': [
            "doesn't know", "no sabe", "no sabe.", "doesnot know", "doesn't know.", "doesn't know the reason.",
            "does not know", "sin razón específica", "ninguna de las anteriores", "ninguno de los anteriores", 
            "ninguno de los anteriores aplica", "no especificó"
        ],

        'Physical Appearance': [
            'por su rostro', 'por la ropa que tenia puesta', 'por el pelo', 'apariencia física',
            'fisico', 'por apariencia', 'por apariencia.', 'her physical appearance and she demanded respect',
            'la participante fue discriminada por su físico cuando estuvo en sexto grado.',
            'aspecto fisico', 'deformación en la boca', 'apariencia', 'por nariz', 'peso'
        ],

        'Education & Intellectual Capacity': [
            'he was not a good student', 'subestimaron su capacidad', 'subestimaron su capacidad',
            'sentimientos de superioridad debido a sus niveles de educación', 'nivel de estudios.',
            'competencia profesional', 'porque los niños la molestaban sin razón', 'nivel educativo',
            'prejuicio por nivel educativo', 'por sus notas.', 'por las notas', 'menosprecio a maestros de educación física',
            'educación'
        ],

        'Housing & Social Status': [
            'vivienda', 'vivían en casa grande. Tenían dinero.', 'situación socioeconómica.',
            'por ser del barrio y por su condición de vih', 'estatus socioeconómico', 'estatus social',
            'clases sociales', 'clase social', 'condición socioeconómica.'
        ],

        'Workplace Environment': [
            'work related environment', 'situaciones laborales', 'condiciones laborales.', 'situaciones de trabajo',
            'problemas en el trabajo', 'presión en el trabajo', 'conflictos laborales', 'condiciones de empleo'
        ]}




    # Flattening the dictionary for lookup
    discrimination_map = {reason.lower().strip(): category 
                          for category, reasons in discrimination_reasons_4.items() 
                          for reason in reasons}

    # Function to replace reasons with categories in a DataFrame column
    def map_discrimination_to_category(df, column_name):
        df[column_name] = df[column_name].astype(str).str.lower().str.strip().map(discrimination_map)
        return df

    df_hmz_sdoh_prospect= map_discrimination_to_category(df_hmz_sdoh_prospect, 'pdq4h1')





    # pdq4i1
    discrimination_reasons_5 = {
        'Physical or Health-Related Conditions': [
            'condition de salud mental', 'problemas de salud-depresion', 'por condición médica',
            'condiciones de salud', 'condicion de salud', 'por condición medica, favoritismo, por falta de empatía',
            'por condición de salud mental', 'su condición', 'razones médicas.', 'impericia medica',
            'por su discapacidad', 'impedimento y sexo', 'por espejuelos', 'atencion medica: servicio no profesional, escuela: maestros y estudiantes bulleaban a participante, trabajo: aprovechaban de poder'
        ],

        'Bullying & Harassment': [
            'bullying', 'bullying y prepotencia', 'bullying en la escuela', 'bullying y problemas laborales',
            'bullying y tácticas de abogados', 'bullying en la escuela', 'bullying y prepotencia',
            'acoso', 'acoso en la escuela por ser estudiosa.', 'sobrenombres', 'celos de niños, le quitaban la lonchera'
        ],

        'Work-Related Issues': [
            'malas condiciones laborales.', 'conflicto en el trabajo', 'conflicto en el trabajo como directora en empleo anterior',
            'despido injustificado', 'experiencia laboral', 'celos profesionales en el trabajo.', 'por ser nueva en el empleo.',
            'por ser nueva en el empleo.', 'preferencias laborales', 'lo sobrecargaban de tareas en el trabajo.',
            'problemas con abogado de la otra parte', 'falta de madurez (trabajo)/ medico (trato no profesional)',
            'ambiente laboral disfuncional', 'jefe lo humillaba porque si'
        ],

        'Social & Personal Conflicts': [
            'envy', 'celos profesionales', 'celos profesionales en el trabajo.', 'celos profesionales.',
            'choque de personalidades', 'personalidad, chisme del trabajo', 'su actitud.', 'forma de ser',
            'prepotencia de la otra parte', 'mentiras de otras personas', 'personalidad jovial.', 'complejo',
            'envidia laboral', 'envidia', 'envidia', 'celos profesionales, religion.', 'celos en su trabajo',
            'los demás se creían mejores. que la participante.', 'participante no desea desglosar razón'
        ],

        'Family & Domestic Issues': [
            'de parte de su ex esposo (padres de sus hijas)', 'injusticia familiar', 'su prioridad son sus hijos y no le respetaban por eso',
            'familiares', 'problemas personales con hija de maestra', 'su condición de su hijo'
        ],

        'Legal & Authority-Related Issues': [
            'discriminado en el tribunal por problema en trabajo', 'problema en tribunales por no tener buen abogado',
            'demanda', 'razón laboral', 'afiliación política', 'política', 'política', 'razones políticas.',
            'razones politicas.', 'afiliaciones políticas', 'posturas políticas', 'diferencias laborales'
        ],

        'Religious or Cultural Beliefs': [
            'religion', 'religion y apariencia fisica', 'religious views', 'creencias religiosas',
            'religión', 'por condiciones mentales de su familiares.', 'afiliación política'
        ],

        'Economic or Financial Issues': [
            'status social', 'social status', 'clase social', 'clases sociales', 'condición socioeconómica',
            'nivel económico, condiciones médicas', 'razones económicas', 'por ingreso', 'por tener plan medico del gobierno',
            'por donde vive.', 'discriminacion por estatus socioeconomico', 'pobreza, carácter difícil.',
            'estatus social'
        ],

        'Political Beliefs & Affiliations': [
            'political affiliations', 'political differences', 'política', 'afiliaciones políticas',
            'afiliación política', 'razones políticas.', 'posturas políticas', 'situaciones políticas'
        ],

        'Doesn\'t Know / No Specific Reason': [
            "no sabe", "no sabe.", "doesn't know", "doesn't know.", "no puede determinar una razón en específico"
        ],

        'Physical Appearance': [
            'fisico', 'apariencia física', 'por apariencia física ("fea").', 'por su apariencia',
            'apariencia.', 'por espejuelos', 'estatura', 'estatura baja.', 'manera en la que caminaba'
        ],

        'Education & Intellectual Capacity': [
            'prejuicio por nivel educativo.', 'nivel de estudio.', 'menosprecio a maestros de educación física',
            'educación', 'potencial laboral e intelectivo', 'formación académica'
        ],

        'Housing & Social Status': [
            'por donde vive.', 'estatus socioeconómico', 'discriminacion por estatus socioeconomico',
            'clases sociales', 'status social'
        ],

        'Workplace Environment': [
            'trabajo relacionado con ambiente laboral.', 'situaciones laborales', 'condiciones laborales.', 'problemas en el trabajo'
        ]
    }




    # Flattening the dictionary for lookup
    discrimination_map = {reason.lower().strip(): category 
                          for category, reasons in discrimination_reasons_5.items() 
                          for reason in reasons}

    # Function to replace reasons with categories in a DataFrame column
    def map_discrimination_to_category(df, column_name):
        df[column_name] = df[column_name].astype(str).str.lower().str.strip().map(discrimination_map)
        return df


    df_hmz_sdoh_prospect= map_discrimination_to_category(df_hmz_sdoh_prospect, 'pdq4i1')




    #'pdq2h1'

    discrimination_reasons_6 = {
        'Physical or Health-Related Conditions': [
            'Problema de salud mental', 'Condicion de HIV', 'facultades mentales',
            'Condición de salud en trabajo', 'Condición médica', 'por su problema de audición.',
            'Condicion medica', 'Incapacidad', 'Por Su salud mental (Depresion)', 
            'Por problemas de audición', 'Concicion medica', 'por enfermedad', 
            'Por condiciÃ³n mÃ©dico', 'Condiciones médicas, nivel de educación formal',
            'Problemas de salud-depresion', 'por condición médica', 
            'Por condición de salud mental', 'Su condicion'
        ],

        'Bullying & Harassment': [
            'hostigamiento, acercamiento impropio', 'hostigamiento sexual cibernetico',
            'Acoso en el empleo'
        ],

        'Work-Related Issues': [
            'work conditions', 'trabajo', 'competencias laborales', 'work related environment',
            'Contexto de trabajo', 'Relaciones interpersonales en el trabajo', 
            'Situación laboral', 'Asunto Laboral', 'Por la posicion de autoridad.',
            'Competencia laboral.', 'Posición de autoridad en el empleo',
            'Puesto de trabajo y política', 'Desacuerdo en el trabajo', 'Celos Laborales',
            'Colegas creen ser superiores en su trabajo', 'Falta de profesionalismo laborar por otros compañeros',
            'Participante indicó que cuando hace manualidades con otra persona.', 
            'Experiencia laboral', 'Porque es mamá y ama de casa; piensan que no tiene educación.',
            'Conflicto laboral', 'aspectos laborales'
        ],

        'Social & Personal Conflicts': [
            'conflicto personal', 'jealousy', 'stressful daily routine make people very tense',
            'way of dress', 'Por ser callada y timida.', 'Por la apariencia.', 
            'Porque es mamÃ¡ y ama de casa; piensan que no tiene educaciÃ³n.', 
            'Diferencias de criterio', 'Por la custodia', 'La hostigo ex-pareja de una pareja de la parcipante', 
            'Relaciones interpersonales en el trabajo', 'por ser madre y no tener disponibilidad suficiente', 
            'porque quizas se ve ingenua', 'Relaciones con el vecino', 'conflicto con supervisor', 
            'Envidia', 'Jealousy', 'Situaciones personales', 'Modus operandi del participante, relaciones interpersonales',
            'confrontaciones Familiares', 'Situaciones personales', 'Personalidad y/o carácter'
        ],

        'Economic or Financial Issues': [
            'Por la situacion economica', 'Estatus socioeconómico', 'estatus socioeconomico', 
            'Estatus economico', 'Situacion economica', 'Problemas economicos', 
            'Estatus socioeconómico'
        ],

        'Family & Domestic Issues': [
            'Familiares', 'problemas familiares', 'confrontaciones Familiares', 'Problema conyugales'
        ],

        'Religious or Cultural Beliefs': [
            'Religion', 'Creencias religiosas', 'religion y forma de vestir'
        ],

        'Education & Knowledge-Related Issues': [
            'Preparación académica', 'Preparacion academica', 'nivel de educación formal', 
            'Personas con más estudios formales.', 'Preparacion academica y Exponer opinion en un asunto sociopolitico'
        ],

        'Disability & Physical Appearance': [
            'Apariencia física', 'por discapacidad', 'trato distinto por su apariencia',
            'Apariencia representar poco dinero', 'Por apariencia física', 'por mi apariencia',
            'Impedimento', 'Problema de salud mental'
        ],

        'Political Issues & Affiliations': [
            'ideología politica', 'Creencia politica', 'Afiliaciones Políticas', 
            'Posturas politicas', 'Política', 'Politics'
        ],

        'Doesn\'t Know / No Specific Reason': [
            "doesn't know", 'doesnot know', "doesnt know", "No sabe", "no sabe.", "don't know", "does not know"
        ]
    
    }

    # Flattening the dictionary for lookup
    discrimination_map = {reason.lower().strip(): category 
                          for category, reasons in discrimination_reasons_6.items() 
                          for reason in reasons}

    # Function to replace reasons with categories in a DataFrame column
    def map_discrimination_to_category(df, column_name):
        df[column_name] = df[column_name].astype(str).str.lower().str.strip().map(discrimination_map)
        return df


    df_hmz_sdoh_prospect = map_discrimination_to_category(df_hmz_sdoh_prospect, 'pdq2h1')



    # pdq2i1

    discrimination_reasons_7 = {
        'Physical or Health-Related Conditions': [
            'Por condición de salud mental',
            'Condiciones médicas',
            'Condición médica',
            'Por Su salud mental (Depresion)',
            'Condiciones de salud',
            'Problema de salud mental',
            'Por ser coja',
            'Due to illness',
            'enfermedad',
            'Discrimen por ser positivo a VIH.',
            'por su pierna/discapacidad',
            'Por estar en probatoria',
            'Por ser diagnosticado con bipolaridad',
            'Por su impedimento.',
            'Debido a sus aparatos de audicion',
            'Razones de salud',
            'Condicion medica',
            'Condicion de salud'
        ],

        'Bullying & Harassment': [
            'hostigamiento, acercamiento impropio',
            'hostigamiento sexual cibernetico',
            'A mi pasado',
            'La gente quiere aparentar algo que no son',
            'Mal carácter del supervisor.',
            'acoso laboral',
            'Abuso de poder en el empleo.'
        ],

        'Work-Related Issues': [
            'Asunto Laboral',
            'En el empleo, por excederse en sus responsabilidades.',
            'Ocupación/nivel académico',
            'Position laboral',
            'Situacion laboral',
            'Problemas laborales',
            'Contexto de trabajo',
            'work conditions',
            'Trabajo',
            'Empleo',
            'Laboral',
            'situacion personal en trabajo',
            'aspectos laborales',
            'Situaciones en la calle',
            'Colegas creen ser superiores en su trabajo',
            'Falta de profesionalismo laborar por otros compañeros',
            'Modus operandi del participante, relaciones interpersonales',
            'Relaciones interpersonales en trabjo',
            'work related environment'
        ],

        'Social & Personal Conflicts': [
            'Envy',
            'apariencia',
            'Apariencia',
            'Expresion',
            'Actitud',
            'Honestidad',
            'Politica',
            'Posturas politicas',
            'Ideologías distintas',
            'Por ser del campo',
            'Por su forma de ser',
            'por educar a sus hijos en su casa',
            'condition de su hijo',
            'Por manera de pensar',
            'Ignorancias de la jefa',
            'Participant´s temper',
            'Mi hermana',
            'Por la custodia',
            'Las otras personas tienen sus problemas y se desquitan',
            'es muy tranquila',
            'Because of the confidence she portrays',
            'Muestra mucha seguridad en si misma.',
            'arrogancia de otras personas',
            'no familiar',
            'Family issues',
            'Apariencias',
            'No pertenezco al grupo',
            'Por ser madre soltera',
            'Por personalidad',
            'Issues that other people have',
            'Temper',
            'Por exceso de confianza, burla',
            'Discusiones del momento',
            'Falta de respeto',
            'Tono de voz',
            'Forma de ser',
            'Por las cosas que han pasado en la vida',
            'Forma de ser, honestidad',
            'Hijo fastidia mucho',
            'Confrontaciones familiares',
            'Situaciones personales',
            'Acento de voz',
            'Situacion personal',
            'Profesion',
            'No estar de acuerdo con situaciones',
            'Falta de educacion de otras personas',
            'Celos',
            'Peleas de vecino',
            'problemas con vecino por uso de careterras',
            'La gente no es empatica',
            'Sus pocos recursos economicos.',
            'Ha estado preso',
            'Desconocimiento',
            'Tiene un carácter fuerte',
            'Por pintarse las uñas',
            'Situacion familiar',
            'Personalidad.',
            'Celos profesionales.',
            'en el trabajo',
            'Por no estar enterada de algún acontecimiento.',
            'la misma razon',
            'Sentimientos de rechazo debido a sus opiniones',
            'La hostigo ex-pareja de una pareja de la participante',
            'Por mi forma de ser',
            'mal interpretacion del tono de voz natural del participante',
            'caracter',
            'Ignorancia',
            'Jealousy',
            'por sincera',
            'Inseguridad de la otra persona',
            'Diferentes puntos de vista',
            'hermana celosa por cosas del pasado'
        ],

        'Economic or Financial Issues': [
            'situacion economica',
            'Problemas economicos',
            'Estatus economico',
            'estatus socioeconomico',
            'Por experiencia',
            'razon economica'
        ],

        'Family & Domestic Issues': [
            'cuido de otro',
            'Confrontaciones familiares',
            'Situacion familiar',
            'Malas crianzas de su hijo',
            'Family issues'
        ],

        'Religious or Cultural Beliefs': [
            'Religion',
            'Religión',
            'Creencias religiosas',
            'Religiones'
        ],

        'Education & Knowledge-Related Issues': [
            'Educacion',
            'por educación',
            'grado académico',
            'Preparación Academica',
            'Personas con más estudios formales.',
            'Hay personas que piensan que son mejores por tener muchos diplomas académicos.',
            'Preparación académica',
            'Escolaridad',
            'Preparacion academica'
        ],

        'Disability & Physical Appearance': [
            'Por su apariencia',
            'vestimenta',
            'Apariencia fisica',
            'por tatuajes',
            'Tatuajes',
            'por su pierna/discapacidad',
            'Discriminacion por estatus socioeconomico',
            'discapacidad',
            'Incapacidad'
        ],

        'Political Issues & Affiliations': [
            'Politics',
            'ideología politica',
            'Politica',
            'Posturas politicas'
        ],

        'Doesn\'t Know / No Specific Reason': [
            'Participant no desea desglosar razon',
            'Participante indica que simplemente hay gente así',
            'No sabe porque.'
        ]
    }
    # Flattening the dictionary for lookup
    discrimination_map = {reason.lower().strip(): category 
                          for category, reasons in discrimination_reasons_7.items() 
                          for reason in reasons}

    # Function to replace reasons with categories in a DataFrame column
    def map_discrimination_to_category(df, column_name):
        df[column_name] = df[column_name].astype(str).str.lower().str.strip().map(discrimination_map)
        return df


    df_hmz_sdoh_prospect = map_discrimination_to_category(df_hmz_sdoh_prospect, 'pdq2i1')




    # Renaming 
    df_hmz_sdoh_prospect.rename(columns={
        'pdq1a': 'hmz_pdq_1a_prospect',
        'pdq1b': 'hmz_pdq_1b_prospect',
        'pdq1c': 'hmz_pdq_1c_prospect',
        'pdq1d': 'hmz_pdq_1d_prospect',
        'pdq1e': 'hmz_pdq_1e_prospect',
        'pdq1f': 'hmz_pdq_1f_prospect',
        'pdq1g': 'hmz_pdq_1g_prospect',
        'pdq1h': 'hmz_pdq_1h_prospect',
        'pdq2a': 'hmz_pdq_2a_prospect',
        'pdq2b': 'hmz_pdq_2b_prospect',
        'pdq2c': 'hmz_pdq_2c_prospect',
        'pdq2d': 'hmz_pdq_2d_prospect',
        'pdq2e': 'hmz_pdq_2e_prospect',
        'pdq2f': 'hmz_pdq_2f_prospect',
        'pdq2g': 'hmz_pdq_2g_prospect',
        'pdq2h': 'hmz_pdq_2h_prospect',
        'pdq2h1': 'hmz_pdq_2h_other_prospect',
        'pdq3a': 'hmz_pdq_3a_prospect',
        'pdq3b': 'hmz_pdq_3b_prospect',
        'pdq3c': 'hmz_pdq_3c_prospect',
        'pdq3d': 'hmz_pdq_3d_prospect',
        'pdq3e': 'hmz_pdq_3e_prospect',
        'pdq4a': 'hmz_pdq_4a_prospect',
        'pdq4b': 'hmz_pdq_4b_prospect',
        'pdq4c': 'hmz_pdq_4c_prospect',
        'pdq4d': 'hmz_pdq_4d_prospect',
        'pdq4e': 'hmz_pdq_4e_prospect',
        'pdq4f': 'hmz_pdq_4f_prospect',
        'pdq4g': 'hmz_pdq_4g_prospect',
        'pdq4h': 'hmz_pdq_4h_prospect',
        'pdq4i': 'hmz_pdq_4i_prospect',
        'pdq4i1': 'hmz_pdq_4i_other_prospect',
        'pdq2i': 'hmz_pdq_2i_prospect',
        'pdq2j': 'hmz_pdq_2j_prospect',
        'pdq2i1': 'hmz_pdq_2i_other_prospect',
        'pdq4j': 'hmz_pdq_4j_prospect'
    }, inplace=True)




    # Saving
    df_hmz_sdoh_prospect.to_csv('data/intermediate/df_hmz_sdoh_prospect.csv', index=False)



    #------------------------------------------------------------------------------------------------
    #  Food Security 
    # -----------------------------------------------------------------------------------------------


    # --------------------------------------
    # BPRHS
    # --------------------------------------

    base_variables = ["fss1", "fss1a1", "fss1a2", "fss1a3", "fss1a4", "fss1a5", "fss1a6","fss1b1","fss1b3","fss1b4","fss1b5","fss2","fss3","fss4",
                      "fss5","fss5a","fss6","fss7","fss8","fss9","fss9a"] 



    # only exists in 8 year
    # but some of these variables do not have data
    # fss2_8yr count: 0
    #fss3_8yr count: 0
    #fss4_8yr count: 0
    #fss5_8yr count: 0
    #fss5a_8yr count: 0
    #fss6_8yr count: 0
    #fss7_8yr count: 0
    #fss8_8yr count: 0
    #fss9_8yr count: 0
    #fss9a_8yr count: 0

    # Recoding no answer in 8-Year dataset
    for var in base_variables:
        var_with_suffix = var + "_8yr"  # Add _8yr suffix for the 8-Year dataset variables
        if var_with_suffix in df_hmz_sdoh_bprhs_8.columns:
            df_hmz_sdoh_bprhs_8[var_with_suffix] = df_hmz_sdoh_bprhs_8[var_with_suffix].apply(
                lambda x: int(x.strip()) if isinstance(x, str) and x.strip().isdigit() else x
            )
            df_hmz_sdoh_bprhs_8[var_with_suffix] = df_hmz_sdoh_bprhs_8[var_with_suffix].replace({
                96: np.nan, 97: np.nan, 98: np.nan
            })


    # Renaming 
    df_hmz_sdoh_bprhs_8.rename(columns={
    'fss1_8yr': 'hmz_fss1_bprhs_8',
    'fss1a1_8yr': 'hmz_fss1a1_bprhs_8',
    'fss1a2_8yr': 'hmz_fss1a2_bprhs_8',
    'fss1a3_8yr': 'hmz_fss1a3_bprhs_8',
    'fss1a4_8yr': 'hmz_fss1a4_bprhs_8',
    'fss1a5_8yr': 'hmz_fss1a5_bprhs_8',
    'fss1a6_8yr': 'hmz_fss1a6_bprhs_8',
    'fss1b1_8yr': 'hmz_fss1b1_bprhs_8',
    'fss1b3_8yr': 'hmz_fss_time_shopping_bprhs_8',
    'fss1b4_8yr': 'hmz_fss_store_bprhs_8',
    'fss1b5_8yr': 'hmz_fss_diet_bprhs_8'
                                                                   
     }, inplace=True)


        
    # Saving
    df_hmz_sdoh_bprhs_8.to_csv('data/intermediate/df_hmz_sdoh_bprhs_8.csv', index=False)


    # --------------------------------------
    # PROSPECT
    # --------------------------------------

    variables_to_recode = ["fss1", "fss1a_1", "fss1a_2", "fss1a_3", "fss1a_4", "fss1a_5", "fss1a_6",
                           "fss1b_1", "fss1b_2", "fss1b_3", "fss1b_4", "fss2", "fss3", "fss4", "fss5",
                           "fss5a", "fss6", "fss7", "fss8", "fss9", "fss9a"]


    for var in variables_to_recode:
        if var in df_hmz_sdoh_prospect.columns:
            df_hmz_sdoh_prospect[var] = df_hmz_sdoh_prospect[var].replace({96: np.nan, 97: np.nan, 98: np.nan})


    # Renaming 
    df_hmz_sdoh_prospect.rename(columns={
        "fss1": 'hmz_fss1_prospect',
        'fss1a_1': 'hmz_fss1a1_prospect',
        'fss1a_2': 'hmz_fss1a2_prospect',
        'fss1a_3': 'hmz_fss1a3_prospect',
        'fss1a_4': 'hmz_fss1a4_prospect',
        'fss1a_5': 'hmz_fss1a5_prospect',
        'fss1a_6': 'hmz_fss1a6_prospect',
        'fss1b_1': 'hmz_fss1b1_prospect',
        'fss1b_2': 'hmz_fss_time_shopping_prospect',
        'fss1b_3': 'hmz_fss_store_prospect',
        'fss1b_4': 'hmz_fss_diet_prospect',
  
    }, inplace=True)


    # Saving
    df_hmz_sdoh_prospect.to_csv('data/intermediate/df_hmz_sdoh_prospect.csv', index=False)


    #------------------------------------------------------------------------------------------------
    # Neighborhood Community
    # -----------------------------------------------------------------------------------------------


    # --------------------------------------
    # BPRHS
    # --------------------------------------

    # Transformation 1: recoding 97, 98 as nan
    base_variables = ["nfa10c", "nfa10d", "nfa10e", "nfa8u", "nfa8v", "nfa8w", "nfa8y"]

    for var in base_variables:
        var_with_suffix = var + "_5yr"
        if var_with_suffix in df_hmz_sdoh_bprhs_5.columns:
            df_hmz_sdoh_bprhs_5[var_with_suffix] = df_hmz_sdoh_bprhs_5[var_with_suffix].apply(
                lambda x: int(x.strip()) if isinstance(x, str) and x.strip().isdigit() else x)
            df_hmz_sdoh_bprhs_5[var_with_suffix] = pd.to_numeric(df_hmz_sdoh_bprhs_5[var_with_suffix], errors='coerce')
            df_hmz_sdoh_bprhs_5[var_with_suffix] = df_hmz_sdoh_bprhs_5[var_with_suffix].replace({97: np.nan, 98: np.nan})

    # Transformation 2: recoding options 1,2,3,4 as 3,2,1,0
    variables_to_recode = ["nfa10a_5yr", "nfa10b_5yr", "nfa10c_5yr", "nfa10d_5yr", "nfa10e_5yr"]

    for var in variables_to_recode:
        if var in df_hmz_sdoh_bprhs_5.columns:
            df_hmz_sdoh_bprhs_5[var] = df_hmz_sdoh_bprhs_5[var].replace({1: 3, 2: 2, 3: 1, 4: 0})

    # Transformation 3: recoding 1,2,3,4,5 as 5,4,3,2,1
    variables_to_recode = ["nfa8v_5yr", "nfa8y_5yr"]

    for var in variables_to_recode:
        if var in df_hmz_sdoh_bprhs_5.columns:
            df_hmz_sdoh_bprhs_5[var] = pd.to_numeric(df_hmz_sdoh_bprhs_5[var], errors='coerce')
            df_hmz_sdoh_bprhs_5[var] = df_hmz_sdoh_bprhs_5[var].replace({1: 5, 2: 4, 3: 3, 4: 2, 5: 1, 97: np.nan, 98: np.nan})

    # Renaming columns (only those that exist)
    rename_dict = {
        'nfa10a_5yr': 'hmz_nfa_favors_bprhs_5', 
        'nfa10b_5yr': 'hmz_nfa_watch_property_bprhs_5',
        'nfa10c_5yr': 'hmz_nfa_advice_bprhs_5', 
        'nfa10d_5yr': 'hmz_nfa_parties_bprhs_5',
        'nfa10e_5yr': 'hmz_nfa_interactions_bprhs_5',
        'nfa8u_5yr': 'hmz_nfa_close_knit_bprhs_5',
        'nfa8v_5yr': 'hmz_nfa_get_along_bprhs_5',
        'nfa8w_5yr': 'hmz_nfa_trust_bprhs_5',
        'nfa8y_5yr': 'hmz_nfa_values_bprhs_5',
    }

    # Only rename columns that exist in the DataFrame
    df_hmz_sdoh_bprhs_5.rename(columns={k: v for k, v in rename_dict.items() if k in df_hmz_sdoh_bprhs_5.columns}, inplace=True)

    # Saving
    df_hmz_sdoh_bprhs_5.to_csv('data/intermediate/df_hmz_sdoh_bprhs_5.csv', index=False)


    # --------------------------------------
    # PROSPECT
    # --------------------------------------

    variables_to_recode = ["nss44","nss45","nss46", "nss47", "nss48", "nss36", "nss37", "nss38", "nss39"]

    for var in variables_to_recode:
        if var in df_hmz_sdoh_prospect.columns:
            df_hmz_sdoh_prospect[var] = df_hmz_sdoh_prospect[var].replace({96: np.nan, 97: np.nan, 98: np.nan})

    # Renaming 
    df_hmz_sdoh_prospect.rename(columns={
        'nss44': 'hmz_nfa_favors_prospect',
        'nss45': 'hmz_nfa_watch_property_prospect',
        'nss46': 'hmz_nfa_advice_prospect',
        'nss47': 'hmz_nfa_parties_prospect',
        'nss48': 'hmz_nfa_interactions_prospect',
        'nss36': 'hmz_nfa_close_knit_prospect',
        'nss37': 'hmz_nfa_get_along_prospect',
        'nss38': 'hmz_nfa_trust_prospect',
        'nss39': 'hmz_nfa_values_prospect'
    }, inplace=True)


    # Saving
    df_hmz_sdoh_prospect.to_csv('data/intermediate/df_hmz_sdoh_prospect.csv', index=False)





    #------------------------------------------------------------------------------------------------
    # Outdoors, Education, and Sports Facilities in Neighborhood
    # -----------------------------------------------------------------------------------------------


    # --------------------------------------
    # BPRHS
    # --------------------------------------
    base_variables = ["nfa7a", "nfa7b", "nfa7c", "nfa7d", "nfa7e", "nfa7g","nfa7h" "nfa8h"]


    # Processing the bprhs v3
    print("\n5-Year dataset - Variable counts before transformation:")

    for var in base_variables:
        var_with_suffix = var + "_5yr"  # Add _5yr suffix for the 5-Year dataset variables
        if var_with_suffix in df_hmz_sdoh_bprhs_5.columns:
            # Convert to numeric, handling possible string or formatted values
            df_hmz_sdoh_bprhs_5[var_with_suffix] = pd.to_numeric(df_hmz_sdoh_bprhs_5[var_with_suffix], errors='coerce')

            # Recoding 
            df_hmz_sdoh_bprhs_5[var_with_suffix] = df_hmz_sdoh_bprhs_5[var_with_suffix].replace({97: np.nan, 98: np.nan})

    # Saving
    df_hmz_sdoh_bprhs_5.to_csv('data/intermediate/df_hmz_sdoh_bprhs_5.csv', index=False)


    # # Renaming
    df_hmz_sdoh_bprhs_5.rename(columns={
         'nfa7a_5yr': 'hmz_nfa_park_bprhs_5', 
         'nfa7b_5yr': 'hmz_nfa_sports_field_bprhs_5',
         'nfa7c_5yr': 'hmz_nfa_pool_bprhs_5',
         'nfa7d_5yr': 'hmz_nfa_recreational_bprhs_5',
         'nfa7e_5yr': 'hmz_nfa_gym_bprhs_5',
         'nfa7g_5yr': 'hmz_nfa_bicycle_path_bprhs_5',
         'nfa8h_5yr': 'hmz_nfa_exercise_bprhs_5'}, inplace=True)



    # Saving 
    df_hmz_sdoh_bprhs_5.to_csv('data/intermediate/df_hmz_sdoh_bprhs_5.csv', index=False)



    # --------------------------------------
    # PROSPECT
    # --------------------------------------
    variables_to_recode = ["nss49", "nss50", "nss51", "nss52", "nss53", "nss55", "nss10"]

    for var in variables_to_recode:
        if var in df_hmz_sdoh_prospect.columns:
            df_hmz_sdoh_prospect[var] = df_hmz_sdoh_prospect[var].replace({96: np.nan, 97: np.nan, 98: np.nan})



    # Renaming 
    df_hmz_sdoh_prospect.rename(columns={
        'nss49': 'hmz_nfa_park_prospect',
        'nss50': 'hmz_nfa_sports_field_prospect',
        'nss51': 'hmz_nfa_pool_prospect',
        'nss52': 'hmz_nfa_recreational_prospect',
        'nss53': 'hmz_nfa_gym_prospect',
        'nss55': 'hmz_nfa_bicycle_path_prospect',
        'nss10': 'hmz_nfa_exercise_prospect'}, inplace=True)



    # Saving
    df_hmz_sdoh_prospect.to_csv('data/intermediate/df_hmz_sdoh_prospect.csv', index=False)



    #------------------------------------------------------------------------------------------------
    # Household Income
    # -----------------------------------------------------------------------------------------------


    # --------------------------------------
    # BPRHS
    # --------------------------------------

    base_variables = ["hi_tot"]

    bprhs_datasets = {
        "Baseline": (df_hmz_sdoh_bprhs_0, ""),
        "2-Year": (df_hmz_sdoh_bprhs_2, "_2yr"),
        "5-Year": (df_hmz_sdoh_bprhs_5, "_5yr"),
        "8-Year": (df_hmz_sdoh_bprhs_8, "_8yr")}



    # Transformation 1: 97, 98 recoded as np.nan
 
    for name, (df, suffix) in bprhs_datasets.items():
        for var in base_variables:
            variable_name = var + suffix  # Add the suffix to the variable name
            if variable_name in df.columns:
                df[variable_name] = df[variable_name].apply(
                    lambda x: int(x.strip()) if isinstance(x, str) and x.strip().isdigit() else x
                )
                df[variable_name] = df[variable_name].replace({97: np.nan, 98: np.nan})




    # Transformation 2: categorizing
    categories = [
        (0.0, 10000.0), 
        (10000.1, 15000.0),
        (15000.1, 20000.0),
        (20000.1, 25000.0),
        (25000.1, 30000.0),
        (30000.1, 40000.0),
        (40000.1, 50000.0),
        (50000.1, 75000.0),
        (75000.1, 100000.0),
        (100000.1, float('inf'))
    ]

    def assign_category(value):
        if pd.isna(value):
            return np.nan   # Keep it as NaN
        for i, (lower, upper) in enumerate(categories):
            if lower <= value <= upper:
                return i
        return None

    print("\nVariable counts before Transformation 2:")
    for name, (df, suffix) in bprhs_datasets.items():
        for var in base_variables:
            variable_name = var + suffix
            if variable_name in df.columns:
                print(f"{variable_name} counts before Transformation 2:\n{df[variable_name].value_counts().sort_index()}\n")
                df[variable_name] = df[variable_name].apply(assign_category)


    # Renaming 
    df_hmz_sdoh_bprhs_0.rename(columns={'hi_tot': 'hmz_hi_total_bprhs_0'}, inplace=True)
    df_hmz_sdoh_bprhs_2.rename(columns={'hi_tot_2yr': 'hmz_hi_total_bprhs_2'}, inplace=True)
    df_hmz_sdoh_bprhs_5.rename(columns={'hi_tot_5yr': 'hmz_hi_total_bprhs_5', 
    }, inplace=True)
    df_hmz_sdoh_bprhs_8.rename(columns={'hi_tot_8yr': 'hmz_hi_total_bprhs_8'}, inplace=True)




    # Saving
    df_hmz_sdoh_bprhs_0.to_csv('data/intermediate/df_hmz_sdoh_bprhs_0.csv', index=False)
    df_hmz_sdoh_bprhs_2.to_csv('data/intermediate/df_hmz_sdoh_bprhs_2.csv', index=False)
    df_hmz_sdoh_bprhs_5.to_csv('data/intermediate/df_hmz_sdoh_bprhs_5.csv', index=False)
    df_hmz_sdoh_bprhs_8.to_csv('data/intermediate/df_hmz_sdoh_bprhs_8.csv', index=False)


    # --------------------------------------
    # PROSPECT
    # --------------------------------------
    if "whi10" in df_hmz_sdoh_prospect.columns:
        df_hmz_sdoh_prospect["whi10"] = df_hmz_sdoh_prospect["whi10"].replace({96: np.nan, 97: np.nan, 98: np.nan})

    # Renaming 
    df_hmz_sdoh_prospect.rename(columns={'whi10': 'hmz_hi_total_prospect'}, inplace=True)


    # Saving
    df_hmz_sdoh_prospect.to_csv('data/intermediate/df_hmz_sdoh_prospect.csv', index=False)


    #------------------------------------------------------------------------------------------------
    # Migration History
    # -----------------------------------------------------------------------------------------------

    # --------------------------------------
    # BPRHS
    # --------------------------------------
    # Transformation: recoding 

    df_hmz_sdoh_bprhs_0['mh1'] = df_hmz_sdoh_bprhs_0['mh1'].replace({3: 2, 4: 2, 5: 2, 6: 3})

 
    df_hmz_sdoh_bprhs_0.rename(columns={
        'mh1': 'hmz_mh_pob_bprhs_0' }, inplace=True)


    df_hmz_sdoh_bprhs_0.to_csv('data/intermediate/df_hmz_sdoh_bprhs_0.csv', index=False)


    # --------------------------------------
    # PROSPECT
    # --------------------------------------

    # Variables to check
    # Recoding
    df_hmz_sdoh_prospect['mha1'] = df_hmz_sdoh_prospect['mha1'].replace({ 4: 3})

    # Renaming 
    df_hmz_sdoh_prospect.rename(columns={
        "mha1": 'hmz_mh_pob_prospect'}, inplace=True)


    # Saving 
    df_hmz_sdoh_prospect.to_csv('data/intermediate/df_hmz_sdoh_prospect.csv', index=False)

    #------------------------------------------------------------------------------------------------
    # Post-Processing - BPRHS and PROSPECT (Spanish) – SDOH
    #------------------------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------------------------------------
    #  Adding prefix 'hmz_sdoh_' to variables starting with 'hmz_' 
    # ------------------------------------------------------------------------------------------------------------
    datasets_sdoh = {
        "df_hmz_sdoh_bprhs_0": df_hmz_sdoh_bprhs_0,
        "df_hmz_sdoh_bprhs_2": df_hmz_sdoh_bprhs_2,
        "df_hmz_sdoh_bprhs_5": df_hmz_sdoh_bprhs_5,
        "df_hmz_sdoh_bprhs_8": df_hmz_sdoh_bprhs_8,
        "df_hmz_sdoh_prospect": df_hmz_sdoh_prospect}

    for name, df in datasets_sdoh.items():
        df.columns = [f"hmz_sdoh_{col[4:]}" if col.startswith('hmz_') else col for col in df.columns]
        df.to_csv(f"data/intermediate/{name}.csv", index=False)
        

    # ------------------------------------------------------------------------------------------------------------
    #  Adding visit column (bprhs)
    # ------------------------------------------------------------------------------------------------------------
    df_hmz_sdoh_bprhs_0["hmz_visit_bprhs_0"] = df_hmz_sdoh_bprhs_0["studyid"].notna().map({True: "v1", False: None})
    df_hmz_sdoh_bprhs_2["hmz_visit_bprhs_2"] = df_hmz_sdoh_bprhs_2["studyid"].notna().map({True: "v2", False: None})
    df_hmz_sdoh_bprhs_5["hmz_visit_bprhs_5"] = df_hmz_sdoh_bprhs_5["studyid"].notna().map({True: "v3", False: None})
    df_hmz_sdoh_bprhs_8["hmz_visit_bprhs_8"] = df_hmz_sdoh_bprhs_8["studyid"].notna().map({True: "v4", False: None})


    # Saving 
    df_hmz_sdoh_bprhs_0.to_csv('data/intermediate/df_hmz_sdoh_bprhs_0.csv', index=False)
    df_hmz_sdoh_bprhs_2.to_csv('data/intermediate/df_hmz_sdoh_bprhs_2.csv', index=False)
    df_hmz_sdoh_bprhs_5.to_csv('data/intermediate/df_hmz_sdoh_bprhs_5.csv', index=False)
    df_hmz_sdoh_bprhs_8.to_csv('data/intermediate/df_hmz_sdoh_bprhs_8.csv', index=False)
    df_hmz_sdoh_prospect.to_csv('data/intermediate/df_hmz_sdoh_prospect.csv', index=False)

    # ------------------------------------------------------------------------------------------------------------
    # Renaming redcap event --> hmz_visit (prospect)
    # ------------------------------------------------------------------------------------------------------------
    if "redcap_event_name" in df_hmz_sdoh_prospect.columns:
        df_hmz_sdoh_prospect["redcap_event_name"] = df_hmz_sdoh_prospect["redcap_event_name"].replace({
            "baseline_arm_1": "v1",
            "visit_2_arm_1": "v2"})
        df_hmz_sdoh_prospect.rename(columns={"redcap_event_name": "hmz_visit_prospect"}, inplace=True)
        df_hmz_sdoh_prospect.to_csv('data/intermediate/df_hmz_sdoh_prospect.csv', index=False)


    # ------------------------------------------------------------------------------------------------------------
    # Renaming record_id --> hmz_record_id (prospect)
    # ------------------------------------------------------------------------------------------------------------
    if "record_id" in df_hmz_sdoh_prospect.columns:
        print(df_hmz_sdoh_prospect["record_id"].value_counts())
        df_hmz_sdoh_prospect.rename(columns={"record_id": "hmz_record_id_prospect"}, inplace=True)
        print(df_hmz_sdoh_prospect["hmz_record_id_prospect"].value_counts())
        df_hmz_sdoh_prospect.to_csv('data/intermediate/df_hmz_sdoh_prospect.csv', index=False)


    # ------------------------------------------------------------------------------------------------------------ 
    # Keeping only studyid and 'hmz' variables
    # ------------------------------------------------------------------------------------------------------------
    df_hmz_sdoh_bprhs_0 = df_hmz_sdoh_bprhs_0.loc[:, df_hmz_sdoh_bprhs_0.columns.str.startswith('hmz') | (df_hmz_sdoh_bprhs_0.columns == 'studyid')]
    df_hmz_sdoh_bprhs_2 = df_hmz_sdoh_bprhs_2.loc[:, df_hmz_sdoh_bprhs_2.columns.str.startswith('hmz') | (df_hmz_sdoh_bprhs_2.columns == 'studyid')]
    df_hmz_sdoh_bprhs_5 = df_hmz_sdoh_bprhs_5.loc[:, df_hmz_sdoh_bprhs_5.columns.str.startswith('hmz') | (df_hmz_sdoh_bprhs_5.columns == 'studyid')]
    df_hmz_sdoh_bprhs_8 = df_hmz_sdoh_bprhs_8.loc[:, df_hmz_sdoh_bprhs_8.columns.str.startswith('hmz') | (df_hmz_sdoh_bprhs_8.columns == 'studyid')]
    df_hmz_sdoh_prospect = df_hmz_sdoh_prospect[[col for col in df_hmz_sdoh_prospect.columns if col.startswith('hmz_') or col in ['studyid']]]
    
    # saving
    df_hmz_sdoh_bprhs_0.to_csv('data/intermediate/df_hmz_sdoh_bprhs_0.csv', index=False)
    df_hmz_sdoh_bprhs_2.to_csv('data/intermediate/df_hmz_sdoh_bprhs_2.csv', index=False)
    df_hmz_sdoh_bprhs_5.to_csv('data/intermediate/df_hmz_sdoh_bprhs_5.csv', index=False)
    df_hmz_sdoh_bprhs_8.to_csv('data/intermediate/df_hmz_sdoh_bprhs_8.csv', index=False)
    df_hmz_sdoh_prospect.to_csv('data/intermediate/df_hmz_sdoh_prospect.csv', index=False)



    # ------------------------------------------------------------------------------------------------------------
    # Creating PROSPECT visit-specific files
    # ------------------------------------------------------------------------------------------------------------
    # Filering not null studyids
    df_hmz_sdoh_prospect = pd.read_csv("data/intermediate/df_hmz_sdoh_prospect.csv")
    df_hmz_sdoh_prospect = df_hmz_sdoh_prospect[df_hmz_sdoh_prospect["studyid"].notnull()]

    # Visit 1
    df_hmz_sdoh_prospect_visit_1 = df_hmz_sdoh_prospect[df_hmz_sdoh_prospect["hmz_visit_prospect"] == "v1"].copy()
    df_hmz_sdoh_prospect_visit_1.rename(columns={col: f"{col}_v1" for col in df_hmz_sdoh_prospect_visit_1.columns if col != "studyid"}, inplace=True)
    df_hmz_sdoh_prospect_visit_1.rename(columns={"hmz_visit_prospect_v1": "visit"}, inplace=True)
    df_hmz_sdoh_prospect_visit_1.to_csv("data/intermediate/df_hmz_sdoh_prospect_visit_1.csv", index=False)

    # Visit 2
    df_hmz_sdoh_prospect_visit_2 = df_hmz_sdoh_prospect[df_hmz_sdoh_prospect["hmz_visit_prospect"] == "v2"].copy()
    df_hmz_sdoh_prospect_visit_2.rename(columns={col: f"{col}_v2" for col in df_hmz_sdoh_prospect_visit_2.columns if col != "studyid"}, inplace=True)
    df_hmz_sdoh_prospect_visit_2.rename(columns={"hmz_visit_prospect_v2": "visit"}, inplace=True)
    df_hmz_sdoh_prospect_visit_2.to_csv("data/intermediate/df_hmz_sdoh_prospect_visit_2.csv", index=False)

   # ------------------------------------------------------------------------------------------------------------
   # Renaming hmz visit --> visit
   # ------------------------------------------------------------------------------------------------------------
  
    df_hmz_sdoh_bprhs_0.rename(columns={'hmz_visit_bprhs_0': 'visit'}, inplace=True)
    df_hmz_sdoh_bprhs_2.rename(columns={'hmz_visit_bprhs_2': 'visit'}, inplace=True)
    df_hmz_sdoh_bprhs_5.rename(columns={'hmz_visit_bprhs_5': 'visit'}, inplace=True)
    df_hmz_sdoh_bprhs_8.rename(columns={'hmz_visit_bprhs_8': 'visit'}, inplace=True)
    df_hmz_sdoh_prospect_visit_1.rename(columns={'hmz_visit_prospect_v1': 'visit'}, inplace=True)
    df_hmz_sdoh_prospect_visit_2.rename(columns={'hmz_visit_prospect_v2': 'visit'}, inplace=True)


  

    # Saving
    df_hmz_sdoh_bprhs_0.to_csv('data/intermediate/df_hmz_sdoh_bprhs_0.csv', index=False)
    df_hmz_sdoh_bprhs_2.to_csv('data/intermediate/df_hmz_sdoh_bprhs_2.csv', index=False)
    df_hmz_sdoh_bprhs_5.to_csv('data/intermediate/df_hmz_sdoh_bprhs_5.csv', index=False)
    df_hmz_sdoh_bprhs_8.to_csv('data/intermediate/df_hmz_sdoh_bprhs_8.csv', index=False)
    df_hmz_sdoh_prospect_visit_1.to_csv("data/intermediate/df_hmz_sdoh_prospect_visit_1.csv", index=False)
    df_hmz_sdoh_prospect_visit_2.to_csv("data/intermediate/df_hmz_sdoh_prospect_visit_2.csv", index=False)

   


    
    #-------------------------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------------------
    # loading the data: english (only PROSPECT)
    from scripts.load.loader_sdoh import load_sdoh_english_data
    data = load_sdoh_english_data(config)
    df_hmz_sdoh_prospect_english = data['prospect_english']


    # ------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------


    # -------------------------------------------------------------------------------------------------
    # Gender
    # -------------------------------------------------------------------------------------------------

    # Renaming 
    df_hmz_sdoh_prospect_english.rename(columns={'dem3': 'hmz_gender_prospect'}, inplace=True)

    # Saving 
    df_hmz_sdoh_prospect_english.to_csv('data/intermediate/df_hmz_sdoh_prospect_english.csv', index=False)



    # -------------------------------------------------------------------------------------------------
    # Age
    # -------------------------------------------------------------------------------------------------

    # Renaming the variable
    df_hmz_sdoh_prospect_english.rename(columns={'age_calc': 'hmz_age_prospect'}, inplace=True)

    # Ceiling function (function that converts decimal numbers into whole numbers) to hmz_age_prospect
    df_hmz_sdoh_prospect_english['hmz_age_prospect'] = np.ceil(df_hmz_sdoh_prospect_english['hmz_age_prospect'])

    # Saving 
    df_hmz_sdoh_prospect_english.to_csv('data/intermediate/df_hmz_sdoh_prospect_english.csv', index=False)



    # -------------------------------------------------------------------------------------------------
    # Neighborhood Features and Access 
    # -------------------------------------------------------------------------------------------------

    # Combined transformation and renaming
    recode_rename_map = {
        # Transformation 1
        "nss33": "hmz_nfa_violence_prospect",
        "nss34": "hmz_nfa_safety_prospect",
        "nss40": "hmz_nfa_weapon_prospect",
        "nss41": "hmz_nfa_gang_fights_prospect",
        "nss42": "hmz_nfa_assault_prospect",
        "nss43": "hmz_nfa_rob_prospect",
        "nss32": "hmz_nfa_safety_walk_prospect",

        # Transformation 2
        "nss56": "hmz_nfa_sidewalks_prospect",
        "nss14": "hmz_nfa_roads_prospect",
        "nss15": "hmz_nfa_walk_prospect",
        "nss16": "hmz_nfa_stores_prospect",
        "nss17": "hmz_nfa_people_walk_prospect",
        "nss11": "hmz_nfa_pleasant_walk_prospect",
        "nss1": "hmz_nfa_shopping_distance_prospect",
        "nss2": "hmz_nfa_shopping_food_prospect",
        "nss13": "hmz_nfa_traffic_prospect",

        # Transformation 3
        "nss19": 'hmz_nfa_fruits_vegetables_i_prospect',
        "nss20": 'hmz_nfa_fruits_vegetables_ii_prospect',
        "nss21": 'hmz_nfa_fruits_vegetables_iii_prospect',
        "nss22": 'hmz_nfa_lowfat_i_prospect',
        "nss23": 'hmz_nfa_lowfat_ii_prospect',
        "nss24": 'hmz_nfa_lowfat_iii_prospect',
        "nss25": 'hmz_nfa_wholegrain_i_prospect',
        "nss26": 'hmz_nfa_wholegrain_ii_prospect',
        "nss27": 'hmz_nfa_wholegrain_iii_prospect',
        "nss28": 'hmz_nfa_fish_prospect',
        "nss31": 'hmz_nfa_fastfood_prospect'
    }

    for var in recode_rename_map:
        if var in df_hmz_sdoh_prospect_english.columns:
            df_hmz_sdoh_prospect_english[var] = pd.to_numeric(df_hmz_sdoh_prospect_english[var], errors='coerce')
            df_hmz_sdoh_prospect_english[var] = df_hmz_sdoh_prospect_english[var].replace({96: np.nan, 97: np.nan, 98: np.nan})

    # Renaming
    df_hmz_sdoh_prospect_english.rename(columns=recode_rename_map, inplace=True)

    # Saving
    df_hmz_sdoh_prospect_english.to_csv('data/intermediate/df_hmz_sdoh_prospect_english.csv', index=False)


    #------------------------------------------------------------------------------------------------
    # Work History and Income
    # -----------------------------------------------------------------------------------------------


    occupations = {
        1: ["Administrador", "Administradora", "Gerente", "Director", "Directora", "Coordinador", "Coordinadora",
            "Secretaria", "Asistente administrativo", "Analista de presupuesto"],
        2: ["Funcionario ejecutivo", "Policia", "Sargento", "Inspectora de contribuciones", "Oficial administrativo",
            "Catedratico", "Profesor universitario", "Educador en salud", "Abogada", "Abogado"],
        3: ["Enfermera", "Médico", "Farmaceutica", "Doctor", "Tecnologa Medica", "Terapista fisica", "Terapista Respiratoria",
            "Psicologa", "Trabajadora social", "Consejera", "Nutricionista", "Paramédico", "Tecnica oftalmica"],
        4: ["Maestro", "Maestra", "Profesor", "Profesora", "Tutor", "Tutora", "Asistente de maestra", "Educador",
            "Facilitadora Docente", "Trabajadora Social Escolar"],
        5: ["Técnico automotriz", "Técnico de refrigeración", "Electricista", "Tecnico de permisos", "Tecnólogo Médico",
            "Técnica de biblioteca", "Técnico el reparación"],
        6: ["Vendedor", "Ventas", "Cajera", "Call Center", "Servicio al cliente", "Consultora", "Representante de ventas",
            "Agente de Seguros", "Tienda comercial", "Mercadeo"],
        7: ["Empleada doméstica", "Ama de llaves", "Housekeeping", "Cuidadora de envejecientes", "Cuida ancianos",
            "Niñera", "Cuidadora"],
        8: [],  # Armed Services 
        9: ["Agricultura", "Agronomo", "Farming", "Forestry"],
        10: ["Handyman", "Mantenimiento", "Carpinteria", "Plomero", "Pintor", "Mecanico", "Contratista"],
        11: ["Operador de equipo pesado", "Operador de manufactura", "Operador Multitrabajo", "Encargado de almacén"],
        12: ["Chofer", "Transporte", "Uber", "Delivery", "Conductor"],
        13: ["Limpieza", "Recolección de basura", "Trabajador general", "Auxiliar", "Mantenimiento de hogares"],
        14: ["Artesana", "Artista", "Barbero", "Estilista", "Cocinero", "Reposteria", "Chef", "Dueño de negocio"]
    }



    def categorize_occupation(text):
        if pd.isna(text) or text.strip() == "":
            return np.nan  
        text = text.lower()
        for category, keywords in occupations.items():  # Using 'occupations' dictionary
            if any(keyword.lower() in text for keyword in keywords):
                return category
        return np.nan  

    def transform_occupation(df, suffix):
        col_name = f"whi7"  
        df[f"hmz_whi_occupation_{suffix}"] = df[col_name].apply(categorize_occupation)  


    transform_occupation(df_hmz_sdoh_prospect_english, "prospect")


    df_hmz_sdoh_prospect_english.to_csv('data/intermediate/df_hmz_sdoh_prospect_english.csv', index=False)



    #------------------------------------------------------------------------------------------------
    # Social Support
    # -----------------------------------------------------------------------------------------------

    # Transformation 1
    rename_map = {
        "soc1": "hmz_soc1_prospect",
        "soc2a": "hmz_soc2a_prospect",
        "soc2b": "hmz_soc2b_prospect",
        "soc3a": "hmz_soc3a_prospect",
        "soc3b": "hmz_soc3b_prospect",
        "soc4a": "hmz_soc4a_prospect",
        "soc4b": "hmz_soc4b_prospect",
        "soc5a": "hmz_soc5a_prospect",
        "soc5b": "hmz_soc5b_prospect",
        "soc6": "hmz_soc6_prospect",
        "soc_20": "hmz_soc_activities_feel _prospect",
        "nor1a": "hmz_soc_support_ii_1_prospect",
        "nor2a": "hmz_soc_support_ii_2_prospect",
        "nor3a": "hmz_soc_support_ii_3_prospect",
        "nor4a": "hmz_soc_support_ii_4_prospect",
        "nor5a": "hmz_soc_support_ii_5_prospect",
        "nor6a": "hmz_soc_support_ii_6_prospect",
        "nor7a": "hmz_soc_support_ii_7_prospect",
        "nor8a": "hmz_soc_support_ii_8_prospect",
        "nor9a": "hmz_soc_support_ii_9_prospect",
        "nor10a": "hmz_soc_support_ii_10_prospect",
        "nor1c": "hmz_soc_emo1_1_prospect",
        "nor2c": "hmz_soc_emo1_2_prospect",
        "nor3c": "hmz_soc_emo1_3_prospect",
        "nor4c": "hmz_soc_emo1_4_prospect",
        "nor5c": "hmz_soc_emo1_5_prospect",
        "nor6c": "hmz_soc_emo1_6_prospect",
        "nor7c": "hmz_soc_emo1_7_prospect",
        "nor8c": "hmz_soc_emo1_8_prospect",
        "nor9c": "hmz_soc_emo1_9_prospect",
        "nor10c": "hmz_soc_emo1_10_prospect",
        "nor1d": "hmz_soc_emo2_1_prospect",
        "nor2d": "hmz_soc_emo2_2_prospect",
        "nor3d": "hmz_soc_emo2_3_prospect",
        "nor4d": "hmz_soc_emo2_4_prospect",
        "nor5d": "hmz_soc_emo2_5_prospect",
        "nor6d": "hmz_soc_emo2_6_prospect",
        "nor7d": "hmz_soc_emo2_7_prospect",
        "nor8d": "hmz_soc_emo2_8_prospect",
        "nor9d": "hmz_soc_emo2_9_prospect",
        "nor10d": "hmz_soc_emo2_10_prospect",
        "nor1e": "hmz_soc_emo3_1_prospect",
        "nor2e": "hmz_soc_emo3_2_prospect",
        "nor3e": "hmz_soc_emo3_3_prospect",
        "nor4e": "hmz_soc_emo3_4_prospect",
        "nor5e": "hmz_soc_emo3_5_prospect",
        "nor6e": "hmz_soc_emo3_6_prospect",
        "nor7e": "hmz_soc_emo3_7_prospect",
        "nor8e": "hmz_soc_emo3_8_prospect",
        "nor9e": "hmz_soc_emo3_9_prospect",
        "nor10e": "hmz_soc_emo3_10_prospect",
        "nor1f": "hmz_soc_emo4_1_prospect",
        "nor2f": "hmz_soc_emo4_2_prospect",
        "nor3f": "hmz_soc_emo4_3_prospect",
        "nor4f": "hmz_soc_emo4_4_prospect",
        "nor5f": "hmz_soc_emo4_5_prospect",
        "nor6f": "hmz_soc_emo4_6_prospect",
        "nor7f": "hmz_soc_emo4_7_prospect",
        "nor8f": "hmz_soc_emo4_8_prospect",
        "nor9f": "hmz_soc_emo4_9_prospect",
        "nor10f": "hmz_soc_emo4_10_prospect"
    }


    variables_to_recode = list(rename_map.keys())

    # Recoding
    for var in variables_to_recode:
        if var in df_hmz_sdoh_prospect_english.columns:
            df_hmz_sdoh_prospect_english[var] = df_hmz_sdoh_prospect_english[var].replace({96: np.nan, 97: np.nan, 98: np.nan})

    # Renaming
    df_hmz_sdoh_prospect_english.rename(columns=rename_map, inplace=True)

    # Saving
    df_hmz_sdoh_prospect_english.to_csv('data/intermediate/df_hmz_sdoh_prospect_english.csv', index=False)


    # Transformation 2
    # Variables to sum for creating soc_activities
    variables_prospect = [
        "soc7", "soc8", "soc9", "soc10", "soc11",
        "soc12", "soc13", "soc14", "soc15", "soc16", "soc17", "soc18", "soc19"]



    for var in variables_prospect:
        if var in df_hmz_sdoh_prospect_english.columns:
            df_hmz_sdoh_prospect_english[var] = pd.to_numeric(df_hmz_sdoh_prospect_english[var], errors='coerce')
            df_hmz_sdoh_prospect_english[var] = df_hmz_sdoh_prospect_english[var].replace({96: np.nan, 97: np.nan, 98: np.nan})



    df_hmz_sdoh_prospect_english.to_csv('data/intermediate/df_hmz_sdoh_prospect_english.csv', index=False)



    # Creating the new variable
    # Lambda function that filters non-NaN and non-zero values, assigning NaN if the entire row is NaN
    df_hmz_sdoh_prospect_english["hmz_soc_activities_prospect"] = (
        df_hmz_sdoh_prospect_english[variables_prospect]
        .apply(lambda row: np.nan if row.isna().all() else row[(row.notna()) & (row != 0)].count(), axis=1))



    # Renaming variables
    df_hmz_sdoh_prospect_english.rename(columns={
        "soc7": "hmz_soc_get_together_i_prospect",
        "soc8": "hmz_soc_volunteer_prospect",
        "soc9": "hmz_soc_phone_i_prospect",
        "soc10": "hmz_soc_get_together_ii_prospect",
        "soc11": "hmz_soc_phone_ii_prospect",
        "soc12": "hmz_soc_church_prospect",
        "soc13": "hmz_soc_event_prospect",
        "soc14": "hmz_soc_sports_prospect",
        "soc15": "hmz_soc_read_prospect",
        "soc16": "hmz_soc_hobbies_prospect",
        "soc17": "hmz_soc_repairs_prospect",
        "soc18": "hmz_soc_care_relative_prospect",
        "soc19": "hmz_soc_help_prospect",
        "nor0": "hmz_soc_support_i_prospect"
    }, inplace=True)




    # Saving 
    df_hmz_sdoh_prospect_english.to_csv('data/intermediate/df_hmz_sdoh_prospect_english.csv', index=False)





    # Transformation 3: Creating derived variables
    # hmz_soc_emo1_avg

    # List of variables to sum in df_hmz_sdoh_prospect_english
    emo1_vars_prospect = [
        "hmz_soc_emo1_1_prospect", "hmz_soc_emo1_2_prospect", "hmz_soc_emo1_3_prospect", 
        "hmz_soc_emo1_4_prospect", "hmz_soc_emo1_5_prospect", "hmz_soc_emo1_6_prospect", 
        "hmz_soc_emo1_7_prospect", "hmz_soc_emo1_8_prospect", "hmz_soc_emo1_9_prospect", 
        "hmz_soc_emo1_10_prospect"]



    # 'hmz_soc_emo1_avg_prospect'
    def calculate_avg_with_nans_and_zeros(row):
        if row.isna().all():
            return np.nan  # All values are NaN, keep as NaN
        return row.sum() / 10  # Include zeros, divide by 10

    df_hmz_sdoh_prospect_english['hmz_soc_emo1_avg_prospect'] = df_hmz_sdoh_prospect_english[emo1_vars_prospect].apply(
        calculate_avg_with_nans_and_zeros, axis=1
    )


    # hmz_soc_emo2_avg
    # List of variables to sum for emo2 in df_hmz_sdoh_prospect_english
    emo2_vars_prospect = [
        "hmz_soc_emo2_1_prospect", "hmz_soc_emo2_2_prospect", "hmz_soc_emo2_3_prospect", 
        "hmz_soc_emo2_4_prospect", "hmz_soc_emo2_5_prospect", "hmz_soc_emo2_6_prospect", 
        "hmz_soc_emo2_7_prospect", "hmz_soc_emo2_8_prospect", "hmz_soc_emo2_9_prospect", 
        "hmz_soc_emo2_10_prospect"
    ]



    # 'hmz_soc_emo2_avg_prospect' following the specified logic
    def calculate_avg_with_nans_and_zeros(row):
        if row.isna().all():
            return np.nan  # All values are NaN, keep as NaN
        return row.sum() / 10  # Include zeros, divide by 10

    df_hmz_sdoh_prospect_english['hmz_soc_emo2_avg_prospect'] = df_hmz_sdoh_prospect_english[emo2_vars_prospect].apply(
        calculate_avg_with_nans_and_zeros, axis=1
    )


    # hmz_soc_emo3_avg
    # List of variables to sum for emo3 in df_hmz_sdoh_prospect_english
    emo3_vars_prospect = [
        "hmz_soc_emo3_1_prospect", "hmz_soc_emo3_2_prospect", "hmz_soc_emo3_3_prospect", 
        "hmz_soc_emo3_4_prospect", "hmz_soc_emo3_5_prospect", "hmz_soc_emo3_6_prospect", 
        "hmz_soc_emo3_7_prospect", "hmz_soc_emo3_8_prospect", "hmz_soc_emo3_9_prospect", 
        "hmz_soc_emo3_10_prospect"
    ]


    #  'hmz_soc_emo3_avg_prospect' following the specified logic
    def calculate_avg_with_nans_and_zeros(row):
        if row.isna().all():
            return np.nan  # All values are NaN, keep as NaN
        return row.sum() / 10  # Include zeros, divide by 10

    df_hmz_sdoh_prospect_english['hmz_soc_emo3_avg_prospect'] = df_hmz_sdoh_prospect_english[emo3_vars_prospect].apply(
        calculate_avg_with_nans_and_zeros, axis=1
    )


    # hmz_soc_emo4_avg
    # List of variables to sum for emo4 in df_hmz_sdoh_prospect_english
    emo4_vars_prospect = [
        "hmz_soc_emo4_1_prospect", "hmz_soc_emo4_2_prospect", "hmz_soc_emo4_3_prospect", 
        "hmz_soc_emo4_4_prospect", "hmz_soc_emo4_5_prospect", "hmz_soc_emo4_6_prospect", 
        "hmz_soc_emo4_7_prospect", "hmz_soc_emo4_8_prospect", "hmz_soc_emo4_9_prospect", 
        "hmz_soc_emo4_10_prospect"
    ]


    # Create 'hmz_soc_emo4_avg_prospect' following the specified logic
    def calculate_avg_with_nans_and_zeros(row):
        if row.isna().all():
            return np.nan  # All values are NaN, keep as NaN
        return row.sum() / 10  # Include zeros, divide by 10

    df_hmz_sdoh_prospect_english['hmz_soc_emo4_avg_prospect'] = df_hmz_sdoh_prospect_english[emo4_vars_prospect].apply(
        calculate_avg_with_nans_and_zeros, axis=1
    )


    # Saving
    df_hmz_sdoh_prospect_english.to_csv('data/intermediate/df_hmz_sdoh_prospect_english.csv', index=False)


    # Transformation 4: Creating the new emosup variable

    #  'hmz_soc_emosup_avg_prospect' as the sum of the four averages
    df_hmz_sdoh_prospect_english['hmz_soc_emosup_avg_prospect'] = (
        df_hmz_sdoh_prospect_english['hmz_soc_emo1_avg_prospect'] +
        df_hmz_sdoh_prospect_english['hmz_soc_emo2_avg_prospect'] +
        df_hmz_sdoh_prospect_english['hmz_soc_emo3_avg_prospect'] +
        df_hmz_sdoh_prospect_english['hmz_soc_emo4_avg_prospect']
    )


    # Saving 
    df_hmz_sdoh_prospect_english.to_csv('data/intermediate/df_hmz_sdoh_prospect_english.csv', index=False)



    # Transformation 5: aid5
    variables_to_recode = ["nor1g", "nor2g","nor3g","nor4g","nor5g","nor6g","nor7g","nor8g","nor9g","nor10g"]


    # Recoding 96, 97, 98 as nan
    for var in variables_to_recode:
        if var in df_hmz_sdoh_prospect_english.columns:
            df_hmz_sdoh_prospect_english[var] = df_hmz_sdoh_prospect_english[var].replace({96: np.nan, 97: np.nan, 98: np.nan})


    # Renaming variables
    df_hmz_sdoh_prospect_english.rename(columns={
        "nor1g": "hmz_soc_aid5_1_prospect",
        "nor2g": "hmz_soc_aid5_2_prospect",
        "nor3g": "hmz_soc_aid5_3_prospect",
        "nor4g": "hmz_soc_aid5_4_prospect",
        "nor5g": "hmz_soc_aid5_5_prospect",
        "nor6g": "hmz_soc_aid5_6_prospect",
        "nor7g": "hmz_soc_aid5_7_prospect",
        "nor8g": "hmz_soc_aid5_8_prospect",
        "nor9g": "hmz_soc_aid5_9_prospect",
        "nor10g": "hmz_soc_aid5_10_prospect"}, inplace=True)


    # Saving 
    df_hmz_sdoh_prospect_english.to_csv('data/intermediate/df_hmz_sdoh_prospect_english.csv', index=False)



    # Transformation 6: Creating derived variables
    # hmz_soc_aid5_avg

    # List of variables to sum in df_hmz_sdoh_prospect_english
    aid5_vars_prospect = [
        "hmz_soc_aid5_1_prospect", "hmz_soc_aid5_2_prospect", "hmz_soc_aid5_3_prospect", 
        "hmz_soc_aid5_4_prospect", "hmz_soc_aid5_5_prospect", "hmz_soc_aid5_6_prospect", 
        "hmz_soc_aid5_7_prospect", "hmz_soc_aid5_8_prospect", "hmz_soc_aid5_9_prospect", 
        "hmz_soc_aid5_10_prospect"
    ]



    # 'hmz_soc_aid_avg_prospect' following the specified logic
    def calculate_avg_with_nans_and_zeros(row):
        if row.isna().all():
            return np.nan  # All values are NaN, keep as NaN
        return row.sum() / 10  # Include zeros, divide by 10

    df_hmz_sdoh_prospect_english['hmz_soc_aid5_avg_prospect'] = df_hmz_sdoh_prospect_english[aid5_vars_prospect].apply(
        calculate_avg_with_nans_and_zeros, axis=1
    )




    # Transformation 7: aid6
    variables_to_recode = ["nor1h", "nor2h","nor3h","nor4h","nor5h","nor6h","nor7h","nor8h","nor9h","nor10h"]


    # Recoding 96, 97, 98 as nan
    for var in variables_to_recode:
        if var in df_hmz_sdoh_prospect_english.columns:
            df_hmz_sdoh_prospect_english[var] = df_hmz_sdoh_prospect_english[var].replace({96: np.nan, 97: np.nan, 98: np.nan})


    # Renaming variables
    df_hmz_sdoh_prospect_english.rename(columns={
        "nor1h": "hmz_soc_aid6_1_prospect",
        "nor2h": "hmz_soc_aid6_2_prospect",
        "nor3h": "hmz_soc_aid6_3_prospect",
        "nor4h": "hmz_soc_aid6_4_prospect",
        "nor5h": "hmz_soc_aid6_5_prospect",
        "nor6h": "hmz_soc_aid6_6_prospect",
        "nor7h": "hmz_soc_aid6_7_prospect",
        "nor8h": "hmz_soc_aid6_8_prospect",
        "nor9h": "hmz_soc_aid6_9_prospect",
        "nor10h": "hmz_soc_aid6_10_prospect"

    }, inplace=True)


    # Saving 
    df_hmz_sdoh_prospect_english.to_csv('data/intermediate/df_hmz_sdoh_prospect_english.csv', index=False)



    # Transformation 8: Creating derived variables
    # hmz_soc_aid6_avg

    # List of variables to sum in df_hmz_sdoh_prospect_english
    aid6_vars_prospect = [
        "hmz_soc_aid6_1_prospect", "hmz_soc_aid6_2_prospect", "hmz_soc_aid6_3_prospect", 
        "hmz_soc_aid6_4_prospect", "hmz_soc_aid6_5_prospect", "hmz_soc_aid6_6_prospect", 
        "hmz_soc_aid6_7_prospect", "hmz_soc_aid6_8_prospect", "hmz_soc_aid6_9_prospect", 
        "hmz_soc_aid6_10_prospect"
    ]



    # Create 'hmz_soc_aid_avg_prospect' following the specified logic
    def calculate_avg_with_nans_and_zeros(row):
        if row.isna().all():
            return np.nan  # All values are NaN, keep as NaN
        return row.sum() / 10  # Include zeros, divide by 10

    df_hmz_sdoh_prospect_english['hmz_soc_aid6_avg_prospect'] = df_hmz_sdoh_prospect_english[aid6_vars_prospect].apply(
        calculate_avg_with_nans_and_zeros, axis=1
    )


    # Saving
    df_hmz_sdoh_prospect_english.to_csv('data/intermediate/df_hmz_sdoh_prospect_english.csv', index=False)




    # Trnasformation 9: Creating new variable aid_avg
    # 'hmz_soc_aid_avg_prospect' as the sum of the four averages
    df_hmz_sdoh_prospect_english['hmz_soc_aid_avg_prospect'] = (
        df_hmz_sdoh_prospect_english['hmz_soc_aid5_avg_prospect'] +
        df_hmz_sdoh_prospect_english['hmz_soc_aid6_avg_prospect'] )


    # Saving 
    df_hmz_sdoh_prospect_english.to_csv('data/intermediate/df_hmz_sdoh_prospect_english.csv', index=False)




    #------------------------------------------------------------------------------------------------
    # Household Composition
    # -----------------------------------------------------------------------------------------------

    variables_to_recode = ["hem1", "hem2a", "hem2b", "hem4"]

    # Recoding hem4
    if 'hem4' in df_hmz_sdoh_prospect_english.columns:
        df_hmz_sdoh_prospect_english['hem4'] = df_hmz_sdoh_prospect_english['hem4'].replace({
            96: np.nan,
            2: 1,
            4: 3,
            5: 4,
            6: 5
        })

    # Renaming
    df_hmz_sdoh_prospect_english.rename(columns={
        "hem1": 'hmz_hc_prospect',
        "hem2a": 'hmz_hc_0_5_prospect',
        "hem2b": 'hmz_hc_6_12_prospect',
        "hem4": 'hmz_hc_marital_prospect'
    }, inplace=True)

    # Saving
    df_hmz_sdoh_prospect_english.to_csv('data/intermediate/df_hmz_sdoh_prospect_english.csv', index=False)




    # Recoding hem3
    # Chceking variables
    variables_to_recode = ["hem3"]

    for var in variables_to_recode:
        if var in df_hmz_sdoh_prospect_english.columns:
            df_hmz_sdoh_prospect_english[var] = df_hmz_sdoh_prospect_english[var].replace({96: np.nan, 97: np.nan, 98: np.nan})


    for var in variables_to_recode:
        if var in df_hmz_sdoh_prospect_english.columns:
            df_hmz_sdoh_prospect_english[var] = df_hmz_sdoh_prospect_english[var].replace({
                1: 1, 2: 1,            # 1 and 2 become 1
                3: 2, 4: 2,            # 3 and 4 become 2
                5: 3, 6: 3, 7: 3, 8: 3, 9: 3,   # 5,6,7,8,9 become 3
                10: 4, 11: 4, 12: 4, 13: 4,     # 10,11,12,13 become 4
                14: 5, 15: 5, 16: 5             # 14,15,16 become 5
            })


    # Renaming 
    df_hmz_sdoh_prospect_english.rename(columns={'hem3': 'hmz_hc_educ_prospect'}, inplace=True)

    # Saving
    df_hmz_sdoh_prospect_english.to_csv('data/intermediate/df_hmz_sdoh_prospect_english.csv', index=False)



    #------------------------------------------------------------------------------------------------
    # Access to Health Services
    # -----------------------------------------------------------------------------------------------

    variables_to_recode = ["hhc5", "hhc5b1", "hhc5b2", "hhc5b13", "hhc5b15", "hhc5b3", "hhc5b4",
                           "hhc5b5", "hhc5b6", "hhc5b7", "hhc5b8", "hhc5b9", "hhc5b10", "hhc5b11",
                           "hhc5b12", "hhc5b14", "hhc5b16", "hhc5b17", "hhc5a"]



    # Recoding no 96, 97, 98 as nan
    for var in variables_to_recode:
        if var in df_hmz_sdoh_prospect_english.columns:
            df_hmz_sdoh_prospect_english[var] = df_hmz_sdoh_prospect_english[var].replace({96: np.nan, 97: np.nan, 98: np.nan})


    # Recoding public insurance
    # Creating a new variable hmz_public_insurance_prospect
    if all(var in df_hmz_sdoh_prospect_english.columns for var in ['hhc5b1', 'hhc5b2', 'hhc5b13', 'hhc5b15']):
        df_hmz_sdoh_prospect_english['hmz_public_insurance_prospect'] = df_hmz_sdoh_prospect_english[['hhc5b1', 'hhc5b2', 'hhc5b13', 'hhc5b15']].max(axis=1)
        print("Variable hmz_public_insurance_prospect created successfully.")
    else:
        print("Some variables required for hmz_public_insurance_prospect are missing from the dataset.")


    # Recoding private insurance
    # Creating a new variable hmz_private_insurance_prospect
    if all(var in df_hmz_sdoh_prospect_english.columns for var in ["hhc5b3", "hhc5b4", "hhc5b5", "hhc5b6", "hhc5b7", "hhc5b8",
                                                           "hhc5b9", "hhc5b10", "hhc5b11", "hhc5b12", "hhc5b14", "hhc5b16", "hhc5b17"]):
        df_hmz_sdoh_prospect_english['hmz_private_insurance_prospect'] = df_hmz_sdoh_prospect_english[
            ["hhc5b3", "hhc5b4", "hhc5b5", "hhc5b6", "hhc5b7", "hhc5b8", "hhc5b9", "hhc5b10",
             "hhc5b11", "hhc5b12", "hhc5b14", "hhc5b16", "hhc5b17"]].max(axis=1)
        print("Variable hmz_private_insurance_prospect created successfully.")
    else:
        print("Some variables required for hmz_private_insurance_prospect are missing from the dataset.")


    # Renaming the other variables
    df_hmz_sdoh_prospect_english.rename(columns={'hhc5': 'hmz_insurance_prospect', 'hhc5a': 'hmz_no_insurance_prospect'}, inplace=True)


    # Saving
    df_hmz_sdoh_prospect_english.to_csv('data/intermediate/df_hmz_sdoh_prospect_english.csv', index=False)



    #------------------------------------------------------------------------------------------------
    # Discrimination
    # -----------------------------------------------------------------------------------------------


    variables_to_recode = [
        "pdq1a", "pdq1b", "pdq1c", "pdq1d", "pdq1e", "pdq1f", "pdq1g", "pdq1h",
        "pdq2a", "pdq2b", "pdq2c", "pdq2d", "pdq2e", "pdq2f", "pdq2g", "pdq2h",
        "pdq2h1", "pdq3a", "pdq3b", "pdq3c", "pdq3d", "pdq3e", "pdq4a", "pdq4b",
        "pdq4c", "pdq4d", "pdq4e", "pdq4f", "pdq4g", "pdq4h", "pdq4i", "pdq4h1",
        "pdq2i","pdq2j", "pdq4i1", "pdq4j"]


    # Recoding 96, 97, 98 as nan
    for var in variables_to_recode:
        if var in df_hmz_sdoh_prospect_english.columns:
            df_hmz_sdoh_prospect_english[var] = df_hmz_sdoh_prospect_english[var].replace({96: np.nan, 97: np.nan, 98: np.nan})
  
      # Saving
    df_hmz_sdoh_prospect_english.to_csv('data/intermediate/df_hmz_sdoh_prospect_english.csv', index=False)
      
    # Categorizing
    # pdq4h1
    print(df_hmz_sdoh_prospect_english['pdq4h1'].value_counts())

    discrimination_reasons_4 = {'Physical or Health-Related Conditions': [
            'por el vih', 'hiv', 'por ser hiv', 'por ser HIV.', 'the participant is HIV positive',
            'nepotismo y dado su aflicion de HIV', 'por tener espejuelos', 'problema de salud mental',
            'condicion de salud mental', 'condicion fisica', 'por discapacidad', 'impedimento',
            'impedimento.', 'por condición médica', 'por condición medica.', 'por condición medica, favoritismo, por falta de empatía',
            'por condición de salud mental', 'porque los niños la molestaban sin razón', 'condiciones medicas',
            'por su problema de audición.', 'problemas con la autoridad o con seguir ordenes dadas',
            'problemas de salud-depresion', 'condición médica', 'diagnóstico medico', 'razones de salud',
            'health issues', 'situación de salud', 'problemas de salud', 'condición socioeconómica y salud',
            'debido a su diagnóstico de VIH', 'condición de salud en el trabajo'
        ],
    
        'Bullying & Harassment': [
            'bullying', 'bullying y prepotencia', 'bullying en la escuela', 'bullying de niños',
            'bullying y problemas laborales', 'bullying y envidia', 'bullying y tacticas de abogados',
            'bullying en la escuela', 'bulling en la escuela', 'bullying, diferencias laborales',
            'sobrenombres', 'acoso', 'acoso en la escuela por ser estudiosa.', 'acoso de niño',
            'preferencia de maestros a estudiantes', 'abuso de poder (gerente)', 'abuso de poder',
            'tratan de minimizar a la participante', 'celos academicos'
        ],

        'Work-Related Issues': [
            'work issues', 'nepotismo en su área de trabajo.', 'hostigamiento, más trabajo por igual paga',
            'trabajo: personas malintencionadas', 'laboral conditions', 'malas condiciones laborales.',
            'trabajo de ventas.', 'problemas laborales con situaciones interinas', 'maltrato en el sistema de salud',
            'explotacion laboral', 'conflicto en el trabajo', 'puesto de trabajo y política', 
            'competencia laboral; agencias gubernamentales la trataron como si fuera deshonesta y negligente..',
            'su actitud.', 'conflicto en el trabajo como directora en empleo anterior',
            'en el empleo, por excederse en sus responsabilidades.', 'condición de salud en el trabajo',
            'presión social por parte de amistades', 'por su posicion en el trabajo', 'injusticias en proceso de vivienda',
            'supervisora queria que hicieran las cosas tal y como ella decia', 'los demás se creían mejores. que la participante.'
        ],

        'Social & Personal Conflicts': [
            'subestimacion', 'subrtimacion', 'por envidia', 'envidia', 'celos profesionales', 'celos profesionales en el trabajo',
            'competencia', 'inteligencia percibida en la escuela(competencia) participante tiene un gemela',
            'porque te ven como competencia', 'su actitud.', 'por la manera de ser', 'actitud general', 
            'por su carácter.', 'problemas personales.', 'por probatoria', 'por su problema de audición.',
            'actitudes', 'actitud.', 'personalidad jovial.', 'falta de madurez', 'presión social',
            'envidia y celos', 'celos profesionales, religion.', 'diferencias en la sociedad', 'competencia entre profesionales',
            'porque decian que era nerd', 'envy', 'competencia profesional', 'personalidad, chisme del trabajo',
            'en el parto no dejaron que se pegara a su bebé.', 'envidia profesional.', 'falta de madurez (trabajo)/ medico (trato no profesional)'
        ],

        'Family & Domestic Issues': [
            'familiares', 'personal relationship problems', 'problemas familiares', 'por su desesperacion',
            'familiares', 'situaciones familiares', 'su prioridad son sus hijos y no le respetaban por eso',
            'porque no le dieron oportunidad de vivir en un apartamento', 'porque no le dieron oportunidad de vivir en un apartamento'
        ],

        'Legal & Authority-Related Issues': [
            'personal issues with police men', 'burocracia gubernamental.', 'burocracia del departamento de educacion',
            'el patrono obstaculizó sus visitas al fondo de seguro del estado por lesión en el empleo',
            'discriminado en el tribunal por problema en trabajo', 'injusticia', 'situaciones políticas',
            'problemas con abogado de la otra parte', 'razones políticas.', 'razones de salud',
            'injusticia familiar', 'secuestro infantil', 'impericia medica', 'despido injustificado',
            'injusticias en proceso de vivienda', 'razones políticas.', 'razones politicas.', 'razones políticas.',
            'presión social por parte de amistades'
        ],

        'Religious or Cultural Beliefs': [
            'religion', 'religion y apariencia fisica', 'religious views', 'creencias religiosas', 
            'afiliaciones religiosas', 'religión'
        ],

        'Economic or Financial Issues': [
            'por la situación económica', 'por lo económico', 'estatus socioeconómico', 'status social',
            'discriminado por el ingreso', 'estatus socioeconómico.', 'por ingresos', 'situaciones económicas y condiciones de salud',
            'nivel económico, condiciones médicas', 'discriminacion por estatus socioeconomico'
        ],

        'Political Beliefs & Affiliations': [
            'politica', 'política', 'situación política', 'por razones politicas', 'political affiliations',
            'political differences', 'diferencias politicas', 'afiliación política', 'posturas politicas',
            'motivos ideológicos.', 'afiliaciones políticas'
        ],

        'Doesn\'t Know / No Specific Reason': [
            "doesn't know", "no sabe", "no sabe.", "doesnot know", "doesn't know.", "doesn't know the reason.",
            "does not know", "sin razón específica", "ninguna de las anteriores", "ninguno de los anteriores", 
            "ninguno de los anteriores aplica", "no especificó"
        ],

        'Physical Appearance': [
            'por su rostro', 'por la ropa que tenia puesta', 'por el pelo', 'apariencia física',
            'fisico', 'por apariencia', 'por apariencia.', 'her physical appearance and she demanded respect',
            'la participante fue discriminada por su físico cuando estuvo en sexto grado.',
            'aspecto fisico', 'deformación en la boca', 'apariencia', 'por nariz', 'peso'
        ],

        'Education & Intellectual Capacity': [
            'he was not a good student', 'subestimaron su capacidad', 'subestimaron su capacidad',
            'sentimientos de superioridad debido a sus niveles de educación', 'nivel de estudios.',
            'competencia profesional', 'porque los niños la molestaban sin razón', 'nivel educativo',
            'prejuicio por nivel educativo', 'por sus notas.', 'por las notas', 'menosprecio a maestros de educación física',
            'educación'
        ],

        'Housing & Social Status': [
            'vivienda', 'vivían en casa grande. Tenían dinero.', 'situación socioeconómica.',
            'por ser del barrio y por su condición de vih', 'estatus socioeconómico', 'estatus social',
            'clases sociales', 'clase social', 'condición socioeconómica.'
        ],

        'Workplace Environment': [
            'work related environment', 'situaciones laborales', 'condiciones laborales.', 'situaciones de trabajo',
            'problemas en el trabajo', 'presión en el trabajo', 'conflictos laborales', 'condiciones de empleo'
        ]}




    # Flattening the dictionary for lookup
    discrimination_map = {reason.lower().strip(): category 
                          for category, reasons in discrimination_reasons_4.items() 
                          for reason in reasons}

    # Function to replace reasons with categories in a DataFrame column
    def map_discrimination_to_category(df, column_name):
        df[column_name] = df[column_name].astype(str).str.lower().str.strip().map(discrimination_map)
        return df

    df_hmz_sdoh_prospect_english= map_discrimination_to_category(df_hmz_sdoh_prospect_english, 'pdq4h1')



    #'pdq2h1'
    discrimination_reasons_6 = {


        'Social & Personal Conflicts': [
            'Failed promises'
        ]
    
    }

    # Flattening the dictionary for lookup
    discrimination_map = {reason.lower().strip(): category 
                          for category, reasons in discrimination_reasons_6.items() 
                          for reason in reasons}

    # Function to replace reasons with categories in a DataFrame column
    def map_discrimination_to_category(df, column_name):
        df[column_name] = df[column_name].astype(str).str.lower().str.strip().map(discrimination_map)
        return df

    df_hmz_sdoh_prospect_english = map_discrimination_to_category(df_hmz_sdoh_prospect_english, 'pdq2h1')



    # pdq2i1
    discrimination_reasons_7 = {
    

        'Social & Personal Conflicts': [ 'Failed promises'
        ],

    
    }
    # Flattening the dictionary for lookup
    discrimination_map = {reason.lower().strip(): category 
                          for category, reasons in discrimination_reasons_7.items() 
                          for reason in reasons}

    # Function to replace reasons with categories in a DataFrame column
    def map_discrimination_to_category(df, column_name):
        df[column_name] = df[column_name].astype(str).str.lower().str.strip().map(discrimination_map)
        return df

    df_hmz_sdoh_prospect_english = map_discrimination_to_category(df_hmz_sdoh_prospect_english, 'pdq2i1')


    # Renaming 
    df_hmz_sdoh_prospect_english.rename(columns={
        'pdq1a': 'hmz_pdq_1a_prospect',
        'pdq1b': 'hmz_pdq_1b_prospect',
        'pdq1c': 'hmz_pdq_1c_prospect',
        'pdq1d': 'hmz_pdq_1d_prospect',
        'pdq1e': 'hmz_pdq_1e_prospect',
        'pdq1f': 'hmz_pdq_1f_prospect',
        'pdq1g': 'hmz_pdq_1g_prospect',
        'pdq1h': 'hmz_pdq_1h_prospect',
        'pdq2a': 'hmz_pdq_2a_prospect',
        'pdq2b': 'hmz_pdq_2b_prospect',
        'pdq2c': 'hmz_pdq_2c_prospect',
        'pdq2d': 'hmz_pdq_2d_prospect',
        'pdq2e': 'hmz_pdq_2e_prospect',
        'pdq2f': 'hmz_pdq_2f_prospect',
        'pdq2g': 'hmz_pdq_2g_prospect',
        'pdq2h': 'hmz_pdq_2h_prospect',
        'pdq2h1': 'hmz_pdq_2h_other_prospect',
        'pdq3a': 'hmz_pdq_3a_prospect',
        'pdq3b': 'hmz_pdq_3b_prospect',
        'pdq3c': 'hmz_pdq_3c_prospect',
        'pdq3d': 'hmz_pdq_3d_prospect',
        'pdq3e': 'hmz_pdq_3e_prospect',
        'pdq4a': 'hmz_pdq_4a_prospect',
        'pdq4b': 'hmz_pdq_4b_prospect',
        'pdq4c': 'hmz_pdq_4c_prospect',
        'pdq4d': 'hmz_pdq_4d_prospect',
        'pdq4e': 'hmz_pdq_4e_prospect',
        'pdq4f': 'hmz_pdq_4f_prospect',
        'pdq4g': 'hmz_pdq_4g_prospect',
        'pdq4h': 'hmz_pdq_4h_prospect',
        'pdq4i': 'hmz_pdq_4i_prospect',
        'pdq4i1': 'hmz_pdq_4i_other_prospect',
        'pdq2i': 'hmz_pdq_2i_prospect',
        'pdq2j': 'hmz_pdq_2j_prospect',
        'pdq2i1': 'hmz_pdq_2i_other_prospect',
        'pdq4j': 'hmz_pdq_4j_prospect'
    }, inplace=True)



    # Saving
    df_hmz_sdoh_prospect_english.to_csv('data/intermediate/df_hmz_sdoh_prospect_english.csv', index=False)



    #------------------------------------------------------------------------------------------------
    # Food Security
    # -----------------------------------------------------------------------------------------------

    variables_to_recode = ["fss1", "fss1a_1", "fss1a_2", "fss1a_3", "fss1a_4", "fss1a_5", "fss1a_6",
                           "fss1b_1", "fss1b_2", "fss1b_3", "fss1b_4", "fss2", "fss3", "fss4", "fss5",
                           "fss5a", "fss6", "fss7", "fss8", "fss9", "fss9a"]

    # Recoding 96, 97, 98 as nan
    for var in variables_to_recode:
        if var in df_hmz_sdoh_prospect_english.columns:
            df_hmz_sdoh_prospect_english[var] = df_hmz_sdoh_prospect_english[var].replace({96: np.nan, 97: np.nan, 98: np.nan})

    # Renaming 
    df_hmz_sdoh_prospect_english.rename(columns={
        "fss1": 'hmz_fss1_prospect',
        'fss1a_1': 'hmz_fss1a1_prospect',
        'fss1a_2': 'hmz_fss1a2_prospect',
        'fss1a_3': 'hmz_fss1a3_prospect',
        'fss1a_4': 'hmz_fss1a4_prospect',
        'fss1a_5': 'hmz_fss1a5_prospect',
        'fss1a_6': 'hmz_fss1a6_prospect',
        'fss1b_1': 'hmz_fss1b1_prospect',
        'fss1b_2': 'hmz_fss_time_shopping_prospect',
        'fss1b_3': 'hmz_fss_store_prospect',
        'fss1b_4': 'hmz_fss_diet_prospect',
  
    }, inplace=True)



    variables_to_check = [
        'hmz_fss1_prospect', 'hmz_fss1a1_prospect', 'hmz_fss1a2_prospect',
        'hmz_fss1a3_prospect', 'hmz_fss1a4_prospect', 'hmz_fss1a5_prospect',
        'hmz_fss1a6_prospect', 'hmz_fss1b1_prospect', 'hmz_fss_time_shopping_prospect',
        'hmz_fss_store_prospect', 'hmz_fss_diet_prospect',
        'hmz_food_running_out_prospect', 'hmz_food_not_lasting_prospect',
        'hmz_food_balanced_meals_prospect', 'hmz_food_size_meals_prospect',
        'hmz_food_size_meals_often_prospect', 'hmz_food_eat_less_prospect',
        'hmz_food_no_eat_prospect', 'hmz_food_lose_weight_prospect',
        'hmz_food_no_eat_full_day_prospect', 'hmz_food_no_eat_full_day_often_prospect'
    ]


    # Saving
    df_hmz_sdoh_prospect_english.to_csv('data/intermediate/df_hmz_sdoh_prospect_english.csv', index=False)




    #------------------------------------------------------------------------------------------------
    # Neighborhood Community
    # -----------------------------------------------------------------------------------------------

    variables_to_recode = ["nss44","nss45","nss46", "nss47", "nss48", "nss36", "nss37", "nss38", "nss39"]

    # Recoding 96, 97, 98 as nan
    for var in variables_to_recode:
        if var in df_hmz_sdoh_prospect_english.columns:
            df_hmz_sdoh_prospect_english[var] = df_hmz_sdoh_prospect_english[var].replace({96: np.nan, 97: np.nan, 98: np.nan})


    # Renaming variables
    df_hmz_sdoh_prospect_english.rename(columns={
        'nss44': 'hmz_nfa_favors_prospect',
        'nss45': 'hmz_nfa_watch_property_prospect',
        'nss46': 'hmz_nfa_advice_prospect',
        'nss47': 'hmz_nfa_parties_prospect',
        'nss48': 'hmz_nfa_interactions_prospect',
        'nss36': 'hmz_nfa_close_knit_prospect',
        'nss37': 'hmz_nfa_get_along_prospect',
        'nss38': 'hmz_nfa_trust_prospect',
        'nss39': 'hmz_nfa_values_prospect'
    }, inplace=True)



    # Saving
    df_hmz_sdoh_prospect_english.to_csv('data/intermediate/df_hmz_sdoh_prospect_english.csv', index=False)




    #------------------------------------------------------------------------------------------------
    # Outdoors, Education, and Sports Facilities in Neighborhood
    # -----------------------------------------------------------------------------------------------

    variables_to_recode = ["nss49", "nss50", "nss51", "nss52", "nss53", "nss55", "nss10"]

    # Recoding 96, 97, 98 as nan
    for var in variables_to_recode:
        if var in df_hmz_sdoh_prospect_english.columns:
            df_hmz_sdoh_prospect_english[var] = df_hmz_sdoh_prospect_english[var].replace({96: np.nan, 97: np.nan, 98: np.nan})


    # Renaming 
    df_hmz_sdoh_prospect_english.rename(columns={
        'nss49': 'hmz_nfa_park_prospect',
        'nss50': 'hmz_nfa_sports_field_prospect',
        'nss51': 'hmz_nfa_pool_prospect',
        'nss52': 'hmz_nfa_recreational_prospect',
        'nss53': 'hmz_nfa_gym_prospect',
        'nss55': 'hmz_nfa_bicycle_path_prospect',
        'nss10': 'hmz_nfa_exercise_prospect'
    }, inplace=True)

    # Saving
    df_hmz_sdoh_prospect_english.to_csv('data/intermediate/df_hmz_sdoh_prospect_english.csv', index=False)



    #------------------------------------------------------------------------------------------------
    # Household Income
    # -----------------------------------------------------------------------------------------------

    if 'whi10' in df_hmz_sdoh_prospect_english.columns:
        df_hmz_sdoh_prospect_english['whi10'] = df_hmz_sdoh_prospect_english['whi10'].replace({96: np.nan, 97: np.nan, 98: np.nan})
        df_hmz_sdoh_prospect_english.rename(columns={'whi10': 'hmz_hi_total_prospect'}, inplace=True)

    # Saving
    df_hmz_sdoh_prospect_english.to_csv('data/intermediate/df_hmz_sdoh_prospect_english.csv', index=False)





    #------------------------------------------------------------------------------------------------
    # Access to Food
    # -----------------------------------------------------------------------------------------------

    variables_to_recode = ["nss19", "nss20", "nss21", "nss22", "nss23", "nss24", "nss25", "nss26", "nss27", "nss28", "nss31"]

    # Recoding 96, 97, 98 as nan
    for var in variables_to_recode:
        if var in df_hmz_sdoh_prospect_english.columns:
            df_hmz_sdoh_prospect_english[var] = df_hmz_sdoh_prospect_english[var].replace({96: np.nan, 97: np.nan, 98: np.nan})


    # Renaming variables
    df_hmz_sdoh_prospect_english.rename(columns={
        "nss19": 'hmz_nfa_fruits_vegetables_i_prospect',
        "nss20": 'hmz_nfa_fruits_vegetables_ii_prospect',
        "nss21": 'hmz_nfa_fruits_vegetables_iii_prospect',
        "nss22": 'hmz_nfa_lowfat_i_prospect',
        "nss23": 'hmz_nfa_lowfat_ii_prospect',
        "nss24": 'hmz_nfa_lowfat_iii_prospect',
        "nss25": 'hmz_nfa_wholegrain_i_prospect',
        "nss26": 'hmz_nfa_wholegrain_ii_prospect',
        "nss27": 'hmz_nfa_wholegrain_iii_prospect',
        "nss28": 'hmz_nfa_fish_prospect',
        "nss31": 'hmz_nfa_fastfood_prospect'
    }, inplace=True)




    # Saving 
    df_hmz_sdoh_prospect_english.to_csv('data/intermediate/df_hmz_sdoh_prospect_english.csv', index=False)


    #------------------------------------------------------------------------------------------------
    # Migration History
    # -----------------------------------------------------------------------------------------------

    if 'mha1' in df_hmz_sdoh_prospect_english.columns:
        df_hmz_sdoh_prospect_english['mha1'] = df_hmz_sdoh_prospect_english['mha1'].replace({4: 3})
        df_hmz_sdoh_prospect_english.rename(columns={'mha1': 'hmz_mh_pob_prospect'}, inplace=True)

    # Saving
    df_hmz_sdoh_prospect_english.to_csv('data/intermediate/df_hmz_sdoh_prospect_english.csv', index=False)




   # -------------------------------------------------------------------------------------------------
   # Post-Processing  – PROSPECT English  SDOH
   # -------------------------------------------------------------------------------------------------

   # --------------------------
   # Adding “sdoh” prefix to every variable that starts with “hmz_”
   # --------------------------
    df_hmz_sdoh_prospect_english.columns = [
       f"hmz_sdoh_{c[4:]}" if c.startswith("hmz_") else c
       for c in df_hmz_sdoh_prospect_english.columns]
    df_hmz_sdoh_prospect_english.to_csv('data/intermediate/df_hmz_sdoh_prospect_english.csv', index=False)


   # --------------------------
   #  Renaming REDCap event variable --> hmz_visit
   # --------------------------
    if "redcap_event_name" in df_hmz_sdoh_prospect_english.columns:
       df_hmz_sdoh_prospect_english["redcap_event_name"] = (
           df_hmz_sdoh_prospect_english["redcap_event_name"]
           .replace({"baseline_arm_1": "v1", "visit_2_arm_1": "v2"}) )
       df_hmz_sdoh_prospect_english.rename(
           columns={"redcap_event_name": "hmz_visit_prospect"}, inplace=True )
     
    df_hmz_sdoh_prospect_english.to_csv('data/intermediate/df_hmz_sdoh_prospect_english.csv', index=False)

   # --------------------------
   # Renaming record_id → hmz_record_id_prospect
   # --------------------------
    if "record_id" in df_hmz_sdoh_prospect_english.columns:
       df_hmz_sdoh_prospect_english.rename(
           columns={"record_id": "hmz_record_id_prospect"}, inplace=True)
       
    df_hmz_sdoh_prospect_english.to_csv('data/intermediate/df_hmz_sdoh_prospect_english.csv', index=False)


   # --------------------------
   # Keeping only studyid and hmz variables
   # --------------------------
    df_hmz_sdoh_prospect_english = df_hmz_sdoh_prospect_english[[col for col in df_hmz_sdoh_prospect_english.columns if col.startswith('hmz_') or col in ['studyid']]]   
    df_hmz_sdoh_prospect_english.to_csv('data/intermediate/df_hmz_sdoh_prospect_english.csv', index=False)



   
   # ------------------------------------------------------------------------------------------------------------
   # Creating PROSPECT visit-specific files
   # ------------------------------------------------------------------------------------------------------------

    df_hmz_sdoh_prospect_english = pd.read_csv("data/intermediate/df_hmz_sdoh_prospect_english.csv")
    df_hmz_sdoh_prospect_english = df_hmz_sdoh_prospect_english[df_hmz_sdoh_prospect_english["studyid"].notnull() ]

   # --------------------------
   # Splitting into Visit-1 and Visit-2 files
   # --------------------------
   # Visit 1
    df_hmz_sdoh_prospect_english_visit_1 = df_hmz_sdoh_prospect_english[df_hmz_sdoh_prospect_english["hmz_visit_prospect"] == "v1"].copy()
    df_hmz_sdoh_prospect_english_visit_1.rename(columns={col: f"{col}_v1" for col in df_hmz_sdoh_prospect_english_visit_1.columns if col != "studyid"}, inplace=True)
    df_hmz_sdoh_prospect_english_visit_1.rename(columns={"hmz_visit_prospect_v1": "visit"}, inplace=True)
    df_hmz_sdoh_prospect_english_visit_1.to_csv("data/intermediate/df_hmz_sdoh_prospect_english_visit_1.csv", index=False)

   # Visit 2
    df_hmz_sdoh_prospect_english_visit_2 = df_hmz_sdoh_prospect_english[df_hmz_sdoh_prospect_english["hmz_visit_prospect"] == "v2"].copy()
    df_hmz_sdoh_prospect_english_visit_2.rename(columns={col: f"{col}_v2" for col in df_hmz_sdoh_prospect_english_visit_2.columns if col != "studyid"}, inplace=True)
    df_hmz_sdoh_prospect_english_visit_2.rename(columns={"hmz_visit_prospect_v2": "visit"}, inplace=True)
    df_hmz_sdoh_prospect_english_visit_2.to_csv("data/intermediate/df_hmz_sdoh_prospect_english_visit_2.csv", index=False)


   # ------------------------------------------------------------------------------------------------------------
   # Renaming hmz visit --> visit
   # ------------------------------------------------------------------------------------------------------------
  
    df_hmz_sdoh_prospect_english_visit_1.rename(columns={'hmz_visit_prospect_english_v1': 'visit'}, inplace=True)
    df_hmz_sdoh_prospect_english_visit_2.rename(columns={'hmz_visit_prospect_english_v2': 'visit'}, inplace=True)
  
   
  # Saving
    df_hmz_sdoh_prospect_english_visit_1.to_csv("data/intermediate/df_hmz_sdoh_prospect_english_visit_1.csv", index=False)
    df_hmz_sdoh_prospect_english_visit_2.to_csv("data/intermediate/df_hmz_sdoh_prospect_english_visit_2.csv", index=False)


   # Returning final DataFrames
    return {
            "df_hmz_sdoh_bprhs_0": df_hmz_sdoh_bprhs_0,
            "df_hmz_sdoh_bprhs_2": df_hmz_sdoh_bprhs_2,
            "df_hmz_sdoh_bprhs_5": df_hmz_sdoh_bprhs_5,
            "df_hmz_sdoh_bprhs_8": df_hmz_sdoh_bprhs_8,
            "df_hmz_sdoh_prospect_visit_1": df_hmz_sdoh_prospect_visit_1,
            "df_hmz_sdoh_prospect_visit_2": df_hmz_sdoh_prospect_visit_2,
            "df_hmz_sdoh_prospect_english_visit_1": df_hmz_sdoh_prospect_english_visit_1,
            "df_hmz_sdoh_prospect_english_visit_2": df_hmz_sdoh_prospect_english_visit_2}

   