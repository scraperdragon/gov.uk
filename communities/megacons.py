import scraperwiki
import lxml.html
import requests
import html2text

scraperwiki.sqlite.execute("create table if not exists raw (link primary key, type)")
def dclg_pubs(cat='communities', url=None, t='dclg_pubs'):
        if not url:
            url = 'http://www.communities.gov.uk/%s/publications/all/'%cat
        page=scraperwiki.sqlite.get_var('dclg_pub_'+cat)
        print url
        if not page:
            page=1
        print page
        bail=False
        while not bail:
            print url, page
            
            params={'viewPrevious':'true','currentPageNumber':page}
            html=requests.get(url, params=params).content
            root=lxml.html.fromstring(html)
            root.make_links_absolute(url)
            links=root.xpath("//ul[@class='searchResultList']//h4/a")
            print len(links)
            try:
              print links[0].text_content()
            except:
              pass
            if len(links)<20:
                print "Only %d links on page %d of %s... bailing"%(len(links), page, url)
                bail=True
            if page>300:
                print "HUGE."
                bail=True
                
            for link in links:
                newurl=link.get('href')
                gotalready=scraperwiki.sqlite.select ("link from raw where link = ? and type = ?", [newurl, t])
                if len(gotalready)>0:
                #  print "Skip %r", gotalready
                   continue
                page_req=requests.get(newurl)
                page_u=page_req.text # guess
                page_stat=page_req.status_code
        
                data={'link':newurl, 'title':link.text_content(), 'html':page_u, 'status':page_stat, 'meta':'{"subtype":"%s"}'%cat, 'type':t} # TODO: META is wrong, should be json.
                scraperwiki.sqlite.save(table_name='raw', data={i:unicode(data[i]) for i in data}, unique_keys=['link'])
            page=page+1
            scraperwiki.sqlite.save_var('dclg_pub_'+cat, page)

pairs = [['nr_pn','http://www.communities.gov.uk/newsroom/pressnotices/'],
         ['nr_iar','http://www.communities.gov.uk/newsroom/issuesandresponses/'],
         ['nr_n','http://www.communities.gov.uk/newsroom/news/'],
         ['f_nr_ns','http://www.communities.gov.uk/fire/newsroom/newsstories/'],
         ['f_nr_n','http://www.communities.gov.uk/fire/newsroom/news/'],
         ['h_nr_ns','http://www.communities.gov.uk/housing/newsroom/newsstories/'],
         ['h_nr','http://www.communities.gov.uk/housing/newsroom/'],
         ['c_nr,ns','http://www.communities.gov.uk/corporate/newsroom/newsstories/'],
         ['c_nr_n','http://www.communities.gov.uk/corporate/newsroom/news/'],
         ['r_nr_ns','http://www.communities.gov.uk/regeneration/newsroom/newsstories/'],
         ['r_nr_n','http://www.communities.gov.uk/regeneration/newsroom/news/'],
         ['cs_nr_ns','http://www.communities.gov.uk/communities/newsroom/newsstories/'],
         ['cs_nr_n','http://www.communities.gov.uk/communities/newsroom/news/'],
         ['lg_nr_ns','http://www.communities.gov.uk/localgovernment/newsroom/newsstories/'],
         ['lg_nr_n','http://www.communities.gov.uk/localgovernment/newsroom/news/']]

for i in pairs:
    print i
    dclg_pubs(i[0], i[1], 'dclg_newsscrape')
