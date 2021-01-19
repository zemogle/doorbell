#!/usr/bin/env python3

import sys
import time
import logging
import requests
import blinkt
from datetime import datetime, timedelta

import local_settings as l

logging.basicConfig(level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S',
                    format='%(asctime)-15s - [%(levelname)s] %(module)s: %(message)s', )

etf = None

def parse_response(data):
    buttonid = data['field1']
    timestamp = datetime.strptime(data['created_at'],"%Y-%m-%dT%H:%M:%SZ")
    if buttonid == l.DOORBELL_RF_ID:
        return timestamp
    else:
        return False

def blink_blinkt():
    for i in range(3):
        for j in range(blinkt.NUM_PIXELS):
            blinkt.set_pixel(j, 255, 0, 0)

        blinkt.show()
        time.sleep(0.1)

        for j in range(blinkt.NUM_PIXELS):
            blinkt.set_pixel(j, 0, 0, 0)

        blinkt.show()
        time.sleep(0.2)

def main():
    etag = None
    url = f"https://thingspeak.com/channels/1284652/feed/last.json?api_key={l.THINKSPEAK_KEY}"

    while True:
        headers = {'Prefer': 'wait=120'}  # <----- add hint
        if etag:
            headers['If-None-Match'] = etag
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            etag = resp.headers.get('ETag')
            status = parse_response(resp.json())
        elif resp.status_code != 304:
            # back off if the server is throwing errors
            time.sleep(60)
            continue
        if status and (datetime.now() - status) < timedelta(minutes=10):
            blink_blinkt()
        time.sleep(0.1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
