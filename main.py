# from flask import Flask, render_template, Response
# import sys
# from time import sleep
# import telnetlib

# HOST = "192.168.10.48"
# user = 'adtec'
# password = 'none'

# tn = telnetlib.Telnet(HOST, 23, 10)

# tn.write(user+'\r\n')
# sleep(2)
# tn.write(password+'\r\n')
# sleep(2)

# tn.write('*.DCMD PL'+'\r\n')

# print tn.read_until('User adtec connected',10)

# tn.close

from flask import Flask, render_template, Response
from lib.adtec import AdtecAPI, AdtecFTP, PlaylistBuilder
from threading import Thread
from time import sleep
status = ''
results = [None]
x = [0]

# def getStatus():
# 	status = ''
# 	for key,value in api.status().iteritems():
# 		status += key + ': ' + str(value) + '\n'

# 	results.append(status.rstrip())


def getStatus():
	api = AdtecAPI('192.168.10.49', 'adtec', 'none')
	api.open()
	x[0] = 1
	while True:
		results[0] = (api.status()['Percent'][0])
		sleep(.25)
	api.close()



t = Thread(target=getStatus, args=())
t.start()

while True:
	if x[0] == 1:
		print results[0]
		sleep(1)

#api.play(playlist='myList')


# ftp = AdtecFTP('192.168.10.49', 'adtec', 'none') # download all playlists upon connecting, playlist folder
# pb = PlaylistBuilder()

# pb.createPlaylist([], 'myList')

# pb.editPlaylist('myList', add="default2.mpg")
# pb.editPlaylist('myList', add="default10.mpg")

# ftp.addPlaylist('myList')

# api.close()
#ftp.close()

def addPlayer(ip, user, passwd, name):
	playerApi = AdtecAPI()
	playerFtp = AdtecFTP()
	pass

def getConfig():
	pass