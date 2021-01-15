#!/usr/bin/env python3

import argparse
import signal
import sys
import time
import logging

from rpi_rf import RFDevice
import telepot

import local_settings as l


logging.basicConfig(level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S',
                    format='%(asctime)-15s - [%(levelname)s] %(module)s: %(message)s', )

def main():
    bot = telepot.Bot(l.telegram['token'])
    signal.signal(signal.SIGINT, exithandler)
    rfdevice = RFDevice(27)
    rfdevice.enable_rx()
    timestamp = None
    logging.info("Listening for codes on GPIO")
    while True:
       if rfdevice.rx_code_timestamp != timestamp:
           timestamp = rfdevice.rx_code_timestamp
           if str(rfdevice.rx_code) == l.DOORBELL_RF_ID:
               bot.sendMessage(l.telegram['to_user_id'], "Doorbell!")
               logging.info("Doorbell sounded")
               time.sleep(1)  # prevent registering multiple times
           elif rfdevice.rx_code == 5592321:
               logging.info("Not doorbell")
       time.sleep(0.001)
    rfdevice.cleanup()

if __name__ == "__main__":
    main()
    sys.exit(0)
