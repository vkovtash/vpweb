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
        showRawTitle="".join(self.showPage.data.xpath('//div[@id="dle-content"]/div[@class="new_"]/div[@class="head_"]/a/descendant::text()'))
        #Приводим название в человеческий вид
        titles=showRawTitle.split(" / ")
		
        try:
            showTitle=titles[1]
        except IndexError:
            showTitle="Unknown"
            logging.error("Can't parse show title " + showRawTitle)
        	
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
            result="".join(["http://animeonline.su/",self.showPage.data.xpath('//div[@id="dle-content"]//div[@class="img_"]//img')[0].get('src')])
            self._showPoster=result
        except IndexError:
            pass

        #=======================================================
        return result

    @property
    def showSeason(self):
        result="1"
        #=================Add your code here====================

        showRawTitle="".join(self.showPage.data.xpath('//div[@id="dle-content"]/div[@class="new_"]/div[@class="head_"]/a/descendant::text()'))
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


        aosKey1 = {
            "codec_a":["5", "d", "9", "U", "D", "y", "H", "7", "t", "6", "l", "x", "c", "w", "R", "p", "s", "g", "e", "L", "8", "o", "V", "M", "b", "="],
            "codec_b":["T", "f", "W", "i", "n", "1", "G", "B", "Y", "I", "a", "J", "v", "X", "Z", "k", "0", "4", "u", "m", "Q", "2", "3", "z", "N", "j"]
        }

        aosKey2 = {
            "codec_a":["a","H","R","c","D","v","u","W","1","l","b","5","s","w","G","9","Z","M","X","T","I","N","p","=","U","6"],
            "codec_b":["2","i","o","3","g","L","B","x","z","4","0","m","8","V","d","J","k","t","f","Q","n","y","7","r","Y","e"]
        }


        playerURL = "".join(self.showPage.data.xpath('//a[@id="full_anime_watch"]/@onclick'))
        playerURLStartIndex = playerURL.find("'")
        if  playerURLStartIndex > 0:
            playerURL = playerURL[playerURLStartIndex+1:playerURL.find("'",playerURLStartIndex+1)]
            playerURL = "".join(['http://',self.showService[0],playerURL])

            try:
                playerPage=downloader.HTMLDocGet(playerURL)
            except ValueError:
                logging.error(self._showTitle +":bad player page URL " + playerURL)
                return result
        else:
            logging.error('Can not parse player URL: %s'%playerURL)
            return result

        playlistRawURL="".join(playerPage.data.xpath('//object[@id="aosplayer"]/param[@name="flashvars"]/@value'))
        flashVars = playlistRawURL.split('&')

        playlistURL = None

        for var in flashVars:
            if var.find('pl=') > -1:
                playlistURL = var.replace('pl=','')

        if  playlistURL is None:
            logging.error(self._showTitle +"No playlist found in the player flashvars")
            return result

        if playlistURL.find("http:")>-1:
            playlistRequestURL=playlistURL      #Unencrypted playlist
        else:
            #Encrypted playlist

            #Try first key
            playlistRequestURL=self.decryptPlaylistURL(aosKey1,playlistURL)
            if not len(playlistRequestURL):
                #Try second key
                playlistRequestURL=self.decryptPlaylistURL(aosKey2,playlistURL)

        #Return an empty episodes set when playlistURL not found
        if not len(playlistRequestURL):
            return result

        playlistRequestURL = ''.join([playlistRequestURL,'?ts=',str(int(time.time()/3600))])
        
        try:
            playlistData=downloader.DocGet(playlistRequestURL).data
        except ValueError:
            logging.error(self._showTitle +":bad playlist URL " + playlistRequestURL)
            return result


        if playlistData is None:
            return result
        
        #Расшифровка плейлиста, если он зашифрован 
        if playlistData[0:11] != '{"playlist"':
            decryptedPlaylistData = self.decryptPlaylistURL(aosKey1,playlistData)
            
            if decryptedPlaylistData[0:11] != '{"playlist"':
                decryptedPlaylistData = self.decryptPlaylistURL(aosKey2,playlistData)
                
            playlistData = decryptedPlaylistData

        #Очистка плэйлиста от ненужных символов
        playlistData=playlistData.replace("\r\n","")
        playlistData=playlistData.replace(chr(255),"")
        playlistData=playlistData.replace(chr(254),"")
        playlistData=playlistData.replace(chr(0),"")

        #Загрузка плэйлиста в словарь
        try:
            playlist=json.loads(playlistData)
        except ValueError:
            logging.error(self._showTitle +":playlist data not in JSON format " + playlistData + " for URL " + playlistRequestURL)
            return result

        for episode in playlist["playlist"]:
            result.append(episodeNumber=playlist["playlist"].index(episode)+1,episodeURL=episode["file"])

        #=======================================================
        self._showEpisodes=result
        return result

    def decryptPlaylistURL(self,key,secretText):

        lg27 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="
        result=""
        workingArray1=list(range(4))
        workingArray2=list(range(3))


        for i in xrange(len(key["codec_b"])):
            secretText = secretText.replace(key["codec_b"][i], "___")
            secretText = secretText.replace(key["codec_a"][i], key["codec_b"][i])
            secretText = secretText.replace("___", key["codec_a"][i])


        for x in xrange(0,len(secretText),4):

            for y in xrange(4):
                if (x + y) < (len(secretText)):
                    workingArray1[y] = lg27.find(secretText[x + y])


            workingArray2[0] = ((workingArray1[0] << 2) + ((workingArray1[1] & 48) >> 4))
            workingArray2[1] = (((workingArray1[1] & 15) << 4) + ((workingArray1[2] & 60) >> 2))
            workingArray2[2] = (((workingArray1[2] & 3) << 6) + workingArray1[3])


            for z in xrange(len(workingArray2)):
                if workingArray1[(z + 1)] == 64 or workingArray2[z] >139:
                    return result
                else:
                    result+=chr(workingArray2[z])

        return result