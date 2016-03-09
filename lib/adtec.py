import telnetlib
from ftplib import FTP
import xml.etree.ElementTree as ET
from time import sleep

class AdtecAPI():

	def __init__(self, ip, user, passwd):
		self.user = user
		self.passwd = passwd
		self.ip = ip

	def open(self):
		self.tn = telnetlib.Telnet(self.ip, 23, 10)
		self.tn.write(self.user+'\r\n')
		sleep(1)
		self.tn.write(self.passwd+'\r\n')
		sleep(1)
		status = self.tn.read_until('User ' + self.user + ' connected')

	def read(self):
		#sleep(2)
		output = self.tn.read_very_eager()
		output = output.splitlines()[:-1]
		if len(output) < 1:
			return output
		else:
			return output[len(output)-1]

	def write(self, msg):
		self.tn.write(str(msg)+'\r\n')
		sleep(1)
		return self.read()

	def read_debug(self):
		sleep(2)
		output = self.tn.read_eager()
		return output

	def close(self):
		self.tn.close()

	# Transport Controls #
	######################

	def stop(self):
		self.write('*.DCMD STOP')

	def play(self, playlist=None):
		if playlist:
			self.write('*.DCMD LIST LOAD /media/hd0/list/' + playlist + '.smil')
			#self.tn.read_until('OK')
		resp = self.write('*.DCMD PLAY')

		if resp == 'OK':
			return 'OK'
		else:
			return 'ERROR'

	# Network Settings #
	####################

	def network(self, ip=None, subnet=None, gateway=None, dhcp=None):
		if ip:
			return self.write('*.SYSD IPADDRESS ' + str(ip))
		if subnet:
			return self.write('*.SYSD IPMASK ' + str(subnet))			
		if gateway:
			return self.write('*.SYSD GATEIPADDRESS ' + str(gateway))
		if dhcp:
			self.write('*.SYSD DHCP '+state)		

		ipa = self.write('*.SYSD IPADDRESS')[5:]
		mask = self.write('*.SYSD IPMASK')[5:]	
		gate = self.write('*.SYSD GATEIPADDRESS')[15:]
		dhcp = self.write('*.SYSD DHCP')[6:]

		return [ipa,mask,gate,dhcp]

	# System Settings #
	###################

	def timedate(self, time=None, date=None, tz=None, day=None): # Not complete - wont set date
		if time:
			self.write('*.SYSD TIME ' + str(time)) # 24:00:00
		if date:
			self.write('*.SYSD TIME ' + str(date)) # xx/xx/xx
		if day:
			self.write('*.SYSD TIME ' + str(day)) # Mon, Tue, Wed, Thur, Fri, Sat, Sun
		if tz:
			self.write('*.SYSD TIMEZONE ' + str(tz)) # Don't know

		return self.write('*.SYSD TIME')

	def userpass(self, user, passwd): # Doesn't work
		self.tn.write('*.SYSD SRVUSERPASSWORD '+ user +','+ passwd)
		return self.read()

	def name(self, name=None):
		if name:
			self.write('*.SYSD NAME ' + str(name))

		return self.write('*.SYSD NAME')

	# Advance #
	###########

	def serial(self, msg):
		# space = [32]
		# \r    = [13]
		# \n    = [10]
		self.write('PORT2 ' + msg)

	def status(self, terse=False):
		resp = self.write('*.DCMD TR').split(' ')
		terms = {'State':[0],'File':[1], 'SizeNumber':[2], 'Length':[3,4,5,6], 'Bitrate':[7], 
		'Date':[8,9,10], 'Time':[11,12], 'Timecode':[13,14,15,16], 'Percent':[17,18]}

		for key,value in terms.iteritems():
			val = []
			for i in terms[key]:
				val.append(resp[i])
			terms[key] = val 
			
		stateCodes = ['Unit Not Ready','Idling','Idle Cuing','Idle Next','Stopping','Playing','Buffered','Warning',
		'Fatal','Next','Previous','Paused','Pause Cueing','Pause next']

		if not terse: # set terse=True to get state codes instead of verbose
			terms['State'] = stateCodes[int(terms['State'][0])]

		return terms

class AdtecFTP():

	def __init__(self, ip, user, passwd):
		self.ip = ip
		self.user = user
		self.passwd = passwd

	def open(self):
		self.ftp = FTP(self.ip)
		self.ftp.login(self.user, self.passwd)

	def sendFile(self, file, name, destPath):
		file = open(file, 'rb')
		self.ftp.cwd(destPath)
		self.ftp.storbinary('STOR ' + name, file)

	def delFile(self, file):
		self.ftp.delete(file)

	def addPlaylist(self, playlist):
		self.sendFile('playlists/'+playlist + '.smil', playlist + '.smil', '/media/hd0/list/')

	def delPlaylist(self, playlist):
		self.delFile('/media/hd0/list/'+ playlist + '.smil')

	def getPlaylist(self): # need to download files from adtec
		self.ftp.cwd('/media/hd0/list/')
		return self.ftp.nlst()

	def media(self):
		self.ftp.cwd('/media/hd0/media/')
		return self.ftp.nlst()

	def close(self):
		self.ftp.quit()


class PlaylistBuilder():

	def readPlaylist(self, playlist):
		tree = ET.parse('playlists/' + playlist + '.smil').getroot()
		files = []
		for i in tree[1][0]:
			files.append(i.attrib['src'])

		return files

	def createPlaylist(self, filelist, name):
		playlist = open('playlists/' + name + '.smil', 'w')
		lines = []

		header = '''<?xml version="1.0" encoding="UTF-8"?>\n<smil xmlns="http://www.w3.org/2001/SMIL20/Language">\n<head></head>\n<body>\n<seq>\n'''
		footer = '''	</seq>\n</body>\n</smil>'''

		lines.append(header)
		for file in filelist:
			lines.append('		<ref src="' + file + '" />\n')

		lines.append(footer)

		for line in lines:
			playlist.write(line)

		playlist.close()

	def editPlaylist(self, playlist, add=None, rem=None):
		files = self.readPlaylist(playlist)
		if add:
			files.append('/media/hd0/media/' + add)

		if rem:
			files.remove('/media/hd0/media/' + rem)
		self.createPlaylist(files, playlist)

