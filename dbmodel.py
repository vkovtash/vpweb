#!/usr/bin/env python
# -*- coding: utf-8 -*-

from google.appengine.ext import ndb
from urlparse import urlparse

class ShowNDB(ndb.Model):
    url = ndb.StringProperty()
    service = ndb.ComputedProperty(lambda self: self.serviceName)
    data = ndb.JsonProperty()
    hash = ndb.StringProperty()
    lastChanged = ndb.DateTimeProperty(auto_now_add=True)

    @property
    def serviceName(self):
        return urlparse(self.url).netloc

class UsersWatchListNDB(ndb.Model):
    user = ndb.StringProperty()
    downloaded = ndb.JsonProperty(default=[])

if __name__=="__main__":
    pass