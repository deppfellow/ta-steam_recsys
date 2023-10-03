import streamlit as st
from streamlit_option_menu import option_menu
from func import *


if "user_preferences" not in st.session_state:
    st.session_state["user_preferences"] = []

# Main Page Header
# Consist of Home page, Result page, About page, and Log page


def spr_sidebar():
    menu = option_menu(
        menu_title=None,
        options=['Home', 'Result', 'About'],
        icons=['house', 'joystick', 'info-square'],
        menu_icon='cast',
        default_index=0,
        orientation='horizontal'
    )

    # Change 'app_mode' state based on current page
    if menu == 'Home':
        st.session_state['app_mode'] = 'Home'
    elif menu == 'Result':
        st.session_state['app_mode'] = 'Result'
    elif menu == 'About':
        st.session_state['app_mode'] = 'About'

# Home page. One of the page in Main Header


def home_page():
    st.title("Steam Recommendation System")

    # st.session_state['user_title'] = st.session_state['input_title']
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

    user_input = generate_gamebox(preferences)

    state = st.button("Get state")
    if state:
        st.session_state


# Result page
# Show the list of predictions for active user


def result_page():
    pass

# About page
# Show the information of the project and the sites


def about_page():
    pass


def main():
    spr_sidebar()
    # st.session_state

    if st.session_state['app_mode'] == 'Home':
        home_page()
    elif st.session_state['app_mode'] == 'Result':
        result_page()
    elif st.session_state['app_mode'] == 'About':
        about_page()


if __name__ == '__main__':
    main()
