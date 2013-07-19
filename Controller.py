#!/usr/bin/env python
# -*- coding: utf-8 -*-

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

import Model, json, os.path , logging
from AOSShowFetcher import AOSShowFetcher

userName="aluzar"
Service=Model.Service([AOSShowFetcher])

class AddShow(webapp.RequestHandler):
    def get(self):
        url=self.request.get('u')
        url = url.split("#",1)[0]
        print url
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
        isDownloaded = self.request.get('is_downloaded')

        userSubscription=Model.Subscription(userName)
        logging.error(isDownloaded)

        if isDownloaded=='0':
            userSubscription.markEpisodeAsNotDownloaded(showKey,episodeNumber)
        else:
            userSubscription.markEpisodeAsDownloaded(showKey,episodeNumber)

class UserSubscriprions(webapp.RequestHandler):
    def get(self):
        userSubscription=Model.Subscription(userName)

        showsData=userSubscription.subscribedShowsData

        #showsData=sorted( showsData, key=lambda k:"".join([k["title"],k["season"].zfill(2)]) )
        showsData=sorted( showsData, key=lambda k:k["lastChanged"], reverse=True )
        Tmain_values={
            "Shows":showsData
        }

        path = os.path.join(os.path.dirname(__file__), 'templates/UserSubscriptionData.tpl')
        self.response.out.write(template.render(path, Tmain_values))

class MainHandler(webapp.RequestHandler):
    def get(self):
        pass

