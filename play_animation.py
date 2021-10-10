# -*- coding: utf-8 -*-
"""
Created on Sat Oct  9 13:18:46 2021

@author: liamd
"""
#%% Import packages and set working directory
import pandas as pd
import os
os.chdir('C:\\Users\\liamd\\Documents\\NFL Big Data Bowl\\Data\\')

#%% Import datasets
games = pd.read_csv('games.csv')
pff = pd.read_csv('PFFScoutingData.csv')
players = pd.read_csv('players.csv')
plays = pd.read_csv('plays.csv')
tracking2018 = pd.read_csv('tracking2018.csv')
tracking2019 = pd.read_csv('tracking2019.csv')
tracking2020 = pd.read_csv('tracking2020.csv')

#%% Merge scouting, game, player, and play data onto tracking data
# 2018 season
tracking2018 = tracking2018.merge(pff, on = ['gameId', 'playId'])
tracking2018 = tracking2018.merge(games, on = 'gameId')
tracking2018 = tracking2018.merge(players, on = 'nflId')
tracking2018 = tracking2018.merge(plays, on = ['gameId', 'playId'])

# View missing data
missing = tracking2018.isnull().sum().sort_values(ascending = False)

# 2019 season
tracking2019 = tracking2019.merge(pff, on = ['gameId', 'playId'])
tracking2019 = tracking2019.merge(games, on = 'gameId')
tracking2019 = tracking2019.merge(players, on = 'nflId')
tracking2019 = tracking2019.merge(plays, on = ['gameId', 'playId'])

# View missing data
missing = tracking2019.isnull().sum().sort_values(ascending = False)

# 2020 season
tracking2020 = tracking2020.merge(pff, on = ['gameId', 'playId'])
tracking2020 = tracking2020.merge(games, on = 'gameId')
tracking2020 = tracking2020.merge(players, on = 'nflId')
tracking2020 = tracking2020.merge(plays, on = ['gameId', 'playId'])

# View missing data
missing = tracking2020.isnull().sum().sort_values(ascending = False)

#%% Separate data into kicks and punts
kicks2018 = tracking2018[tracking2018['kickType'].isin(['D', 'F', 'K', 'O', 
                                                       'P', 'Q', 'S', 'B'])]
kicks2019 = tracking2019[tracking2019['kickType'].isin(['D', 'F', 'K', 'O', 
                                                       'P', 'Q', 'S', 'B'])]
kicks2020 = tracking2020[tracking2020['kickType'].isin(['D', 'F', 'K', 'O', 
                                                       'P', 'Q', 'S', 'B'])]

punts2018 = tracking2018[tracking2018['kickType'].isin(['N', 'R', 'A'])]
punts2019 = tracking2019[tracking2019['kickType'].isin(['N', 'R', 'A'])]
punts2020 = tracking2020[tracking2020['kickType'].isin(['N', 'R', 'A'])]

# Subset on Kickoff Team Recovery
korecov2018 = kicks2018[kicks2018['specialTeamsResult'] == 'Kickoff Team Recovery']

#%% Subset on Panthers and Patriots plays where they are the punting team (2020)
panthers2020 = punts2020[ punts2020[ 'possessionTeam' ] == 'CAR' ]
patriots2020 = punts2020[ punts2020[ 'possessionTeam' ] == 'NE']