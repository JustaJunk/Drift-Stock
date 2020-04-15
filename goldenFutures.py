#!/usr/bin/python
#-*- coding: UTF-8 -*-

###########################################################################
#	import
###########################################################################
import requests
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

###########################################################################
#
#	Functions
#
###########################################################################
def goldenCutter(lower, upper):
	return [lower, lower+0.382*(upper-lower), (lower+upper)/2, lower+0.618*(upper-lower), upper]

def mostDataInRange(priArray, cutter):
	rangeNum = len(cutter)
	counts = [0]*(rangeNum-1)
	for pri in priArray:
		for i in range(rangeNum-1):
			if pri >= cutter[i] and pri < cutter[i+1]:
				counts[i] += 1

	return counts.index(max(counts))

###########################################################################
#
#	Object of future products
#
###########################################################################
class Future:
	def __init__(self, futureID):
		# url and requests setiing
		self.ID = futureID;
		self.url = 'http://djinfo.cathaysec.com.tw/Z/ZM/ZMB/CZMB.djbcd?'
		self.req = requests.session()
		retries = Retry(total=10,backoff_factor=1,status_forcelist=[ 500, 502, 503, 504 ])
		self.req.mount('http://', HTTPAdapter(max_retries=retries))

		# price and volume
		self.openPri		= []
		self.highPri 		= []
		self.lowPri 		= []
		self.closePri 		= []
		# self.volume 		= []

		# golden retracement
		self.goldenCutter	= []

	#------------------------------------------
	#	getData
	#------------------------------------------
	def getData(self, dataNum):
		reqParam = 'a=' + self.ID + '&b=-1&c=D&d=' + str(dataNum) + "&ver=2"
		try:
			resp = self.req.get(self.url + reqParam)
			respSplit = resp.text.split()
			self.openPri  	= [float(pri) for pri in respSplit[1].split(',')]
			self.highPri  	= [float(pri) for pri in respSplit[2].split(',')]
			self.lowPri   	= [float(pri) for pri in respSplit[3].split(',')]
			self.closePri 	= [float(pri) for pri in respSplit[4].split(',')]
			# self.volume  	= [  int(vol) for vol in respSplit[5].split(',')]
			return True

		except:
			return False

	def getGoldenRatio(self, dataNum, cutNum):
		self.getData(dataNum)
		lowerPri = min(self.lowPri)
		upperPri = max(self.highPri)
		for i in range(cutNum):
			cutter = goldenCutter(lowerPri, upperPri)
			whichRange = mostDataInRange(self.closePri, cutter)
			lowerPri = cutter[whichRange]
			upperPri = cutter[whichRange+1]

		self.goldenCutter = cutter

if __name__ == '__main__':
	FITX = Future("FITX")
	FITX.getGoldenRatio(1440, 3)

	for cut in FITX.goldenCutter:
		print(cut)
