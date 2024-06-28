import streamlit as st
from streamlit_ldap_authenticator import Authenticate

st.set_page_config(
    page_title="AI tools",
    page_icon=":bookmark_tabs:",
    layout="wide",
    initial_sidebar_state="auto",
)

auth = Authenticate(
    st.secrets['ldap'],
    st.secrets['session_state_names'],
    st.secrets['auth_cookie']
)

#@st.experimental_dialog("Sign out")
def logout_modal():
    user = st.session_state["login_user"]["displayName"]
    auth.createLogoutForm({'message': f"Autheticated as {user}"})      
    
user = auth.login()
    
# Declare the authentication object
#if st.session_state["login_user"]["displayName"]:
if user is not None:
    semantic_search = st.Page("pages/Semantic_search.py", title="Search in documents", icon=":material/search:", default=True)
    manage = st.Page("pages/Upload_file.py", title="Manage documents", icon=":material/dashboard:")
    chatbot = st.Page("pages/Chatbot.py", title="Chatbot", icon="🤖")
    logout_page = st.Page(logout_modal, title="Log out", icon=":material/logout:")
    pg = st.navigation([semantic_search, manage, chatbot, logout_page])
    pg.run()