from sklearn.neighbors import KNeighborsClassifier


class KnnCBF:
    def __init__(self, train, items, user_col='user_id', item_col='app_id', score_col='is_recommended'):

        self.user_col = user_col
        self.item_col = item_col
        self.score_col = score_col

        self.user_id_col = user_col + "_index"
        self.item_id_col = item_col + "_index"

        self.user_lookup = self.generate_label(train, self.user_col)
        self.item_lookup = self.generate_label(items, self.item_col)

        self.item_map = {}
        # Made the lookup item into dictionary key-value
        for _item, _item_index in self.item_lookup.values:
            self.item_map[_item_index] = _item

        train = train.merge(self.user_lookup, on=[self.user_col], sort=False)
        train = train.merge(self.item_lookup, on=[self.item_col], sort=False)

        # Creating similarity items
        items = items.merge(items.merge(
            self.item_lookup, on=[self.item_col], sort=False)
        )
        items = items.drop(items.columns[:2], axis=1)

        # Reindexing items dataframe
        cols = list(items.columns)
        items = items[cols[-1:] + cols[:-1]]

        self.train = train
        self.items = items

    def generate_label(self, df, col):
        dist_labels = df[[col]].drop_duplicates()
        dist_labels[col +
                    "_index"] = dist_labels[col].astype("category").cat.codes

        return dist_labels

    def classifier_fit(self, X, y, test, num_point, metric):
        classifier = KNeighborsClassifier(n_neighbors=num_point, metric=metric)
        classifier.fit(X, y)

        return classifier.kneighbors(test)

    def predict(self, pred_df, num_point=5, metric='cosine', k=10, remove_owned=True):
        pred_df = pred_df[[self.user_col]].drop_duplicates()
        n_orig = pred_df.shape[0]

        pred_df = pred_df.merge(self.user_lookup, on=[
                                self.user_col], sort=False)
        n_curr = pred_df.shape[0]

        if n_orig - n_curr:
            print(
                f"Number of unknown users from prediction data {n_orig - n_curr}")

        _output_preds = []
        _score_preds = []
        # Works with each user in pred_df
        # Get the rating for each interacted items
        for _user in pred_df[self.user_col]:
            # Get current user's interacted items and respective rating
            curr_user = self.train[self.train[self.user_col]
                                   == _user][[self.item_id_col, self.score_col]]
            items = self.items

            # Get contents of the user's interacted items
            user_items = items.merge(curr_user, on=[self.item_id_col])

            # Get items not interacted by user
            non_items = items[~items[self.item_id_col].isin(
                curr_user[self.item_id_col])]

            # Fitting through classifier
            X = user_items.iloc[:, 1:-1]
            y = user_items.iloc[:, -1]
            test = non_items.iloc[:, 1:]

            # Retrieve the output for current user
            output = self.classifier_fit(X, y, test, num_point, metric)

            # For each non-interacted items, get the nearest point (interacted items) and its distance.
            # For each nearest point, get its rating, and multiply by its distance, then divide by total n_neighbors.
            # Return the result as relevance score for those non-interacted item
            rating = y.loc[output[1].flatten()].values.reshape(output[1].shape)
            result = np.sum(rating * output[0], axis=1) / num_point

            # Get top-k similar non-interacted items
            top_tensor = torch.from_numpy(result).topk(10)
            indices = top_tensor.indices.tolist()
            score = top_tensor.values.tolist()

            # Appending into initialized list
            _output_preds.append([self.item_map[_id] for _id in indices])
            _score_preds.append(score)

        pred_df['predicted_items'] = _output_preds
        pred_df['relevance_score'] = _score_preds

        # _items_tensor = self.items.drop(self.items.columns[1:], axis=1)
        return pred_df
