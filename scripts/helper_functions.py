import pandas as pd
import os
from base import BASE_PATH
from typing import List, Set, Dict, Tuple, Optional

class data_handler:

    def __init__(self):
        self.dfexports = self.__prepare_df("exports")
        self.dfimports = self.__prepare_df("imports")
        self.dfexportsdaily = self.__prepare_df("exportsdaily")
        self.dfimportsdaily = self.__prepare_df("importsdaily")
        self.dfco2 = self.__prepare_df("co2")
        self.dfco2daily = self.__prepare_df("co2daily")
        self.dfconsumption = self.__prepare_df("consumption")
        self.dfconsumptiondaily = self.__prepare_df("consumptiondaily")
        self.dfexchange = self.__prepare_df("ex")
        self.dfexchangedaily = self.__prepare_df("exdaily")
        self.dfprices = self.__prepare_df("prices")
        self.dfpricesdaily = self.__prepare_df("pricesdaily")
        self.dfproduction = self.__prepare_df("production")
        self.dfproductiondaily = self.__prepare_df("productiondaily")

        self.dataframes = {"co2": self.dfco2,
                           "co2_daily":self.dfco2daily,
                           "consumption": self.dfconsumption,
                           "consumption_daily": self.dfconsumptiondaily,
                           "exchange": self.dfexchange,
                           "exchange_daily": self.dfexchangedaily,
                           "imports": self.dfimports,
                           "imports_daily": self.dfimportsdaily,
                           "exports": self.dfexports,
                           "exports_daily": self.dfexportsdaily,
                           "prices": self.dfprices,
                           "prices_daily": self.dfpricesdaily,
                           "production_daily": self.dfproductiondaily,
                           "production": self.dfproduction}


    def __prepare_df(self, name: str) -> pd.DataFrame:
        df = pd.read_pickle(os.path.join(BASE_PATH, 'data', f'{name}.pkl'))
        df.to_pickle(os.path.join(BASE_PATH, 'data', f'{name}.pkl'))
        df.__name__ = name
        return df

    def __find_common_index(self):
        idxpower = self.dfpower.index
        idxbalance = self.dfbalance.index
        idxprice = self.dfprice.index

        idxcommon = idxpower.intersection(idxbalance).intersection(idxprice)

        return idxcommon


