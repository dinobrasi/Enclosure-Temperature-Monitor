#sudo python3 /home/tim/Documents/www/webserver.py

from flask import Flask, render_template
from functions import getPublicIP
import sys
import time

#net = "eth0"
net = "wlan0"
expected_ip = "192.168.1.241"# waiting for the network at boot. I know there is a setting, but it wasn't working for me.
waiting = True
counter = 0

while waiting:
    public_ip = getPublicIP(net)
    
    sys.stdout.write("[" + str(counter) + "] Waiting for IP Address " + expected_ip + ". Getting: " + public_ip + "\r")
    sys.stdout.flush()

    if expected_ip == public_ip:
        waiting = False
    else:
        counter = counter + 1
        
        if counter == 1000:
            waiting = False 
    
    time.sleep(1)# waiting for the network at boot. I know there is a setting, but it wasn't working for me.

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.route('/')
def index():
    f = open("/home/tim/Documents/www/templates/index.html", "r")
    return f.read()
    #return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=False, host=public_ip, port=80)