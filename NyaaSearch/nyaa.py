#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__      = "Ankirama"
__version__     = "1.0"
__email__       = "ankirama@gmail.com"
__status__      = "Development"

'''
Kat Search used as a base (just kept emojii unicodes)
'''

import sys, re
import urllib, urllib2
from bs4 import BeautifulSoup
from workflow import Workflow, ICON_WEB, web, ICON_WARNING
from transmission import Transmission
from workflow.notify import notify


URL = 'http://www.nyaa.se/?page=search&cats=0_0&filter=0&term='

def nyaa(wf):
    """
    Execute the query on nyaa.se and show the results.
    """
    # Emojii unicodes
    arrow_up = u"⬆"  # Seed
    arrow_down = u"⬇"  # Leech
    arrow_double = u"↕"  # Double arrow
    info = u"ℹ"
    # Take args and do the get request
    args = wf.args
    query = urllib.quote_plus(args[0].encode('utf-8'))
    url = URL + query
    r = web.get(url)
    try:  # Check for connection or HTTP error
        r.raise_for_status()
    except:
        wf.add_item('No torrents found with this query found.',
                subtitle='Check also your internet connection.',
                icon=ICON_WARNING)
        wf.send_feedback()
        return 0
    soup = BeautifulSoup(r.content, 'lxml') #use beautiful to parse html

    elts = soup.findAll('tr', attrs={'class':u'tlistrow'})
    if len(elts) == 0:
        wf.add_item('No torrents found with this query found.')
        wf.send_feedback()
        return 0
    for i in range(len(elts)):
        name = elts[i].find('td', attrs={'class':u'tlistname'}).text
        link = 'http://' + elts[i].find('td', attrs={'class':u'tlistdownload'}).a.get('href')[2:]
        size = elts[i].find('td', attrs={'class':u'tlistsize'}).text
        if elts[i].find('td', attrs={'class':u'tlistfailed'}):
            seeders = u'Unknown'
            leechers = u'Unknown'
        else:
            seeders = elts[i].find('td', attrs={'class':u'tlistsn'}).text
            leechers = elts[i].find('td', attrs={'class':u'tlistln'}).text
        downloads = elts[i].find('td', attrs={'class':u'tlistdn'}).text
        wf.add_item(name,
                    subtitle=arrow_up + "Seed: " + seeders + "|" + arrow_down + "Leech: " + leechers + "| " + arrow_double + "Size: " + size,
                    arg = link,
                    valid=True,
                    icon='torrent.png')
    wf.send_feedback()
    return 0

def registerTransmission(wf, tr):
    '''
    Create our file with server configuration
    '''
    args = wf.args[1].split()
    if len(args) == 2:
        # only address port
        tr.registerConfig(args[0], args[1])
    elif len(args) == 4:
        # address port user password
        tr.registerConfig(args[0], args[1], args[2], args[3])
    else:
        # error
        wf.add_item('You must specify at least an address and a port',
            icon=ICON_WARNING)
        wf.send_feedback()
    return

def main(wf):
    '''
    main to check args and call
    '''
    tr = Transmission(wf)
    if wf.args[0] == '--register' and len(wf.args) > 1:
        registerTransmission(wf, tr)
    elif wf.args[0] == '--reset':
        tr.resetConfig()
    elif wf.args[0] == '--copy' and len(wf.args) > 1:
        print(wf.args[1], end='')
        notify(title='Link copied in your clipboard')
    elif wf.args[0] == '--open' and len(wf.args) > 1:
        if tr.connection():
            tr.addTorrent(wf.args[1])
    else:
        nyaa(wf)

if __name__ == u"__main__":
    wf = Workflow()
    sys.exit(wf.run(main))
