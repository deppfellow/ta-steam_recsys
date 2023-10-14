import streamlit as st
from streamlit_option_menu import option_menu
from func import *
from model import *

if "user_preferences" not in st.session_state:
    st.session_state["user_preferences"] = {}

if "user_titles" not in st.session_state:
    st.session_state["user_titles"] = []

# if "hahahihi" not in st.session_state["user_preferences"]:
#     st.session_state["user_preferences"]["hahahihi"] = "ANJIANGGGGG"
titles_dict = pd.read_pickle("data/2k_titles.pkl")


def games_recomm(pref_dict, k=10):
    if "rs" in st.session_state:
        del st.session_state["rs"]

    with st.spinner("Getting recommendation..."):
        pred_df = pd.DataFrame({
            "user_id": [999999] * len(pref_dict),
            "app_id": pref_dict.keys(),
            "is_recommended": pref_dict.values()
        })

        res = ease_model(pred_df=pred_df, k=k)
        st.session_state['rs'] = res

        if len(res) >= 1:
            st.success(
                f"Go to result page to view top {len(res)} recommendations")
        else:
            st.error("Recommendation failed. Please restart the session")


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
        options=list(titles_dict),
        key="user_titles")

    user_input = generate_gamebox(preferences)

    state = st.button("Get recommendations")

    if state:
        if "user_preferences" in st.session_state:
            del st.session_state["user_preferences"]
            st.session_state["user_preferences"] = {}

        for i in user_input:
            if st.session_state[i] == "Positive":
                st.session_state["user_preferences"][i] = 1
            elif st.session_state[i] == "Negative":
                st.session_state["user_preferences"][i] = 0

            del st.session_state[i]

        games_recomm(st.session_state["user_preferences"])

        st.markdown("---")
        # st.session_state


# Result page
# Show the list of predictions for active user


def result_page():
    if "rs" not in st.session_state:
        st.error(
            'Please input game preferences in Home page and run "Get recommendations')
    else:
        st.success(f"Top {len(st.session_state['rs'])} recommendations")

        st.session_state
        generate_resbox(st.session_state["rs"])

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
