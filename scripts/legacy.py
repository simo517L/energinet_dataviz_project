import urllib.request
import os
import numpy as np
import pandas as pd
import json
import pickle
import datetime as dt

def load_data(number_of_rows, database):
    df_final = pd.DataFrame()
    offset = 0
    while offset < number_of_rows: # As of 12-09-2021 there are 1_494_416 rows
        print(offset)
        url = f'https://api.energidataservice.dk/datastore_search?resource_id={database}&limit=32000&offset={offset}'
        fileobj = urllib.request.urlopen(url)
        read_json = json.loads(fileobj.read())
        df = pd.DataFrame(read_json["result"]["records"])
        df_final = df_final.append(df)
        offset += 32000
    return df_final




df = load_data(1_600_000, "powersystemrightnow")
df.set_index("_id",inplace=True)
df.to_pickle(r"C:\Users\simon\Desktop\master kurser\viz\energinet_dataviz\data\powersystemrightnow.pkl")

df = load_data(86_000, "electricitybalancenonv")
df.set_index("_id",inplace=True)
df.to_pickle(r"C:\Users\crans\Desktop\git\dataviz\data\electricitybalancenonv.pkl")

df = load_data(1_577_000, "elspotprices")
df.set_index("_id",inplace=True)
df.to_pickle(r"C:\Users\crans\Desktop\git\dataviz\data\elspotprices.pkl")





# Build 5 dataframes:
dfpower = pd.read_pickle(os.path.join(r'C:\Users\simon\Desktop\master kurser\viz\energinet_dataviz\data', f'powersystemrightnow.pkl'))
dfprice = pd.read_pickle(os.path.join(r'C:\Users\simon\Desktop\master kurser\viz\energinet_dataviz\data', f'elspotprices.pkl'))
dfbalance = pd.read_pickle(os.path.join(r'C:\Users\simon\Desktop\master kurser\viz\energinet_dataviz\data', f'electricitybalancenonv.pkl'))

#Dont include the end-date (since dont have full day of data)
today = dt.datetime(2021,11,21)
dfpower["Minutes1DK"] = pd.to_datetime(dfpower["Minutes1DK"])
dfpower = dfpower[dfpower["Minutes1DK"] < today]
dfprice["HourDK"] = pd.to_datetime(dfprice["HourDK"])
dfprice = dfprice[dfprice["HourDK"] < today]
dfbalance["HourDK"] = pd.to_datetime(dfbalance["HourDK"])
dfbalance = dfbalance[dfbalance["HourDK"] < today]

# Removes bad 'balance' rows:
dfbalance.sort_index(inplace=True)
dfbalance = dfbalance.drop([14281, 50816, 54650, 60175, 60182, 60216])

# build consumption
dfconsumption = dfbalance[["HourDK", "PriceArea", "TotalLoad"]]
dfconsumption = dfconsumption.pivot_table('TotalLoad',"HourDK", "PriceArea")
dfconsumption.reset_index(inplace=True)
dfconsumption.to_pickle(r"C:\Users\crans\Desktop\git\dataviz\data\consumption.pkl")

#build price
import datetime as dt
dfprice["HourDK"] = pd.to_datetime(dfprice["HourDK"])
dfprice = dfprice[dfprice["HourDK"] >= dt.datetime(2017,1,1)]
dfprice = dfprice[["HourDK", "PriceArea", "SpotPriceDKK"]]
dfprice = dfprice.pivot_table('SpotPriceDKK',"HourDK", "PriceArea")
dfprice.reset_index(inplace=True)
dfprice.to_pickle(r"C:\Users\crans\Desktop\git\dataviz\data\prices.pkl")

dfbalance.columns
dfbalance.set_index("HourDK", inplace=True)
dfbalance.sort_index(inplace=True)
dfbalance.reset_index(inplace=True)
dfproduction = dfbalance[['HourDK','PriceArea', 'Biomass', 'FossilGas',
       'FossilHardCoal', 'FossilOil', 'HydroPower', 'OtherRenewable',
       'SolarPower', 'Waste', 'OnshoreWindPower', 'OffshoreWindPower']]
dfproduction.to_pickle(r"C:\Users\crans\Desktop\git\dataviz\data\production1.pkl")


dfpower.columns
dfpower.index = pd.to_datetime(dfpower["Minutes1DK"])
dfpower["CO2Emission"] = dfpower["CO2Emission"].astype("float64")
dfpower = dfpower.groupby(pd.Grouper(freq='1h')).mean()
dfpower.reset_index(inplace=True)
dfpower.rename(columns={'Minutes1DK':'HourDK'}, inplace=True)
dfexchange = dfpower[['HourDK', 'Exchange_DK1-DE',
                      'Exchange_DK1-NL', 'Exchange_DK1-NO', 'Exchange_DK1-SE',
                      'Exchange_DK1-DK2', 'Exchange_DK2-DE', 'Exchange_DK2-SE',
                      'Exchange_Bornholm-SE']]
