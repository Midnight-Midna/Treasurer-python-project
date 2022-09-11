#############################
#Authors : Faith & Midna
#Date : 9/10/2022
#Name : Treasurer Helper
#Purpose : Database frontend for financial transactions, acceessible by multiple levels of user
#############################

import os
import json
import hashlib
from decimal import *
from sys import audit
from datetime import datetime

def OpenDB():
    # convert json file to usable dictionary
    f = open("db.json",)
    db = json.load(f)
    db['balance'] = Decimal(db['balance'])
    return db

def SaveDB(dbfile):
    # save json file
    dbfile['balance'] = str(dbfile['balance'])
    jsondump = json.dumps(dbfile, indent=2)
    currentDate = datetime.fromtimestamp(datetime.now().timestamp())
    os.rename("./db.json", "db." + currentDate.strftime("%d%m%y%H%M%S") + ".json")
    f = open("db.json", "w")
    f.write(jsondump)


def SignIn(username, password):
    #read the input as a hash
    pwhash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    print(pwhash)
    database = OpenDB()
    for signin in database['signins']:
        if signin['username'] == username:
            if signin['pass'] == pwhash:
                print("Signed in successfully!")
                StartMenu(database, signin['level'])
            else:
                print("Incorrect Password")
            


def StartMenu(d, userLevel):
    print("Welcome!")
    print("$" + str(d['balance']) + " is the class' current balance")
    inputString = "\n Enter 0 to exit\n Enter 1 to display Audit logs"

    match userLevel:
        case 2:
            inputString += "\n Enter 2 to make a request\n"
        case 3:
            inputString += "\n Enter 2 to manage requests\n"
    userInput = int(input(inputString + "\nChoice: "))
    match userInput:
        case 0:
            return()
        case 1:
            #request audit and how many logs to audit
            ReadAudits(d)
        case 2:
            match userLevel:
                case 2:
                    RequestChange(d)
                case 3:
                    VerifyChange(d)
            
def ReadAudits(d):
    auditRequestAmount = int(input("How many logs would you like to view? "))
    while auditRequestAmount > 0:
        log = d['logs'][-auditRequestAmount]
        requestInEnglish = 'at ' + datetime.fromtimestamp(int(log['date'])).strftime('%m/%d/%y %H:%M:%S') + ', the balance was requested to be changed by $' + str('{:.2f}'.format(float(log['value']))) + ' for "' +str(log['desc']) + '".'
        if bool(log['accepted']):
            requestInEnglish += ' The request has been approved.'
        else:
            requestInEnglish += ' The request was denied.'

        print(requestInEnglish)
        auditRequestAmount -= 1

def RequestChange(d):
    unix_timestamp = datetime.now().timestamp()
    today = datetime.fromtimestamp(int(unix_timestamp))
    #fills out data for JSON importing
    newRequest = {
        "date"    : int(unix_timestamp),
        "value"   : str(input("What are you changing the balance by? ")),
        "desc"    : input('Why are you changing the value? '),
        "accepted": False 
    }
    confirm = input("You are requesting to change the balance by " + newRequest['value'] + ", for reason \"" + newRequest['desc'] + "\". Is this correct? (y/n):")
    #save after conformation
    if confirm == "y":
        d['pendingRequests'].append(newRequest)
        SaveDB(d)
        print("Request saved! Returning to main menu.")
        StartMenu(d, 2)
    else:
        retry = input("Canceled. Would you like to retry? (y/n):")
        if retry == 'y':
            RequestChange(d, 2)
        else:
            print("Returning to main menu.")
            StartMenu(d, 2)

def VerifyChange(d):
    counter = 1
    for request in d["pendingRequests"] :
        requestdate = datetime.fromtimestamp(int(request['date'])).strftime('%m/%d/%y %H:%M:%S')
        print("\n\nID: " + str(counter) + "\nDate: " + requestdate + "\nValue: " + request['value'] + " \nReason: " + request['desc'])
        counter += 1
    choice = input("Choose a transaction ID: ")
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

getcontext().prec = 2

SignIn(input("Username: "), input("Password: "))