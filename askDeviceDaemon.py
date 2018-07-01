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
from contextlib import contextmanager

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

os.system('clear')

sock = socket.socket(socket.AF_INET,  # Internet
                     socket.SOCK_DGRAM)  # UDP
sock.bind((UDP_IP, UDP_PORT))


class MyEvent:
    id = 0
    idStop = False
    idThread = threading.Thread


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


# Sets Roof Lights to minimum Dimming
def do_launch_web_url(id, stop, my_url):
    webbrowser.get(CHROME_PATH).open(my_url)

@contextmanager
def suppress_stdout():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:  
            yield
        finally:
            sys.stdout = old_stdout


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
        if "STOP" in strData:
            launch_this.idStop = True
            launch_this.idThread.join()


do_events()

