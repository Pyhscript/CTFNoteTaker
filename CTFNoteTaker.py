#!/usr/bin/env python3

# modified ircecho.py https://gist.github.com/RobertSzkutak/1326452

import sys
import re
import socket
import string
import sqlite3
from bannedStrings import *



def handle():
    print("GETTING BUFFER\n")
    global readbuffer
    ircmsg=s.recv(1024)
    readbuffer = readbuffer+ircmsg.decode("UTF-8")
    temp = str.split(readbuffer, "\n")
    readbuffer=temp.pop()
    for line in temp:
        print(line)
        line = str.rstrip(line)
        line = str.split(line)
        if(line[0] == "PING"):
            pingpong(line[1])
        elif(line[1]=="PRIVMSG"):
            cmd=line[3]
            cmd=cmd[1:]
            if(cmd==".help"):
                help()

            elif(cmd==".startnew"):
                if(filter_msg(line[4])==False):
                    startnew(line[4])


            elif(cmd==".listchal"):
                if(len(line)>4):
                    list_chals(line[4:])
                else:
                    help()

            elif(cmd==".listctf"):
                list_CTFs()

            elif(cmd==".create"):
                if(len(line)>5):
                    if(filter_msg(line[4])==False and filter_msg(" ".join(line[5:]))==False):
                        create(line[4],line[5:])
                else:
                    help()

            elif(cmd==".add"):
                #CTF,chal,contributor,comment
                if(len(line)>6):
                    user=line[0]
                    CTF=line[4]
                    pattern=re.compile("note:(.*)")
                    pattern2=re.compile("(.*?)note:")
                    note=re.findall(pattern," ".join(line[5:]))
                    note=" ".join(note)
                    challenge=re.findall(pattern2," ".join(line[5:]))
                    challenge=" ".join(challenge)
                    if(filter_msg(note)==False):
                        add_note(CTF,challenge,line[0],note)


                else:
                    help()


            elif(cmd==".read"):
                if(len(line)>5):
                    read_note(line[4]," ".join(line[5:]))
                else:
                    help()
            elif(cmd==".joinfail"):#pm to bot if it connects but doesnt join channel
                join_chan_if_it_fails()
            elif(cmd==".quit"):
                if(len(line)>4):
                    quit(line[4])
                else:
                    help()







def format_output(rows):
    output=[]
    for i in rows:
        for j in i:
            output.append(j)
    output=" , ".join(output)
    s.send(bytes("PRIVMSG %s :output:%s\r\n" % (CHAN,output),"UTF-8"))

def check_pass(password):
    passfile=open("password","r").read()
    passfile=passfile.replace("\n","")
    if(password==passfile):
        return True
    else:
        return False

def pingpong(pong):
    s.send(bytes("PONG %s\r\n" % pong,"UTF-8"))
    print("PONG\n")

def help():
    s.send(bytes("PRIVMSG %s :.help , .startnew <CTF> , .listchal <CTF> , .listctf , .create <CTF> <chalname> , .add <CTF> <chalname> <note>, .read <CTF> <chalname> , .quit <pass>\r\n" % CHAN,"UTF-8"))
    s.send(bytes("PRIVMSG %s :Do not use whitespace in CTF name(you can use it in challenge name)\r\n" % CHAN,"UTF-8"))
    s.send(bytes("PRIVMSG %s :Prefix your note with \"note:\" (without quotes)\r\n" % CHAN,"UTF-8"))
    print("HELP\n")
def startnew(CTF):

    c.execute("INSERT INTO ctf(name) VALUES((?))",(CTF,))
    conn.commit()
    s.send(bytes("PRIVMSG %s :%s created\r\n" % (CHAN,CTF),"UTF-8"))
def list_CTFs():
    c.execute("SELECT name FROM ctf")
    rows=c.fetchall()
    format_output(rows)


def list_chals(CTF):
    #"SELECT title FROM challenge, ctf WHERE ctf.ctfID = challenge.ctfID and ctf.name = (?);
    CTF=CTF[0]
    print(CTF)
    c.execute("SELECT title FROM challenges WHERE ctfID=(SELECT ctfID FROM ctf WHERE name=(?))",(CTF,))
    rows=c.fetchall()
    format_output(rows)


def create(CTF,challenge):
    try:
        challenge=" ".join(challenge)
        c.execute("INSERT INTO challenges(title,ctfID) VALUES((?),(SELECT ctfID FROM ctf WHERE name=(?)))",(challenge,CTF))
        conn.commit()
        s.send(bytes("PRIVMSG %s :added challenge %s to %s\r\n" % (CHAN , challenge , CTF),"UTF-8"))
    except:
        s.send(bytes("PRIVMSG %s :CTF doesnt exist , if you are certain it does spam NETWORKsecurity\r\n" % CHAN,"UTF-8"))

def add_note(CTF,challenge,contributor,comment):
    print(CTF+"\n"+challenge+"\n"+contributor+"\n"+comment+"\n")
    challenge=challenge.rstrip() #trailing whitespace bug fix
    try:
        c.execute("INSERT INTO note (contributor,note,challengeID) VALUES((?),(?),(SELECT challengeID FROM challenges WHERE title=(?) AND ctfID=(SELECT ctfID FROM ctf WHERE name=(?))))",(contributor,comment,challenge,CTF))
        conn.commit()
        s.send(bytes("PRIVMSG %s :Note added\r\n" % CHAN,"UTF-8"))
    except:
        s.send(bytes("PRIVMSG %s :Error: CTF or challenge doesnt exist(at least I hope thats error and that nsm didnt completly screw me up)\r\n","UTF-8"))
        #its going to be ok

def read_note(CTF,challenge):
    c.execute("SELECT note FROM note WHERE challengeID=(SELECT challengeID FROM challenges WHERE title=(?) AND ctfID=(SELECT ctfID from ctf WHERE name=(?)))" , (challenge,CTF))
    rows=c.fetchall()
    format_output(rows)

def join_chan_if_it_fails():
    #patch because it doesnt join each time
    s.send(bytes("JOIN %s\r\n" % CHAN,"UTF-8"))

def quit(password):

    if(check_pass(password)):
        s.send(bytes("QUIT :\r\n","UTF-8"))

        conn.close()
        sys.exit()
    else:
        print("FAILED QUIT\n")






sqlite_file = "database.sqlite"
conn = sqlite3.connect(sqlite_file)
c=conn.cursor()

HOST = "irc.hackthissite.org"
PORT = 6667
CHAN="#ctf"
NICK = "CTFNoteTaker"
IDENT = "CTF_"
REALNAME = "Hal Glados"
MASTER = "NETWORKsecurity"
readbuffer=""

s=socket.socket()
s.connect((HOST, PORT))
handle()
s.send(bytes("NICK %s\r\n" % NICK, "UTF-8"))
s.send(bytes("USER %s %s Wolf :%s\r\n" % (IDENT, HOST, REALNAME), "UTF-8"))
handle()
s.send(bytes("JOIN %s\r\n" % CHAN,"UTF-8"))
s.send(bytes("PRIVMSG %s :Hello Master\r\n" % MASTER, "UTF-8"))

while(1):
    handle()
