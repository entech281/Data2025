import streamlit as st
import streamlit_authenticator as stauth
from motherduck import con
import cached_data
st.session_state["on_login"] = True
import forcedAuth
st.session_state["on_login"] = False

st.title('Login')
st.text(str(st.session_state['authentication_status']) + " " + str(forcedAuth.on_login))
forcedAuth.authenticator.login(clear_on_submit=True)

forcedAuth.authenticator.logout(location="sidebar")