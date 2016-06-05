import urllib2 as ulib2
import base64
import json

url="http://localhost:7474/db/data/transaction/commit"
headers={
"Accept":"application/json; charset=UTF-8",
"Content-Type":"application/json"
}

#fname=raw_input("Enter file name:")
fname="merge-transfer.cql"
#fname="create-network.cql"
fh=open(fname,"r")

sl=list()
str=""    

for line in fh:
    if line.strip().endswith(";"):
        #print "1:",line
        sl.append({"statement": str+" "+line.strip()})
        str=""
    else:
        #print "2:",line
        str+=" "+line.strip()

data=json.dumps({"statements": sl})
#print data


request=ulib2.Request(url,data,headers)

username="neo4j"
password="SSD0564"
base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
request.add_header("Authorization", "Basic %s" % base64string)   

response=ulib2.urlopen(request)

print response.read()