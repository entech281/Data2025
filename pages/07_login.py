import streamlit as st
import streamlit_authenticator as stauth
from motherduck import con
import cached_data

hashed_passwords = st.secrets['admin']['passwords']
usernames = st.secrets['admin']['usernames']
cookie_name = st.secrets['admin']['cookie_name']
cookie_key = st.secrets['admin']['cookie_key']
expiry_days = st.secrets['admin']['expiry_days']

st.title('Login')


credentials = {'usernames' : {}}

for username, hashed_password in zip(usernames, hashed_passwords):
    credentials['usernames'][username] = {'password' : hashed_password, 'email' : "", 'name' : username}

authenticator = stauth.Authenticate(
    credentials=credentials,
    cookie_name=cookie_name,
    cookie_key=cookie_key,
    expiry_days=expiry_days
)

authenticator.login(clear_on_submit=True)

if st.session_state['authentication_status']:
    authenticator.logout(location='sidebar')