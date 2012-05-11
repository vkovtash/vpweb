#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path	
			
BK_UPDATE_TIMEOUT=10
VIDEO_DIR=os.path.expanduser("/hd0/ds0/iTunes Media/Automatically Add to iTunes.localized") #Путь к хранилищу фильмов
SETTINGS_DIR=os.path.expanduser("/hd0/ds0/Library/vipaper") #Путь к локальному хранилищу настроек
#VIDEO_DIR=os.path.expanduser("/Users/kovtash/vipaper/video") #Путь к хранилищу фильмов
#SETTINGS_DIR=os.path.expanduser("/Users/kovtash/vipaper") #Путь к локальному хранилищу настроек
SQLLITE_BD = 'vipaper' #Имя файла БД
REFRESH_INTERVAL=15*60
