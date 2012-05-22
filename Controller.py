#!/usr/bin/env python
# -*- coding: utf-8 -*-

from google.appengine.ext import webapp

import Model, json
from AOSShowFetcher import AOSShowFetcher
from SORGShowFetcher import SORGShowFetcher

userName="aluzar"
Service=Model.Service([AOSShowFetcher,
                       SORGShowFetcher])

class AddShow(webapp.RequestHandler):
    def get(self):

        url=self.request.get('u')
        showKey=Service.registerShow(url)

        userSubscription=Model.Subscription(userName)
        userSubscription.subscribeByShowKey(showKey)

    post = get

class UpdateShowsJob(webapp.RequestHandler):
    def get(self):
        Service.updateAllShows()

class UserNewEpisodes(webapp.RequestHandler):
    def get(self):
        userSubscription=Model.Subscription(userName)
        response=json.dumps({'response':userSubscription.newEpisodes})
        self.response.out.write(response)

class MarkEpisodeAsDownloaded(webapp.RequestHandler):
    def get(self):
        episodeNumber=self.request.get('ep_num')
        showKey=self.request.get('show_key')
        userSubscription=Model.Subscription(userName)
        userSubscription.markEpisodeAsDownloaded(showKey,episodeNumber)

class MainHandler(webapp.RequestHandler):
    def get(self):
        pass

