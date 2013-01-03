import requests
import lxml.html
import html2text
import scraperwiki
import requests_cache
import datetime

def parsedate(datestring, silent=False):
  import dateutil.parser
  import re
  if not datestring: return None
  if re.match('\d{4}-\d{2}-\d{2}', datestring): return datestring
  info=dateutil.parser.parserinfo(dayfirst=True)
  value=dateutil.parser.parser(info)._parse(datestring)
  if value==None: return None
  retval=[value.year, value.month, value.day]
  nones = retval.count(None)
  if nones==3:
    return None
  if nones==0:
    return u"%04d-%02d-%02d"%(retval[0], retval[1], retval[2])
  if not silent: 
    raise AttributeError, "Partial date: %s"%datestring
  return None

def htmlize(html):
  html2text.IGNORE_IMAGES=True
  md =html2text.HTML2Text()
  md.IGNORE_IMAGES=True
  #md.parse_weird_links=True # turn off images?
  return md.handle(html)

def doindex():
  sess = requests.session()

  url = 'http://news.bis.gov.uk/content/default.aspx?NewsAreaId=2'

  data = """__EVENTTARGET:PageIndex
__EVENTARGUMENT:6
__VIEWSTATE:/wEPDwUENTM4MQ9kFgJmD2QWAgIDDxYCHgdWaXNpYmxlaGRkON8gh+1oL6X0kby6IOIQ16qaik4=
txtKeyword:Keywords
txtFromDate:dd/mm/yy
txtToDate:dd/mm/yy
txtQuickSearch:Keywords"""

  datadict = dict([[h.partition(':')[0], h.partition(':')[2]] for h in data.split('\n')])
  x=sess.get(url)
  root=lxml.html.fromstring(x.text)
  datadict['__VIEWSTATE']= root.xpath('//input[@name="__VIEWSTATE"]/@value')[0]

  for i in range(1,130):
    print i
    datadict['__EVENTARGUMENT']=str(i)
    x=sess.post(url, data=datadict)
    root = lxml.html.fromstring(x.text)
    root.make_links_absolute(url)
    datadict['__VIEWSTATE']= root.xpath('//input[@name="__VIEWSTATE"]/@value')[0]
    builder=[]
    for item in root.xpath("//div[@class='results news']/div"):
      data = {
        'url':item.xpath("self::*//h3/a/@href")[0],
        'title':item.xpath("self::*//h3/a/text()")[0],
        'rawdate':item.xpath("self::*//p[@class='date']/text()")[0].strip(),
        'summary':htmlize(''.join([lxml.html.tostring(x) for x in item.xpath("self::*//div[@class='item-summary']/p[not(@class)]")]))
      }
      builder.append(data)
    scraperwiki.sqlite.save(table_name = '_index', data = builder, unique_keys = ['url'])
    print len(builder)
    if len(builder) != 10:
      break
try:
  scraperwiki.sqlite.execute("alter table _index add column date")
  scraperwiki.sqlite.execute("alter table _index add column markdown")
except Exception,e:
  print repr(e)


requests_cache.configure()
for i in scraperwiki.sqlite.select("url, rawdate from _index"):
  print i['url']
  r=requests.get(i['url'])
  html=r.text
  root=lxml.html.fromstring(html)
  fragment = root.xpath("//div[@class='news-details-body']")[0]
  markdown = htmlize(lxml.html.tostring(fragment))
  scraperwiki.sqlite.execute("update _index set markdown = ? where url = ?",(markdown, i['url']))
  
  nicedate = parsedate(i['rawdate'])
  nicerdate= datetime.datetime.strftime( datetime.datetime.strptime(nicedate, '%Y-%m-%d'), '%d-%b-%Y')
  if nicerdate[0]=='0': nicerdate=nicerdate[1:]
  scraperwiki.sqlite.execute("update _index set date = ? where url = ?",(nicerdate, i['url']))
  scraperwiki.sqlite.commit()
