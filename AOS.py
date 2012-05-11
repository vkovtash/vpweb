#!/usr/bin/env python
# -*- coding: utf-8 -*-

from google.appengine.ext import db
from dbmodel import *

import time,downloader,os.path,re
from urlparse import urlparse
from settings import *
import json
import hashlib	
	
SERVICE_NAME='animeonline.su'
SERVICE_IDX="AOS"

AOS_KEY1 = {
			"codec_a":["5", "d", "9", "U", "D", "y", "H", "7", "t", "6", "l", "x", "c", "w", "R", "p", "s", "g", "e", "L", "8", "o", "V", "M", "b", "="],
			"codec_b":["T", "f", "W", "i", "n", "1", "G", "B", "Y", "I", "a", "J", "v", "X", "Z", "k", "0", "4", "u", "m", "Q", "2", "3", "z", "N", "j"]
			}
			
AOS_KEY2 = {
 	"codec_a":["a","H","R","c","D","v","u","W","1","l","b","5","s","w","G","9","Z","M","X","T","I","N","p","=","U","6"],
 	"codec_b":["2","i","o","3","g","L","B","x","z","4","0","m","8","V","d","J","k","t","f","Q","n","y","7","r","Y","e"]
 }
			

def decrypt_pl_url(key,secret_text):
		
	lg27 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="
	result_string=""
	wrk_arr1=list(range(4))
	wrk_arr2=list(range(3))
	
	
	for i in xrange(len(key["codec_b"])):
		secret_text = secret_text.replace(key["codec_b"][i], "___")
		secret_text = secret_text.replace(key["codec_a"][i], key["codec_b"][i])
		secret_text = secret_text.replace("___", key["codec_a"][i])
	
	
	for x in xrange(0,len(secret_text),4):
		
		for y in xrange(4):
			if ((x + y) < (len(secret_text))):
				wrk_arr1[y] = lg27.find(secret_text[x + y])
	
	
		wrk_arr2[0] = ((wrk_arr1[0] << 2) + ((wrk_arr1[1] & 48) >> 4))
		wrk_arr2[1] = (((wrk_arr1[1] & 15) << 4) + ((wrk_arr1[2] & 60) >> 2))
		wrk_arr2[2] = (((wrk_arr1[2] & 3) << 6) + wrk_arr1[3])
		
		
		for z in xrange(len(wrk_arr2)):
			if (wrk_arr1[(z + 1)] == 64 or wrk_arr2[(z)] >139):
				return result_string
			else:
				result_string+=chr(wrk_arr2[z])
	
	return result_string
	
	
def FetchSeason(title):
	m=re.search(u'\[ТВ-([0-9]).*\]',title)
	#print title
	if m!=None:
		return int(m.group(1))
	else:
		return 1


def UpdateBK():
	#---------Обновление плэйлистов---------------
	#Определяет начало и конец зашифрованного урла плэйлиста
	pl_eurl_start="var playlist = \""
	pl_eurl_end="\";"
	
	
	#Получаем список закладок
	#bk=downloader.JSONDocGet('http://movpaper.appspot.com/get',{"s":SERVICE_NAME}).data
	query = Show.all()
	query.filter('service =',SERVICE_NAME)
	
	
	for b in query.fetch(1000):
		
		show_key_name=b.key().name()
		show_key=b.key()
		
		#print b["title"]
		bk_path=urlparse(b.url).path
		#print b["href"]
		

		#Получаем интересующую страницу
		aos_page=downloader.HTMLDocGet(b.url)
		
		#Если не удалось получить страницу, перейти к слеующей
		if aos_page.data==None:
			continue
		
		
		vi_title="".join(aos_page.data.xpath('//div[@id="dle-content"]/div[@class="new_"]/div[@class="head_"]/a/descendant::text()'))
		epl="".join(aos_page.data.xpath('//div[@id="dle-content"]/script/descendant::text()'))
		
		try:
			poster="".join(aos_page.data.xpath('//div[@id="dle-content"]//div[@class="img_"]//img')[0].get('src'))
		except (IndexError):
			poster=None
			
		#Приводим название в человеческий вид
		titles=vi_title.split(" / ")

		showtitle=titles[1]
		showtitle=re.sub("\[.*\]","",showtitle)
		showtitle=re.sub("\(.*\)","",showtitle)
		showtitle=showtitle.replace(":","")
		showtitle=showtitle.replace(";","")
		showtitle=showtitle.replace(",","")
		showtitle=showtitle.replace(".","")
		showtitle=showtitle.replace("_"," ")
		showtitle=re.sub(" +"," ",showtitle)
		showtitle=showtitle.strip()
		
		showdata={'title':showtitle,'season':str(FetchSeason(titles[0])),'poster_url':poster}
		
		#print poster
		
		pl_eurl_start_index=epl.find(pl_eurl_start)
		if pl_eurl_start_index>0:
			pl_eurl=epl[pl_eurl_start_index+len(pl_eurl_start):epl.find(pl_eurl_end)]
			#print pl_eurl
			if pl_eurl.find("http:")>-1:
				pl_url=pl_eurl
			else:
				pl_url=decrypt_pl_url(AOS_KEY1,pl_eurl)
				if len(pl_url)==0:
					pl_url=decrypt_pl_url(AOS_KEY2,pl_eurl)
			
			if len(pl_url)==0:
				#print "Can't decode playlist link"
				continue
			
				
			pl_data=downloader.DocGet(pl_url).data
			
			if pl_data==None:
				continue
			
			#Очистка плэйлиста от ненужных символов
			pl_data=pl_data.replace("\r\n","")
			pl_data=pl_data.replace(chr(255),"")
			pl_data=pl_data.replace(chr(254),"")
			pl_data=pl_data.replace(chr(0),"")		
			
			#Загрузка плэйлиста в словарь
			pl=json.loads(pl_data)
			
			showepisodes={}
			episode_list=[]
			for pl_ent in pl["playlist"]:
				
				sq_num=pl["playlist"].index(pl_ent)+1 #Порядок записи в плэйлисте (в данном случае это номер эпизода)				
				showepisodes[str(sq_num)]=pl_ent["file"] #Записывается url эпизода
				episode_list.append(str(sq_num))
			
			showdata['episodes']=showepisodes
			showdata['episode_list']=episode_list
			showdata_json=json.dumps(showdata)
			
			hash=hashlib.md5()
			hash.update(showdata_json)
			showdata_checksum=hash.hexdigest()
			
			if b.checksum!=showdata_checksum:
				b.checksum=showdata_checksum
				b.data=showdata_json
				b.episode_count=len(episode_list)
				b.put()
