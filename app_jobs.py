#!/usr/bin/env python
# -*- coding: utf-8 -*-


from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
import hashlib
from urlparse import urlparse
import os.path
		
import AOS
from dbmodel import *
import json

class AddShow(webapp.RequestHandler):
	def get(self):
        
		title=self.request.get('t')
		url=self.request.get('u')
		service=urlparse(url).netloc
		
		hash=hashlib.md5()
		hash.update(url)
		key=hash.hexdigest()
		
		bookmark=Show.get_or_insert(key)
		bookmark.url=url
		bookmark.service=service
		bookmark.put()
		
		watch_list_et=TestWatchList()
		watch_list_et.show=bookmark.key()
		watch_list_et.put()
	
	post = get
	
class UpdateShowsJob(webapp.RequestHandler):
	def get(self):
		AOS.UpdateBK()
		#SORG.UpdateBK()
		
class GetNewEpisodes(webapp.RequestHandler):
	def get(self):
		
		new_ep_list=[]
		
		for bk in TestWatchList.all().fetch(1000):
			if bk.episode_count<bk.show.episode_count:
				bk_ep=set([])
				show_data={}
				if bk.show.data!=None:
					show_data=json.loads(bk.show.data)
				else:
					continue
					
				if bk.data!=None:
					bk_ep=set(json.loads(bk.data)['episode_list'])
				
				show_ep=set(show_data['episode_list'])
				
				for new_ep in (show_ep-bk_ep):
					new_ep_list.append({'show':str(bk.show.key()),'episode':new_ep,'url':show_data['episodes'][new_ep]})
		
		resp=json.dumps({'response':{'episodes':new_ep_list}})
		self.response.out.write(resp)
		
class MainHandler(webapp.RequestHandler):
	def get(self):
		for show in Show.all().fetch(1000):
			self.response.out.write(show.data)
			

