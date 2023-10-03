import pandas as pd
from sklearn.model_selection import train_test_split, StratifiedKFold

drive_path = "drive/MyDrive/Dataset_Collections/steamgame_6june/"

users = pd.read_csv(drive_path + "users.csv")
games = pd.read_csv(drive_path + "games.csv")
recs = pd.read_csv(drive_path + "recommendations.csv")
metadatas = pd.read_json(drive_path + "games_metadata.json", lines=True)

# 1.a. Filtering users with at least >= 20 interactions and >= 10 positive interactions
recs.drop(['helpful', 'funny', 'date', 'review_id'], axis=1, inplace=True)
recs = recs.reindex(['user_id', 'app_id', 'is_recommended', 'hours'], axis=1)
recs['is_recommended'] = recs['is_recommended'].astype(int)

users_gt = users[users['reviews'] >= 20]
recs = recs[recs['user_id'].isin(users_gt['user_id'])].reset_index(drop=True)

users_pos_ease = recs.groupby('user_id').agg(
    {'is_recommended': 'sum'}).query('is_recommended >= 10')
recs_ease = recs[recs['user_id'].isin(
    users_pos_ease.index)].reset_index(drop=True)

# 1.b. Merging games with tags, but save the `positive_ratio`
games = games.merge(metadatas, on='app_id')
tags = metadatas.explode('tags')
top_tags = tags['tags'].value_counts().head(88).index

for tag in top_tags:
    games[tag] = games['tags'].apply(lambda x: int(tag in x))

games.drop(['tags', 'description'], axis=1, inplace=True)

# 1.c. Get users who appears in recs_ease
users_ease = users[users['user_id'].isin(
    recs_ease['user_id'])].reset_index(drop=True)
users_ease.drop(['products', 'reviews'], axis=1, inplace=True)

# 1.d. Get prefrank (pos and neg) for each users in recs_ease. Save to 'users_ease'
recs_ease_copy = recs_ease.copy()

ease_true = recs_ease_copy[recs_ease_copy['is_recommended'] == 1].sort_values(
    'hours', ascending=False)
ease_false = recs_ease_copy[recs_ease_copy['is_recommended'] == 0].sort_values(
    'hours', ascending=True)

ease_pos = ease_true.groupby('user_id')['app_id'].apply(list)
ease_neg = ease_false.groupby('user_id')['app_id'].apply(list)

users_ease_copy = users_ease.copy()
users_ease_copy['pos_preferences'] = users_ease_copy['user_id'].map(ease_pos)
users_ease_copy['neg_preferences'] = users_ease_copy['user_id'].map(ease_neg)

users_ease = users_ease_copy.copy()

users_ease['neg_preferences'] = [
    [] if row is np.nan else row for row in users_ease['neg_preferences']]

ease_neg = pd.Series(
    users_ease['neg_preferences'].values, index=users_ease['user_id'])

# ------------------------------------------------------------------------------------------------------
# 2.a. Modify games data to only include games with >= 80% positive ratio
games = games[games['positive_ratio'] >= 80].reset_index(drop=True)
games.drop(['date_release', 'win', 'mac', 'linux', 'rating', 'positive_ratio',
            'user_reviews', 'price_final', 'price_original', 'discount', 'steam_deck'], axis=1, inplace=True)

# 2.b. Take only recs who interacts with "80%" popular games and filter users with >= 10 positive interactions
recs_cbf = recs[recs['app_id'].isin(games['app_id'])].reset_index(drop=True)

users_pos_cbf = recs_cbf.groupby('user_id').agg(
    {'is_recommended': 'sum'}).query('is_recommended >= 10')
recs_cbf = recs_cbf[recs_cbf['user_id'].isin(
    users_pos_cbf.index)].reset_index(drop=True)

# 2.c. Get users who appears in recs_cbf
users_cbf = users[users['user_id'].isin(
    recs_cbf['user_id'])].reset_index(drop=True)
users_cbf.drop(['products', 'reviews'], axis=1, inplace=True)

# 2.d. Get prefrank (pos and neg) for each users in recs_cbf. Save to 'users_cbf'
recs_cbf_copy = recs_cbf.copy()

cbf_true = recs_cbf_copy[recs_cbf_copy['is_recommended']
                         == 1].sort_values('hours', ascending=False)
cbf_false = recs_cbf_copy[recs_cbf_copy['is_recommended']
                          == 0].sort_values('hours', ascending=True)

cbf_pos = cbf_true.groupby('user_id')['app_id'].apply(list)
cbf_neg = cbf_false.groupby('user_id')['app_id'].apply(list)

users_cbf_copy = users_cbf.copy()
users_cbf_copy['pos_preferences'] = users_cbf_copy['user_id'].map(cbf_pos)
users_cbf_copy['neg_preferences'] = users_cbf_copy['user_id'].map(cbf_neg)

users_cbf = users_cbf_copy.copy()

users_cbf['neg_preferences'] = [
    [] if row is np.nan else row for row in users_cbf['neg_preferences']]

cbf_neg = pd.Series(
    users_cbf['neg_preferences'].values, index=users_cbf['user_id'])

# 3. Split both data into trainset and testset
# EASE's data split
trainset_ease, testset_ease = train_test_split(
    recs_ease, test_size=0.2, stratify=recs_ease['is_recommended'], random_state=101)

users_pos_ease = users_pos_ease.index
trainset_ease.drop(['hours'], axis=1, inplace=True)
testset_ease.drop(['hours'], axis=1, inplace=True)

# CBF's data split
trainset_cbf, testset_cbf = train_test_split(
    recs_cbf, test_size=0.2, stratify=recs_cbf['is_recommended'], random_state=101)

users_pos_cbf = users_pos_cbf.index
trainset_cbf.drop(['hours'], axis=1, inplace=True)
testset_cbf.drop(['hours'], axis=1, inplace=True)
