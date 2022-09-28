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
    d = OpenDB()
    
    return render_template('welcome.html', balance = str(d['balance']))


@app.route('/meetinglogs')
def meetinglogs():
    d=OpenDB()
    requestInEnglish = ''
    for loginToken in d['tokens']:
        if request.cookies.get('loginToken') == loginToken['token']:
            meetingLogs = len(d['meetingLogs'])
            while meetingLogs > 0:
                meetingLog = d['meetingLogs'][-meetingLogs]
                requestInEnglish += 'A meeting was logged at ' + datetime.fromtimestamp(int(meetingLog['date'])).strftime('%m/%d/%y %H:%M:%S') +', with the meeting ID of ' +str(int(meetingLog['ID']))+ '. The meeting happened for the reason "' + str(meetingLog['reason']) + '". The meeting summary was "' +str(meetingLog['summary']) + '".<br>'
                meetingLogs -= 1
    return requestInEnglish

# Return all audit logs (no authentication, open to all users)
@app.route('/treasurerlogs')
def logs():
    d = OpenDB()
    requestInEnglish = ''
    logs = len(d['logs'])
    while logs > 0:
        log = d['logs'][-logs]
        requestInEnglish += '\nAt ' + datetime.fromtimestamp(int(log['date'])).strftime('%m/%d/%y %H:%M:%S') + ', The balance was requested to be changed by $' + str('{:.2f}'.format(float(log['value']))) + ' for "' +str(log['desc']) + '".'
        if bool(log['accepted']):
            requestInEnglish += ' The request has been approved.</br>'
        else:
            requestInEnglish += ' The request was denied.</br>'
        logs -= 1
    return requestInEnglish

@app.route('/createrequest', methods = ['POST', 'GET'])
def CreateRequest():
    d = OpenDB()
    # Gets current unix timestamp for dating the request
    unix_timestamp = datetime.now().timestamp()
    today = datetime.fromtimestamp(int(unix_timestamp))

    
    for loginToken in d['tokens']:
        if request.cookies.get('loginToken') == loginToken['token'] and int(loginToken['level']) != 3:
            # Constructs request from POST data and saves
            if request.method == 'POST':

                    newRequest = {
                    "date"    : int(unix_timestamp),
                    "value"   : str(request.form["change"]),
                    "desc"    : request.form['reason'],
                    "accepted": 0
                    }
                    d['pendingRequests'].append(newRequest)
                    SaveDB(d)
                    return("Request submitted!\n<a href=/createrequest>Return to Create Request</a>")
            else:
            # ...or returns the file to send the POST
                return app.send_static_file('makerequest.html')
    abort(403)

@app.route('/meetinglogger', methods = ['POST', 'GET'])
def meetinglogger():
    d = OpenDB()
    nextID = len(d['meetingLogs']) + 1
    # Gets current unix timestamp for dating the request
    unix_timestamp = datetime.now().timestamp()
    today = datetime.fromtimestamp(int(unix_timestamp))
    
    for loginToken in d['tokens']:
        if request.cookies.get('loginToken') == loginToken['token'] and int(loginToken['level']) == 1:
            # Constructs request from POST data and saves
            #needs date, reason, and summary
            if request.method == 'POST':

                    newRequest = {
                    "ID"    : nextID,
                    "date"    : int(unix_timestamp),
                    "reason"   : str(request.form["reason"]),
                    "summary"    : request.form['summary'],
                    }
                    d['meetingLogs'].append(newRequest)
                    SaveDB(d)
                    return("Log Saved<br><a href=/meetinglogger>Return to the meeting logger</a>")
            else:
            # ...or returns the file to send the POST
                return app.send_static_file('makelog.html')
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
                        case 1:
                            resp = make_response(render_template('parliamentarian-loggedin.html'))
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
                    choice
    else:
        return app.send_static_file('login.html')

@app.route('/requestmanager', methods = ['POST', 'GET'])
def ResponseManager():
    d = OpenDB()
    for loginToken in d['tokens']: 
        if request.cookies.get('loginToken') == loginToken['token'] and int(loginToken['level']) == 3:
            if request.method == 'POST':
                match request.form['Action']:
                    case 'Approve':
                        chosenRequest = d['pendingRequests'][int(request.form['ID'])-1]
                        chosenRequest['accepted'] = 1
                        d['logs'].append(chosenRequest)
                        d['balance'] += Decimal(chosenRequest['value'])
                        d['balance'] = str(d['balance'])
                        del d["pendingRequests"][int(request.form['ID'])-1]
                        SaveDB(d)
                        return('Approved!\n<a href=/requestmanager>Return to Request Manager</a>')
                    case 'Deny':
                        chosenRequest = d['pendingRequests'][int(request.form['ID'])-1]
                        chosenRequest['accepted'] = 0
                        d['logs'].append(chosenRequest)
                        del d["pendingRequests"][int(request.form['ID'])-1]
                        SaveDB(d)
                        return('Denied.\n<a href=/requestmanager>Return to Request Manager</a>')
            else:
                
                counter = 1
                request_table = ''
                for pendingrequest in d["pendingRequests"] :
                    requestdate = datetime.fromtimestamp(int(pendingrequest['date'])).strftime('%m/%d/%y %H:%M:%S')
                    request_table += "\n\nID: " + str(counter) + "\nDate: " + requestdate + "\nValue: " + pendingrequest['value'] + " \nReason: " + pendingrequest['desc']
                    counter += 1
                return render_template('requestmanager.html', request_table = request_table)
    abort(403)
    
        
# actual main application start

if __name__=='__main__':
    app.debug=True
    app.run()
