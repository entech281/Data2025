import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import streamlit_authenticator as stauth
from motherduck import con
import cached_data

hashed_passwords = st.secrets['admin']['passwords']
usernames = st.secrets['admin']['usernames']
cookie_name = st.secrets['admin']['cookie_name']
cookie_key = st.secrets['admin']['cookie_key']
expiry_days = st.secrets['admin']['expiry_days']

credentials = {'usernames' : {}}

for username, hashed_password in zip(usernames, hashed_passwords):
    credentials['usernames'][username] = {'password' : hashed_password, 'email' : "", 'name' : username}

authenticator = stauth.Authenticate(
    credentials=credentials,
    cookie_name=cookie_name,
    cookie_key=cookie_key,
    expiry_days=expiry_days
)
on_login = False
if "on_login" in st.session_state.keys():
    on_login = st.session_state["on_login"]

authed = False
if "authentication_status" in st.session_state.keys():
    on_login = st.session_state["authentication_status"]

if not authed and not on_login:
    switch_page("login")
elif authed and on_login:
    switch_page("home")
elif authed:
    authenticator.logout(location="sidebar")