import streamlit as st
import requests
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

if "user_preferences" not in st.session_state:
    st.session_state['user_preferences'] = []

st.title("Playground System")

# def fetch_image(titles):
#     # Get id of each games
#     id_arr = []
#     for game in titles:
#         id_arr.append(data[game])

#     for app_id in id_arr:
#         img_url = f"https://cdn.cloudflare.steamstatic.com/steam/apps/{app_id}/header.jpg"
#         response = requests.get(img_url)

#         if response.status_code == 200:
#             poster_img = Image.open(response.content)


#         else:
#             return f"Failed to fetch poster image of game {app_id}"


def generate_game_container(title):
    container = st.container()
    img, pref = container.columns([3.8, 1.2])

    img.write(f"{title} Image")
    preference = pref.selectbox(
        "Preference:", ["Positive", "Negative"], key=title)

    return container

# # Tabs
# tab1, tab2 = st.tabs(["Tab 1", "Tab2"])
# tab1.write("this is tab 1")
# tab2.write("this is tab 2")

# # Columns
# col1, col2 = st.columns(2)
# col1.write('Column 1')
# col2.write('Column 2')


preferences = st.multiselect(
    label="Input games you like:",
    options=[
        "Sekiro™: Shadows Die Twice - GOTY Edition",
        "ELDEN RING",
        "Dota 2",
        "Counter-Strike 2",
        "Tom Clancy's Rainbow Six® Siege",
        "Doki Doki Literature Club!"],
    key="user_preferences")

st.markdown("<br>", unsafe_allow_html=True)

# st.write(preferences)
# # Creating initial container
# img, rate_input = st.columns([3.5, 1.5])
# img.write("Game's poster image")
# rate_input.selectbox("Your rating?", ['Positive', 'Negative'])
for title in preferences:
    container = generate_game_container(title)

st.markdown("---", unsafe_allow_html=True)
# st.write(st.session_state)

state = st.button("Get state")
if state:
    st.session_state

st.markdown("<br>", unsafe_allow_html=True)
