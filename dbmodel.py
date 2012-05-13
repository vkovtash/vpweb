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
    service = ndb.ComputedProperty(lambda self: self.serviceName())
    data = ndb.JsonProperty()
    hash = ndb.StringProperty()

    def serviceName(self):
        if self.url is not None:
            return urlparse(self.url).netloc
        else:
            return None

class UsersWatchListNDB(ndb.Model):
    user = ndb.StringProperty()
    downloaded = ndb.JsonProperty(default=[])

if __name__=="__main__":
    pass