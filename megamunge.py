# coding=utf-8
deleteme = u"""
### Twitter
Keep up to date with\xa0the Department by following us on [Twitter](http://twitter.com/CommunitiesUK) (external link).
### Media enquiries
Visit our [newsroom contacts page](http://www.communities.gov.uk/corporate/about/who/policycontacts/newsroomcontacts) for media enquiry contact details.
*[ kb]: Kilobytes
*[kb]: Kilobytes
*[MS Word]: Microsoft Word
*[PDF]: Portable Document
*[PDF]: Portable Document Format
*[MS Excel]: Microsoft Excel
""".strip().split('\n')

warnme = ['### Twitter', '[Twitter]','### Media','[newsroom contacts page]', '[ kb]', '[MS Word]', '[kb]', '[MS Excel]', '[PDF]']

w = open('http/megacsv2.csv','w')
with open('http/megacsv.csv', 'r') as f:
  for rn, r in enumerate(f.readlines()):
    p=True
    for i in warnme:
      if i in r:
        p=False
        if unicode(r.strip(), 'utf-8') not in deleteme:
          print rn
          print repr(unicode(r.strip(), 'utf-8')) 
          print repr(deleteme[4])
          exit()
    if p:
      w.write(r)
      
w.close()



