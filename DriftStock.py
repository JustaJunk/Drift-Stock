#!/usr/bin/python
#-*- coding: UTF-8 -*-

###########################################################################
#	import
###########################################################################
import twstock, time
import requests
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

###########################################################################
#	Global variables
###########################################################################
stkType = '股票'

###########################################################################
#
#	stkInfo: object to aquire stock informations
#
###########################################################################
class stkInfo:
	def __init__(self):
		# url and requests setiing
		self.url = 'http://djinfo.cathaysec.com.tw/Z/ZC/ZCW/CZKC1.djbcd?'
		self.req = requests.session()
		retries = Retry(total=10,backoff_factor=1,status_forcelist=[ 500, 502, 503, 504 ])
		self.req.mount('http://', HTTPAdapter(max_retries=retries))

		# price and volume
		self.openPri	= []
		self.highPri 	= []
		self.lowPri 	= []
		self.closePri 	= []
		self.volume 	= []

	#------------------------------------------
	#	getInfo
	#------------------------------------------
	def getInfo(self, sid, mode, count, which):
		reqParam = 'a=' + str(sid) + '&b=' + str(mode) + '&c=' + str(count)
		try:
			resp = self.req.get(self.url + reqParam)
			respSplit = resp.text.split()
			if 'o' in which:
				self.openPri  	= [float(pri) for pri in respSplit[1].split(',')]
			if 'h' in which:
				self.highPri  	= [float(pri) for pri in respSplit[2].split(',')]
			if 'l' in which:
				self.lowPri   	= [float(pri) for pri in respSplit[3].split(',')]
			if 'c' in which:	
				self.closePri 	= [float(pri) for pri in respSplit[4].split(',')]
			if 'v' in which:
				self.volume  	= [  int(vol) for vol in respSplit[5].split(',')]
			return True

		except:
			return False

###########################################################################
#
#	findDrift: object to find stocks which drifted today
#
###########################################################################
class findDrift:
	def __init__(self):
		self.stkInfo = stkInfo()
		self.sidList = [ sid for sid in list(twstock.codes) if twstock.codes[sid].type == stkType ]
		self.ratio 	 = 0.0
		self.before  = 1

	#------------------------------------------
	#	isDrift
	#------------------------------------------
	def isDrift(self, sid):
		count = 9*self.before
		if self.stkInfo.getInfo(sid, '30', count, 'ohlcv'):
			preDiff = [self.stkInfo.highPri[i] - self.stkInfo.lowPri[i] for i in range(count-1)]
			preDiff = preDiff[0:9-1]
			lastDiff = self.stkInfo.closePri[9-1] - self.stkInfo.openPri[9-1]
			volSum = sum(self.stkInfo.volume[0:9])
			self.ratio = round(self.stkInfo.volume[9-1]/volSum*100,2)
			return lastDiff > 1.1*max(preDiff) and volSum >= 500
		else:
			return False

	#------------------------------------------
	#	run
	#------------------------------------------
	def run(self):
		print('all stock:', len(self.sidList), '\n')
		for sid in self.sidList:
			time.sleep(0.2)
			if self.isDrift(sid):
				print(sid, ' ', self.ratio)

###########################################################################
#
#	main
#
###########################################################################
if __name__ == '__main__':
	findDrift = findDrift()
	findDrift.run()