def parsedate(datestring, outformat = "%d %b %Y", silent=False):
  """returns formatted date or None."""
  """fails if only partial date."""
  """Note: ISO = %Y-%m-%d"""
  """Cabinet office like %d %b %Y"""
  # TODO make dateformat optional.

  import dateutil.parser
  import datetime
  import re
  if not datestring: return None
  info=dateutil.parser.parserinfo(dayfirst=True)
  value=dateutil.parser.parser(info)._parse(unicode(datestring))
  if value==None: return None
  retval=[value.year, value.month, value.day]
  nones = retval.count(None)
  if nones==3: # complete failure to parse anything dateshaped
    return None
  if nones==0:
    d = datetime.date(value.year,value.month,value.day)
    return d.strftime(outformat)
    #return u"%04d-%02d-%02d"%(retval[0], retval[1], retval[2])
    pass    
  if not silent: # and there's some but not all date fragments
    raise AttributeError, "Partial date: %s"%datestring
  return None
