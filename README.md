shellshock-hunter
========

Search Google and concurrently test each result for vulnerability to CVE-2014-6271: remote code execute bug in bash otherwise known as Shellshock.

Installation
-----
Requires Python 2.7

``` shell
pip install --user selenium gevent
git clone https://github.com/DanMcInerney/shellshock-hunter-google
cd shellshock-hunter-google/
```

Example
-----

``` shell
python shellshock-hunter-google.py -s "inurl:cgi-bin filetype:sh" -p 2
```

Open up Firefox, search for the dork "inurl:cgi-bin filetype:sh", and visit the first two pages of results where one page = 100 results. Then it will test each result URL for Shellshock vulnerability. -p option will default to 1 page if not given.


Output will look like:
``` shell
[!] SHELLSHOCK VULNERABLE: http://domain.com/cgi-bin/script.sh
```

Google Dorks
-----
* inurl:"server-status"  intitle:apache "cgi-bin"
* sitemap.xml filetype:xml intext:"cgi-bin"
* filetype:sh inurl:cgi-bin
* inurl:cgi-bin "GATEWAY_INTERFACE = CGI"
* inurl:cgi-bin inurl:printenv intext:SERVER_ADDR

