import pandas as pd
import torch

from sklearn.neighbors import KNeighborsClassifier

class EASE:
    def __init__(self, train, 
            user_col='user_id', 
            item_col='app_id', 
            score_col='is_recommended',
            reg=250.):
        """
            train: (DataFrame) data of training set
            user_col: (String) column name of users column
            item_col: (String) column name of items column
            score_col: (String) column name of interactions column
            reg: (Float) EASE's regularization value
        """

        self.user_col = user_col
        self.item_col = item_col
        self.score_col = score_col
        self.train = train
        self.reg = reg

        self.user_id_col = user_col + "_index"
        self.item_id_col = item_col + "_index"

        self.item_lookup = self.generate_label(train, self.item_col)

        self.item_map = {}
        for item, item_index in self.item_lookup.values:
            self.item_map[item_index] = item

    def generate_label(self, df, col):
        dist_labels = df[[col]].drop_duplicates()
        dist_labels[col +
                    "_index"] = dist_labels[col].astype("category").cat.codes
        
        return dist_labels
        
    def predict_active(self, pred_df, weight, k=10, remove_owned=True):
        """
            Args:
                pred_df: (DataFrame) data of user interactions
                weight: (Tensor) Weight matrix of pre-trained EASE model
                k: (Integer) number of recommendation to be shown
                remove_owned: (Boolean) Whether to remove already interacted items
        """
        train = pd.concat([self.train, pred_df], axis=0)
        user_lookup = self.generate_label(train, self.user_col)

        train = train.merge(user_lookup, on=[self.user_col], sort=False)
        train = train.merge(self.item_lookup, on=[self.item_col], sort=False)

        pred_df = pred_df[[self.user_col]].drop_duplicates()
        pred_df = pred_df.merge(user_lookup, on=[self.user_col], sort=False)

        indices = torch.LongTensor(train[[self.user_id_col, self.item_id_col]].values)
        values = torch.FloatTensor(train[self.score_col])
        sparse = torch.sparse.FloatTensor(indices.T, values)

        # --------------------------------------------------
        user_act_tensor = sparse.index_select(
            dim=0, index=torch.LongTensor(pred_df[self.user_id_col])
        )

        _preds_act_tensor = user_act_tensor @ weight
        if remove_owned:
            _preds_act_tensor += -1. * user_act_tensor

        output_preds = []
        score_preds = []
        for _preds in _preds_act_tensor:
            top_items = _preds.topk(k)

            output_preds.append([self.item_map[id] for id in top_items.indices.tolist()])
            score_preds.append( top_items.values.tolist() )

        pred_df['predicted_items'] = output_preds
        pred_df['predicted_score'] = score_preds
        
        escaped = [
            ele for i_list in pred_df['predicted_items'].values for ele in i_list
        ]

        return escaped
    
def ease_model(pred_df, k=10):
    ease_B = torch.load("data/ease_B.pt")
    train = pd.read_csv("data/recs.csv")

    ease = EASE(train)
    res = ease.predict_active(pred_df=pred_df, weight=ease_B, k=k)

    return res


# def main():
#     pass
#     # act_user = pd.DataFrame({
#     #     'user_id': [999999, 999999, 999999, 999999, 999999, 999999],
#     #     'app_id': [1689910, 1245620, 814380, 620980, 1551360, 774171],
#     #     'is_recommended': [0, 1, 1, 0, 1, 1]
#     # })
#     # act_indices = torch.FloatTensor(ac)

#     # print(
#     #     torch.sparse.FloatTensor(sparse_indices.T, sparse_values)
#     # )

# if __name__ == '__main__':
#     main()