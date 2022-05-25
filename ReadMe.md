# DaisyHttp

> DaisyHttp can be used as Data Center Server for Bio Big Files (bam, fasta, ...), with CORS and range header enabled.




## How to use?


### step1: start the service
```
$ python3 DaisyHttp.py 8001 /home/wangjl/
Perhaps, you also need to open the port using `iptables`.

Get help
$ python3 DaisyHttp.py -h
```




### step2: open your browser
```
Home page is also help page: http://192.168.2.120:8001/


You can list a dir, with /list/your/path/to/dir/: 
http://192.168.2.120:8001/list/data/web/docs/audio/
{"current_dir": "data/web/docs/audio/", 
"files": ["20041118_day_10-Atlantis.mp3", "How_The_Economic_Machine_Works_by_Ray.mp3",  "log.txt"], 
"directories": ["NCE4", "time_machine"]}


You can get the file with CORS and range enabled: /list/your/path/to/file
http://192.168.2.120:8001/list/data/web/docs/audio/20041118_day_10-Atlantis.mp3

```









## About the file path

This file path in the url after /list/ is relative to the Root Path you set when starting up the server.

```
$ cd /home/wangjl/
$ ls -lth data/web/docs/audio/20041118_day_10-Atlantis.mp3
-rw-rw-r-- 1 wangjl wangjl 1.4M Jul 15  2009 data/web/docs/audio/20041118_day_10-Atlantis.mp3
```






# refer
- [range is inspired by] https://programtalk.com/vs4/python/2323/scout/scout/blueprints/pileup/partial.py/
- https://developer.mozilla.org/en-US/docs/Web/HTTP
- https://github.com/igvteam/igv.js/issues/1508
- https://github.com/igvteam/igv.js/wiki/Data-Server-Requirements