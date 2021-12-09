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

#trevor's file
punts_df <- read.csv("model train set.csv")

###### New Variables ######
#Is a player moving when making the catch?

return2018 <- tracking2018 %>%
  filter(tracking2018$event %in% c("punt_received"))


return2020hines <- tracking2020 %>%
 filter(displayName == "Nyheim Hines" & tracking2020$event %in% c("punt_received","fair_catch"))

return2018 <- tracking2018 %>%
  



#filter for test, just punts received
test <- tracking2020 %>%
  filter(displayName == "Nyheim Hines" & tracking2020$event %in% c("punt_received","fair_catch"))

#moving at catch?
test$moving_at_catch <- ifelse(test$s < 1.5 | test$a < 1, 0, 1)

#was the punt received outside the numbers?
test$hash <- ifelse(test$y < 17.78 | test$y > 35.56, 1, 0)

###### XG Boost ######
#filter on returns
returns <- punts_df %>% 
  filter(specialTeamsResult == "Return") %>% 
  filter(!is.na(kickReturnYardage))

# Subset test
train <- returns %>% sample_frac(0.7)

# XG Boost Modeling
# Set all columns in df that are factor to ordinal (needed for XGBoost)
for (col in colnames(df)) {
  if (class(df[,col]) == "factor") {
    df[,col] <- ordered(df[,col])
  }
}

# Create matrix for x and vector for y
train_x <- model.matrix(kickReturnYardage ~ quarter + down + yardsToGo + yardlineNumber + preSnapHomeScore + preSnapVisitorScore
                        + kickLength, data = training)[,-1]
train_y <- training$kickReturnYardage
# Model
xgb.yard <- xgboost(data = train_x, label = train_y, subsample = .5, nrounds = 100)
```


## Parameter Tuning
```{r parameter tuning}
set.seed(4321)
# Get nrounds first
xgb.yard.cv <- xgb.cv(data = train_x, label = train_y, subsample = .5, nrounds = 100, nfold = 10)
# Other parameters: eta, max_depth, gamma, colsample_bytree, min_child_weight
nrounds.results <- as.data.frame(xgb.yard.cv$evaluation_log)
nrounds.results[which.min(nrounds.results$test_rmse_mean),]
# Lowest rmse value (10.95142) has nrounds = 4
# Create tuning grid
tune_grid <- expand.grid(
  nrounds = 4,
  eta = seq(0, 1, by = 0.1),
  max_depth = c(1:10),
  gamma = c(0),
  colsample_bytree = 1,
  min_child_weight = 1,
  subsample = seq(0, 1, by = 0.1)
)
# Tune parameters
xgb.yard.caret <- train(x = train_x, y = train_y,
                        method = "xgbTree",
                        tuneGrid = tune_grid,
                        trControl = trainControl(method = 'cv', # Using 10-fold cross-validation
                                                 number = 10))
plot(xgb.yard.caret)
tune.results <- as.data.frame(xgb.yard.caret$results)
tune.results[which.min(tune.results$RMSE),]
```
> After first tune:
  * nrounds = 4
* subsample = .3
* max_depth = 1
* eta = .6
* gamma = 0
* colsample_bytree = 1
* min_child_weight = 1
* Test RMSE = 10.52559
## Tuning playground
```{r tuning playground}
set.seed(4321)
# Create tuning grid
tune_grid <- expand.grid(
  nrounds = 4,
  eta = seq(.25, .40, by = 0.01),
  max_depth = c(1:3),
  gamma = c(1:10),
  colsample_bytree = 1,
  min_child_weight = 1,
  subsample = seq(.25, .35, by = 0.01)
)
# Tune parameters
xgb.yard.caret <- train(x = train_x, y = train_y,
                        method = "xgbTree",
                        tuneGrid = tune_grid,
                        trControl = trainControl(method = 'cv', # Using 10-fold cross-validation
                                                 number = 10))
plot(xgb.yard.caret)
tune.results <- as.data.frame(xgb.yard.caret$results)
tune.results[which.min(tune.results$RMSE),]
set.seed(4321)
# Get nrounds first
xgb.yard.cv <- xgb.cv(data = train_x, label = train_y, subsample = .33, max_depth = 1, eta = .39, gamma = 7,
                      colsample_bytree = 1, min_child_weight = 1, nrounds = 100, nfold = 10)
# Other parameters: eta, max_depth, gamma, colsample_bytree, min_child_weight
nrounds.results <- as.data.frame(xgb.yard.cv$evaluation_log)
nrounds.results[which.min(nrounds.results$test_rmse_mean),]
```
> Current Interation:
  * nrounds = 5
* subsample = .33
* max_depth = 1
* eta = .39
* gamma = 7
* colsample_bytree = 1
* min_child_weight = 1
* Test RMSE = 10.51416
