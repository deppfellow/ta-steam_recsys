class NDCG:
    def __init__(self, pred_df, pref_rank, k=10):
        self.pred_df = pred_df
        self.pref_rank = pref_rank
        self.k = k

        # Get relevance score for each predictions
        _rel_score_tensor = [
            [1 if _item in pref_rank[_row[0]] else 0 for _item in _row[1]]
            for _row in zip(pred_df['user_id'], pred_df['predicted_items'])
        ]

        self.pred_df['rel_score'] = _rel_score_tensor

    def eval_ndcg(self):
        # Evaluate ndcg for each predictions
        _rel_score_list = list(self.pred_df['rel_score'].values)
        _rank = list(np.arange(self.k))

        _ndcg_list = [self.ndcg_from_rank(
            _rel_score_list[i], _rank) for i in range(len(_rel_score_list))]

        return np.sum(np.asarray(_ndcg_list)) / len(_ndcg_list)

    def ndcg_from_rank(self, y_true, rank):
        y_true = np.asarray(y_true)
        rank = np.asarray(rank)

        if y_true.nonzero()[0].size == 0:
            return 0

        k = len(y_true)
        ideal_rank = np.argsort(y_true)[::-1]

        dcg = self.dcg_from_rank(y_true, rank[:k])
        idcg = self.dcg_from_rank(y_true, ideal_rank[:k])

        return dcg / idcg

    def dcg_from_rank(self, y_true, rank):
        rel = y_true[rank]
        gains = 2 ** rel - 1
        discount = np.log2(np.arange(len(rank)) + 2)

        return np.sum(gains / discount)
