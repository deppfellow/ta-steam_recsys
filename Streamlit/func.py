import pandas as pd
import streamlit as st
import requests

from io import BytesIO
from PIL import Image

titles_dict = pd.read_pickle("data/2k_titles.pkl")
ids_dict = pd.read_pickle("data/2k_ids.pkl")


def generate_gamebox(titles):
    titles_id = []
    for title in titles:
        titles_id.append(titles_dict[title])

    for id in titles_id:
        url = f"https://cdn.cloudflare.steamstatic.com/steam/apps/{id}/header.jpg"
        resp = requests.get(url)

        if resp.status_code == 200:
            container = st.container()
            img_col, pref_col = container.columns([3, 2])

            img_col.image(BytesIO(resp.content))
            pref_col.selectbox(
                "Your rating:",
                options=["Positive", "Negative"],
                key=id
            )

    return titles_id
