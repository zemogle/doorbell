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

def reset_blinkt():
    for j in range(blinkt.NUM_PIXELS):
        blinkt.set_pixel(j, 0, 0, 0)
    blinkt.show()

def blink_blinkt(colours):
    blinkt.set_brightness(0.5)
    for i in range(3):
        for j in range(blinkt.NUM_PIXELS):
            blinkt.set_pixel(j, colours[0], colours[1], colours[2])
        blinkt.show()
        time.sleep(0.1)
        reset_blinkt()
        time.sleep(0.2)

def blink_single(colours,pix):
    reset_blinkt()
    blinkt.set_pixel(j, colours[0], colours[1], colours[2])
    for i in range(-5,6):
        b = (5 - abs(i))/10.
        blinkt.set_brightness(b)
        blinkt.show()
        time.sleep(0.1)
    reset_blinkt()


def main():
    etag = None
    url = f"https://thingspeak.com/channels/1284652/feed/last.json?api_key={l.THINKSPEAK_KEY}"

    while True:
        headers = {'Prefer': 'wait=120'}
        if etag:
            headers['If-None-Match'] = etag
        try:
            resp = requests.get(url, headers=headers)
        except requests.exceptions.ConnectionError:
            blink_blinkt(colours=[220,118,51])
            time.sleep(60)
            continue

        if resp.status_code == 200:
            etag = resp.headers.get('ETag')
            status = parse_response(resp.json())
        elif resp.status_code != 304:
            # back off if the server is throwing errors
            blink_blinkt(colours=[255,0,0])
            time.sleep(60)
            continue
        if status:
            timesince = datetime.now() - status
            if timesince < timedelta(seconds=30):
                blink_blinkt(colours=[0,0,255])
            elif timesince >= timedelta(seconds=30) and timesince < timedelta(hours=1):
                blink_single(colours=[1, 193, 22], pix=1)
            elif timesince >= timedelta(hours=1) and timesince < timedelta(hours=4):
                blink_single(colours=[1, 193, 22], pix=2)
        time.sleep(0.1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
