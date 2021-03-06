import sys
import re
import socket
import string
import sqlite3
from Utilities.conf import *
from Utilities.StringUtils import *
from commands.formatoutput import *
from Utilities.dbUtils import *

def list_chals(user,line):
    if(len(line)>4):
        c = getC()
        #"SELECT title FROM challenge, ctf WHERE ctf.ctfID = challenge.ctfID and ctf.name = (?);
        CTF=line[4:]
        CTF=CTF[0]
        print(CTF)
        if(CTFExists(CTF)):
            c.execute("SELECT title FROM challenges WHERE ctfID=(?);",(getCTFIDByName(CTF),))
            rows=c.fetchall()
            if(len(rows) > 0):
                format_output(rows,user)
            else:
                #detect this in the future
                printUser("This CTF has no challenges?",user)
        else:
            printUser("This CTF does not exist",user)
    else:
        printUser("Please enter CTF name.",user)
