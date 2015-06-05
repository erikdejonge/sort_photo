#!/usr/bin/env python
"""
unsplash-download - Downloads images from unsplash.com

Usage:
  unsplash-download <folder>
  unsplash-download -h | --help
  unsplash-download -v | --version

Options:
  -h --help                 Show this screen
  -v --version              Show version

"""

DEBUG = False
ud_version='1.0.2'

import urllib.request
import re
import os
import sys

from docopt import docopt, DocoptExit

try:
    from bs4 import BeautifulSoup, SoupStrainer
except ImportError as e:
    print("Could not import beatifulsoup4. Make sure it is installed.")
    if DEBUG:
        print(e, file=sys.stderr)
    sys.exit()

arguments     = docopt(__doc__, help=True, version='unsplash-download '+ud_version)
download_path = arguments['<folder>']
base_url      = 'https://unsplash.com'
page          = 1
link_search   = re.compile("/photos/[a-zA-Z0-9-]+/download")

if not os.path.exists(download_path):
    os.makedirs(download_path)

while True:
    url = base_url + "/?page=" + str(page)
    print("Parsing page %s" % url)
    try:
        soup = BeautifulSoup(urllib.request.urlopen(url).read(), "lxml")
        for tag in soup.find_all(href=link_search):
            image_id     = str(tag['href']).split('/')[2]
            download_url = base_url + str(tag['href'])
            
            if os.path.exists("%s/%s.jpeg" % (download_path, image_id)):
                print("Not downloading duplicate %s" % download_url)
                continue

            print("Downloading %s" % download_url)
            urllib.request.urlretrieve(
                base_url + str(tag["href"]),
                "%s/%s.jpeg" % (download_path, image_id)
            )
            
    except urllib.error.HTTPError as e:
        print("HTML error. This would be all.")
        if DEBUG:
            print(e, file=sys.stderr)
        break
    except HTMLParser.HTMLParseError as e:
        print('Error parsing the HTML', file=sys.stderr)
        if DEBUG:
            print(e, file=sys.stderr)
    except:
        print("An unknown error occured", file=sys.stderr)
    finally:
        page = page + 1