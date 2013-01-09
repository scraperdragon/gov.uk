import lxml.html
from lxml import etree
import requests
import urlparse
import json

from dumptruck import DumpTruck
from common import dumptruck_to_csv

URL = "http://www.scotlandoffice.gov.uk/scotlandoffice/14463.363.html"

req = requests.get(URL)
doc = lxml.html.fromstring(req.text)

dt = DumpTruck(dbname="scotland.db")
dt.create_table({"Title": "",
                 "Publication date": "",
                 "Old URL": "",
                 "Body": "",
                 "Attachments": "",
                 "Associated organisations": "",
                 "Associated Document Series": ""}, "statistics")
dt.create_index(["Title", "Old URL"], "statistics", unique=True)

for link in doc.xpath("//div[@class='wrapper']/ul/li/a"):
    series_title, series_url = link.text, urlparse.urljoin(URL, link.attrib["href"])
    print series_title

    series_req = requests.get(series_url)
    series_doc = lxml.html.fromstring(series_req.text)

    for table_line in series_doc.xpath("//tr[not(@bgcolor) or @bgcolor!='#004093']"):
        file_pub_date = table_line.xpath("./td[3]")[0].text

        for file_node in table_line.xpath("./td[2]//a"):
            file_title = etree.tostring(file_node, method="text", encoding="utf8")
            file_link = file_node.attrib["href"]
            if not file_link.startswith("http"):
                file_link = urlparse.urljoin(URL, file_link)

            file_data = {"Old URL": series_url,
                         "Title": file_title,
                         "Body": file_title,
                         "Publication date": file_pub_date,
                         "Attachment": file_link,
                         "Attachment title": file_title,
                         "Associated organisations": "Scotland Office",
                         "Associated Document Series": series_title}
            dt.upsert(file_data, "statistics")

dumptruck_to_csv(dt, "statistics", "/home/http/scotland/stats.csv")
