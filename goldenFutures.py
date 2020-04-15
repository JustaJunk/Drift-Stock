#!/usr/bin/python
#-*- coding: UTF-8 -*-

###########################################################################
#	import
###########################################################################
import requests
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import plotly.graph_objects as go

###########################################################################
#
#	Functions
#
###########################################################################
def date(dateString):
	ymd = [int(dts) for dts in dateString.split('/')]
	return datetime(ymd[0],ymd[1],ymd[2])

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
		self.volume 		= []

		# golden retracement
		self.goldenCutter	= []

		# chart bound
		self.yRange 		= []

	#------------------------------------------
	#	getData
	#------------------------------------------
	def getData(self, dataNum):
		reqParam = 'a=' + self.ID + '&b=-1&c=D&d=' + str(dataNum)
		try:
			resp = self.req.get(self.url + reqParam)
			respSplit = resp.text.split()
		except:
			return False
		self.dataNum 	= dataNum;
		self.dateline 	= respSplit[0].split(',')
		self.openPri  	= [float(pri) for pri in respSplit[1].split(',')]
		self.highPri  	= [float(pri) for pri in respSplit[2].split(',')]
		self.lowPri   	= [float(pri) for pri in respSplit[3].split(',')]
		self.closePri 	= [float(pri) for pri in respSplit[4].split(',')]
		self.volume  	= [  int(vol) for vol in respSplit[5].split(',')]
		return True

	#------------------------------------------
	#	getGoldenRatio
	#------------------------------------------
	def getGoldenRatio(self, dataNum, cutDepth):
		if not self.getData(dataNum):
			return False
		lowerPri = min(self.lowPri)
		upperPri = max(self.highPri)
		self.yRange = [lowerPri, upperPri]
		for i in range(cutDepth):
			cutter = goldenCutter(lowerPri, upperPri)
			whichRange = mostDataInRange(self.closePri, cutter)
			lowerPri = cutter[whichRange]
			upperPri = cutter[whichRange+1]

		self.goldenCutter = cutter
		return True

	#------------------------------------------
	#	getHeightRatio
	#------------------------------------------
	def getHeightRatio(self, level):
		return (level-self.yRange[0])/(self.yRange[1]-self.yRange[0])

	#------------------------------------------
	#	getShapes
	#------------------------------------------
	def getShapes(self):
		dicts = []
		for level in self.goldenCutter:
			dicts.append(dict(	x0=self.dateline[0], 
								x1=self.dateline[-1],
								y0=self.getHeightRatio(level), 
								y1=self.getHeightRatio(level),
								xref='x',
								yref='paper',
								line_width=2))
		return dicts

	#------------------------------------------
	#	plotChart
	#------------------------------------------
	def plotChart(self):
		candleData = go.Candlestick(x=self.dateline,
									open=self.openPri,
									high=self.highPri,
									low=self.lowPri,
									close=self.closePri,
									increasing_line_color= 'red', 
									decreasing_line_color= 'green')

		fig = go.Figure(data=[candleData])
		fig.update_yaxes(range=self.yRange)
		fig.update_layout(
			title = self.ID,
			shapes = self.getShapes()
			)
		fig.show()


if __name__ == '__main__':
	FITX = Future("FITX")
	if FITX.getGoldenRatio(480, 1):
		for cut in FITX.goldenCutter:
			print(cut)
		FITX.plotChart()
	else:
		print('fail')
