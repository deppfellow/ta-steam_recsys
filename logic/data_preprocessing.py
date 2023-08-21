import pandas as pd
from sklearn.model_selection import train_test_split

drive_path = "drive/MyDrive/Dataset_Collections/steamgame_6june/"

users = pd.read_csv(drive_path + "users.csv")
games = pd.read_csv(drive_path + "games.csv")
recs = pd.read_csv(drive_path + "recommendations.csv")
metadatas = pd.read_json(drive_path + "games_metadata.json", lines=True)

# 1. Data reduction
users_gt = users[users['reviews'] >= 10]

recs_gte10 = recs[recs['user_id'].isin(users_gt['user_id'])]
recs_gte10 = recs_gte10.reset_index(drop=True)

# 2. Games creation and tags filtering
games.drop(['date_release', 'win', 'mac', 'linux', 'rating', 'positive_ratio',
            'user_reviews', 'price_final', 'price_original', 'discount', 'steam_deck'], axis=1, inplace=True)

games = games.merge(metadatas, on='app_id')
tags = metadatas.explode('tags')
top_tags = tags['tags'].value_counts().head(88).index

for tag in top_tags:
    games[tag] = games['tags'].apply(lambda x: int(tag in x))

games.drop(['tags', 'description'], axis=1, inplace=True)

# 3. Users creation
users_gte10 = users[users['user_id'].isin(recs_gte10['user_id'])]
users_gte10 = users_gte10.reset_index(drop=True)

users_gte10.drop(['products', 'reviews'], axis=1, inplace=True)

# 4. Interactions creation
recs_gte10.drop(['helpful', 'funny', 'date', 'review_id'],
                axis=1, inplace=True)
recs_gte10 = recs_gte10.reindex(
    columns=['user_id', 'app_id', 'is_recommended', 'hours'])

recs_gte10['is_recommended'] = recs_gte10['is_recommended'].astype(int)

# 5. Data splitting
trainset, testset = train_test_split(recs_gte10,
                                     test_size=0.2,
                                     stratify=recs_gte10['is_recommended'],
                                     random_state=101)
