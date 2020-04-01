import math
import time
import decimal
import json
import MetaTrader5 as mt
from malgo import malgogram
from malgo import malgometer
from datetime import datetime
from datetime import timedelta


mt.initialize()

class malgo:
    def __init__(self):
        __account, __open_positon = mt.account_info(), mt.positions_get()
    def  set_stage(self,__open_positon):
        """ 
        leverage = __account[2]
        balance = __account[10]
        limit_orders = __account[3]
        equity = __account[13]
        margin = __account[14]
        margin_free = __account[15]"""

        profit = __account[12]
        margin_level = round(__account[16],2)
        name = __account[24]
        try:
            if len(__open_positon) > 0:
                exchange_rate = __open_positon[0][10]
                new_exchange_rate = __open_positon[0][13]
                symbol = __open_positon[0][16]  
                self.get_malgo(name,margin_level,profit,exchange_rate,new_exchange_rate,symbol)
                self.prepare_trade()
                self.get_ticks() 
            else:
                self.get_ticks()
        except Exception as e:
            print(e)
    def get_ticks(self):
        eur_usd_tick, usd_jpy_tick = mt.symbol_info_tick("EURUSD"), mt.symbol_info_tick("USDJPY")
        eur_usd_time = self.get_local_time(eur_usd_tick[0])
        usd_jpy_time = self.get_local_time(usd_jpy_tick[0])
        eur_usd = {"bid":eur_usd_tick[1],"ask":eur_usd_tick[2],"LT": eur_usd_time}
        usd_jpy = {"bid":usd_jpy_tick[1],"ask":usd_jpy_tick[2],"LT": usd_jpy_time}

        self.trades = {"EURUSD":eur_usd, "USDJPY":usd_jpy}
    def get_malgo(self,name,margin_level,profit,exchange_rate,new_exchange_rate,symbol):

        #volume = __open_positon[0][9]
        #swap = __open_positon[0][14]
        #stop_loss = __open_positon[0][11]
        #stop_loss = __open_positon[0][12]
        
        select_time = self.get_local_time(mt.symbol_info_tick("EURUSD")[0])

        self.trade_positions = [{"Account Name":name, "Margin Level": round(margin_level,2),
            "Symbol": symbol,"exchnage rate": exchange_rate,"Current Exchange Rate": new_exchange_rate,"Profit":profit,"Local Time":select_time}]
    def get_local_time(self,raw_time):
        raw_time = time.ctime(raw_time)
        date_time = datetime.strptime(raw_time, '%a %b %d %H:%M:%S %Y')
        local_date_time = date_time - timedelta(hours=3)
        local_date_time_string = local_date_time.strftime('%a %b %d %H:%M:%S %Y')

        return local_date_time_string
    def prepare_trade(self):

if __name__ == "__main__":
    trial = malgo()
    with open('c:/Users/melvi/git/malgo/malgo_says.json','a+') as ch:
        for trad in trial.trades:
            json.dump({trad:trial.trades[trad]},ch)
            ch.write('\n')
        try:
            json.dump(trial.trade_positions,ch)
        except AttributeError:
            ch.write('\n')
        