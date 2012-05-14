#!/usr/bin/env python
# -*- coding: utf-8 -*-


from Model import *
import json,re

class SORGShowFetcher(ShowFetcher):
    showService=["serialsonline.org"]

    @property
    def showTitle(self):
        if self._showTitle is not None:
            return self._showTitle
        #=================Add your code here====================

        showRawTitle="".join(self.showPage.data.xpath('//h1[@class="show-title"]/span[@class="en"]/descendant::text()')).replace("\n","").replace("\t","")
        showTitle=showRawTitle.strip()

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

        result="".join(self.showPage.data.xpath('//ul[@class="seasons-list"]/li[@class="active"]/a/img/@src'))

        #=======================================================
        return result

    @property
    def showSeason(self):
        result="1"
        #=================Add your code here====================

        showRawSeasone="".join(self.showPage.data.xpath('//h1[@class="show-title"]/span[@class="ru"]/descendant::text()')).replace("\n","").replace("\t","")
        m=re.search(u'.*([0-9]+).*',showRawSeasone)
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

        playListRaw="".join(self.showPage.data.xpath('//div[@class="content"]/script/descendant::text()')).replace('\\/','/')
        playlistDataStart=playListRaw.find('p.setPlaylist( ')+15
        playlistData=playListRaw[playlistDataStart:playListRaw.find(']',playlistDataStart)+1]

        playlist=json.loads(playlistData)

        for episode in playlist:
            result.append(playlist.index(episode)+1,episode[u"episodeId"])

        #=======================================================
        self._showEpisodes=result
        return result
