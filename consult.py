import requests
import scraperwiki
import lxml.html

sess=requests.session()
def get(url):
    return sess.get(url, verify=False) 

def dclg_consult():
    #sess.get('http://www.communities.gov.uk/corporate/publications/consultations/') # set cookies
    baseurl='http://www.communities.gov.uk/corporate/publications/consultations/?doPaging=true&resultsPerPage=1000&currentPageNumber=1'
    #resp=sess.get(baseurl)
    #html=resp.content
    #with open("consult.html", "w") as f:
    #    f.write(html)
    #    exit()
    html=""
    with open("consult.html", "r") as f:
        html=f.read()
    root=lxml.html.fromstring(html)
    root.make_links_absolute(baseurl)
    links=root.xpath("//form[@id='frmConsultations']//a")
    sql = "link from raw"
    print sql
    gotalready=scraperwiki.sqlite.select(sql)
    gotlinks=[x['link'] for x in gotalready]
    print len(gotlinks), repr(gotlinks[0])
    print len(links), repr(links[3])
    for i, link in enumerate(links):
        #gotalready=scraperwiki.sqlite.select ("link from raw where link = ? and type = 'dclg_consult'", link.get('href'))
        if link.get('href') in gotlinks:
            print "Skip %r"% gotalready
            continue
                
        print 'get',i,link.get('href')
        page_req=get(link.get('href'))
        page_u=page_req.text # guess
        page_stat=page_req.status_code
        print page_stat

        data={'link':link.get('href'), 'title':unicode(link.text_content()), 'html':unicode(page_u), 'status':unicode(page_stat), 'meta':unicode(''), 'type':'dclg_consult'}
        print 'save'
        scraperwiki.sqlite.save(table_name='raw', data=data, unique_keys=['link'])

scraperwiki.sqlite.execute("create table if not exists raw(link, title, html, status, meta, type)")
dclg_consult()
