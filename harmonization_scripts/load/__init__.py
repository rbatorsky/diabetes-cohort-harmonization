# -*- coding: utf-8 -*-
"""
Created on Mon Jun 23 10:07:12 2025

@author: andreia
"""
from .loader_ffq import load_ffq_data   
from .loader_health import load_health_data
from .loader_sdoh import load_sdoh_data

def run_loading(config):
    print("Loading SDOH data...")
    sdoh_data = load_sdoh_data(config)

    print("Loading Health data...")
    health_data = load_health_data(config)

    print("Loading FFQ data...")
    ffq_data = load_ffq_data(config)

    return {
        "sdoh": sdoh_data,
        "health": health_data,
        "ffq": ffq_data
    }

