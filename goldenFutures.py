
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
def goldenCut(lower, upper):
	return [lower, lower+0.382*(upper-lower), (lower+upper)/2, lower+0.618*(upper-lower), upper]

def mostDataInRange(prices, levels):
	rangeNum = len(levels)
	counts = [0]*(rangeNum-1)
	for pri in prices:
		for i in range(rangeNum-1):
			if pri >= levels[i] and pri < levels[i+1]:
				counts[i] += 1

	return counts.index(max(counts))

def mostDataOnLevel(openPrices, closePrices, levels):
	levelNum = len(levels)
	counts = [0]*levelNum
	for i,level in enumerate(levels):
		for openPri,closePri in zip(openPrices, closePrices):
			condition1 = (openPri >= level and closePri <= level)
			condition2 = (openPri <= level and closePri >= level)
			if condition1 or condition2:
				counts[i] += 1

	return counts.index(max(counts))

def normalizeVolumes(volumes, bound):
	max_vol = max(volumes)
	return [bound[0]+vol/max_vol*(bound[1]-bound[0]) for vol in volumes]

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
		retries = Retry(total=10, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
		self.req.mount('http://', HTTPAdapter(max_retries=retries))

		# price and volume
		self.openPri		= []
		self.highPri 		= []
		self.lowPri 		= []
		self.closePri 		= []
		self.volumes 		= []

		# golden retracement
		self.goldenLevels	= []

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
			print('Connection fail')
			return False

		self.dataNum 	= dataNum;
		self.dateline 	= respSplit[0].split(',')
		self.openPri  	= [float(pri) for pri in respSplit[1].split(',')]
		self.highPri  	= [float(pri) for pri in respSplit[2].split(',')]
		self.lowPri   	= [float(pri) for pri in respSplit[3].split(',')]
		self.closePri 	= [float(pri) for pri in respSplit[4].split(',')]
		self.volumes  	= [  int(vol) for vol in respSplit[5].split(',')]
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
			levels = goldenCut(lowerPri, upperPri)
			whichRange = mostDataInRange(self.closePri, levels)
			self.goldenLevels.append(levels)
			lowerPri = levels[whichRange]
			upperPri = levels[whichRange+1]

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
		for depth,levels in enumerate(self.goldenLevels):
			for level in levels:
				dicts.append(dict(	x0=self.dateline[0], 
									x1=self.dateline[-1],
									y0=self.getHeightRatio(level), 
									y1=self.getHeightRatio(level),
									xref='x',
									yref='paper',
									line_width=2,
									line_color='gray'))
		return dicts

	#------------------------------------------
	#	plotChart
	#------------------------------------------
	def plotChart(self):
		priData = go.Candlestick(	x=self.dateline,
									open=self.openPri,
									high=self.highPri,
									low=self.lowPri,
									close=self.closePri,
									increasing_line_color= 'red', 
									decreasing_line_color= 'green')
		volData = go.Bar(	x=self.dateline,
							y=normalizeVolumes(self.volumes, self.yRange),
							marker_color='LightBlue')
		fig = go.Figure(data=[volData, priData])
		fig.update_yaxes(range=self.yRange)
		fig.update_layout(
			title = self.ID+'  from '+self.dateline[0]+' ('+str(self.dataNum)+' days)',
			shapes = self.getShapes()
			)
		fig.show()


###########################################################################
#
#	main
#
###########################################################################
if __name__ == '__main__':
	FITX = Future("FITX")
	if FITX.getGoldenRatio(1200, 2):
		# print('levels:')
		# for levels in FITX.goldenLevels:
		# 	for level in reversed(levels):
		# 		print('  %8.2f' % (level))
		FITX.plotChart()
