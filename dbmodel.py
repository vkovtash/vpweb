#!/usr/bin/env python
# -*- coding: utf-8 -*-

from google.appengine.ext import db
	
class Show(db.Model):
	service = db.StringProperty()
	url = db.StringProperty()
	data = db.BlobProperty()
	checksum = db.StringProperty()
	episode_count = db.IntegerProperty(default=0)
	
class TestWatchList(db.Model):
	show = db.ReferenceProperty(Show)
	data = db.BlobProperty()
	episode_count = db.IntegerProperty(default=0)