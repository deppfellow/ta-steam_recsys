# import pandas as pd

# # with open("data/games_obj.pkl", "r") as f:
# #     data = pickle.load(f)
# #     f.close()

# data = pd.read_pickle("data/games_obj.pkl")
# print(data["ELDEN RING"])

a = "https://open.spotify.com/playlist/6VPV9xY0SbUOHdhSOGYatd?si=b68b4d86b087435f".split(
    '/')[-1].split('?')[0]

print(a)
