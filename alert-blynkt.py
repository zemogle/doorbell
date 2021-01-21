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

def cheerlights():
    resp = requests.get('http://api.thingspeak.com/channels/1417/field/2/last.json').json()
    h = resp['field2'].lstrip('#')
    colours = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    return colours

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
    blinkt.set_pixel(pix, colours[0], colours[1], colours[2])
    for i in range(-20,20):
        b = (20 - abs(i))/20.
        blinkt.set_brightness(b)
        blinkt.show()
        time.sleep(0.05)
    reset_blinkt()


def main():
    etag = None
    url = f"https://thingspeak.com/channels/1284652/feed/last.json?api_key={l.THINKSPEAK_KEY}"
    reset_blinkt()
    colours = [255,0,0]
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
            blink_blinkt(colours=colours)
            time.sleep(60)
            continue
        if status:
            timesince = datetime.now() - status
            if timesince < timedelta(minutes=10):
                colours = cheerlights()
            if timesince < timedelta(seconds=30):
                blink_blinkt(colours=colours)
            elif timesince >= timedelta(seconds=30) and timesince < timedelta(minutes=2):
                blink_single(colours=colours, pix=1)
            elif timesince >= timedelta(minutes=2) and timesince < timedelta(minutes=5):
                blink_single(colours=colours, pix=2)
            else:
                reset_blinkt()
        time.sleep(0.1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        reset_blinkt()
        pass
