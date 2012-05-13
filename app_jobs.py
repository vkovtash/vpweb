#!/usr/bin/env python
# -*- coding: utf-8 -*-


from google.appengine.ext import webapp

userName="aluzar"


import AOS
from dbmodel import *
import json,logging

class AddShow(webapp.RequestHandler):
    def get(self):

        url=self.request.get('u')

        if genHash(url) is not None:
            showKey=ndb.Key('ShowNDB',genHash(url))
            if showKey.get() is None:
                show = ShowNDB(key=showKey)
                show.url = url
                show.put()

            subscriptionKey=ndb.Key('UsersWatchListNDB',userName,parent=showKey)
            if subscriptionKey.get() is None:
                subscription = UsersWatchListNDB(key=subscriptionKey)
                subscription.user=userName
                subscription.put()

    post = get

class UpdateShowsJob(webapp.RequestHandler):
    def get(self):
        worker=AOS.Service()
        worker.updateShows()

class GetNewEpisodesNDB(webapp.RequestHandler):
    def get(self):

        response={'response':{'shows':[]}}

        for showSubscription in UsersWatchListNDB.query(UsersWatchListNDB.user==userName).fetch(1000):

            showData=showSubscription.key.parent().get()

            if showData.data is not None:
                result={'subscription':showSubscription.key.urlsafe(),
                        'title':showData.data["title"],
                        'season':showData.data["season"],
                        'posterURL':showData.data["posterURL"],
                        'episodes':[]}

                if showData.data is not None:
                    showEpisodes=set(showData.data['episodes'].keys())
                else:
                    showEpisodes=set([])

                downloadedEpisodes=set(showSubscription.downloaded)

                for newEpisode in (showEpisodes-downloadedEpisodes):

                    result["episodes"].append({'number':newEpisode,
                                               'url':showData.data['episodes'][newEpisode]})

                response['response']['shows'].append(result)

        resp=json.dumps(response)
        self.response.out.write(resp)

class MainHandler(webapp.RequestHandler):
    def get(self):
        pass


