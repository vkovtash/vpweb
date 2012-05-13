#!/usr/bin/env python
# -*- coding: utf-8 -*-

from google.appengine.ext import ndb
import hashlib
from urlparse import urlparse

def genHash(value):
    hash=hashlib.md5()
    hash.update(value)
    return hash.hexdigest()

class ShowNDB(ndb.Model):
    url = ndb.StringProperty()
    version = ndb.IntegerProperty(default=0)
    service = ndb.StringProperty()
    data = ndb.JsonProperty()
    hash = ndb.StringProperty()

class UsersWatchListNDB(ndb.Model):
    user = ndb.StringProperty()
    downloaded = ndb.JsonProperty(default=[])

if __name__=="__main__":
    pass