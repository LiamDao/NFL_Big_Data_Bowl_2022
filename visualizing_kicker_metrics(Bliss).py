# -*- coding: utf-8 -*-
"""
Created on Sun Oct 10 23:33:37 2021

@author: liamd
"""

#%% import
import numpy as np 
import pandas as pd
from joypy import joyplot
import matplotlib.pyplot as plt
import os
os.chdir('C:\\Users\\liamd\\Documents\\NFL Big Data Bowl\\Data\\')

#%% reading in non-tracking data %%#

#includes play-by-play info on specific plays
df_plays = pd.read_csv("plays.csv")

#includes background info for players
df_players = pd.read_csv("players.csv")

df_plays.head()
df_players.head()

#%% Reading tracking data (needs to be done iteratively) %%#

#years of NFL seasons
seasons = ["2018", "2019", "2020"]

#blank dataframe to store tracking data
df_tracking = pd.DataFrame()

#iterating through all seasons
for s in seasons:
    
    #temperory dataframe used for reading week for given iteration
    df_trackingTemp = pd.read_csv("tracking"+s+".csv")
    
    #storing temporary dataframe in full season dataframe
    df_tracking = df_tracking.append(df_trackingTemp)   
    
df_tracking.head()

#%% Cleaning data
#Standardizing tracking data so its always in direction of kicking team vs raw on-field coordinates.
df_tracking.loc[df_tracking['playDirection'] == "left", 'x'] = 120-df_tracking.loc[df_tracking['playDirection'] == "left", 'x']
df_tracking.loc[df_tracking['playDirection'] == "left", 'y'] = 160/3-df_tracking.loc[df_tracking['playDirection'] == "left", 'y']

#dataframe will store where ball was when kick is crosses uprights

#filtering for football
df_ballFieldGoal = df_tracking[df_tracking['displayName'] == 'football']

df_ballFieldGoal.sort_values(by = ['gameId', 'playId', 'frameId'])

#grouping by gameId and playId
df_ballFieldGoal = df_ballFieldGoal.loc[df_ballFieldGoal.groupby(by=['playId', 'gameId']).x.transform(lambda z: (z >= 120) & (z.shift(1) < 120))]

#selecting first occurence in case it crosses uprights multiple times
df_ballFieldGoal = df_ballFieldGoal.groupby(by=['playId', 'gameId']).first().reset_index()

#creating and adding a variable for absolute offset from center. Center of field is at coordiante 160/6
df_ballFieldGoal.insert(loc = 18, column = "offsetFromCenter", value = abs(df_ballFieldGoal['y'] - 160/6))

#selecting offsetFromCenter and key variables only
df_ballFieldGoal = df_ballFieldGoal[['gameId', 'playId', 'offsetFromCenter']]

#dataframe storing kick offset for each kicker on each play

#filtering for unblocked extra points and field goals only
df_fieldGoalAnalysis = df_plays[df_plays['specialTeamsResult'].isin(['Kick Attempt Good', 'Kick Attempt No Good'])]

#using play description to filter out kick attempts that were missed because they were short   
df_fieldGoalAnalysis = df_fieldGoalAnalysis[~df_fieldGoalAnalysis['playDescription'].str.contains('No Good, Short')]


#kickLength is sometimes missing on extra points. In that case we use impute as yards from target endzone + 18.
conditions = [
    (df_fieldGoalAnalysis['yardlineNumber'] == 50),
    (df_fieldGoalAnalysis['possessionTeam'] == df_fieldGoalAnalysis['yardlineSide']),
    (df_fieldGoalAnalysis['possessionTeam'] != df_fieldGoalAnalysis['yardlineSide'])
]

values = [df_fieldGoalAnalysis['yardlineNumber'], df_fieldGoalAnalysis['yardlineNumber'] + 50, df_fieldGoalAnalysis['yardlineNumber']]

df_fieldGoalAnalysis['yardsFromTargetEndzone'] = np.select(conditions, values)

#imputing kick length as yards from target endzone + 18
df_fieldGoalAnalysis.loc[df_fieldGoalAnalysis['kickLength'].isnull(), 'kickLength'] = 18.0+df_fieldGoalAnalysis.loc[df_fieldGoalAnalysis['kickLength'].isnull(), 'yardsFromTargetEndzone']

#joining players by kickerId to get displayName
df_fieldGoalAnalysis = pd.merge(df_fieldGoalAnalysis, df_players, left_on=['kickerId'], right_on =['nflId'])

#joining filtered tracking data
df_fieldGoalAnalysis = pd.merge(df_fieldGoalAnalysis, df_ballFieldGoal, left_on=['gameId', 'playId'], right_on =['gameId', 'playId'])

#selecting only variables of interest:
df_fieldGoalAnalysis = df_fieldGoalAnalysis[['gameId', 'playId', 'displayName', 'kickLength', 'offsetFromCenter', 'playDescription']]


#%% Visualizing matric by kicker %%#
#dataframe for visualization

#filtering for length between 30 and 40 yards
df_visual = df_fieldGoalAnalysis[(df_fieldGoalAnalysis['kickLength'] >= 30) & (df_fieldGoalAnalysis['kickLength'] <= 40)]

#filtering for only kickers with 75+ attempts
df_visual = df_visual[df_visual['displayName'].map(df_visual['displayName'].value_counts()) >= 75]

#grouping by kickerId and taking mean of data
df_visual = df_visual.groupby('displayName').agg(avgOffsetFromCenter = ('offsetFromCenter', 'mean'))

#sorting data by average offset from center
df_visual = df_visual.sort_values(by = 'avgOffsetFromCenter', ascending=False)

#ungrouping
df_visual = df_visual.reset_index()

fig = plt.figure(figsize=(10,10))
plt.rc('grid', linestyle=':', color='lightgray', linewidth=0.5)
plt.grid(True, zorder = 0)

plt.barh(list(df_visual['displayName']), list(df_visual['avgOffsetFromCenter']), color = "lightblue")
plt.xticks([0.0, 0.5, 1, 1.5])


plt.title("Average Offset from Center by Place Kicker on 30 to 40 yard Attempts \n (Ordered from Best to Worst)", fontsize = 16)
plt.xlabel("Average Offset from Center", fontsize = 14)

plt.show()

#dataframe for visualization

#filtering for length between 30 and 40 yards
df_visual2 = df_fieldGoalAnalysis[(df_fieldGoalAnalysis['kickLength'] >= 30) & (df_fieldGoalAnalysis['kickLength'] <= 40)]

#filtering by previous list of kickers with 75+ attempts
df_visual2 = df_visual2[df_visual2['displayName'].isin(list(df_visual['displayName']))]

df_visual2['order'] = df_visual2.groupby('displayName').offsetFromCenter.transform(lambda x: np.mean(x))

df_visual2 = df_visual2.sort_values(['order'])

grouped = df_visual2.groupby("displayName", sort=False)

joyplot(grouped, column = 'offsetFromCenter', figsize = (10,10), overlap = 0.5, color = 'lightblue')
plt.xticks([0.0, 2.5, 5.0, 7.5])

plt.rc('grid', linestyle=':', color='lightgray', linewidth=0.5)
plt.grid(True, zorder = 0)

plt.title("Density of Offset from Center by Kicker on 30 to 40 yard Attempts \n (Ordered from Best to Worst)", fontsize = 16)
plt.xlabel("Kick Attempt Offset from Center Values", fontsize = 14)

plt.show()

