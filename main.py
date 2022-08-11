from ast import dump
import getopt
import shlex
import sys
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
import ctypes
import signal
import os
import time
import re
import subprocess
import logging
# creating an instance of the watchdog.observers.Observer from watchdogs class.
from watchdog.observers import Observer
from ctypes import *
import wmi
import pythoncom
from pyfiglet import Figlet


_handle_pat = re.compile(r'(.*?)\s+pid:\s+(\d+).*[0-9a-fA-F]+:\s+(.*)')


custom_fig = Figlet(font='larry3d')
print(custom_fig.renderText('CyperGate'))
print('devloped by Abdulrhman Al-Obaidi for CyperGate')
print('Our Team: Ghala Al-Obuod, Dhay Al-Harbi, Rashidah Al-Rashidi, Yousef Al-Yami ')

document = os.path.join(os.path.join(
    os.environ['USERPROFILE']), 'Documents') + '\\'
desktop = os.path.join(os.path.join(
    os.environ['USERPROFILE']), 'Desktop') + '\\'

dump_enabled = False
unmount_enabled = False

def memdump():
    handlePath = '"' + os.path.dirname(os.path.realpath(
        __file__)) + '\winpmem_mini_x64_rc2" memdump.raw' 
    print('dumpping memory')
    process = subprocess.Popen(handlePath,shell=True,stdout=subprocess.PIPE , stderr=subprocess.STDOUT)
    process.wait()
    print('dumpping done')


def unmount():
    import win32api
    drives = win32api.GetLogicalDriveStrings()
    drives = drives.split('\000')[:-1]
    print (drives)
    for drive in drives:
        # if(drive != 'C:\\'):
        try:
            lines = subprocess.check_output('mountvol %s /p' % drive.rstrip('\\')).splitlines()
            print(lines)
        except:
            pass


def gameOver():
    if dump_enabled:
        memdump()
    if unmount_enabled:
        unmount()
    os.system('shutdown /s /f /t 0')


def open_files(name):
    handlePath = os.path.dirname(os.path.realpath(
        __file__)) + '\\handle.exe -accepteula "' + name + '"'
    lines = subprocess.check_output(handlePath).splitlines()
    results = (_handle_pat.match(line.decode('mbcs')) for line in lines)
    return [m.groups() for m in results if m]


def list_all_processes():
    handlePath = os.path.dirname(os.path.realpath(
        __file__)) + '\\handle.exe -accepteula'
    lines = subprocess.check_output(handlePath).decode('utf-8')
    regex = r'(pid: \d+)+'
    pid = re.findall(regex, lines)
    # print(pid)
    # results = (_handle_pat.match(line.decode('mbcs')) for line in lines)
    return pid


def generateFiles():

    f = open(document + '\\test.test', "w")
    f.write("Don't modify this file at all. if it is modified it going to start security measures that you will regret.")
    f.close()
    f = open(desktop + '\\test.test', "w")
    f.write("Don't modify this file at all. if it is modified it going to start security measures that you will regret.")
    f.close()


class OnMyWatch:

    # Set the directory on watch
    document = os.path.join(os.path.join(
        os.environ['USERPROFILE']), 'Documents') + '\\'
    desktop = os.path.join(os.path.join(
        os.environ['USERPROFILE']), 'Desktop') + '\\'
    watchDirectory = desktop
    generateFiles()
    # memdump()
    # print(desktop)
    watchDirectory2 = document

    def __init__(self, mode):
        self.observer = Observer()
        print(mode)

    def run(self):
        event_handler = Handler()
        self.observer.schedule(
            event_handler, self.watchDirectory, recursive=True)
        self.observer.start()
        self.observer.schedule(
            event_handler, self.watchDirectory2, recursive=True)

        try:
            while True:
                time.sleep(5)
        except:
            self.observer.stop()
            print("Observer Stopped")

        self.observer.join()


def killNewOnly():
    print('hydra killing started')
    pythoncom.CoInitialize()
    c = wmi.WMI()

    watcher = c.watch_for(
        notification_type="Creation",
        wmi_class="Win32_Process",
        # delay_secs=3,
    )
    if dump_enabled:
        memdump()
    if unmount_enabled:
        unmount()
    while 1:
        try:
            process_created = watcher()
            print(process_created.Name)
            print(process_created.ProcessId)
            os.kill(int(process_created.ProcessId), signal.SIGTERM)
            PROCESS_TERMINATE = 1
            handle = ctypes.windll.kernel32.OpenProcess(
                PROCESS_TERMINATE, False, process_created.ProcessId)
            ctypes.windll.kernel32.TerminateProcess(handle, -1)
            ctypes.windll.kernel32.CloseHandle(handle)
        except:
            pass




class Handler(FileSystemEventHandler):

    @staticmethod
    def on_any_event(event):
        fi = open_files(event.src_path.replace('\\', '/'))
        print(fi)
        if(len(fi) > 0):
            print(fi[0][1])
            print(os.path.basename(fi[0][2]))
            if(os.path.basename(fi[0][2]) == 'test.test'):
                os.kill(int(fi[0][1]), signal.SIGTERM)
                unmount()
            if(mode == 'normal'):
                killNewOnly()
            elif(mode == 'super'):
                gameOver()
       
        if event.is_directory:
            return None
        elif event.event_type == 'created':
            # Event is created, you can process it now
            print("Watchdog received created event - % s." % event.src_path)
        elif event.event_type == 'modified':
            # Event is modified, you can process it now
            print("Watchdog received modified event - % s." % event.src_path)


if __name__ == '__main__':

    # Remove 1st argument from the
    # list of command line arguments
    argumentList = sys.argv[1:]

    # Options
    options = "hsndu"

    # Long options
    long_options = ["Help", "Super", "Normal", "Dump", "Unmount"]
    mode = ''
    try:
        # Parsing argument
        arguments, values = getopt.getopt(argumentList, options, long_options)
        if(len(arguments) == 0):
            print("-n --Normal will kill new started processes \n-s --Super  emergency shutdown \n-d --Dump   enable momery dump\n-u --Unmount Unmount all drives")
            quit()

        # checking each argument

        for currentArgument, currentValue in arguments:
            if currentArgument in ("-d", "--Dump"):
                dump_enabled = True
                print('dump enabled')

            if currentArgument in ("-u", "--Unmount"):
                unmount_enabled = True
                print('umonunt enabled')

            if currentArgument in ("-h", "--Help"):
                print(
                    "-n --Normal will kill new started processes \n-s --Super  emergency shutdown \n-d --Dump   enable momery dump\n-u --Unmount Unmount all drives")
                quit()
            if currentArgument in ("-s", "--Super"):
                agree = input("Are you sure ? n or y : ")
                if(agree == 'y'):
                    mode = 'super'
                elif(agree == 'n'):
                    print('OK')
                    quit()
                else:
                    print('uknown input')
                    quit()

            elif currentArgument in ("-n", "--Normal"):
                mode = 'normal'

        watch = OnMyWatch(mode)
        watch.run()

    except getopt.error as err:
        # output error, and return with an error code
        print(str(err))
