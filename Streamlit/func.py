import streamlit as st
import requests
import shutil

from io import BytesIO
from PIL import Image


data = {
    "Sekiro™: Shadows Die Twice - GOTY Edition": 814380,
    "ELDEN RING": 1245620,
    "Dota 2": 570,
    "Counter-Strike 2": 730,
    "Tom Clancy's Rainbow Six® Siege": 359550,
    "Doki Doki Literature Club!": 698780}

games = [
    "ELDEN RING", "Counter-Strike 2", "Doki Doki Literature Club!"
]


def generate_container():
    container = st.container()
    img_col, pref_col = container.columns([3.8, 1.2])

    # img_col.image(Image.open(response.content))
    # pref_col.selectbox(
    #     "Your rating:"
    #     ["Positive", "Negative"],
    #     key=app_id
    # )
    return img_col, pref_col


def generate_gamebox(titles):
    titles_id = []
    for title in titles:
        titles_id.append(data[title])

    for id in titles_id:
        url = f"https://cdn.cloudflare.steamstatic.com/steam/apps/{id}/header.jpg"
        resp = requests.get(url)

        if resp.status_code == 200:
            container = st.container()
            img_col, pref_col = container.columns([3, 2])
            # img_col, pref_col = generate_container()

            img_col.image(BytesIO(resp.content))
            pref_col.selectbox(
                "Your rating:",
                options=["Positive", "Negative"],
                key=id
            )


# def fetch_image(games_title):
#     # Get id of each games
#     id_arr = []
#     for game in games_title:
#         id_arr.append(data[game])

#     for app_id in id_arr:
#         img_url = f"https://cdn.cloudflare.steamstatic.com/steam/apps/{app_id}/header.jpg"
#         response = requests.get(img_url)

#         if response.status_code == 200:
#             # with open(f"{app_id}.jpg", 'wb') as out_f:
#             #     shutil.copyfileobj(response.raw, out_f)
#             return generate_container(app_id=app_id, response=response)
#         else:
#             return f"Cannot generate {app_id} column"
