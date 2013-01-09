#!/usr/bin/env python

import sys
import json
import requests
import lxml.html
import html2text
from lxml import etree

from dumptruck import DumpTruck
from common import scrape_list_page, dumptruck_to_csv

URLS = [
    "http://www.scotlandoffice.gov.uk/scotlandoffice/16402.html?tID=16682&mon=jan",
    "http://www.scotlandoffice.gov.uk/scotlandoffice/16402.html?tID=16683&mon=feb",
    "http://www.scotlandoffice.gov.uk/scotlandoffice/16402.html?tID=16684&mon=mar",
    "http://www.scotlandoffice.gov.uk/scotlandoffice/16402.html?tID=16685&mon=apr",
    "http://www.scotlandoffice.gov.uk/scotlandoffice/16402.html?tID=16686&mon=may",
    "http://www.scotlandoffice.gov.uk/scotlandoffice/16402.html?tID=16687&mon=jun",
    "http://www.scotlandoffice.gov.uk/scotlandoffice/16402.html?tID=16688&mon=jul",
    "http://www.scotlandoffice.gov.uk/scotlandoffice/16402.html?tID=16689&mon=aug",
    "http://www.scotlandoffice.gov.uk/scotlandoffice/16402.html?tID=16690&mon=sep",
    "http://www.scotlandoffice.gov.uk/scotlandoffice/16402.html?tID=16691&mon=oct",
    "http://www.scotlandoffice.gov.uk/scotlandoffice/16402.html?tID=16692&mon=nov",
    "http://www.scotlandoffice.gov.uk/scotlandoffice/16402.html?tID=16693&mon=dec",
    "http://www.scotlandoffice.gov.uk/scotlandoffice/11311.162.html",
    "http://www.scotlandoffice.gov.uk/scotlandoffice/14802.html?tID=14804&mon=jan",
    "http://www.scotlandoffice.gov.uk/scotlandoffice/14802.html?tID=14805&mon=feb",
    "http://www.scotlandoffice.gov.uk/scotlandoffice/14802.html?tID=14806&mon=mar",
    "http://www.scotlandoffice.gov.uk/scotlandoffice/14802.html?tID=14807&mon=apr",
    "http://www.scotlandoffice.gov.uk/scotlandoffice/14802.html?tID=14808&mon=may",
    "http://www.scotlandoffice.gov.uk/scotlandoffice/14802.html?tID=14809&mon=jun",
    "http://www.scotlandoffice.gov.uk/scotlandoffice/14802.html?tID=14810&mon=jul",
    "http://www.scotlandoffice.gov.uk/scotlandoffice/14802.html?tID=14811&mon=aug",
    "http://www.scotlandoffice.gov.uk/scotlandoffice/14802.html?tID=14826&mon=sep",
    "http://www.scotlandoffice.gov.uk/scotlandoffice/14802.html?tID=14827&mon=oct",
    "http://www.scotlandoffice.gov.uk/scotlandoffice/14802.html?tID=14828&mon=nov",
    "http://www.scotlandoffice.gov.uk/scotlandoffice/14802.html?tID=14829&mon=dec",
    "http://www.scotlandoffice.gov.uk/scotlandoffice/13141.221.html?tID=13147&mon=may",
    "http://www.scotlandoffice.gov.uk/scotlandoffice/13141.221.html?tID=13148&mon=jun",
    "http://www.scotlandoffice.gov.uk/scotlandoffice/13141.221.html?tID=13149&mon=jul",
    "http://www.scotlandoffice.gov.uk/scotlandoffice/13141.221.html?tID=13150&mon=aug",
    "http://www.scotlandoffice.gov.uk/scotlandoffice/13141.221.html?tID=13151&mon=sep",
    "http://www.scotlandoffice.gov.uk/scotlandoffice/13141.221.html?tID=13152&mon=oct",
    "http://www.scotlandoffice.gov.uk/scotlandoffice/13141.221.html?tID=13153&mon=nov",
    "http://www.scotlandoffice.gov.uk/scotlandoffice/13141.221.html?tID=13154&mon=dec",
    "http://www.scotlandoffice.gov.uk/scotlandoffice/11330.162.html",
]

def htmlize(html):
    html2text.IGNORE_IMAGES=True
    md =html2text.HTML2Text()
    md.IGNORE_IMAGES=True
    return md.handle(html)


def scrape_main_article(url):
    req = requests.get(url)
    doc = lxml.html.fromstring(req.text)

    div = doc.xpath("//*[@class='wrapper']")[0]
    div.remove(div.find("h1"))
    for para in div.findall("p"):
        if para.find("strong") is not None:
            div.remove(para)
    return htmlize(etree.tostring(div))

dt = DumpTruck(dbname="scotland.db")
dt.create_table({"Title": "",
                 "Publication date": "",
                 "Old URL": "",
                 "Summary": "",
                 "Body": "",
                 "Associated organisations": ""}, "news")
dt.create_index(["Title", "Old URL"], "news", unique=True)

for url in URLS:
    for news_item in scrape_list_page(url):
        attachments = json.loads(news_item.pop("Attachments"))
        link = attachments[0]["link"]
        news_item["Old URL"] = link
        news_item["Body"] = scrape_main_article(link)
        dt.upsert(news_item, "news")

dumptruck_to_csv(dt, "news", "/home/http/scotland/news.csv")
