import sys
import math
import time
import json
import decimal
import logging
import threading
import malgometer
from datetime import datetime
from datetime import timedelta


class malgogram(threading.Thread):
    def __init__(self,group=None, target=None, name=None, args=(), kwargs=None):
        super().__init__(group=None, target=target, name=name)
        self.args = args
        self.handler = {"log":args[0],"mt":args[1], "event":args[1]}
        account, open_position =self.handler["mt"].account_info(),self.handler["mt"].positions_get()
        self.malgogram = {"account":account, "open_trades":open_position, "watched_trades": {} }
        return
    
    def run(self):
        try:    
            if self.handler["log"] == True:
                set_stage =threading.Thread(target=self.set_stage)
                send_json =threading.Thread(target=self.send_json)
                set_stage.start()
                set_stage.join()
                send_json.start()
                send_json.join()
                logging.info(f"{self.__class__.__name__}:run: was SUCCESSFUL")
            else:
                logging.error(f"{self.__class__.__name__}:run:Sorry INITIALIZATION FAILED")
                return
        except Exception as e:
            logging.error(f"{self.__class__.__name__}:run: {e}")    
    def  set_stage(self):
        try:
            if len(self.malgogram["open_trades"]) > 0:
                self.get_malgogram()
                #self.prepare_trade()
                self.get_ticks() 
            else:
                self.get_ticks()
        except Exception as e:
            logging.error(f"{self.__class__.__name__}staging: Failure {e}")
    def get_ticks(self):
        try:
            eur_usd_tick, usd_jpy_tick =self.handler["mt"].symbol_info_tick("EURUSD"),self.handler["mt"].symbol_info_tick("USDJPY")
            eur_usd_time = self.get_local_time(eur_usd_tick[0])
            usd_jpy_time = self.get_local_time(usd_jpy_tick[0])
            eur_usd = {"bid":eur_usd_tick[1],"ask":eur_usd_tick[2],"LT": eur_usd_time}
            usd_jpy = {"bid":usd_jpy_tick[1],"ask":usd_jpy_tick[2],"LT": usd_jpy_time}
            self.malgogram["watched_trades"] = {"EURUSD":eur_usd, "USDJPY":usd_jpy}
        except Exception as e:
            logging.error(f"{self.__class__.__name__}:get_ticks: Error {e}")
        return
    def get_malgogram(self):
        try:
            select_time = self.get_local_time(self.handler["mt"].symbol_info_tick("EURUSD")[0])
            self.local_time = select_time
        except Exception as e:
            logging.error(f"{self.__class__.__name__}:get_malgogram: {e}")
        return
    def get_local_time(self,raw_time):
        try:    
            raw_time = time.ctime(raw_time)
            date_time = datetime.strptime(raw_time, '%a %b %d %H:%M:%S %Y')
            local_date_time = date_time - timedelta(hours=3)
            local_date_time_string = local_date_time.strftime('%a %b %d %H:%M:%S %Y')
        except Exception as e:
            logging.error(f"{self.__class__.__name__}:get_local_time: {e}")
        return local_date_time_string
    def send_json(self):
        try:
            with open('c:/Users/melvi/git/malgo/malgo_says.json','a+') as ch:
                json.dump("====================================== \
                ==================================================",ch)
                ch.write('\n')
                json.dump({"LT":self.local_time},ch)
                ch.write('\n')
                json.dump({"Account":self.malgogram["account"][24]},ch)
                ch.write('\n')
                json.dump(
                    {
                    "symbol": self.malgogram["open_trades"][0][16],
                    "profit": self.malgogram["open_trades"][0][15],
                    "current positon": self.malgogram["open_trades"][0][10],
                    "open postion": self.malgogram["open_trades"][0][13]},ch)
                ch.write('\n')
                for trad in self.malgogram["watched_trades"]:
                    json.dump({trad:self.malgogram["watched_trades"][trad]},ch)
                    ch.write('\n')
                json.dump("====================================== \
                ==================================================",ch)
                ch.write('\n')
        except Exception as e:
            logging.error(f"{self.__class__.__name__}:send_json: {e}")
        return

