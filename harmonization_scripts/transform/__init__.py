# -*- coding: utf-8 -*-
"""
Created on Tue Jun 24 05:13:03 2025

@author: andreia
"""

from .transform_ffq import transform_ffq
from .transform_health import transform_health
from .transform_sdoh import transform_sdoh

def run_transformation(loaded_data):
    """
    Runs all transformation steps (FFQ, Health, SDOH) on the loaded data.
    Returns a dictionary with the transformed outputs.
    """
    print("Running Health transformations...")
    transformed_health = transform_health(loaded_data["health"])
    
    print("Running SDOH transformations...")
    transformed_sdoh = transform_sdoh(loaded_data["sdoh"])

    print("Running FFQ transformations...")
    transformed_ffq = transform_ffq(loaded_data["ffq"])

    return {
        "sdoh": transformed_sdoh,
        "health": transformed_health,
        "ffq": transformed_ffq }
