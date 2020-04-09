import os
import sys
import time
import logging
import threading
import MetaTrader5 as mt


class malgometer(threading.Thread):
    def __init__(self,group=None, target=None, name=None, args=(), kwargs=None):
        super().__init__(group=None, target=target, name=name)

        self.mt = mt
        self.args = args
        self.kwargs = kwargs
        self.credentials = {"login":args[0],"password":args[1],"server":args[2]
                            ,"event":args[3],"log":False,"timeout":5.0}

        return

    def run(self):
        try:
            logging.info("setting up profile")
        except Exception as e:
            logging.error(f"{self.__class__.__name__}:run: is not starting:{e}")
        try:
            init = threading.Timer(0.01,function=self.init)
            log = threading.Timer(0.01,function=self.mt_log)
            init.start()
            #init.join(1.0)
            while init.is_alive():
                #logging.debug("waiting for init response")
                self.credentials["event"].wait(1.0)
            else:
                logging.info("loging in....")
                log.start()
                #log.join(1.0)
                while log.is_alive():
                    #logging.debug("Waiting for MT5 response")
                    self.credentials["event"].wait(1.0)
                if self.credentials["log"]== False:
                    return
                elif self.credentials["log"]== True:
                    self.credentials["event"].set()
                    return self.mt

        except Exception as e:
            logging.error(f"{self.__class__.__name__}:run:Timed out: {e}")
            return
    def init(self):
        meter = self.mt.initialize()
        while meter != True:
            self.credentials["event"].wait(2.0)
            if meter != True:
                logging.error(f"{self.__class__.__name__}:init:FAILED INITIALIZING: check your internet connection")
                return
        if meter == True:
            logging.info(f"{self.__class__.__name__}:init: SUCCESSFULY INITIALIZED")
            return
    def mt_log(self):
        log = mt.login(self.credentials["login"],
        self.credentials["password"],self.credentials["server"])
        while log != True:
            try:
                self.credentials["event"].wait(2)
                if log != True:
                    logging.error(f"{self.__class__.__name__}:log: FAILED LOG IN: check credentials")
                    return

            except Exception as e:
                logging.error(f"{self.__class__.__name__}:mt_log: {e}")
        if log == True:
            self.credentials["log"] = True
            logging.info(f"{self.__class__.__name__}:log: SUCCESSFULY LOGGED IN")            
            return
if __name__=="__main__":
    e = threading.Event()
    T = malgometer(args=(27191676,"r6zkrtmb","MetaQuotes-Demo",e))
    T.start()
    T.join()