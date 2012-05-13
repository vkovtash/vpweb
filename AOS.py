#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dbmodel import *
import downloader,re,json,hashlib
import logging

class EpisodeList(dict):
    def __init__(self,*args):
        dict.__init__(self, args)

    def append(self,episodeNumber,episodeURL):
        if episodeNumber is not None:
            dict.__setitem__(self, str(episodeNumber), episodeURL)

    def remove(self,episodeNumber):
        if episodeNumber is not None:
            try:
                dict.pop(self, str(episodeNumber))
            except KeyError:
                pass

    @property
    def episodeNumbers(self):
        return dict.keys(self)


class ShowGetter():
    def __init__(self,showURL):
        self._showURL=showURL
        self._showPage=None
        self._showEpisodes=None
        self._showTitle=None
        self._showPoster=None

    def __getShowPage(self):
        return downloader.HTMLDocGet(self._showURL)

    def __normalizeTitle(self,title=""):

        showTitle=title.replace(":","")
        showTitle=showTitle.replace(";","")
        showTitle=showTitle.replace(",","")
        showTitle=showTitle.replace(".","")
        showTitle=showTitle.replace("_"," ")
        showTitle=re.sub(" +"," ",showTitle)
        showTitle=showTitle.strip()

        return showTitle

    @property
    def showPage(self):
        if self._showPage is None:
            self._showPage=self.__getShowPage()
            if self._showPage.data is None:
                self._showPage=None
        return self._showPage

    @property
    def showTitle(self):
        if self._showTitle is not None:
            return self._showTitle

        showRawTitle="".join(self.showPage.data.xpath('//div[@id="dle-content"]/div[@class="new_"]/div[@class="head_"]/a/descendant::text()'))
        #Приводим название в человеческий вид
        titles=showRawTitle.split(" / ")

        showTitle=titles[1]
        showTitle=re.sub("\[.*\]","",showTitle)
        showTitle=re.sub("\(.*\)","",showTitle)

        result=self.__normalizeTitle(showTitle)

        self._showTitle=result
        return result

    @property
    def showPoster(self):
        if self._showPoster is not None:
            return self._showPoster

        try:
            result="".join(["http://animeonline.su/",self.showPage.data.xpath('//div[@id="dle-content"]//div[@class="img_"]//img')[0].get('src')])
        except IndexError:
            result=None

        self._showPoster=result
        return result

    @property
    def showSeason(self):
        showRawTitle="".join(self.showPage.data.xpath('//div[@id="dle-content"]/div[@class="new_"]/div[@class="head_"]/a/descendant::text()'))
        m=re.search(u'\[ТВ-([0-9]).*\]',showRawTitle)
        #print title
        if m is not None:
            return m.group(1)
        else:
            return "1"

    @property
    def showEpisodes(self):
        """
        Return dictionary in format
        {episodeNumber:episodeURL,...}"

        example: {"1":"http://1.html","2":"http://2.html","3":"http://1.html",...}"
        """
        if self._showEpisodes is not None:
            return self._showEpisodes

        result=EpisodeList()


        aosKey1 = {
            "codec_a":["5", "d", "9", "U", "D", "y", "H", "7", "t", "6", "l", "x", "c", "w", "R", "p", "s", "g", "e", "L", "8", "o", "V", "M", "b", "="],
            "codec_b":["T", "f", "W", "i", "n", "1", "G", "B", "Y", "I", "a", "J", "v", "X", "Z", "k", "0", "4", "u", "m", "Q", "2", "3", "z", "N", "j"]
        }

        aosKey2 = {
        "codec_a":["a","H","R","c","D","v","u","W","1","l","b","5","s","w","G","9","Z","M","X","T","I","N","p","=","U","6"],
        "codec_b":["2","i","o","3","g","L","B","x","z","4","0","m","8","V","d","J","k","t","f","Q","n","y","7","r","Y","e"]
        }

        #Определяет начало и конец зашифрованного урла плэйлиста
        playlistURLStart='var playlist = "'
        playlistURLEnd='";'

        playlistRawURL="".join(self.showPage.data.xpath('//div[@id="dle-content"]/script/descendant::text()'))

        playlistURLStartIndex=playlistRawURL.find(playlistURLStart)
        if playlistURLStartIndex>0:
            playlistURL=playlistRawURL[playlistURLStartIndex+len(playlistURLStart):playlistRawURL.find(playlistURLEnd)]

            if playlistURL.find("http:")>-1:
                playlistRequestURL=playlistURL      #Unencrypted playlist
            else:
                #Encrypted playlist

                #Try first key
                playlistRequestURL=self.__decryptPlaylistURL(aosKey1,playlistURL)
                if not len(playlistRequestURL):
                    #Try second key
                    playlistRequestURL=self.__decryptPlaylistURL(aosKey2,playlistURL)

            #Return an empty episodes set when playlistURL not found
            if not len(playlistRequestURL):
                return result


            playlistData=downloader.DocGet(playlistRequestURL).data

            if playlistData is None:
                return result

            #Очистка плэйлиста от ненужных символов
            playlistData=playlistData.replace("\r\n","")
            playlistData=playlistData.replace(chr(255),"")
            playlistData=playlistData.replace(chr(254),"")
            playlistData=playlistData.replace(chr(0),"")

            #Загрузка плэйлиста в словарь
            playlist=json.loads(playlistData)

            for episode in playlist["playlist"]:
                result.append(episodeNumber=playlist["playlist"].index(episode)+1,episodeURL=episode["file"])

            self._showEpisodes=result

        return result

    def __decryptPlaylistURL(self,key,secretText):

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

class Service():
    def __init__(self):
        self.serviceName="animeonline.su"

    def updateShows(self):
        """
        asd
        """
        #TODO: сделать возможность регитсрации новых обработчиков и в цикле проходить по всем обработчикам

        #Получаем список закладок
        query = db.Query(ShowDB,keys_only=True)
        query.filter('service =',self.serviceName)

        for show in query.fetch(1000):
            dbShow=Show(show)

            #Получаем интересующую страницу
            showPage=ShowGetter(dbShow.showURL)

            if showPage.showPage is not None:
                showData={'title':showPage.showTitle,'season':showPage.showSeason,'posterURL':showPage.showPoster,'episodes':showPage.showEpisodes}
                showDataJSON=json.dumps(showData)
                dbShow.setShowData(showDataJSON)



if __name__ == "__main__":
    testPage=ShowGetter("http://animeonline.su/anime-sub/tv-sub/7084-kartochnye-boi-avangarda-tv-2-cardfight-vanguard-asia-circuit-hen.html")
    showData={'title':testPage.showTitle,'season':testPage.showSeason,'posterURL':testPage.showPoster,'episodes':testPage.showEpisodes}

    print testPage.showTitle
    print testPage.showSeason
    print testPage.showPoster
    print testPage.showEpisodes
    print testPage.showEpisodes.episodeNumbers
    print json.dumps(showData)
