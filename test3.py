################################
##Generated with a lot of love##
##    with   EasyPython       ##
##Web site: easycoding.tn     ##
################################
import RPi.GPIO as GPIO
import pymysql
from http.server import BaseHTTPRequestHandler, HTTPServer

GPIO.setmode(GPIO.BCM)
GPIO.setup(2, GPIO.OUT)
GPIO.setup(3, GPIO.OUT)
switch1 = None
toggle1 = None
toggle2 = None


class RequestHandler_httpd(BaseHTTPRequestHandler):
    def read_from_db():
        global toggle1
        global toggle2
        c =[GPIO.LOW,GPIO.HIGH]
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

    def do_GET(self):
        global switch1
        c =[GPIO.LOW,GPIO.HIGH]
        toggle1, _, toggle2, _ = RequestHandler_httpd.read_from_db()
        messagetosend = bytes('Hello World!',"utf")
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.send_header('Content-Length', len(messagetosend))
        self.end_headers()
        self.wfile.write(messagetosend)
        switch = self.requestline
        switch = switch[5 : int(len(switch)-9)]
        print(switch)
        if (switch == 'switch1_on')|(switch == 'switch1_off')|(switch == 'switch1'):
            toggle1 = not(toggle1)
            RequestHandler_httpd.update_db("toggle1", toggle1)
            GPIO.output(2,c[toggle1])
        elif (switch == 'switch2_on')|(switch == 'switch2_off')|(switch == 'switch1_off'):
            toggle2 = not(toggle2)
            RequestHandler_httpd.update_db("toggle2", toggle2)
            GPIO.output(2,c[toggle2])


server_address_httpd = ('10.27.206.24',8080)
httpd = HTTPServer(server_address_httpd, RequestHandler_httpd)
print('Starting server....')
httpd.serve_forever()
GPIO.cleanup()

