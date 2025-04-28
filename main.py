import os 
import qbittorrentapi
from qbittorrentapi import Client, TorrentStates
import time
import json
import subprocess

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
    time.sleep(10)
    print('Was dead now is alive')
    sys.exit()

# instantiate a Client using the appropriate WebUI configuration
qbt_client = qbittorrentapi.Client(
    host='localhost',
    port=8080,
    username='admin',
    password='password',
)

# the Client will automatically acquire/maintain a logged-in state
# in line with any request. therefore, this is not strictly necessary;
# however, you may want to test the provided login credentials.
try:
  qbt_client.auth_log_in()
except qbittorrentapi.LoginFailed as e:
  print(e)

print("got client")

# Determine if we're in a bad connection state
# This is when there are others in the swarm yet no progress is being made.
numBadTorrents = 0
numGoodTorrents = 0
now = int(time.time())
for torrent in qbt_client.torrents_info():
  # check if torrent is downloading
  if torrent.state_enum.is_downloading or torrent.state_enum.is_uploading:
    swarmCount = torrent.num_complete + torrent.num_incomplete + torrent.num_seeds + torrent.num_leechs
    lastChunkDownloadedSecondsAgo = now - torrent.last_activity
    print(f'last chunk was DL {lastChunkDownloadedSecondsAgo} seconds ago. DL speed is {torrent.dlspeed}. Swarm count {swarmCount}')

    if swarmCount >= 0 and torrent.dlspeed <= 1 and lastChunkDownloadedSecondsAgo > 60*10 and torrent.upspeed <= 1:
      print(f'{torrent.name} {torrent.hash} is downloading or seeding but is BAD!')
      numBadTorrents += 1
    else:
      print(f'{torrent.name} {torrent.hash} is downloading or seeding and is GOOD!')
      numGoodTorrents += 1
  else:
    print(f'{torrent.name} {torrent.hash} is not being counted')

print(f'good {numGoodTorrents} bad {numBadTorrents}')
if numBadTorrents > 0 and numGoodTorrents == 0:
  print("Commencing Reboot")
  killClient(qbt_client)
  numtry = 0
  
  while checkClient() == True :
    print('Shutting Down')
    time.sleep(10)
  
  while checkClient() == False :  
    if numtry == 0 :
      startClient()
      print('Booting')
      numtry += 1
      time.sleep(10)

print("done")


