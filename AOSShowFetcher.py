#!/usr/bin/env python
# -*- coding: utf-8 -*-

import downloader,re,json, logging, time
from Model import *

class AOSShowFetcher(ShowFetcher):
    showService=["animeonline.su"]

    @property
    def showTitle(self):
        if self._showTitle is not None:
            return self._showTitle

        #=================Add your code here====================
        showTitle="".join(self.showPage.data.xpath('//span[@class="label_eng"]/descendant::text()'))
        showTitle=re.sub("\[.*\]","",showTitle)
        showTitle=re.sub("\(.*\)","",showTitle)
        #=======================================================
        result=self.normalizeTitle(showTitle)
        self._showTitle=result
        return result

    @property
    def showPoster(self):
        if self._showPoster is not None:
            return self._showPoster

        result=""
        #=================Add your code here====================
        try:
            result="".join(["http://animeonline.su/",self.showPage.data.xpath('//div[@class="poster_container"]/a/img')[0].get('src')])
            self._showPoster=result
        except IndexError:
            pass

        #=======================================================
        return result

    @property
    def showSeason(self):
        result="1"
        #=================Add your code here====================

        showRawTitle="".join(self.showPage.data.xpath('//span[@class="label_rus"]/descendant::text()'))
        m=re.search(u'\[ТВ-([0-9]).*\]',showRawTitle)
        #print title
        if m is not None:
            result=m.group(1)

        #=======================================================
        return result

    @property
    def showEpisodes(self):
        if self._showEpisodes is not None:
            return self._showEpisodes

        result=EpisodeList()
        #=================Add your code here====================

        playlistRequestURL = None
        player_data = "".join(self.showPage.data.xpath('//div[@id="playerApp"]/@data-ng-init'))
        player_data_elements = player_data.split(';')

        for element in player_data_elements:
            element_data = element.split('=')
            if element_data[0]=='anime_id':
                playlistRequestURL = 'http://animeonline.su/zend/anime/one/data/?anime_id='+element_data[1]

        if playlistRequestURL is None:
            logging.error('Can\'t get show id: %s',self._showURL)
            return  result

        try:
            playlistData=downloader.DocPost(playlistRequestURL).data
        except ValueError:
            logging.error(self._showTitle +":bad playlist URL " + playlistRequestURL)
            return result


        if playlistData is None:
            return result

        #Загрузка плэйлиста в словарь
        try:
            playlist=json.loads(playlistData)
        except ValueError:
            logging.error(self._showTitle +":playlist data not in JSON format " + playlistData + " for URL " + playlistRequestURL)
            return result

        for episode in playlist["episodes"]:
            result.append(episodeNumber=playlist["episodes"].index(episode)+1,episodeURL=episode["file"])

        #=======================================================
        self._showEpisodes=result
        return result