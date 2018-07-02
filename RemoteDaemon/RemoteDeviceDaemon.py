#!/usr/bin/env python3
# udp listener (client) This is the daemon that will monitor for udp commands
# when you start this app it will attempt to connect to the stream
# This app will spawn a thread when it receives a udp command

import os
import sys
import socket
import threading
from websocket import create_connection
import json
import webbrowser
from adapt.intent import IntentBuilder
from adapt.engine import IntentDeterminationEngine

URL_TEMPLATE = "{scheme}://{host}:{port}{path}"
UDP_IP = "192.168.0.10"  # this should be the ip address of the device that the client, this software,  is running on
UDP_PORT = 20465  # this port should match that configured by the server

URL_FAITH = 'http://streamdb3web.securenetsystems.net/v5/CJTWFM'
URL_LIFE = 'https://tunein.com/radio/Life-1003-s24762/'
URL_KLOVE = 'https://tunein.com/radio/K-LOVE-Morning-Show-893-s33828/'
URL_AIR1 = 'https://tunein.com/radio/Air1-Radio-907-s33843/'
URL_NATIONAL_RADAR = 'http://www.intellicast.com/National/Radar/Current.aspx?animate=true'
URL_REGIONAL_RADAR = 'http://www.intellicast.com/Local/WxMap.aspx?latitude=44.26&longitude=-85.4&' \
                     'zoomLevel=8&opacity=1&basemap=0014&layers=0039'
CHROME_PATH = '/usr/bin/google-chrome %s'
sock = socket.socket(socket.AF_INET,  # Internet
                     socket.SOCK_DGRAM)  # UDP
sock.bind((UDP_IP, UDP_PORT))


class MyEvent:
    id = 0
    idStop = False
    idThread = threading.Thread


# Sends a response back to the mycroft device
def send_message(message, host="192.168.0.41", port=8181, path="/core", scheme="ws"):
    payload = json.dumps({
        "type": "recognizer_loop:utterance",
        "context": "",
        "data": {
            "utterances": [message]
        }
    })
    url = URL_TEMPLATE.format(scheme=scheme, host=host, port=str(port), path=path)
    ws = create_connection(url)
    ws.send(payload)
    ws.close()


# Reads keywords for Adapt-parser
def parse_keyword(keyword_file):
    start_path = sys.path[0]
    keyword_path = '/vocab/en-us/'
    fname = start_path + keyword_path + keyword_file +'.voc'
    with open(fname) as f:
        content = f.readlines()
    # you may also want to remove whitespace characters like `\n` at the end of each line
    content = [x.strip() for x in content]
    print(content)
    return content


def __initialize__():
    engine = IntentDeterminationEngine()
    launch_keyword = parse_keyword('LaunchKeyword')
    for lk in launch_keyword:
        engine.register_entity(lk, "LaunchKeyword")
    launch_intent = IntentBuilder("LaunchIntent") \
        .require("LaunchKeyword") \
        .build()
    engine.register_intent_parser(launch_intent)

    play_keyword = parse_keyword('PlayKeyword')
    for pk in play_keyword:
        engine.register_entity(pk, "PlayKeyword")
    play_intent = IntentBuilder("PlayIntent") \
        .require("PlayKeyword") \
        .build()
    engine.register_intent_parser(play_intent)


# Sets Roof Lights to minimum Dimming
def do_launch_web_url(id, stop, my_url):
    webbrowser.get(CHROME_PATH).open(my_url)


def do_events():
    while True:
        print("Waiting Until A Message Is Received")
        data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
        print("Received Message:", data.decode("utf-8"))
        strData = data.decode("utf-8")
        #
        if "play" in strData:
            launch_this = MyEvent
            launch_this.idStop = False
            launch_this.id = 901
            launch_url = ""
            if "faith" in strData:
                launch_url = URL_FAITH
            if "life" in strData:
                launch_url = URL_LIFE
            if "love" in strData:
                launch_url = URL_KLOVE
            if "air" in strData:
                launch_url = URL_AIR1
            launch_this.idThread = threading.Thread(target=do_launch_web_url,
                                                    args=(launch_this.id, lambda: launch_this.idStop, launch_url))
            launch_this.idThread.start()
        if "stop" in strData:
            launch_this.idStop = True
            launch_this.idThread.join()


# do_events()
load_keyword('LaunchKeyword')
load_keyword('PlayKeyword')
