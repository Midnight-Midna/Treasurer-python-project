#############################
#Authors : Faith & Midna
#Date : 9/10/2022
#Name : Treasurer Helper API
#Purpose : Database backend for financial transactions, acceessible through javascript program
#############################

import os
import json
import hashlib
from decimal import *
from datetime import datetime
from urllib import response
from flask import *
import random

def OpenDB():
    
    # convert json file to usable dictionary

    f = open("db.json",)
    d = json.load(f)

    # Some values needed conversion to str to serialize, convert back out to Decimal
    
    d['balance'] = Decimal(d['balance'])

    return d

def SaveDB(d):

    # Convert to string (it gets mad if we don't) and serialize to JSON
    d['balance'] = str(d['balance'])
    jsondump = json.dumps(d, indent=2)

    # Make database backup

    currentDate = datetime.fromtimestamp(datetime.now().timestamp())
    os.rename("./db.json", "db-" + currentDate.strftime("%d%m%y%H%M%S") + ".json")
    
    # Write updated database to file

    f = open("db.json", "w")
    f.write(jsondump)

app=Flask(__name__)

@app.route('/')
def func():
    return 'mewheniGETyou'

# Return all audit logs (no authentication, open to all users)

@app.route('/logs')
def logs():
    d = OpenDB()
    return d['logs']

@app.route('/createrequest', methods = ['POST', 'GET'])
def CreateRequest():
    d = OpenDB()
    # Gets current unix timestamp for dating the request
    unix_timestamp = datetime.now().timestamp()
    today = datetime.fromtimestamp(int(unix_timestamp))
    
    for loginToken in d['tokens']:
        if request.cookies.get('loginToken') == loginToken:
            # Constructs request from POST data and saves
            if request.method == 'POST':

                    newRequest = {
                    "date"    : int(unix_timestamp),
                    "value"   : str(request.form["change"]),
                    "desc"    : request.form['reason'],
                    "accepted": False 
                    }
                    d['pendingRequests'].append(newRequest)
                    SaveDB(d)
                    return("Request submitted!")
            else:
            # ...or returns the file to send the POST
                return app.send_static_file('makerequest.html')
    abort(403)
        

@app.route('/login',methods = ['POST', 'GET'])
def login():
    d = OpenDB()
    if request.method == 'POST':
        user = request.form['name']
        pw = request.form['pass']
        pwhash = hashlib.sha256(pw.encode('utf-8')).hexdigest()
        for signin in d['signins']:
            if signin['username'] == user:
                if signin['pass'] == pwhash:
                    match signin['level']:
                        case 2:
                            resp = make_response(render_template('admin-loggedin.html'))
                        case 3:
                            resp = make_response(render_template('treasurer-loggedin.html'))
                    
                    # login tokens are this easy? i didn't know

                    loginToken = ''
                    while len(loginToken) < 32:
                        random_integer = random.randint(97, 97 + 26 - 1)
                        flip_bit = random.randint(0, 1)
                        random_integer = random_integer - 32 if flip_bit == 1 else random_integer
                        loginToken += chr(random_integer)
                    resp.set_cookie('loginToken', loginToken)
                    d['tokens'].append({'token': loginToken, 'level': signin['level']})

                    SaveDB(d)
                    return resp
                    
                else:
                    return("Incorrect Password")
        return("Incorrect Username")
    else:
        return app.send_static_file('login.html')

@app.route('/responsemanager', methods = ['POST', 'GET'])
def ResponseManager():
    d = OpenDB()
    counter = 1
    resp = ''
    for request in d["pendingRequests"] :
        requestdate = datetime.fromtimestamp(int(request['date'])).strftime('%m/%d/%y %H:%M:%S')
        resp += "\n\nID: " + str(counter) + "\nDate: " + requestdate + "\nValue: " + request['value'] + " \nReason: " + request['desc']
        counter += 1
    return resp
    choice = request.form['Transaction ID']
    chosenRequest = d["pendingRequests"][int(choice)-1]
    requestdate = datetime.fromtimestamp(int(chosenRequest['date'])).strftime('%m/%d/%y %H:%M:%S')
    print("\n\nID: " + str(choice) + "\nDate: " + requestdate + "\nValue: " + chosenRequest['value'] + " \nReason: " + chosenRequest['desc'])
    approval = input("Would you like to (A)pprove or (D)eny this request? (N to exit) ")
    if approval == "A":
        chosenRequest['accepted'] = 'true'
        d['logs'].append(chosenRequest)
        d['balance'] += Decimal(chosenRequest['value'])
        d['balance'] = str(d['balance'])
        del d["pendingRequests"][int(choice)-1]
        SaveDB(d)
    elif approval == "D":
        chosenRequest['accepted'] = 'false'
        d['logs'].append(chosenRequest)
        del d["pendingRequests"][int(choice)-1]
        SaveDB(d)
    elif approval == "N":
        print("Exiting.")
        StartMenu(d, 2)
    else:
        print("Restarting.")
        VerifyChange(d)
        
# actual main application start

if __name__=='__main__':
    app.debug=True
    app.run()