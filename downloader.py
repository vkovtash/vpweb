#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib, urllib2, email, lxml, lxml.html, json, httplib, os, time, socket

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


def fetchfile (url,dest_filename,callback=None,cookie=None,part_size=524288,try_count=5):

    tmp_filename=dest_filename+'.tmp'

    #Создаем opener c обработкой кукисов
    if cookie is None:
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
    else:
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))

    req = urllib2.Request(url)

    for ctry in xrange(try_count):

        try:

            resp=opener.open(req,timeout=10)


            finfo = email.message_from_string(str(resp.info()))

            if finfo.get('Content-Length') is None:
                #Не поддерживает Content-Length
                tmpfile = open(tmp_filename,"wb")
                resp=opener.open(req,timeout=10)
                tmpfile.write(resp.read())

            else:
                #Поддерживает Content-Length
                full_clength=int(finfo.get('Content-Length'))

                if os.path.exists(tmp_filename):
                    tmpfile = open(tmp_filename,"ab")
                    foffset = os.path.getsize(tmp_filename)

                    if foffset>=full_clength:
                        tmpfile.close()
                        os.rename(tmp_filename,dest_filename)
                        return True

                    #If the file exists, then only download the remainder
                    req.add_header("Range","bytes=%s-" % foffset)
                #print foffset
                else:
                    tmpfile = open(tmp_filename,"wb")
                    foffset=0

                resp=opener.open(req,timeout=10)

                finfo = email.message_from_string(str(resp.info()))
                clength=int(finfo.get('Content-Length'))

                #print 'Left: ', clength

                parts=xrange(foffset,clength+foffset,part_size)

                for part in parts:
                    tmpfile.write(resp.read(part_size))

                    if callback is not None:
                        callback(full_clength,part)

            tmpfile.close()
            os.rename(tmp_filename,dest_filename)
            return True #Выход в случае, если загрузка завершилась без ошибок
        except urllib2.URLError:
            print "\nUrlError",ctry
            #tmpfile.close()
            time.sleep(10)
            continue
        except urllib2.HTTPError as url_err:
            #print url_err.code
            if url_err.code!=416: #416 возникает когда загрузка завершена
                print "\nHTTPError not 416",url_err.code,ctry
                tmpfile.close()
                resp.close()
                time.sleep(10)
                continue
            else:
                print "\nHTTPError 416",ctry
                tmpfile.close()
                resp.close()
                break
        except httplib.BadStatusLine:
            print "\nBadStatusLine",ctry
            tmpfile.close()
            resp.close()
            time.sleep(10)
            continue
        except socket.timeout:
            print "\nsocket timeout",ctry
            tmpfile.close()
            resp.close()
            time.sleep(10)
            continue

    return False