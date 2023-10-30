import json
import psutil
import subprocess
import time
#import schedule
from datetime import datetime

def readJsonMap(path_mapping: str):
    with open(path_mapping, 'r', encoding='utf-8') as f:
        jsonMap = json.load(f)
    return jsonMap

procJson = readJsonMap("./proc.json")

def procFind(id0:str, id1:str, id2:str):
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        if proc.info['name'] == 'ffmpeg':
            if id0 in proc.info['cmdline'] and id1 in proc.info['cmdline'] and id2 in proc.info['cmdline']:
                yield proc.pid

def procKill(pid):
    if psutil.pid_exists(pid):
        p = psutil.Process(pid)
        p.terminate()
        p.wait()
        print(f"PID '{pid}'Killed process")

#def procStart(cmd):
#    subprocess.Popen(cmd, shell=True)
#    print(f"Command '{cmd}' is executed.")

def procStart(cmd):
    proc = subprocess.Popen(cmd, shell=True)
    print(f"Command '{cmd}' Started process with PID: {proc.pid}")
    return proc.pid

def procRestart(cmd, pid):
    procKill(pid)
    pid = procStart(cmd)
    return pid

#def procRestart(cmd, id0, id1, id2):
#    for pid in procFind(id0, id1, id2):
#        procKill(pid)
#        print(f"Terminated ffmpeg process with PID {pid} for source {source} and destination {destination}.")
#    procStart(cmd)

def procAllRestart():
    global procJson
    for i in procJson["proc"]:
        procKill(i["pid"])
        i["pid"] = procStart(i["cmd"])

def runningTime(timeRunning):
    days = timeRunning.days
    seconds = timeRunning.seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = (seconds % 60)
    return f"{days}:{hours}:{minutes}:{seconds}"

def main():
    global procJson
    reHour = int(procJson["reTime"]["hour"])
    reMin = int(procJson["reTime"]["min"])
    reMinPlus = reMin + int(procJson["reTime"]["delayMin"])

    swNeedRestart = True
    timeStart = datetime.now()
    for i in procJson["proc"]:
        i["pid"] = procStart(i["cmd"])
#    schedule.every().minute.at(":00").do(procAllRestart)
#    schedule.every().minute.at(":00").do(procAllRestart)
    while True:
#        schedule.run_pending()
        timeNow = datetime.now()
        if  timeNow.hour == reHour:
            if timeNow.minute == reMin and swNeedRestart:
                procAllRestart()
                timeRunning = timeNow - timeStart
                print("\n------------------------------------------")
                print(f"RUNNING TIME : {runningTime(timeRunning)}")
                print("------------------------------------------\n")
                swNeedRestart = False
            elif timeNow.minute == reMinPlus:
                swNeedRestart = True
        time.sleep(1)

if __name__ == "__main__":
    main()