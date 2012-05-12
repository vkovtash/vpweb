#!/usr/bin/env python
# -*- coding: utf-8 -*-

from google.appengine.ext import db
import hashlib
from urlparse import urlparse

class ShowDB(db.Model):
	service = db.StringProperty()
	url = db.StringProperty()
	data = db.BlobProperty()
	hash = db.StringProperty()
	episodeCount = db.IntegerProperty(default=0)
	
class TestWatchList(db.Model):
	show = db.ReferenceProperty(ShowDB)
	data = db.BlobProperty()
	episodeCount = db.IntegerProperty(default=0)


class Show():
    def __init__(self):
        self._showDBEnry=None
        self._showURL=None
        self._showData=None


    @property
    def showURL(self):
        return self._showURL

    @showURL.setter
    def showURL(self,value):
        self._showURL=value

    @property
    def showKey(self):
        hash=hashlib.md5()
        hash.update(self.showURL)
        key=hash.hexdigest()

        return key

    @property
    def showService(self):
        return urlparse(self.showURL).netloc

    def register(self,url):
        self._showDBEnry=ShowDB()

        self.showURL=urlparse(url).netloc

        self._showDBEnry=ShowDB.get_or_insert(self.showKey)
        self._showDBEnry=self.showURL
        self._showDBEnry.service=self.showService
        self._showDBEnry.put()




