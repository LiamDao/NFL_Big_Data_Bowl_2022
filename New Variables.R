###### Data bowl ######
# Load in Libraries
library(tidyverse)
library(caret)
library(leaps)
library(glmnet)
library(ggplot2)
library(earth)
library(mgcv)
library(ROCR)
library(ROCR)
library(randomForest)
library(xgboost)
library(Ckmeans.1d.dp)
library(pdp)
library(Matrix)
library(gganimate)

#Read in Data
#original
games = read.csv("games.csv")
PFF = read.csv("PFFScoutingData.csv")
players = read.csv("players.csv")
plays = read.csv("plays.csv")
#tracking
tracking2018 = read.csv("tracking2018.csv")
tracking2019 = read.csv("tracking2019.csv")
tracking2020 = read.csv("tracking2020.csv")
#subset
punts_df <- read.csv("df_plays_punts.csv")

###### New Variables ######
#Is a player moving when making the catch?
#filter for test, just punts received
test <- tracking2020 %>%
  filter(displayName == "Nyheim Hines" & tracking2020$event %in% c("punt_received","fair_catch"))

#moving at catch?
test$moving_at_catch <- ifelse(test$s < 1.5 | test$a < 1, 0, 1)

#was the punt received outside the numbers?
test$hash <- ifelse(test$y < 17.78 | test$y > 35.56, 1, 0)
