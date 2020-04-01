import re
import math
import json
import decimal
import warnings
import pandas as pd
import MetaTrader5 as mt
from datetime import datetime
warnings.simplefilter(action='ignore', category=FutureWarning)

class malgo:

    def __init__(self, lot, type, base, volume, exchange_rate,
        new_exchange_rate, leverage, balance,target,swap,time_base):

        mt.initialize()
        self.exchange_rate = exchange_rate
        self.new_exchange_rate = new_exchange_rate
        self.time = time_base
        self.volume = volume
        self.base = base
        
        self.swap = round(swap,3)
        self.type = type
        self.set_lot(lot)
        self.set_expo()

        self.calculate_pip_value()

        self.set_ROC()
        self.set_ERD(target)

        
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
    def set_ROC(self):
        self.rate_of_currency_change = round(self.exchange_rate/self.new_exchange_rate,5)
    def set_ERD(self,target):
        target_exchange = (target * pow(10,self.exponent)) / self.price_per_pip_change
        if self.type == "sell":
            self.exchange_rate_difference = round(self.exchange_rate\
                - self.new_exchange_rate,5)
            self.target_exchange = target_exchange / self.rate_of_currency_change
            self.target_exchange = round((self.target_exchange - self.exchange_rate) / -1,5)
        elif self.type == "buy":
            self.exchange_rate_difference = round(self.new_exchange_rate\
                - self.exchange_rate,5)
            self.target_exchange = round((target_exchange / self.rate_of_currency_change)\
                + self.exchange_rate,5)
    def calculate_pip_value(self):
        one_pip = math.pow(10, self.exponent)
        pip_change = one_pip/self.exchange_rate
        self.price_per_pip_change = round(pip_change * self.lot_size,8)
    def get_profit(self):
        get_rates = None
        if self.base[:3].lower() != "usd":
            try:
                self.us_base = self.base[:3].upper() + "USD"
                get_rates = mt.copy_rates_from(self.us_base,
                    mt.TIMEFRAME_M1,self.time,10)
                if get_rates == None:
                    self.us_base = "USD" + self.base[:3].upper() 
                    get_rates = mt.copy_rates_from(self.us_base,
                        mt.TIMEFRAME_M1,self.time,10)
                    if get_rates == None:
                        self.bid = 1.0
                        self.ask = 1.0
            except Exception as e:
                print(self.base,self.us_base,e)
        """
        elif self.base[:3].lower() == "usd":
            try:
                self.us_base = self.base[3:6].upper() + "USD"
                get_rates = mt.copy_rates_from(self.us_base,
                    mt.TIMEFRAME_M1,self.time,10)
                if get_rates == None:
                    self.us_base = "USD" + self.base[3:6].upper()
                    get_rates = mt.copy_rates_from(self.us_base,
                        mt.TIMEFRAME_M1,self.time,10)
                    if get_rates == None:
                        self.bid = 1.0
                        self.ask = 1.0
            
            except Exception as e:
                print(self.base,self.us_base,e)
            """
        get_currency = round(self.exchange_rate_difference\
            * self.price_per_pip_change,8)
        bare_currency = get_currency * pow(10, abs(self.exponent))
        if get_rates != None:
            self.bid = get_rates[0][1]
            self.ask = get_rates[0][3]
            self.profit = round(bare_currency * self.ask,2)
            self.profit = self.profit + self.swap
            round(self.profit,2)
        else:
            self.profit = bare_currency + self.swap
            self.profit = round(self.profit,2)
    def get_margin(self,leverage,balance):
        margin = self.lot_size * self.exchange_rate/leverage
        equity = balance + self.profit
        #free_margin = equity - margin
        #margin_level = equity/margin * 100
    def get_self(self):
        data = {"Exchange rate":self.exchange_rate,"Exponent":self.exponent,
        "New Exchange":self.new_exchange_rate,"Volume":self.volume,"Lot ":self.lot_size,"Profits":self.profit}
        return data
    def send_data(self):
        data = self.get_self()
        with open('c:/Users/melvi/git/malgo/malgo_compare.json','a+') as ch:
            json.dump(data,ch)
            ch.write('\n')
#cargo = malgo("std", "sell", "eur", 0.12, 1.10370, 1.09715, 500, 50,100)

df = pd.read_excel('C:/Users/melvi/Documents/ReportHistory-26754957.xlsx')
ds = df[6:8]
ds.columns = ['Time_o','Position','Symbol',
           'Type','Volume','Price', 's_l','t_p','Time_c','N_Price','Commision',
           'Swap','Profit','del']
ds.pop('del')
datum = ds.reset_index()
datum.pop('index')

for i in range(0,len(datum)):
    date_t = datum['Time_o'][i][:-4]
    date_time = datetime.strptime(date_t,"%Y.%m.%d %H:%M:%S")

    cargo = malgo(
        "std",
        datum['Type'][i],
        datum['Symbol'][i],
        float(datum['Volume'][i]),
        float(datum['Price'][i]),
        float(datum['N_Price'][i]),
        500,
        50,
        100,
        float(datum['Swap'][i])/10.0,
        date_time
        )
    p = datum['Profit'][i]
    c = cargo.profit
    gc = datum['Symbol'][i]
    x = c - p
    print(f'{i}:{gc}{round(x,2)}')