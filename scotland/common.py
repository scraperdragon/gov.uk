import requests
import urlparse
import lxml.html
import json
from lxml import etree
import sys

from csvtools import UnicodeWriter

def scrape_list_page(url):
    print "Scraping %s" % url
    req = requests.get(url)
    doc = lxml.html.fromstring(req.text)

    items = []
    for item in doc.xpath("//*[@class='newspanel clearDiv']"):
        full_title = etree.tostring(item.xpath("./h2")[0], method="text", encoding='utf8')
        date, title = [x.strip() for x in full_title.split("|")]
       
        attachments = [] 
        raw_links = item.xpath(".//a/@href")
        for raw_link in raw_links:
             attachment = urlparse.urljoin(url, raw_link)
             attachment_title = item.xpath(".//a/text()")[0]
             attachments.append({"link": attachment,
                                 "title": attachment_title})

        try:
            summary = item.xpath("./p")[0].text
        except IndexError:
            summary = ""
   
        items.append({"Title": title,
                      "Publication date": date,
                      "Old URL": url,
                      "Summary": summary,
                      "Attachments": json.dumps(attachments),
                      "Associated organisations": "Scotland Office"})
        
    return items

def dumptruck_to_csv(dt, table, filepath):
    print "Generating CSV"
    with open(filepath, "wb") as csvfile:
        rows =  dt.execute("SELECT * FROM %s" % table)
    
        writer = UnicodeWriter(csvfile)
        writer.writerow(rows[0].keys())
        
        for row in rows:
            writer.writerow([x or '' for x in row.values()])
    
            writer2 = UnicodeWriter(sys.stderr)
            writer2.writerow([x or '' for x in row.values()])
