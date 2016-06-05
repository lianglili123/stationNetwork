# coding: utf-8
import urlparse
import urllib2 as url
from lxml import etree as et
import sys
from HTMLParser import HTMLParser as hp

class Entity():
	name=""
	link=""	
class Line(Entity):
	stations=list()#駅のエンティティを保持する
	checked=0
	def savelines(cur):
		if checked==1:
			cur.execute("insert or replace into line ( name,link) values = (?,?)",(self.name,self.link,))
			for station in self.stations:
				station.savestations(cur,line)

class Station(Entity):
	seq=int()
	tllst=list()#乗り換え線路名
	def savestations(cur,line):
		cur.execute("insert or replace into station ( lname,seq,name,link) values = (?,?,?,?)",
		(line,self.seq,self.name,self.link,))
		for tline in self.tllst:
			cur.execute("insert or replace into transfer ( lname,seq,tolname) values = (?,?,?)",
			(line,self.seq,tline,))

fname="GinzaLine.html"
baseurl="http://www.tokyometro.jp/station/line_ginza/index.html"
ll=dict() #線路情報を保持するリスト


#while len(linelst)==0 or len(linelst)>len(data):
for i in range(5):
	i+=1
	line=Line()
	#llに要素がゼロのとき、銀座線から
	if len(ll)==0:
		line.link=baseurl
	else:
		lst4sort=list()
		for k,v in ll.items():
			lst4sort.append((v.checked,k))
		lst4sort.sort()
		print str(lst4sort).decode("unicode-escape")
		for j in range(len(lst4sort)):
			print lst4sort[j][0],lst4sort[j][1]
			if ll[lst4sort[j][1]].checked==0:
				if ll[lst4sort[j][1]].link.find("tokyometro")>0:
					line.link=ll[lst4sort[j][1]].link
					break
			j+=1
				
		print line.link
	
	response= url.urlopen(line.link)
	html=response.read()

	#線路名を設定
	root=et.fromstring(html,et.HTMLParser())
	lineName=root.xpath('//meta[@name="keywords"]')[0].attrib["content"].split(",")[0].split("/")[0]	
	line.name=lineName

	statlst=list()
	stations=root.xpath('//table//tr')
	for station in stations:
		stree=et.ElementTree(station)
		stationName=stree.xpath('//td//p[@class="v2_routeStationName"]//text()')
		if len(stationName)>0 :
			path=stree.xpath('//td//p[@class="v2_routeStationName"]//@href')[0]
			stationLink=urlparse.urljoin(baseurl,path)
		
			tstations=stree.xpath('//td//ul[@class="v2_routeTransferList"]/li')
			tslst=list()
			for tstation in tstations:
				ttree=et.ElementTree(tstation)
				tname=ttree.xpath('//text()')[0]
				tlink=urlparse.urljoin(baseurl,ttree.xpath('//@href')[0])
				tslst.append(tname)
				#乗り換え情報を格納する
			
				#線路情報を格納する
				tl=Line()
				tl.name=tname
				tl.link=tlink
				ll[tname]=ll.get(tname,tl)
			tstations=stree.xpath('//td//ul[@class="v2_routeTransferListOther"]/li')
			for tstation in tstations:
				ttree=et.ElementTree(tstation)
				tname=ttree.xpath('//text()')[0]
				tlink=ttree.xpath('//@href')[0]
				tslst.append(tname)
				tl=Line()
				tl.name=tname
				tl.link=tlink
				ll[tname]=ll.get(tname,tl)
			s=Station()
			s.seq=len(statlst)+1
			s.name=stationName[0]
			s.link=stationLink
			s.tllst=tslst
			statlst.append(s)

	#線路の情報を補完する
	line.stations=statlst
	line.checked=1
	ll[line.name]=line

	print "-------------------"
	print line.name+":"+line.link+":"
	print line.checked
	for s in line.stations:
		print ">>>>>",s.seq,s.name,s.link,str(s.tllst).decode("unicode-escape")
		
import sqlite3

conn=sqlite3.connect("metro.sqlite")
cur=conn.cursor()

cur.execute("drop table if exists line ")