#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webapp2
import Model
import json
import logging
from AOSShowFetcher import AOSShowFetcher

userName="aluzar"
Service=Model.Service([AOSShowFetcher])

class AddShow(webapp2.RequestHandler):
    def get(self):
        url=self.request.get('u')
        url = url.split("#",1)[0]
        print url
        showKey=Service.registerShow(url)

        userSubscription=Model.Subscription(userName)
        userSubscription.subscribeByShowKey(showKey)

    post = get


class UpdateShowsJob(webapp2.RequestHandler):
    def get(self):
        Service.updateAllShows()


class UserNewEpisodes(webapp2.RequestHandler):
    def get(self):
        userSubscription=Model.Subscription(userName)
        response=json.dumps({'response':userSubscription.newEpisodes})
        self.response.write(response)


class MarkEpisodeAsDownloaded(webapp2.RequestHandler):
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


class ShowListHandler(webapp2.RequestHandler):
    def get(self):
        def remove_extra_data(show):
            del show['lastChanged']
            return show

        userSubscription = Model.Subscription(userName)
        show_list_data = userSubscription.subscribedShowsList
        show_list_data = sorted(show_list_data, key=lambda k:k['lastChanged'], reverse=True)
        show_list_data = map(remove_extra_data,show_list_data)
        show_list = {"Shows":show_list_data}

        self.response.headers['Content-Type'] = 'text/json'
        self.response.write(json.dumps(show_list))


class ShowHandler(webapp2.RequestHandler):
    def get(self, show_id):
        userSubscription = Model.Subscription(userName)
        show_data = userSubscription.show_data(show_id)
        show_episodes = show_data['episodes']
        self.response.write(show_data)


class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.redirect('/shows')