dfexchange.to_pickle(r"C:\Users\crans\Desktop\git\dataviz\data\exchange.pkl")

dfco2 = dfpower[['HourDK', 'CO2Emission']]
dfco2.to_pickle(r"C:\Users\crans\Desktop\git\dataviz\data\co2.pkl")

# Add total production:
df = pd.read_pickle(r'C:\Users\crans\Desktop\git\dataviz\data\production1.pkl')
df.set_index("HourDK", inplace = True)
df.sort_index(inplace=True)
df.index = pd.to_datetime(df.index)
df = df[df.index >= dt.datetime(2018,1,1)]
df["Total"] = df[df.columns[1:]].sum(1)
df["Total Green"] = df[GREEN_COLS].sum(1)
df["Total Dark"] = df[DARK_COLS].sum(1)
df.reset_index(inplace=True)
df.to_pickle(r"C:\Users\crans\Desktop\git\dataviz\data\production.pkl")
df = df.set_index('HourDK')
df.index = pd.to_datetime(df.index)
df_daily = df.groupby([pd.Grouper(level='HourDK', freq='D'), 'PriceArea']).sum()
df_daily.reset_index(inplace=True)
df_daily.to_pickle(r"C:\Users\crans\Desktop\git\dataviz\data\productiondaily.pkl")

def build_plots_test(data_handler):
    out = []
    for df in data_handler.dataframes:
        name = df.__name__
        out += [html.H1(f'Dataframe: {name}')]
        for col in df.columns:
            print(f"Plotting {col}")
            if col == "HourDK" or col == "PriceArea":
                continue
            fig = px.line(df, x=df["HourDK"], y=df[col])
            out += [dcc.Graph(
                id=f'example-graph-{col}-{name}',
                figure=fig
            )]

    return out

def build_histograms(data_handler):
    out = []
    df = data_handler.dfprices
    out += [html.H1(f'HISTOGRAMS')]
    for col in df.columns:
        if col == "HourDK":
            continue
        fig = px.histogram(df[col])
        out += [dcc.Graph(
            id=f'example-histogram-{col}',
            figure=fig
        )]

    return out

#Build exchange:
dfbalance = pd.read_pickle(os.path.join(r'C:\Users\crans\Desktop\git\dataviz\data', f'electricitybalancenonv.pkl'))
dfbalance.set_index("HourDK", inplace = True)
dfbalance.sort_index(inplace=True)
dfbalance.index = pd.to_datetime(dfbalance.index)
dfbalance = dfbalance[dfbalance.index >= dt.datetime(2018,1,1)]

dfexchange = pd.read_pickle(r"C:\Users\crans\Desktop\git\dataviz\data\exchange.pkl")
dfexchange.set_index("HourDK", inplace = True)
dfexchange.sort_index(inplace=True)
dfexchange.index = pd.to_datetime(dfexchange.index)

dk1b = dfbalance[dfbalance["PriceArea"] == "DK1"].reset_index().set_index("HourDK")
dk2b = dfbalance[dfbalance["PriceArea"] == "DK2"].reset_index().set_index("HourDK")

dfex = pd.DataFrame()
dfex.index = dk1b.index
cols = ["DK1_DE", "DK1_NL", "DK1_NO", "DK1_SE", "DK1_Nordic", "DK1_DK2", "DK2_DE", "DK2_SE"]
dfex["DK1_DE"] = dk1b.ExchangeContinent
dfex["DK2_DE"] = dk2b.ExchangeContinent
dfex["DK2_SE"] = dk2b.ExchangeNordicCountries
dfex["DK1_DK2"] = dk1b.ExchangeGreatBelt
dfex["DK1_NL"] = np.nan
dfex["DK1_NO"] = np.nan
dfex["DK1_SE"] = np.nan
dupli = dk1b[dk1b.index < dt.datetime(2018,10,31,10)].ExchangeNordicCountries.index.duplicated()
a = dk1b[dk1b.index < dt.datetime(2018,10,31,10)].loc[~dupli,]
dfex["DK1_NORDIC"] = a.ExchangeNordicCountries

dfex["DK1_NL"] = dfexchange["Exchange_DK1-NL"]
dfex["DK1_NO"] = dfexchange["Exchange_DK1-NO"]
dfex["DK1_SE"] = dfexchange["Exchange_DK1-SE"]

# Removes nordic where either NO or SE is not nan
dfex[~dfex["DK1_NO"].isna()]["DK1_NORDIC"] = np.nan
dfex[~dfex["DK1_SE"].isna()]["DK1_NORDIC"] = np.nan

dfex["Total"] = dfex[['DK1_DE', 'DK2_DE', 'DK2_SE', 'DK1_NL', 'DK1_NO', 'DK1_SE', 'DK1_NORDIC']].sum(1)
dfex["Total DK1"] = dfex[['DK1_DE', 'DK1_NL', 'DK1_NO', 'DK1_SE', 'DK1_NORDIC', 'DK1_DK2']].sum(1)
dfex["Total DK2"] = dfex[['DK2_DE', 'DK2_SE', 'DK1_DK2']].sum(1)
dfex.reset_index(inplace=True)
dfex.to_pickle(r"C:\Users\crans\Desktop\git\dataviz\data\ex.pkl")

