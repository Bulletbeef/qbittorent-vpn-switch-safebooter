import os 
import qbittorrentapi
from qbittorrentapi import Client, TorrentStates
import time
import json
import subprocess
from config import *

def killClient(qbt_client):
  # os.system('cmd /c "taskkill /im qbittorrent.exe"')
  qbt_client.app_shutdown()

def startClient():
  os.system('cmd /c "start qtshortcut.lnk"')


def displayClientInfo(qbt_client):
  print(f'qBittorrent: {qbt_client.app.version}')
  print(f'qBittorrent Web API: {qbt_client.app.web_api_version}')
  for k,v in qbt_client.app.build_info.items(): print(f'{k}: {v}')
  
def process_exists(process_name):
    progs = str(subprocess.check_output('tasklist'))
    if process_name in progs:
        return True
    else:
        return False


def checkClient():
  if process_exists('qbittorrent.exe'):
    print('Running')
    return True
  else:
    print('Not Running')
    return False

# Check if qbit is running, start if it is not and close scrypt  
if checkClient() == False :
    print('Booting')
    startClient()
    time.sleep(waitTime)
    print('Was dead now is alive')
    sys.exit()

# instantiate a Client using the appropriate WebUI configuration
qbt_client = qbittorrentapi.Client( host,port,username,password,)

# the Client will automatically acquire/maintain a logged-in state
# in line with any request. therefore, this is not strictly necessary;
# however, you may want to test the provided login credentials. 

try:
  qbt_client.auth_log_in()
except qbittorrentapi.LoginFailed as e:
  print(e)

print("Got client")

# Determine if we're in a bad connection state
# This is when there is no progress is being made on any torrent that is in a downloading state.

numBadTorrents = 0
numGoodTorrents = 0
now = int(time.time())
torrentSpeed = 0
globalSpeed = 0

for torrent in qbt_client.torrents_info():
  
  # check if torrent is downloading
  
  if torrent.state_enum.is_downloading or torrent.state_enum.is_uploading:
    torrentSpeed = (torrent.dlspeed + torrent.upspeed)
    swarmCount = torrent.num_complete + torrent.num_incomplete + torrent.num_seeds + torrent.num_leechs

    if torrentSpeed<=0 :
      lastChunkDownloadedSecondsAgo = now - torrent.last_activity
      print(f'\n{torrent.name}')
      print(f'BAD! - last chunk was loaded {lastChunkDownloadedSecondsAgo} seconds ago. Speed is {torrentSpeed}. Swarm count {swarmCount}')
      numBadTorrents += 1
   
    else:
      print(f'\n{torrent.name}\nGOOD!')
      numGoodTorrents += 1
  else:
    print(f'\n{torrent.name} \nEXCLUDED!')
    torrentSpeed = 0
  globalSpeed += torrentSpeed

print(f'Good {numGoodTorrents} Bad {numBadTorrents} Global Speed is {globalSpeed}')

#decision to reboot

if globalSpeed <= 0 and numBadTorrents >= 1:
  print("Commencing Reboot")
  killClient(qbt_client)
  numtry = 0
  
  while checkClient() == True :
    print('Shutting Down')
    time.sleep(waitTime)
  
  while checkClient() == False :  
    if numtry == 0 :
      startClient()
      print('Booting')
      numtry += 1
      time.sleep(waitTime)

print("Done")
time.sleep(10+waitTime)
