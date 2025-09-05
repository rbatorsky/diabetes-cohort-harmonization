
# -*- coding: utf-8 -*-
"""
Created on Sun Jul 27 10:59:33 2025

@author: andreia
"""

import os
import yaml

def load_config():
    # Get the path to the project root (where main.py and config.yaml are)
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    config_path = os.path.join(project_root, "config.yaml")

    if not os.path.exists(config_path):
        raise FileNotFoundError("Missing config.yaml at project root.")

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    return config
