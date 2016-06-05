# coding: utf-8
# -*- coding: utf-8 -*-
import urllib2 as url
import xml.etree.ElementTree as et
from HTMLParser import HTMLParser as hp
class GetStationNames(hp):
	def __init__(self):
		hp.__init__(self)
		self.found = False
		self.lineName=""
		self.stationNames=list()
	def handle_starttag(self, tag, attrs):
		if tag=="meta":
			attrs=dict(attrs)
			print attrs,";"
			if "keywords" in attrs.values():
				self.lineName= url.unquote(attrs.get("content")).split(",")[0]
		if tag =="select":
			attrs=dict(attrs)
			if attrs["name"]=="":
				self.found=True

	def handle_endtag(self, tag):
		if tag=="select":
			self.found=False

	def handle_data(self, data):
		if self.found==True:
			#print data
			if data.strip()!="駅を選択" and len(data.strip())>1:
				self.stationNames.append((len(self.stationNames)+1,data.strip()))
				#print self.stationNames

fname="GinzaLine.html"
#response= url.urlopen("http://www.tokyometro.jp/station/line_ginza/index.html")
#html=response.read()
#print html
f=open(fname,"r")
#f.write(html)
html=f.read()
#print html
#stuff=et.parse(fname)
#doc=stuff.findall('///div[@class="v2_stationAsideTimetableSelect"')

parser=GetStationNames();
parser.feed(html)
data=dict()
data[parser.lineName]=parser.stationNames
print "-------------------"
print str(data).decode("string-escape")
parser.close()