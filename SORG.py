#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3,time,downloader,os.path,sys,re,binascii,glob,subprocess,cookielib,re,urllib
from urlparse import urlparse
from settings import *

#import shutil #Удалить после отладки

try: 
	import json
except ImportError: 
	from django.utils import simplejson as json
	
	
SERVICE_NAME='serialsonline.org'
SERVICE_IDX="SORG"
DOWNLOAD_DIR=os.path.join(SETTINGS_DIR,SERVICE_IDX,"dwl")
ENCODE_DIR=os.path.join(SETTINGS_DIR,SERVICE_IDX,"enc")
POSTER_DIR=os.path.join(SETTINGS_DIR,SERVICE_IDX,"poster")
	
def dlcallback(full_length,cur_pos):
	print "\r","Downloaded: ",cur_pos/1048576,"/",full_length/1048576," Mb  ",cur_pos/(full_length/100),"%     ",
	sys.stdout.flush()
	
def FetchSeason(title):
	m=re.search(u'.*([0-9]+).*',title)
	#print title
	if m!=None:
		return int(m.group(1))
	else:
		return 1


def UpdateBK(sql_conn):
	#---------Обновление плэйлистов---------------
	#Определяет начало и конец зашифрованного урла плэйлиста
	pl_eurl_start="var playlist = \""
	pl_eurl_end="\";"
	
	
	#Получаем список закладок
	bk=downloader.JSONDocGet('http://movpaper.appspot.com/get',{"s":SERVICE_NAME}).data
	
	if bk==None:
		return
	
	
	for b in bk:
	
		#print b["title"]
		bk_path=urlparse(b["href"]).path
		bk_id=binascii.b2a_hex(str(binascii.crc32(bk_path)))
		print b["href"]
		
		
		
 		#Получаем интересующую страницу
 		show_page=downloader.HTMLDocGet(b["href"])
 		
 		#Если не удалось получить страницу, перейти к слеующей
 		if show_page.data==None:
 			continue
 		
  		vi_title="".join(show_page.data.xpath('//h1[@class="show-title"]/span[@class="en"]/descendant::text()')).replace("\n","").replace("\t","")
 		vi_season="".join(show_page.data.xpath('//h1[@class="show-title"]/span[@class="ru"]/descendant::text()')).replace("\n","").replace("\t","")
 		vi_title="".join([vi_title,' [',vi_season,']'])
 		print vi_title
 		
  		poster="".join(show_page.data.xpath('//ul[@class="seasons-list"]/li[@class="active"]/a/img/@src'))
  		print poster


 		pl_raw="".join(show_page.data.xpath('//div[@class="content"]/script/descendant::text()')).replace('\\/','/')

 		
 		data_start=pl_raw.find('p.setPlaylist( ')+15
 		pl_data=pl_raw[data_start:pl_raw.find(']',data_start)+1]
 		#print pl_data
 		
 		pl=json.loads(pl_data)
 		#print pl
			
  
 		pl_data=[]
 
 		for pl_ent in pl:
 			sq_num=pl.index(pl_ent)+1 #Порядок записи в плэйлисте
 			contid=binascii.b2a_hex(str(binascii.crc32(b["href"]+str(pl_ent[u"episodeId"]))))
 			pl_data.append((bk_id, contid, pl_ent[u"episodeId"], 0, sq_num))
 
 		#print pl_data
  			
 		bk_data=(bk_id,SERVICE_NAME,b["href"],int(time.time()),vi_title,poster)
		#print bk_data
		sql_conn.execute("replace into bookmarks(bookmarkid, service, bk_href, lastupdate, title, poster) values (?, ?, ?, ?, ?, ?)", bk_data)
		sql_conn.executemany("insert or ignore into bk_content(bookmarkid, contid, cont_href, isdownloaded, sq_num) values (?, ?, ?, ?, ?)", pl_data)
		
		sql_conn.commit()


def DwlCont(sql_conn):

	if not os.path.exists(DOWNLOAD_DIR):
		os.makedirs(DOWNLOAD_DIR)
		
	if not os.path.exists(POSTER_DIR):
		os.makedirs(POSTER_DIR)
		
	#--------Загрузка плэйлистов----------------
	sql_conn.row_factory = sqlite3.Row
	sql_cur=sql_conn.cursor() # создание курсора
	sql_update_cur=sql_conn.cursor()
	
	#Проверка наличия постеров
	
	sql_cur.execute("select * from bookmarks as b where b.service=:service",{"service":SERVICE_NAME})
	
	for row in sql_cur:
		poster_path=os.path.join(POSTER_DIR,row["bookmarkid"])
		
		if not os.path.exists(poster_path):
			downloader.fetchfile(row["poster"],poster_path,dlcallback)
	
	
	#Получить незагруженные файлы
	sql_cur.execute("select * from bookmarks as b inner join bk_content as bc on b.bookmarkid=bc.bookmarkid where bc.isdownloaded=:isdownloaded and b.service=:service",{"isdownloaded":0,"service":SERVICE_NAME})
	
	
	print "Pending downloads"
	
	for row in sql_cur:
		print row["title"],row["sq_num"]
	
	print "\nDownloading"
	
	sql_cur.execute("select * from bookmarks as b inner join bk_content as bc on b.bookmarkid=bc.bookmarkid where bc.isdownloaded=:isdownloaded and b.service=:service",{"isdownloaded":0,"service":SERVICE_NAME})

 	for row in sql_cur:
		cj = cookielib.CookieJar()
		show_page=downloader.HTMLDocGet(row["bk_href"],None,cj)
		
		#Если не удалось получить страницу, перейти к слеующей
 		if show_page.data==None:
 			continue

 		pl_raw="".join(show_page.data.xpath('//div[@class="content"]/script/descendant::text()')).replace('\\/','/')

 		
 		data_start=pl_raw.find('p.setPlaylist( ')+15
 		pl_data=pl_raw[data_start:pl_raw.find(']',data_start)+1]
 		#print pl_data
 		
 		pl=json.loads(pl_data)
 		#print pl
 		
 		rq_url=None
 		
 		for pl_ent in pl:
 			if pl_ent[u"episodeId"]==row["cont_href"]:
 				rq_url=pl_ent[u"file"]
		
		if rq_url==None:
			print "Can\'t find clip url"
			continue
		
		print rq_url
		
		filename=row["contid"]+".flv"
		print row["title"],row["sq_num"]
		
 		download_res=downloader.fetchfile(rq_url,os.path.join(DOWNLOAD_DIR,filename),dlcallback,cj)
 		
 		if download_res:
  			sql_update_cur.execute("update bk_content set isdownloaded=:isdwl where contid=:contid",{"isdwl":1,"contid":row["contid"]})
  			sql_conn.commit() 
  			sys.stdout.write("  OK\n")
			

