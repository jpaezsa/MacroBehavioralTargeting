#!/usr/bin/python
# python ./fire_requests.py 107939332066

import sys
import os
import MySQLdb
import string
import time
import config
import random
import pymongo
from pymongo import MongoClient
import json
import urllib2
import urllib

config = config.config()
cursor_s = config.cursor_s

fb_id = str(sys.argv[1])

def returnListOfFBIDs():
  listOfID = {}
  query = "SELECT fb_id, fb_name , category FROM %s.priority WHERE priority > 0" % (config.db)
  try:
    cursor_s.execute(query)
  except:
    print "error reading fb_id from table" 

  for i in xrange(cursor_s.rowcount):
    row = cursor_s.fetchone()
    try:
      fb_name = unicode(row[1], errors='ignore')
    except:
      fb_name = u""
    try:
      category = unicode(row[2], errors='ignore')
    except:
      category = u""
    listOfID[str(row[0])] =  {"fb_name":fb_name , "category":category}

  query = "SELECT fb_id, fb_name , category FROM %s.priority WHERE category LIKE 'tv%'" % (config.db)
  try:
    cursor_s.execute(query)
  except:
    print "error reading fb_id from table" 

  for i in xrange(cursor_s.rowcount):
    row = cursor_s.fetchone()
    try:
      fb_name = unicode(row[1], errors='ignore')
    except:
      fb_name = u""
    try:
      category = unicode(row[2], errors='ignore')
    except:
      category = u""
    listOfID[str(row[0])] =  {"fb_name":fb_name , "category":category}
  return listOfID

#assume sorted list
def findLargestNegative(lst, num):
  lst = [x - num for x in lst]
  lst = [x for x in lst if x < 0]
  #lst.sort()
  if len(lst) > 0:
    return -lst[-1]
  else:
    return 0
def getPosts(fbid):
  listOfPosts = []
  unix_stamps = []
  query = "SELECT post_id, post_message , UNIX_TIMESTAMP(post_date), num_of_post_likes , num_of_comments , num_of_shares ,\
                  post_type FROM %s.%s%s LIMIT 50" % (config.db , fbid , config.suffix)
  try:
    cursor_s.execute(query)
  except:
    print "error reading fb_id from table" 

  for i in xrange(cursor_s.rowcount):
    row = cursor_s.fetchone()
    try:
      post_message = unicode(row[1], errors='ignore')
    except:
      post_message = u"unicode error"
    post = { "fb_id": fbid,
             "post_id": row[0],
             "text": post_message,
             "unix_stamp": int(row[2]),
             "num_of_post_likes": int(row[3]),
             "num_of_comments": int(row[4]),
             "num_of_shares": int(row[5]),
             "post_type": row[6]
            }
    unix_stamps.add(int(row[2]))
    listOfPosts.add(post)

  # need to get the time_since_last_post variable.
  unix_stamps.sort()
  for post in listOfPosts:
    post["time_since_last_post"] = findLargestNegative(unix_stamps,post["unix_stamp"])
  return listOfPosts


posts = getPosts(fb_id)
cursor_s.close()
req=urllib2.Request(config.endpoint, 
                    json.dumps(posts), 
                    {'Content-Type': 'application/json'} )
#f = urllib2.urlopen(req)
#print f.read()
