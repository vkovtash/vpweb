#!/usr/bin/env python
# -*- coding: utf-8 -*-

import downloader
import re
import json
import logging
from model import ShowFetcher, EpisodeList

class AOSShowFetcher(ShowFetcher):
    showService=["animeonline.su"]

    def extract_show_title(self):
        show_title = "".join(self.showPage.data.xpath('//span[@class="label_eng"]/descendant::text()'))
        show_title = re.sub("\[.*\]","",show_title)
        show_title = re.sub("\(.*\)","",show_title)
        return show_title

    def extract_show_poster_url(self):
        show_poster_url = "" 
        try:
            show_poster_url = "".join(["http://animeonline.su/",self.showPage.data.xpath('//div[@class="poster_container"]/a/img')[0].get('src')])
        except IndexError:
            pass
        return show_poster_url

    def extract_show_season(self):
        result="1"
        showRawTitle="".join(self.showPage.data.xpath('//span[@class="label_rus"]/descendant::text()'))
        m=re.search(u'\[ТВ-([0-9]).*\]',showRawTitle)

        if m is not None:
            result=m.group(1)

        return result

    def extract_show_episodes(self):
        result=EpisodeList()
        playlist_request_url = None
        player_data = "".join(self.showPage.data.xpath('//div[@id="playerApp"]/@data-ng-init'))
        player_data_elements = player_data.split(';')

        for element in player_data_elements:
            element_data = element.split('=')
            if element_data[0] == 'anime_id':
                playlist_request_url = 'http://animeonline.su/zend/anime/one/data/?anime_id='+element_data[1]

        if playlist_request_url is None:
            logging.error('Can\'t get show id: %s',self._showURL)
            return  result

        try:
            playlist_data = downloader.DocPost(playlist_request_url).data
        except ValueError:
            logging.error("%s :bad playlist URL %s",(self._showTitle,playlist_request_url))
            return result


        if playlist_data   is None:
            return result

        #Загрузка плэйлиста в словарь
        try:
            playlist = json.loads(playlist_data ) 
        except ValueError:
            logging.error("%s:playlist data not in JSON format  %s for URL %s"%(self._showTitle,playlist_data,playlist_request_url))
            return result

        logging.error('Episodes %s'%playlist)
        if 'episodes' in playlist:
            for episode in playlist["episodes"]:
                result.append(episodeNumber=playlist["episodes"].index(episode)+1,episodeURL=episode["file"])

        return result