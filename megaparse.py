import lxml.html
import scraperwiki
import json
import html2text

def makeidentifier(s):
    import string
    s=s.strip().replace(' ','_')
    valid_chars = "_%s%s" % (string.ascii_letters, string.digits)
    out=''.join(c for c in s if c in valid_chars)
    if len(out)==0:
        return '_'
    else:
        return out

def __onecss(self, selector, silent=False):
    """Do or be mildly irked: get the first CSSSelector match"""
    x=self.cssselect(selector)
    if len(x) != 1 and not silent:
        #self.notify('looked for "%s" in tag "%s", found %d!'%(selector, self.tag, len(x)))
        self.notify({'source':'onecss', 'selector':selector, 'tag':self.tag, 'count':len(x)})
    if len(x)==0:
        return emptyish
    else:
        return x[0]

lxml.html.HtmlElement.onecss=__onecss

def dclg_core(html,parsearg,meta):
    #print meta['__link']
    #html=html.encode('latin-1')
    root=lxml.html.fromstring(html)
    root.make_links_absolute(meta['__link'])
    data={}
    
    # metadata
    metadata_heads=root.xpath("//div[@id='centerColumn']//table[1]//tr/th")
    metadata_data=root.xpath("//div[@id='centerColumn']//table[1]//tr/td")
    data=dict(zip([m.text_content().strip() for m in metadata_heads], [m.text_content().strip() for m in metadata_data]))

    # breadcrumbs
    breadcrumbs=root.xpath("id('Breadcrumbs')//a")
    for crumb in breadcrumbs:
        assert crumb.attrib['href'] in breadcrumbs[-1].attrib['href']
    data['crumbs']=[{'name':crumb.text, 'crumburl':crumb.get('href')} for crumb in breadcrumbs]
    
    
    if 'speech' not in meta:
        try:
            data['title']=root.get_element_by_id('Page').onecss('h2').text.strip() # not speeches
            if data['title']=='Archived content':
                data['title']=root.get_element_by_id('Page').cssselect('h2')[1].text.strip()
        except AttributeError:
            pass
    #print data
    
    return data,root

def PARSEdclg_news(html, parsearg, meta):
    #print meta['__link']
    data,root=dclg_core(html, parsearg, meta)
    data['html']=''.join([lxml.html.tostring(x) for x in root.xpath("//div[@id='Page']/*[name() != 'h2' and name() != 'table']")])
    for item in root.xpath("//div[@id='Page']/table[1]//tr"):
        data['t_'+makeidentifier(item.onecss('th').text_content())]=item.onecss('td').text_content()
    imgs= root.xpath("//div[@id='Page']//img")
    data['images']=[{'url':i.get('src'), 'alt':i.get('alt')} for i in imgs]
    md =html2text.HTML2Text()
    md.parse_weird_links=True # turn off images?
    data['markdown']=md.handle(data=data['html']) # there's at least one.
    return [data]

scraperwiki.sqlite.execute('create table if not exists output (link primary key, data, err)')

qselect = ["raw.link AS link", "raw.type ctype", "raw.html AS html", "'' AS parsearg", "raw.meta as meta" ]
qselect.append('"" as otype, raw.type as rtype')
qfrom = ["FROM raw"]
qfrom.append("LEFT JOIN output ON raw.link=output.link")
qwhere = ['where ctype is "dclg_newsscrape" and raw.link not in (select link from output)']
qlimit = "limit 200000 offset 0"
query = "%s %s %s %s" % (", ".join(qselect), " ".join(qfrom), " ".join(qwhere), qlimit)
print query
rows = scraperwiki.sqlite.select(query)
print len(rows)
for row in rows:
  meta = json.loads( row['meta'])
  meta['__link'] = row['link']
  out = PARSEdclg_news(row['html'], '', meta)
  out[0]['link']=row['link']
  sql={'link': row["link"],
       'data': json.dumps(out)}
  scraperwiki.sqlite.save(unique_keys=['link'], data=sql, table_name="output", verbose=0)
  print ".",
  
