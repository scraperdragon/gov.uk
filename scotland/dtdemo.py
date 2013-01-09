#!/usr/bin/env python

from dumptruck import DumpTruck

dt = DumpTruck(dbname='scotland.db')
dt.create_table({'title': '', 'date': ''}, 'publications')
dt.create_index(['title'], 'publications', unique=True)


dt.upsert({'title': 'one', 'date': 'today'}, 'publications')
dt.upsert({'title': 'one', 'date': 'yesterday'}, 'publications')

data = dt.execute('SELECT * FROM `publications`')
print data
