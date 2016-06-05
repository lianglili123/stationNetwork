select 
'match (n:'||substr(t.lname,length(t.lname)) ||'_node{name:'''||s.name||'''}), (m:'||substr(tl.name ,length(tl.name))  ||'_node{name:'''||s.name||'''})'||
' merge (n)-[r:transfer]->(m) return r;' as command

from transfer t join station s on (t.lname=s.lname and t.seq=s.seq)
 join line l on (t.tolname=substr(l.name,0,length(l.name)-1)) 
 join line tl on (substr(tl.name,0,length(tl.name)-1)=t.tolname)
 order by s.name; 