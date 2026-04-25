import socket
import time
import json
import math

IP = '127.0.0.1'
PORT = 5700

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

counter=0

while True:
    
    # this creates the message that is used for the button
    message_but = {"button_1" : str(counter)}
    # 0 or 1 is what is sent to show if button pressed or released
    if (counter == 0):
        counter=1
    else:
        counter=0
    final_message_but = json.dumps(message_but)
    #sends button message
    sock.sendto(final_message_but.encode(), (IP, PORT))

    # creates accelerometer data
    x = math.sin(time.time())
    y = math.sin(-3* time.time())
    z = math.sin(4*time.time())
    
    # turns data into a message
    message_acc = {"accelerometer": {'X': x, 'Y': y, 'Z': z}}
    final_message_acc = json.dumps(message_acc)

    # sends accerlerometer data
    sock.sendto(final_message_acc.encode(), (IP, PORT))
    
    time.sleep(1)
