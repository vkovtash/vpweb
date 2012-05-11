#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib, urllib2, email, lxml, lxml.html, json

class Resp:
	data=None
	info=None
	def __init__(self,data,info):
		self.data=data
		self.info=info

def HeadersPost(url,params=None,cookie=None):
	if cookie is None:
		opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
	else:
		opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
	
	if params is not None:
		rq_data=urllib.urlencode(params)
		req=urllib2.Request(url,rq_data)
	else:
		req=urllib2.Request(url)
	
	try:
		resp=opener.open(req)
		return email.message_from_string(str(resp.info()))
	except (urllib2.URLError,urllib2.HTTPError) as url_err:
		print "HTTP Error:",url_err.code
		return None

def HeadersGet(url,params=None,cookie=None):
	if params is not None:
		rq_url="".join([url,"?",urllib.urlencode(params)])
	else:
		rq_url=url
		
	return HeadersPost(rq_url,None,cookie)

def DocPost(url,params=None,cookie=None):
	if cookie is None:
		opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
	else:
		opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))

	if params is not None:
		rq_data=urllib.urlencode(params)
		req=urllib2.Request(url,rq_data)
	else:
		req=urllib2.Request(url)
	
	try:
		resp=opener.open(req)
		#doc=resp.read()
		return Resp(resp.read(),resp.info())
	except (urllib2.URLError,urllib2.HTTPError) as url_err:
		print "HTTP Error:",url_err.code
		return None


def DocGet(url,params=None,cookie=None):
	if params is not None:
		rq_url="".join([url,"?",urllib.urlencode(params)])
	else:
		rq_url=url
		
	return DocPost(rq_url,None,cookie)

def JSONDocGet(url,params=None,cookie=None):
	
	doc = DocGet(url,params,cookie)
	
	if doc.data is None:
		return Resp(None,doc.info)
	else:
		return Resp(json.loads(doc.data),doc.info)

def JSONDocPost(url,params=None,cookie=None):
	
	doc = DocPost(url,params,cookie)
	
	if doc.data is None:
		return Resp(None,doc.info)
	else:
		return Resp(json.loads(doc.data),doc.info)
		
def HTMLDocGet(url,params=None,cookie=None):
	
	doc = DocGet(url,params,cookie)
	
	if doc.data is None:
		return Resp(None,doc.info)
	else:
		return Resp(lxml.html.document_fromstring(doc.data),doc.info)

def HTMLDocPost(url,params=None,cookie=None):
	
	doc = DocPost(url,params,cookie)
	
	if doc.data is None:
		return Resp(None,doc.info)
	else:
		return Resp(lxml.html.document_fromstring(doc.data),doc.info)