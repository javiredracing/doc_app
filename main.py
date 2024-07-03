import streamlit as st
from streamlit_ldap_authenticator import Authenticate

st.set_page_config(
    page_title="AI tools",
    page_icon=":bookmark_tabs:",
    layout="wide",
    initial_sidebar_state="auto",
)

st.logo("https://www.iter.es/wp-content/uploads/2016/05/logo.png")

auth = Authenticate(
    st.secrets['ldap'],
    st.secrets['session_state_names'],
    st.secrets['auth_cookie']
)

#@st.experimental_dialog("Sign out")
def logout():
    user = st.session_state["login_user"]["displayName"]
    auth.createLogoutForm({'message': f"Autheticated as {user}"})    

user = auth.login()   
# Declare the authentication object

#if st.session_state["login_user"]["displayName"]:
if user is not None:
    semantic_search = st.Page("page_menu/Semantic_search.py", title="Search in documents", icon=":material/search:", default=True)
    manage = st.Page("page_menu/Upload_file.py", title="Manage documents", icon=":material/dashboard:")
    chatbot = st.Page("page_menu/Chatbot.py", title="Chatbot", icon="🤖")
    logout_page = st.Page(logout, title="Log out", icon=":material/logout:")
    pg = st.navigation([semantic_search, manage, chatbot, logout_page])
    pg.run()