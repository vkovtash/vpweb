#!/usr/bin/env python
# -*- coding: utf-8 -*-

from DbModel import *
import downloader,re,hashlib,logging
from urlparse import urlparse


def genHash(value):
    hash=hashlib.md5()
    hash.update(value)
    return hash.hexdigest()

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

class ShowFetcher():
    #Требует оверрайда. Должно быть указаны доменные имена сервиса
    showService=["dummyservice.org",
                 "www.dummyservice.org"]

    def __init__(self,showURL):
        self._showURL=showURL
        self._showPage=None
        self._showEpisodes=None
        self._showTitle=None
        self._showPoster=None

        if not self.__checkService():
            raise Exception('URL is not in showServices list')

    def getShowPage(self):
        """
        Требует оверрайда. В зависимости от типа данных может потребоваться изменить используемый метод
        """
        return downloader.HTMLDocGet(self._showURL)

    def __checkService(self):
        serviceFromUrl=urlparse(self._showURL).netloc
        validServices=set(self.showService)
        return serviceFromUrl in validServices

    def normalizeTitle(self,title=""):

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
            self._showPage=self.getShowPage()
            if self._showPage.data is None:
                self._showPage=None
        return self._showPage

    @property
    def showTitle(self):
        """
        Требует оверрайда. Должно возвращаться нормализованое название
        """
        if self._showTitle is not None:
            return self._showTitle
        result=""
        #=================Add your code here====================


        #=======================================================

        result=self.normalizeTitle(result)
        self._showTitle=result
        return result

    @property
    def showPoster(self):
        """
        Требует оверрайда. Должна возвращаться абсолютная ссылка на постер
        """
        if self._showPoster is not None:
            return self._showPoster

        result=""
        #=================Add your code here====================


        #=======================================================
        return result

    @property
    def showSeason(self):
        """
        Требует оверрайда. Дожен возвращаться номер сезона
        """
        result="1"
        #=================Add your code here====================


        #=======================================================
        return result

    @property
    def showEpisodes(self):
        """
        Требует оверрайда. Должен заполняться EpisodeList()
        """
        if self._showEpisodes is not None:
            return self._showEpisodes

        result=EpisodeList()
        #=================Add your code here====================


        #=======================================================
        self._showEpisodes=result
        return result


class Service():
    def __init__(self,showFetchers):
        self._showQueries = [ ]

        for showFetcher in showFetchers:
            self._showQueries.append([  ShowNDB.query(ShowNDB.service.IN(showFetcher.showService)),
                                        showFetcher])

            #Cached read example: db.get_multi(q.fetch(keys_only=True))

    def updateAllShows(self):
        for service in self._showQueries:
            showsToPut=[]

            for ndbShow in ndb.get_multi(service[0].fetch(keys_only=True)):
                showPage=service[1](ndbShow.url)

                if showPage.showPage is not None:
                    showData={'title':showPage.showTitle,'season':showPage.showSeason,'posterURL':showPage.showPoster,'episodes':showPage.showEpisodes}
                    dataHash=genHash(str(showData))
                    if ndbShow.hash != dataHash:
                        logging.info("Show data was changed foк show: %s",showPage.showTitle)
                        ndbShow.data=showData
                        ndbShow.hash=dataHash
                        showsToPut.append(ndbShow)


            ndb.put_multi(showsToPut)

    def registerShow(self,url):
        showKey = None
        if genHash(url) is not None:
            showKey=ndb.Key('ShowNDB',genHash(url))
            if showKey.get() is None:
                show = ShowNDB(key=showKey)
                show.url = url
                show.service = urlparse(url).netloc
                show.put()

        return showKey

class Subscription():
    def __init__(self,userName):
        self._userName=userName
        self._subscribedShowsQuery=UsersWatchListNDB.query(UsersWatchListNDB.user==self._userName)


    def subscribeByShowKey(self,showKey):
        if showKey is not None:
            subscriptionKey=ndb.Key('UsersWatchListNDB',self._userName,parent=showKey)
            if subscriptionKey.get() is None:
                subscription = UsersWatchListNDB(key=subscriptionKey)
                subscription.user=self._userName
                subscription.put()

    @property
    def subscribedShows(self):
        return ndb.get_multi(self._subscribedShowsQuery.fetch(keys_only=True))

    @property
    def newEpisodes(self):

        result={'shows':[]}

        for show in self.subscribedShows:

            showData=show.key.parent().get()

            if showData.data is not None:
                showResult={'showKey':show.key.urlsafe(),
                            'serviceName':showData.service,
                            'title':showData.data["title"],
                            'season':showData.data["season"],
                            'posterURL':showData.data["posterURL"],
                            'episodes':[]}

                if showData.data is not None:
                    showEpisodes=set(showData.data['episodes'].keys())
                else:
                    showEpisodes=set([])

                downloadedEpisodes=set(show.downloaded)

                for newEpisode in (showEpisodes-downloadedEpisodes):

                    showResult["episodes"].append({'number':newEpisode,
                                                    'url':showData.data['episodes'][newEpisode]})

                result['shows'].append(showResult)

        return result

if __name__ == "__main__":
    pass
