# coding: utf-8
import urlparse
import urllib2 as url
from lxml import etree as et
import sys
import sqlite3

class Extractor():
	def getCompany(self,link):
		if link.find("tokyometro")>0:
			return "tokyometro"
		elif link.find("jreast")>0:
			return  "jreast"
		elif link.find("keisei")>0:
			return  "keisei"
		elif link.find("yurikamome")>0:
			return  "yurikamome"
		elif link.find("metro.tokyo")>0:
			return  "metro.tokyo"
class Entity():
	name=""
	link=""	
class Line(Entity):
	company=""
	stations=list()#駅のエンティティを保持する
	checked=0
	def saveline(self,cur):
		if self.checked==1:
			cur.execute("insert or replace into line ( name,link,company) values  (?,?,?)",(self.name,self.link,self.company))
			for station in self.stations:
				station.savestation(cur,self.name)
class Station(Entity):
	seq=int()
	tllst=list()#乗り換え線路名
	def savestation(self,cur,line):
		cur.execute("insert or replace into station ( lname,seq,name,link) values  (?,?,?,?)",
		(line,self.seq,self.name,self.link))
		for tline in self.tllst:
			cur.execute("insert or replace into transfer ( lname,sname,tolname,tosname) values (?,?,?,?)",
			(line,self.name,tline[0],tline[1]))
class TokyoMetroExtractor(Extractor):
	baseurl="http://www.tokyometro.jp/station/line_ginza/index.html"
	def extractStations(self,root,ll):
		statlst=list()
		stationsRoot=root.xpath('//table//tr')
		for station in stationsRoot:
			stree=et.ElementTree(station)
			stationName=stree.xpath('//td//p[@class="v2_routeStationName"]//text()')
			if len(stationName)>0 :
				stationLink=urlparse.urljoin(self.baseurl,stree.xpath('//td//p[@class="v2_routeStationName"]//@href')[0])	

				tslst=list()
				self.extractTransfer(stree.xpath('//td//ul[@class="v2_routeTransferList"]/li'),ll,tslst)
				self.extractTransfer(stree.xpath('//td//ul[@class="v2_routeTransferListOther"]/li'),ll,tslst)
				s=Station()
				s.seq=len(statlst)+1
				s.name=stationName[0]
				s.link=stationLink
				s.tllst=tslst
				statlst.append(s)		
		return statlst
		
	def extractTransfer(self,tstations,ll,tslst):
		#乗り換え情報を格納する
		for tstation in tstations:
			ttree=et.ElementTree(tstation)
			if len(ttree.xpath('//text()'))==1:
				tsname=""
			elif len(ttree.xpath('//text()'))==2:
				tsname=ttree.xpath('//text()')[1]
				tsname=tsname[1:tsname.find(u'駅')]
			tname=ttree.xpath('//text()')[0]
			tlink=ttree.xpath('//@href')[0]
			tslst.append((tname,tsname))
			#線路情報を格納する
			tl=Line()
			tl.name=tname
			tl.link=urlparse.urljoin(self.baseurl,tlink)
			ll[tname]=ll.get(tname,tl)

	def extractLine(self,line,ll):
		response= url.urlopen(line.link)
		line.company=extractor.getCompany(line.link)
		html=response.read()
		#線路名を設定
		root=et.fromstring(html,et.HTMLParser())
		#代表英文字付きの線路名
		lineName=root.xpath('//meta[@name="keywords"]')[0].attrib["content"].split(",")[0].split("/")[0]	
		#線路名のみ
		lineName1=root.xpath('//meta[@name="keywords"]')[0].attrib["content"].split(",")[0]
		line.name=lineName1

		#線路の情報を補完する
		line.stations=self.extractStations(root,ll)
		line.checked=1
		ll[lineName]=line

class MetroTokyoExtractor(Extractor):
	baseurl="http://www.kotsu.metro.tokyo.jp"
	def extractLine(self,line,ll):
		response=url.urlopen(line.link+"subway/stations/")
		line.company=extractor.getCompany(line.link)
		html=response.read()
		lineName=line.name
		root=et.fromstring(html,et.HTMLParser()).xpath('//map/area')
		if line.name==u'都営浅草線':
			line.name+="/A"
			line.stations=self.extractStations(root,ll,"a")
		elif line.name==u'都営三田線':
			line.name+="/I"
			line.stations=self.extractStations(root,ll,"i")
		elif line.name==u'都営新宿線':
			line.name+="/S"
			line.stations=self.extractStations(root,ll,"s")
		elif line.name==u'都営大江戸線':
			line.name+="/E"
			line.stations=self.extractStations(root,ll,"e")
		line.checked=1
		ll[lineName]=line
		
	def extractStations(self,stations,ll,linestr):
		tmp=dict()
		for station in stations:
			stree=et.ElementTree(station)
			stationLink=stree.xpath('//@href')[0]
			if stationLink.split("/")[4].startswith(linestr):
				stationName=stree.xpath('//@title')[0].split(u'（')[0]
				if stationName in tmp.keys():
					continue
				stationSeq=int(stree.xpath('//@href')[0].split("/")[4].split(".")[0][1:])
			else:
				continue
			s=Station()
			s.name=stationName
			s.seq=stationSeq
			s.link=urlparse.urljoin(self.baseurl,stationLink)
			
			tmp[s.name]=s
		return tmp.values()

ll=dict() #線路情報を保持するリスト
extractor=TokyoMetroExtractor()

for i in range(13):
	i+=1
	line=Line()
	#llに要素がゼロのとき、銀座線から
	if len(ll)==0:
		line.link=extractor.baseurl
	else:
		lst4sort=list()
		for k,v in ll.items():
			lst4sort.append((v.checked,k))
		lst4sort.sort()
		for j in range(len(lst4sort)):
			print lst4sort[j][0],lst4sort[j][1]
			if ll[lst4sort[j][1]].checked==0:
				if ll[lst4sort[j][1]].link.find("tokyometro")>0:
					line.link=ll[lst4sort[j][1]].link	
					line.name=ll[lst4sort[j][1]].name			
					break
				elif ll[lst4sort[j][1]].link.find("metro.tokyo")>0 and lst4sort[j][1].find(u'日暮里・舎人ライナー')<0:
					line.link=ll[lst4sort[j][1]].link
					#都営地下鉄の線路は全て共有一つリンクのため
					line.name=ll[lst4sort[j][1]].name
					extractor=MetroTokyoExtractor()
					break
				elif ll[lst4sort[j][1]].link.find("jreast")>0:
					continue
				elif ll[lst4sort[j][1]].link.find("keisei")>0:
					continue
				elif ll[lst4sort[j][1]].link.find("yurikamome")>0:
					continue

			j+=1
	print line.link
	extractor.extractLine(line,ll)

	print "-------------------"
	print line.name+":"+line.link+":"+line.company
	print line.checked
	for s in line.stations:
		print ">>>>>",s.seq,s.name,s.link,str(s.tllst).decode("unicode-escape")
	print "==================="		
	#for l in ll.values():
	#	print l.name+":"+l.link
		
#取得した情報をsqliteに出力する
conn=sqlite3.connect("../sqlite/metro.sqlite")
cur=conn.cursor()

cur.execute('''drop table if exists line ''')
cur.execute('''drop table if exists station ''')
cur.execute('''drop table if exists transfer ''')
cur.execute('''create table line ( name text unique, link text, company text) ''')
cur.execute('''create table station ( lname text , seq integer, name text,link text) ''')
cur.execute('''create table transfer (lname text , sname integer,tolname text,tosname text) ''')

for l in ll.values():
	l.saveline(cur)
	
conn.commit()