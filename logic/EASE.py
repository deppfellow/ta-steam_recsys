import pandas as pd
import torch


class EASE:
    """
    EASE class construction
    """

    def __init__(self, train, user_col='user_id', item_col='app_id', score_col='is_recommended', reg=250.):
        """
        Args:
            train: (DataFrame) data of training set
            user_col: (String) column name of users column
            item_col: (String) column name of items column
            score_col: (String) column name of interactions column
            reg: (Float) EASE's regularization value
        """

        self.user_col = user_col
        self.item_col = item_col
        self.reg = reg

        self.user_id_col = user_col + "_index"
        self.item_id_col = item_col + "_index"

        self.user_lookup = self.generate_label(train, self.user_col)
        self.item_lookup = self.generate_label(train, self.item_col)

        self.item_map = {}
        # Made the lookup item into dictionary key value
        for _item, _item_index in self.item_lookup.values:
            self.item_map[_item_index] = _item

        # Merge encoded lookup index with training data
        train = train.merge(train.merge(
            self.user_lookup, on=[self.user_col], sort=False))
        train = train.merge(train.merge(
            self.item_lookup, on=[self.item_col], sort=False))
        # print(train)

        self.indices = torch.LongTensor(
            train[[self.user_id_col, self.item_id_col]].values
        )

        if not score_col:
            # Calculate implicit interactions
            self.values = torch.ones(self.indices.shape[0])
        else:
            self.values = torch.FloatTensor(train[score_col])

        self.sparse = torch.sparse.FloatTensor(self.indices.T, self.values)

    def generate_label(self, df, col):
        # Select only 'col' column and drop duplicate value in df
        dist_labels = df[[col]].drop_duplicates()

        # Encode each user_id to obtain unique index for lookup
        dist_labels[col +
                    "_index"] = dist_labels[col].astype("category").cat.codes

        return dist_labels

    def fit(self):
        """
        Train EASE model using training set

        Args:
            self: (Object) Object of class EASE
        """

        # 2. Pembentukan matriks gram G
        G = self.sparse.to_dense().T @ self.sparse.to_dense()

        # 3. Regularisasi diagonal matriks G dan pengambilan inverse
        G += torch.eye(G.shape[0]) * self.reg
        P = G.inverse()

        # 4. Mengestimasi matriks bobot B
        B = P / (-1 * P.diag())

        # 5. Inisialisasi diagonal matriks B --> diag(B) = 0
        B = B + torch.eye(B.shape[0])

        self.B = B

        return

    def predict(self, pred_df, k=10, remove_owned=True):
        """
        Args:
            pred_df: (DataFrame) Dataframe of users that need predictions
            k: (Integer) Number of items to recommend
            remove_owned: (Boolean) Whether to remove previously interacted items

        Return:
            Dataframe of users + their predictions in sorted order
        """
        pred_df = pred_df[[self.user_col]].drop_duplicates()
        n_orig = pred_df.shape[0]

        pred_df = pred_df.merge(pred_df.merge(
            self.user_lookup, on=[self.user_col], sort=False))
        n_curr = pred_df.shape[0]

        if n_orig - n_curr:
            print(
                f"Number of unknown users from prediction data {n_orig - n_curr}")

        _output_preds = []

        # Select only user id in user data
        _user_tensor = self.sparse.to_dense().index_select(
            dim=0, index=torch.LongTensor(pred_df[self.user_id_col])
        )
