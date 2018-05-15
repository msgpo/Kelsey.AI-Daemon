#!/usr/bin/env python3
# udp listener (client) This is the daemon that will monitor for udp commands
# when you start this app it will attempt to connect to the stream
# This app will spawn a thread when it receives a udp command

import os
import sys
import socket
import threading
import time
import configparser
import webbrowser
#from playsound import playsound
from contextlib import contextmanager

UDP_IP = "4.27.1.181"  # this should be the ip address of the device that the client, this software,  is running on
UDP_PORT = 20465  # this port should match that configured by the server

url_Faith = 'http://streamdb3web.securenetsystems.net/v5/CJTWFM'
url_Life = 'https://tunein.com/radio/Life-1003-s24762/'
url_KLove = 'https://tunein.com/radio/K-LOVE-Morning-Show-893-s33828/'
url_Air1 = 'https://tunein.com/radio/Air1-Radio-907-s33843/'
url_NationalRadar = 'http://www.intellicast.com/National/Radar/Current.aspx?animate=true'
url_RegionalRadar = 'http://www.intellicast.com/Local/WxMap.aspx?latitude=44.26&longitude=-85.4&zoomLevel=8&opacity=1&basemap=0014&layers=0039'

chrome_path = '/usr/bin/google-chrome %s'

os.system('clear')

sock = socket.socket(socket.AF_INET,  # Internet
                     socket.SOCK_DGRAM)  # UDP
sock.bind((UDP_IP, UDP_PORT))

class myEvent:
    id = 0
    idStop = False
    idThread = threading.Thread


# Sets Roof Lights to minimum Dimming
def do_launchWebURL(id, stop, myURL):
    #print("Preparing to Launch Music", id)
    webbrowser.get(chrome_path).open(myURL)

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
            launchThis = myEvent
            launchThis.idStop = False
            launchThis.id = 901
            launchURL = ""
            if "faith" in strData:
                launchURL = url_Faith
            if "life" in strData:
                launchURL = url_Life
            if "love" in strData:
                launchURL = url_KLove
            if "air" in strData:
                launchURL = url_Air1
            launchThis.idThread = threading.Thread(target=do_launchWebURL,
                                                  args=(launchThis.id, lambda: launchThis.idStop,launchURL))
            launchThis.idThread.start()
        if "STOP" in strData:
            launchThis.idStop = True
            launchThis.idThread.join()

do_events()

