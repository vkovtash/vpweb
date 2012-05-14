#!/usr/bin/env python
# -*- coding: utf-8 -*-


from google.appengine.ext import webapp

import Controller
from AOSShowFetcher import AOSShowFetcher
from SORGShowFetcher import SORGShowFetcher
import json,logging

userName="aluzar"
Service=Controller.Service()
Service.showFetchers=[AOSShowFetcher,
                      SORGShowFetcher]

class AddShow(webapp.RequestHandler):
    def get(self):

        url=self.request.get('u')

        showKey=Service.registerShow(url)

        userSubscription=Controller.Subscription(userName)
        userSubscription.subscribeByShowKey(showKey)

    post = get

class UpdateShowsJob(webapp.RequestHandler):
    def get(self):
        Service.updateAllShows()

class UserNewEpisodes(webapp.RequestHandler):
    def get(self):
        userSubscription=Controller.Subscription(userName)
        responseShows=json.dumps(userSubscription.newEpisodes)
        response={'response':responseShows}
        self.response.out.write(response)

class MainHandler(webapp.RequestHandler):
    def get(self):
        pass

