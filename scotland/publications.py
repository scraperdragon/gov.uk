#!/usr/bin/env python

from dumptruck import DumpTruck
from common import scrape_list_page, dumptruck_to_csv

URLS = [
    ["http://www.scotlandoffice.gov.uk/scotlandoffice/10801.134.html", "Publications"],
    ["http://www.scotlandoffice.gov.uk/scotlandoffice/10802.137.html", "Written Ministerial statements"],
    ["http://www.scotlandoffice.gov.uk/scotlandoffice/13042.182.html", "Oral Ministerial Statements"],
    ["http://www.scotlandoffice.gov.uk/scotlandoffice/10797.135.html", "Reports and accounts"],
    ["http://www.scotlandoffice.gov.uk/scotlandoffice/16668.141.html?tID=16669&mon=jan", "Latest releases"],
    ["http://www.scotlandoffice.gov.uk/scotlandoffice/16668.141.html?tID=16670&mon=feb", "Latest releases"],
    ["http://www.scotlandoffice.gov.uk/scotlandoffice/16668.141.html?tID=16671&mon=mar", "Latest releases"],
    ["http://www.scotlandoffice.gov.uk/scotlandoffice/16668.141.html?tID=16672&mon=apr", "Latest releases"],
    ["http://www.scotlandoffice.gov.uk/scotlandoffice/16668.141.html?tID=16673&mon=may", "Latest releases"],
    ["http://www.scotlandoffice.gov.uk/scotlandoffice/16668.141.html?tID=16674&mon=jun", "Latest releases"],
    ["http://www.scotlandoffice.gov.uk/scotlandoffice/16668.141.html?tID=16677&mon=jul", "Latest releases"],
    ["http://www.scotlandoffice.gov.uk/scotlandoffice/16668.141.html?tID=16676&mon=aug", "Latest releases"],
    ["http://www.scotlandoffice.gov.uk/scotlandoffice/16668.141.html?tID=16678&mon=sep", "Latest releases"],
    ["http://www.scotlandoffice.gov.uk/scotlandoffice/16668.141.html?tID=16679&mon=oct", "Latest releases"],
    ["http://www.scotlandoffice.gov.uk/scotlandoffice/16668.141.html?tID=16680&mon=nov", "Latest releases"],
    ["http://www.scotlandoffice.gov.uk/scotlandoffice/10804.146.html", "Archive releases"], # 2005
    ["http://www.scotlandoffice.gov.uk/scotlandoffice/10805.145.html", "Archive releases"], # 2006
    ["http://www.scotlandoffice.gov.uk/scotlandoffice/10806.144.html", "Archive releases"], # 2007
    ["http://www.scotlandoffice.gov.uk/scotlandoffice/10807.143.html", "Archive releases"], # 2008
    ["http://www.scotlandoffice.gov.uk/scotlandoffice/13342.html", "Archive releases"], # 2009
    ["http://www.scotlandoffice.gov.uk/scotlandoffice/13661.html", "Archive releases"], # 2010
    ["http://www.scotlandoffice.gov.uk/scotlandoffice/15263.html", "Archive releases"], # 2011
]

dt = DumpTruck(dbname="scotland.db")
dt.create_table({"Title": "",
                 "Publication date": "",
                 "Old URL": "",
                 "Summary": "",
                 "Attachments": "",
                 "Type": "",
                 "Associated organisations": ""}, "publications")
dt.create_index(["Title", "Old URL"], "publications", unique=True)

for url, page_type in URLS:
    for publication in scrape_list_page(url):
        publication['Type'] = page_type
        dt.upsert(publication, "publications")

dumptruck_to_csv(dt, "publications", "/home/http/scotland/publications.csv")
