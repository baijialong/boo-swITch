# -*- coding: utf-8 -*-
"""
Created on Sat Mar 23 18:48:44 2019

@author: Chryston
"""

import RPi.GPIO as GPIO
import timeloop
import pymysql
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import timedelta
import threading
import time
import sys

## GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup (2, GPIO.OUT)
GPIO.setup (3, GPIO.OUT)
GPIO.setup (15, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

#Initialisation
c =[GPIO.LOW,GPIO.HIGH]
toggle1 = None
toggle2 = None

def toggle_switch1():
    global toggle1
    toggle1 = not(toggle1)
    GPIO.output(2,c[toggle1])
    
def toggle_switch2():
    global toggle2
    toggle2 = not(toggle2)
    GPIO.output(3,c[toggle2])


def update_db(component, state):
    db = pymysql.connect("localhost","root","password","boobooswitch")
    cursor = db.cursor()
    
    # deciphering component
    if "1" in component:
        switchno = 'switch1'
    elif "2" in component:
        switchno = 'switch2'
    if "toggle" in component:
        statetype = 'Relay_state'
    elif "switch" in component:
        statetype = 'Switch_state'
        
    
    sql = "UPDATE Switch SET {} = {} WHERE SwitchNo = '{}'".format(
        statetype, state, switchno)
    cursor.execute(sql)
    db.commit()
    db.close()
    
tl = timeloop.Timeloop()
@tl.job(interval=timedelta(seconds=1))
def check_switch1_state():
    stime = time.time()
    i = 0
    while time.time() < stime + 0.1:
        i += GPIO.input(15)
    print(i)
    if i > 14:
        print("Switch1: ON")
        switch1state = 1
    else:
        print("Switch1: OFF")
        switch1state = 0
    update_db("switch1", switch1state)

@tl.job(interval=timedelta(seconds=1))
def read_from_db():
    global toggle1
    global toggle2
    db = pymysql.connect("localhost","root","password","boobooswitch")
    cursor = db.cursor()
    sql = "SELECT * FROM Switch".format(0)
    cursor.execute(sql)
    result = cursor.fetchall()
    for data in result:
        if data[0] =="switch1":
            _,toggle1_,switch1 = data
            #check if there is a difference in value retrieved
            if toggle1_ != toggle1:
                GPIO.output(2,c[toggle1_])
            toggle1 = toggle1_
            
        elif data[0] == "switch2":
            _,toggle2_, switch2 = data
            
            #check if there is a difference in value retrieved
            if toggle2_ != toggle2:
                GPIO.output(2,c[toggle2_])
            toggle2 = toggle2_
            
    print (" toggle1: {} switch1: {} \n toggle2: {} switch2: {}".format(
        bool(toggle1),bool(switch1),bool(toggle2),bool(switch2)))
    db.close()
    return (toggle1,switch1,toggle2,switch2)
toggle1,switch1,toggle2,switch2 = read_from_db()

tl.start()
    
while True:
    key = input("Select switch to toggle: \n")
    #There is a 0.5seocnds delay in the switch sensor, because the capacitor requires time to dissipate its energy
    if key == "1":
        toggle_switch1()
        update_db("toggle1", toggle1)
        t = threading.Timer(0.6, check_switch1_state)
        t.start()
    elif key == "2":
        toggle_switch2()
        update_db("toggle2", toggle2)
    elif key == "x":
        tl.stop()
        sys.exit()

