from scripts.base import GREEN_COLS, DARK_COLS

dict_units = {
    "production": "MWh",
    "exchange": "MWh",
    "co2":'g/kWh',
    "consumption": "MWh",
    "prices": "DKK/MWh",
    "imports" : "MWh",
    "exports" : "MWh"
}

dict_colors = {
    "Total": "white",
    "Green": "#006d2c",
    "Dark": 'black',
    "DE": "#b15928",
    "NO": "#984ea3",
    "NO2": "#984ea3",
    "SE": "#377eb8",
    "SE4": "#377eb8",
    "DK1": "#de2d26",
    "DK2": "#fc9272",
    "NORDIC": "#ffff33",
    "NL": "#ff7f00",
}
green_colors = ["#e5f5e0","#c7e9c0","#a1d99b","#74c476","#41ab5d","#238b45"]
dark_colors = ["#bdbdbd","#969696","#737373","#252525"]
for col in GREEN_COLS:
    dict_colors[col] = green_colors[GREEN_COLS.index(col)]
for col in DARK_COLS:
    dict_colors[col] = dark_colors[DARK_COLS.index(col)]
