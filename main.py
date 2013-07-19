#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
from Controller import *
application = webapp2.WSGIApplication([ webapp2.Route(r'/', handler=MainHandler, name='home'),
										webapp2.Route(r'/shows', handler=ShowListHandler, name='show-list'),
										webapp2.Route(r'/shows/<show_id:.+>', handler=ShowHandler, name='show'),
										webapp2.Route(r'/addbookmark', handler=AddShow, name = 'add-show'),
										webapp2.Route(r'/updateshows', handler=UpdateShowsJob, name='update-shows'),
										webapp2.Route(r'/getnewepisodes', handler=UserNewEpisodes, name='new-episodes'),
                                        webapp2.Route(r'/setdownloaded', handler=MarkEpisodeAsDownloaded, name='mark-downloaded')],
                                     debug=True)