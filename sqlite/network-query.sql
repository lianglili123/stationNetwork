select command from
(select lname,seq,'create ('||substr(lname,length(lname))||seq||
':'||substr(lname,length(lname))||'_node{name:'''|| name||'''})-['||
':'||substr(lname,length(lname))||'_line{name:'''||substr(lname,0,length(lname)-1)||'''}]' as command
 from station where seq=1
 union all
select lname,seq,'->('||substr(lname,length(lname))||seq||
':'||substr(lname,length(lname))||'_node{name:'''|| name||'''})-['||
':'||substr(lname,length(lname))||'_line{name:'''||substr(lname,0,length(lname)-1)||'''}]' as command
 from station where seq!=1
 union all
 select lname,99,'->(Dummy:stationNode);' from station group by lname)
 order by lname,seq;