def VideoConvert(sql_conn):

	if not os.path.exists(ENCODE_DIR):
		os.makedirs(ENCODE_DIR)
	
	videos=glob.glob("".join([DOWNLOAD_DIR,"/*.flv"]))
	
	ffmpeg_path=os.path.realpath("/usr/local/bin/ffmpeg")
	for v in videos:
		dfilename=os.path.basename(v)
		dpath=os.path.join(ENCODE_DIR,dfilename)
		
		os.rename(v,dpath)
		SetTags(sql_conn,dpath)

			

		
def SetTags(sql_conn,file):
	
	sql_conn.row_factory = sqlite3.Row
	sql_cur=sql_conn.cursor() # создание курсора

	AtomicParsley_path=os.path.realpath("/usr/bin/AtomicParsley")
	
	file_id=os.path.basename(file).replace(".flv","")
	
	#print file_id
	
	sql_cur.execute("select * from bookmarks as b inner join bk_content as bc on b.bookmarkid=bc.bookmarkid where bc.contid=:contid",{"contid":file_id})
	video_info=sql_cur.fetchone()
	
	print video_info["title"]
	titles=video_info["title"].split('[')
	basefilename=titles[0].strip()
	basefilename=basefilename.replace("  ","_")
	basefilename=basefilename.replace(" ","_")
	basefilename=basefilename.replace(":","")
	basefilename=basefilename.replace(";","")
	basefilename=basefilename.replace(",","")
	
	season=FetchSeason(titles[1])
	
	curfilename="".join([basefilename,"_S",str(season),"E",str(video_info["sq_num"]),".mp4"])
	
	poster_path=os.path.join(POSTER_DIR,video_info["bookmarkid"])
	
	print basefilename,str(season),str(video_info["sq_num"]),curfilename
	
	cmd=[AtomicParsley_path,file,"-W","--stik","TV Show","--TVShowName",video_info["title"],"--artist",video_info["title"],"--TVSeasonNum",str(season),"--TVEpisode",str(video_info["sq_num"]),"--TVEpisodeNum",str(video_info["sq_num"]),"--artwork",poster_path]
	#print "".join(cmd)
	
	print "adding tags"
	p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
	resultcode=p.wait()
	
	if resultcode==0:
		print os.path.join(VIDEO_DIR,curfilename)
		os.rename(file,os.path.join(VIDEO_DIR,curfilename))
		
#=============MAIN==========================
if __name__=="__main__":
	import sqlite3, time, os.path, sys
	
	#--------Проверка не запущен ли уже один экземпляр приложения
	try:
		import socket
		s = socket.socket()
		host = socket.gethostname()
		port = 35636    #make sure this port is not used on this system
		s.bind((host, port))
	except:
		#pass
		print "Already running. Exiting."
		sys.exit(0)
	
	#--------Инициализация приложения-------------
	
	if not os.path.exists(SETTINGS_DIR):
		os.makedirs(SETTINGS_DIR)
		
	if not os.path.exists(DOWNLOAD_DIR):
		os.makedirs(DOWNLOAD_DIR)
		
	if not os.path.exists(ENCODE_DIR):
		os.makedirs(ENCODE_DIR)
		
	if not os.path.exists(POSTER_DIR):
		os.makedirs(POSTER_DIR)
	
	if not os.path.exists(VIDEO_DIR):
		os.makedirs(VIDEO_DIR)
	
	bd_path=os.path.join(SETTINGS_DIR,SQLLITE_BD)
	
	sql_conn = sqlite3.connect(bd_path)
	
	sql_conn.execute("create table if not exists bookmarks(bookmarkid, service, bk_href, lastupdate, title, CONSTRAINT [PK_bookmarks] PRIMARY KEY ([bookmarkid] ASC))")
	sql_conn.execute("create table if not exists bk_content(bookmarkid, contid, cont_href, isdownloaded, sq_num, CONSTRAINT [PK_bk_content] PRIMARY KEY ([contid] ASC))")

	
	print time.ctime()
	print "Checking "+SERVICE_IDX
	UpdateBK(sql_conn)
	DwlCont(sql_conn)
	VideoConvert(sql_conn)

	sql_conn.close()
