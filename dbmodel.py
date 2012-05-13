#!/usr/bin/env python
# -*- coding: utf-8 -*-

from google.appengine.ext import db
from google.appengine.ext.db import Key
from google.appengine.api import memcache
import hashlib
from urlparse import urlparse
import logging

class ShowDB(db.Model):
    service = db.StringProperty()
    url = db.StringProperty()
    data = db.BlobProperty()
    hash = db.StringProperty()
    version = db.IntegerProperty(default=0)

class UsersWatchList(db.Model):
    show = db.ReferenceProperty(ShowDB)
    data = db.BlobProperty()
    version = db.IntegerProperty(default=0)

class Show():
    def __init__(self,showKey=None):
        self._showURL=None
        self._showDBEnry=None
        self._showKey=showKey

    @property
    def showDBEntry(self):
        if self.showKeyName is not None and self._showDBEnry is None:
            self._showDBEnry=ShowDB().get_or_insert(self.showKeyName)
        return self._showDBEnry

    @property
    def showURL(self):
        memcachePrefix="showURL_"

        if self._showURL is None:
            self._showURL=self.__memcacheGet(memcachePrefix)
            if self._showURL is None:
                self._showURL=self.showDBEntry.url
                self.__memcacheSet(memcachePrefix,self._showURL)
        return self._showURL

    @showURL.setter
    def showURL(self,value):
        self._showURL=value

    @property
    def showKeyName(self):
        if self._showKey is None and self.showURL is not None:
            hash=hashlib.md5()
            hash.update(self.showURL)
            self._showKey=Key.from_path('ShowDB',hash.hexdigest())

        return self._showKey.name()

    @property
    def showKey(self):
        return self._showKey

    @property
    def showService(self):
        result=urlparse(self.showURL).netloc
        return result

    @property
    def showHash(self):
        memcachePrefix="showHash_"
        result=self.__memcacheGet(memcachePrefix)

        if result is None and self._showDBEnry is not None:
            self.showDBEntry.get_by_key_name(self.showKeyName)
            result=self._showDBEnry.hash
            self.__memcacheSet(memcachePrefix,result)

        return result

    @property
    def showVersion(self):
        memcachePrefix="showVersion_"
        result=self.__memcacheGet(memcachePrefix)

        if result is None and self._showDBEnry is not None:
            result=self._showDBEnry.version
            self.__memcacheSet(memcachePrefix,result)

        return result

    @property
    def showData(self):
        memcachePrefix="showData_"
        result=self.__memcacheGet(memcachePrefix)

        if result is None and self._showDBEnry is not None:
            result=self._showDBEnry.data
            self.__memcacheSet(memcachePrefix,result)

        return result

    def setShowData(self,value):
        if value is not None:
            hash=hashlib.md5()
            hash.update(value)
            newDataHash=hash.hexdigest()

            if newDataHash!=self.showHash:
                self.showDBEntry.version=self.showVersion+1
                self.showDBEntry.data=value
                self.showDBEntry.hash=newDataHash
                self.showDBEntry.put()
                self.__memcacheSet("showVersion_",self.showVersion+1)
                self.__memcacheSet("showData_",self.showData)
                self.__memcacheSet("showHash_",newDataHash)

    def __memcacheSet(self,keyPrefix,data):
        memcache.add(keyPrefix+self.showKeyName, data)


    def __memcacheGet(self,keyPrefix):
        return memcache.get(keyPrefix+self.showKeyName)


    def register(self,url):
        if self._showURL != url and url is not None:

            self._showURL=url
            self.showDBEntry.url=self.showURL
            self.showDBEntry.service=self.showService
            self.showDBEntry.put()

        else:
            raise


if __name__=="__main__":
    testShow=Show()
    testShow.register("http://ya.ru")
    print testShow.showURL
    print testShow.showKeyName
    print testShow.showService