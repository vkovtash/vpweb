#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webapp2
import model
import json
import logging
from aos_showfetcher import AOSShowFetcher

USER_ID = "aluzar"
Service = model.Service([AOSShowFetcher])

class AddShow(webapp2.RequestHandler):
    def get(self):
        url = self.request.get('u')
        url = url.split("#",1)[0]
        show_key = Service.registerShow(url)

        userSubscription = model.Subscription(USER_ID)
        userSubscription.subscribeByShowKey(show_key)

    post = get


class UpdateShowsJob(webapp2.RequestHandler):
    def get(self):
        Service.updateAllShows()


class UserNewEpisodes(webapp2.RequestHandler):
    def get(self):
        user_subscription = model.Subscription(USER_ID)
        response = json.dumps({'response':user_subscription.new_episodes})
        self.response.write(response)


class MarkEpisodeAsDownloaded(webapp2.RequestHandler):
    def get(self):
        episode_number = self.request.get('ep_num')
        showKey = self.request.get('show_key')
        is_downloaded = self.request.get('is_downloaded')

        user_subscription = model.Subscription(USER_ID)
        logging.error(is_downloaded)

        if is_downloaded == '0':
            user_subscription.markEpisodeAsNotDownloaded(showKey,episode_number)
        else:
            user_subscription.markEpisodeAsDownloaded(showKey,episode_number)


class ShowListHandler(webapp2.RequestHandler):
    def get(self):
        def remove_extra_data(show):
            del show['lastChanged']
            return show

        user_subscription = model.Subscription(USER_ID)
        show_list_data = user_subscription.subscription_list
        show_list_data = sorted(show_list_data, key=lambda k:k['lastChanged'], reverse=True)
        show_list_data = map(remove_extra_data,show_list_data)
        show_list = {"Shows":show_list_data}

        self.response.headers['Content-Type'] = 'text/json'
        self.response.write(json.dumps(show_list))


class ShowHandler(webapp2.RequestHandler):
    def get(self, show_id):
        user_subscription = model.Subscription(USER_ID)
        subscription_data = user_subscription.subscription_data(show_id)
        self.response.write(json.dumps(subscription_data))

    def post(self, show_id):
        request_data = json.loads(self.request.body)
        episode_numbers = []

        for episode in request_data['episodes']:
            if episode['isDownloaded']:
                episode_numbers.append(episode['id'])

        user_subscription = model.Subscription(USER_ID)
        user_subscription.set_subscription_downloaded_episodes(show_id,episode_numbers)

        self.get(show_id=show_id)


class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.redirect('/shows')

