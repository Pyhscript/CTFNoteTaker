import sys
import re
import socket
import string
import sqlite3
from Utilities.conf import *
from Utilities.StringUtils import *
from Utilities.permissionUtils import *
from adminCommands.error import *
from adminCommands.quit import *
from adminCommands.deleteCTF import *
from adminCommands.deleteChal import *
from adminCommands.deleteNote import *
from adminCommands.restart import *
from adminCommands.exportCTF import *
from adminCommands.importCTF import *
from adminCommands.sudo import *


#Some check for user permission
def adminCmdParser(user,line,cmd):
    Perm = False
    print(line)
    if("MASTER" in ADMINCOMMANDMODE.upper()):
        if(Perm == False):
            if(userIsMaster(user)):
                Perm = True
    if("PASSWORD" in ADMINCOMMANDMODE.upper()):
        if(Perm == False):
            if(len(line) > 4):
                if(check_pass(line[4].strip())):
                    Perm = True
                    del line[4]
            else:
                printUser("You must enter the password.",user)
                return
    if(line[len(line)-1].lower() == "public"):
        user = CHAN
        del line[len(line)-1]

    if(Perm == False):
        printUser("You don't have enough perms to use this command!",user)
        return

    cmd = cmd.lower()
    if(cmd=="deletectf"):
        adminDeleteCTF(user,line)
    elif(cmd.startswith("deletechal")):
        adminDeleteChal(user,line)
    elif(cmd == "deletenote"):
        adminDeleteNote(user,line)
    elif(cmd.startswith("export")):
        adminExportCTF(user,line)
    elif(cmd.startswith("import")):
        adminImportCTF(user,line)
    elif(cmd=="sudo"):
        adminSudo(user,line)
    elif(cmd=="help"):
        adminHelp(user)
    elif(cmd=="quit"):
        adminQuit(user)
    elif(cmd=="restart"):
        adminRestart(user)
    elif(cmd=="error"):
        throwErrorAdminCMD(user,line)

def adminHelp(user):
    printUser("<var> denotes optional parameter, [var] denotes required parameter",user)
    printUser("If password mode is enabled, the password must be the first parameter.",user)
    printUser("If you add 'public' as the final parameter, all output will be put in the main chat.",user)
    printUser("~deleteCTF <-v> [ctfname] - deletes a CTF ",user)
    printUser("~deleteChal <-v> [ctfname] [chalname] - deletes a challenge from a given CTF",user)
    printUser("~deleteNote [ctfname] - deletes a Note ",user)
    printUser("~exportCTF [ctfname] <filename> - Exports the CTF, use all instead of ctfname to export all ctfs.",user)
    printUser("~importCTF [filename] - Imports all the CTF's from a given file.",user)
    printUser("~sudo [user] [cmd] - Runs a regular command as a given user. ",user)
    printUser("~error - Generates a sample error for testing purposes.",user)
    printUser("~quit - Shuts me down :(",user)
    printUser("~restart - Restarts me!",user)
