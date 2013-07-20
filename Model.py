#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dbmodel import *
import downloader
import re
import hashlib
import logging
from urlparse import urlparse
from httplib import HTTPException

def genHash(value):
    hash=hashlib.sha1()
    hash.update(value)
    return hash.hexdigest()

class EpisodeList(dict):
    def __init__(self,*args):
        dict.__init__(self, args)

    def append(self,episodeNumber,episodeURL):
        if episodeNumber is not None:
            dict.__setitem__(self, int(episodeNumber), episodeURL)

    def remove(self,episodeNumber):
        if episodeNumber is not None:
            try:
                dict.pop(self, int(episodeNumber))
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
        self._showURL = showURL
        self._showPage = None
        self._showEpisodes = None
        self._showTitle = None
        self._showPoster = None
        self._showSeason = None

        if not self.__checkService():
            raise Exception('URL is not in showServices list')

    def __checkService(self):
        serviceFromUrl=urlparse(self._showURL).netloc
        validServices=set(self.showService)
        return serviceFromUrl in validServices

    @property
    def showPage(self):
        if self._showPage is None:
            self._showPage = self.get_show_page(self._showURL)
        return self._showPage

    @property
    def showURL(self):
        return self._showURL

    @property
    def showTitle(self):
        """
        Возвращает нормализованое название
        """
        if self._showTitle is None:
            self._showTitle = self.extract_show_title()
            self._showTitle = self.normalize_title(self._showTitle)
        return self._showTitle

    @property
    def showPoster(self):
        """
        Возвращает абсолютную ссылку на постер
        """
        if self._showPoster is None:
            self._showPoster = self.extract_show_poster_url()
        return self._showPoster

    @property
    def showSeason(self):
        """
        Возвращает номер сезона
        """
        if self._showSeason is None:
            self._showSeason = self.extract_show_season()
        return self._showSeason

    @property
    def showEpisodes(self):
        """
        Возвращает экземпляр класса EpisodeList()
        """
        if self._showEpisodes is None:
            self._showEpisodes = self.extract_show_episodes()
        return self._showEpisodes

    def normalize_title(self,title):
        show_title = title
        show_title = show_title.replace(":","")
        show_title = show_title.replace(";","")
        show_title = show_title.replace(",","")
        show_title = show_title.replace(".","")
        show_title = show_title.replace("_"," ")
        show_title = re.sub(" +"," ",show_title)
        show_title = re.sub("/"," ",show_title)
        show_title = show_title.strip()

        return show_title

    def extract_show_title(self):
        return ""

    def extract_show_poster_url(self):
        return ""

    def extract_show_season(self):
        return "1"

    def extract_show_episodes(self):
        return EpisodeList()

    def get_show_page(self,url):
        show_page = None
        try:
            show_page = downloader.HTMLDocGet(url)
        except HTTPException:
            logging.error("HTTP exception while getting URL %s"%url)
            return None

        if show_page.data is None:
            return None
        return show_page


class Service():
    def __init__(self,showFetchers):
        self._showQueries = [ ]

        for showFetcher in showFetchers:
            self._showQueries.append([  ShowNDB.query(ShowNDB.service.IN(showFetcher.showService)),
                                        showFetcher])

    def updateAllShows(self):
        for service in self._showQueries:
            showsToPut=[]

            for ndbShow in ndb.get_multi(service[0].fetch(keys_only=True)):
                showPage=service[1](ndbShow.url)

                if showPage.showPage is not None:
                    showData={'title':showPage.showTitle,'season':showPage.showSeason,'posterURL':showPage.showPoster,'episodes':showPage.showEpisodes}
                    dataHash=genHash(str(showData))
                    if ndbShow.hash != dataHash:
                        logging.info("Data changed for show %s with episodes: %s, hash: %s",showPage.showTitle, len(showData['episodes']), dataHash)
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
    def subscription_list(self):
        result=[]

        for subscription in self.subscribedShows:
            show = subscription.key.parent().get()
            if show is not None:
                show_data = show.data
                if show_data is not None:
                    showResult={'showKey':subscription.key.urlsafe(),
                                'service':show.service,
                                'lastChanged':show.lastChanged,
                                'title':show_data["title"],
                                'season':show_data["season"],
                                'posterURL':show_data["posterURL"],
                                'downloadedEpisodes':len(subscription.downloaded),
                                'totalEpisodes':len(show_data['episodes'])
                                }
                    result.append(showResult)
            else:
                subscription.key.delete() #Удаляем подписку пользователя, если она ссылается на удаленную запись в Shows

        return result

    def subscription_data(self,show_key):
        subscription_key = ndb.Key(urlsafe=show_key)
        subscription = subscription_key.get()
        show = subscription.key.parent().get()
        show_data = show.data
        show_data["showId"] = show_key;
        if show_data is not None:
            downloaded_episodes=set(subscription.downloaded)
            episode_list = []
            for episode_key in show_data['episodes'].keys():
                episode_id = int(episode_key)
                episode_url = show_data['episodes'][episode_key]
                episode_data = {'url':episode_url,'id':episode_id}

                if episode_id in downloaded_episodes:
                    episode_data['isDownloaded'] = True
                else:
                    episode_data['isDownloaded'] = False

                episode_list.append(episode_data)
            show_data['episodes'] = episode_list

        return show_data

    def set_subscription_downloaded_episodes(self,show_key,episode_numbers=[]):
        subscription_key = ndb.Key(urlsafe=show_key)
        subscription = subscription_key.get()
        subscription_set = set(episode_numbers)
        subscription.downloaded = list(subscription_set)
        subscription.put()

    @property
    def new_episodes(self):
        result = {'services':{}}

        for subscription in self.subscribedShows:
            show = subscription.key.parent().get()

            if show is not None:
                if show.data is not None:
                    showResult={'showKey':subscription.key.urlsafe(),
                                'showKeyUnsafe':str(subscription.key),
                                'title':show.data["title"],
                                'season':show.data["season"],
                                'posterURL':show.data["posterURL"],
                                'episodes':[]}

                    if show.data is not None:
                        showEpisodes=set(map(int,show.data['episodes'].keys()))
                    else:
                        showEpisodes=set([])

                    downloadedEpisodes=set(subscription.downloaded)

                    for newEpisode in (showEpisodes-downloadedEpisodes):
                        showResult["episodes"].append({'number':newEpisode,
                                                        'url':show.data['episodes'][str(newEpisode)]})

                    try:
                        result['services'][show.service]
                    except KeyError:
                        result['services'][show.service]=[]
                    if len(showResult["episodes"]):
                        result['services'][show.service].append(showResult)
            else:
                subscription.key.delete() #Удаляем подписку пользователя, если она ссылается на удаленную запись в Shows

        return result

    def markEpisodeAsDownloaded(self,showKey,episodeNumber):
        subscriptionKey=ndb.Key(urlsafe=showKey)
        subscription=subscriptionKey.get()
        subscriptionSet=set(subscription.downloaded)
        subscriptionSet.add(int(episodeNumber))
        subscription.downloaded=list(subscriptionSet)
        subscription.put()

    def markEpisodeAsNotDownloaded(self,showKey,episodeNumber):
        subscriptionKey=ndb.Key(urlsafe=showKey)
        subscription=subscriptionKey.get()
        subscriptionSet=set(subscription.downloaded)
        try:
            subscriptionSet.remove(int(episodeNumber))
            subscription.downloaded=list(subscriptionSet)
            subscription.put()
        except KeyError:
            pass

if __name__ == "__main__":
    pass
