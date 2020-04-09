import re
import math
import json
import decimal
import asyncio
import warnings
import multiprocessing
import pandas as pd
import MetaTrader5 as mt
from datetime import datetime
from malgometer import malgometer

warnings.simplefilter(action='ignore', category=FutureWarning)

class malgogram:
    def __init__(self, lot, type, base, volume, exchange_rate,new_exchange_rate, leverage, balance,target,swap,time_base=None):
        self.volt = \
        {
            "time":time_base,
            'base':base,
            'price_per_pip_change':None,
            'ERD':None,'us_base':None,
            'bid':None,
            'ask':None,
            'profit':None,
            'swap':round(swap,3),
            'rate_of_currency_change':None
        }
        self.fund = \
            {
                "target":target,
                "target_rate":None
            }
        self.value = \
        {
        "exchange_rate": exchange_rate,
        "new_exchange_rate": new_exchange_rate,
        "volume": volume,
        "type": type
        }
        self.set_lot(lot)
        self.set_expo()
        self.calculate_pip_value()
        self.set_ROC()
        self.set_ERD()   
        self.get_profit()
        self.get_margin(leverage,balance)
        self.send_data()
    def set_lot(self,lot):
        if lot == "std":
            self.one_lot = 100000
        elif lot == "micro":
            self.one_lot = 1000

        self.lot_size = self.volume * self.one_lot
    def set_expo(self):
        get_exponent = decimal.Decimal(f'{self.exchange_rate}').as_tuple()     
        self.exponent = get_exponent[2]
        if self.exponent < -4:
            self.exponent = self.exponent + 1
        elif self.exponent > -4:
            self.exponent = self.exponent + 1
    def calculate_pip_value(self):
        one_pip = math.pow(10, self.exponent)
        pip_change = one_pip/self.exchange_rate
        self.volt['price_per_pip_change'] = round(pip_change * self.lot_size,8)
    def set_ROC(self):
        self.volt['rate_of_currency_change'] = round(self.exchange_rate/self.new_exchange_rate,5)
    def set_ERD(self):
        target_exchange = (self.fund['target'] * pow(10,self.exponent)) / self.volt['price_per_pip_change']
        if self.type == "sell":
            self.volt['ERD'] = round(
                self.exchange_rate - self.new_exchange_rate,5)
            self.fund['target_rate'] = target_exchange / self.volt['rate_of_currency_change']
            self.fund['target_rate'] = round((self.fund['target_rate'] - self.exchange_rate) / -1,5)
        elif self.type == "buy":
            self.volt['ERD'] = round(self.new_exchange_rate\
                - self.exchange_rate,5)
            self.fund['target_rate'] = round((target_exchange / self.volt['rate_of_currency_change'])\
                + self.exchange_rate,5)
    def get_profit(self):
        get_rates = None
        if self.volt['base'][:3].lower() != "usd":
            try:
                self.volt['us_base'] = self.volt['base'][:3].upper() + "USD"
                get_rates = mt.copy_rates_from(self.volt['us_base'],
                    mt.TIMEFRAME_M1,self.volt['time'],10)
                if get_rates == None:
                    self.volt['us_base'] = "USD" + self.volt['base'][:3].upper() 
                    get_rates = mt.copy_rates_from(self.volt['us_base'],
                        mt.TIMEFRAME_M1,self.volt['time'],10)
                    if get_rates == None:
                        self.volt['bid'] = 1.0
                        self.volt['ask'] = 1.0
            except Exception as e:
                print(self.volt['base'],self.volt['us_base'],e)
        get_currency = round(self.volt['ERD']\
            * self.volt['price_per_pip_change'],8)
        bare_currency = get_currency * pow(10, abs(self.exponent))
        if get_rates != None:
            self.volt['bid'] = get_rates[0][1]
            self.volt['ask'] = get_rates[0][3]
            self.volt['profit'] = round(bare_currency * self.volt['ask'],2)
            self.volt['profit'] = self.volt['profit'] + self.volt['swap']
            round(self.volt['profit'],2)
        else:
            self.volt['profit'] = bare_currency + self.volt['swap']
            self.volt['profit'] = round(self.volt['profit'],2)
    def get_margin(self,leverage,balance):
        margin = self.lot_size * self.exchange_rate/leverage
        equity = balance + self.volt['profit']
        #free_margin = equity - margin
        #margin_level = equity/margin * 100
    def get_self(self):
        data = {"Exchange rate":self.exchange_rate,"Exponent":self.exponent,
        "New Exchange":self.new_exchange_rate,"Volume":self.volume,"Lot ":self.lot_size,"Profits":self.volt['profit']}
        return data
    def send_data(self):
        data = self.get_self()
        with open('c:/Users/melvi/git/malgo/malgo_compare.json','a+') as ch:
            json.dump(data,ch)
            ch.write('\n')

"""
if __name__ == "__main__":
    malgo_init = multiprocessing.Process(name="malgometer", target=malgometer, args=(27093332,"8juvazuy","MetaQuotes-Demo"))
    malgo_init.start()    """