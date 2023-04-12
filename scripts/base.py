from pathlib import Path
import os
import logging
import datetime as dt

BASE_PATH = Path(__file__).resolve().parent.parent

COLOR_HEATMAP_SCALE = [[0, '#f7f7f7'], [1, '#67a9cf']]
COLOR_HEATMAP_div_SCALE = [[0, '#ef8a62'],[0.5,'#f7f7f7'], [1, '#67a9cf']]
COLOR_HEATMAP_LINES = '#19191c'
GREEN_COLS = ['Biomass', 'HydroPower', 'OtherRenewable', 'SolarPower', 'OnshoreWindPower', 'OffshoreWindPower']
DARK_COLS = ['FossilGas', 'FossilHardCoal', 'FossilOil', 'Waste']
