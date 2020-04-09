import sys
import time
import logging
import threading
import malgometer
import malgogram

FORMAT = '%(asctime)s %(levelname)s %(message)s'
logging.basicConfig(filename='c:/Users/melvi/git/malgo/malgo.log',level=10, format=FORMAT)

class trex(threading.Thread):
    def __init__(self,group=None, target=None, name=None, args=(), kwargs=None):
        super().__init__(group=None, target=target, name=name)
        self.args = args
        self.trex = {"account": self.args[0]["account"],
                     "open_trades": self.args[0]["open_trades"],
                     "watched_trades": self.args[0]["watched_trades"]
                     }
        print (self.trex["account"])
        print()
        print (self.trex["open_trades"])
        print()
        print (self.trex["watched_trades"])
        print()
        return
if __name__ == "__main__":
    
    e = threading.Event()
    logging.debug("TREX is starting")
    malgo_meter = malgometer.malgometer(args=(27191676,"r6zkrtmb","MetaQuotes-Demo",e))
    malgo_meter.start()
    malgo_meter.join()
    if malgo_meter.credentials["log"] == False:
        logging.error("NOT WORKING OUT BYE!")

    else:
        logging.debug("TREX is getting account info")
        malgo_gram = malgogram.malgogram(args=(malgo_meter.credentials["log"],malgo_meter.mt,e))
        malgo_gram.start()
        malgo_gram.join()
        #trex = trex(args=(malgo_gram.malgogram,e))