dfex.set_index("HourDK", inplace=True)
df_daily = dfex.groupby([pd.Grouper(level='HourDK', freq='D')]).sum()
df_daily.reset_index(inplace=True)
df_daily.to_pickle(r"C:\Users\crans\Desktop\git\dataviz\data\exdaily.pkl")


# Add CO2:
df = pd.read_pickle(r"C:\Users\crans\Desktop\git\dataviz\data\co2.pkl")
df.set_index("HourDK", inplace = True)
df.sort_index(inplace=True)
df.index = pd.to_datetime(df.index)
df = df[df.index >= dt.datetime(2018,1,1)]

df_daily = df.groupby([pd.Grouper(level='HourDK', freq='D')]).sum()
df_daily.reset_index(inplace=True)
df_daily.to_pickle(r"C:\Users\crans\Desktop\git\dataviz\data\co2daily.pkl")


#ADD CONSUMPTION:
df = pd.read_pickle(r"C:\Users\crans\Desktop\git\dataviz\data\consumption.pkl")
df.set_index("HourDK", inplace = True)
df.sort_index(inplace=True)
df.index = pd.to_datetime(df.index)
df = df.stack().reset_index()
df.rename(columns={ 0:'Value'},inplace=True)
df.to_pickle(r"C:\Users\crans\Desktop\git\dataviz\data\consumption.pkl")
df.set_index("HourDK", inplace = True)

df_daily = df.groupby([pd.Grouper(level='HourDK', freq='D'), "PriceArea"]).sum()
# Removes dates with most data missing.
df_daily.loc["2019-05-29", "Value"] = np.nan
df_daily.loc["2019-05-30", "Value"] = np.nan
df_daily.loc["2020-07-26", "Value"] = np.nan
df_daily.reset_index(inplace=True)
df_daily.to_pickle(r"C:\Users\crans\Desktop\git\dataviz\data\consumptiondaily.pkl")


#ADD PRICES:
df = pd.read_pickle(r"C:\Users\crans\Desktop\git\dataviz\data\prices.pkl")
df.set_index("HourDK", inplace = True)
df.sort_index(inplace=True)
df.index = pd.to_datetime(df.index)
df = df[df.index >= dt.datetime(2018,1,1)]
df.reset_index(inplace=True)
df.to_pickle(r"C:\Users\crans\Desktop\git\dataviz\data\prices.pkl")

df.set_index("HourDK", inplace = True)
df_daily = df.groupby([pd.Grouper(level='HourDK', freq='D')]).mean()
df_daily.reset_index(inplace=True)
df_daily.to_pickle(r"C:\Users\crans\Desktop\git\dataviz\data\pricesdaily.pkl")


#ADD EXPORT AND IMPORT TABLES:
df = pd.read_pickle(r"C:\Users\crans\Desktop\git\dataviz\data\ex.pkl")
df.set_index("HourDK", inplace=True)
df.drop(["Total", "Total DK1", "Total DK2"], axis=1, inplace=True)
df["DK2_DK1"] = -df["DK1_DK2"]
dfi = df.copy()
dfi[dfi < 0] = np.nan
dfi.reset_index(inplace=True)
dfi.to_pickle(r"C:\Users\crans\Desktop\git\dataviz\data\imports.pkl")
dfi.set_index("HourDK", inplace = True)
dfi_daily = dfi.groupby([pd.Grouper(level='HourDK', freq='D')]).sum()
dfi_daily.reset_index(inplace=True)
dfi_daily.to_pickle(r"C:\Users\crans\Desktop\git\dataviz\data\importsdaily.pkl")
dfe = df.copy()
dfe[dfe > 0] = np.nan
dfe = dfe.abs()
dfe.reset_index(inplace=True)
dfe.to_pickle(r"C:\Users\crans\Desktop\git\dataviz\data\exports.pkl")
dfe.set_index("HourDK", inplace = True)
dfe_daily = dfe.groupby([pd.Grouper(level='HourDK', freq='D')]).sum()
dfe_daily.reset_index(inplace=True)
dfe_daily.to_pickle(r"C:\Users\crans\Desktop\git\dataviz\data\exportsdaily.pkl")




#Remove 2017 from consumption
df = pd.read_pickle(r"C:\Users\crans\Desktop\git\dataviz\data\consumption.pkl")
df = df[df["HourDK"] >= dt.datetime(2018,1,1)]
df.to_pickle(r"C:\Users\crans\Desktop\git\dataviz\data\consumption.pkl")
df = pd.read_pickle(r"C:\Users\crans\Desktop\git\dataviz\data\consumptiondaily.pkl")
df = df[df["HourDK"] >= dt.datetime(2018,1,1)]
df.to_pickle(r"C:\Users\crans\Desktop\git\dataviz\data\consumptiondaily.pkl")