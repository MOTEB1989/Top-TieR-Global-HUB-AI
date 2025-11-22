import redis
import streamlit as st

redis_client = redis.Redis(host='redis', port=6379, db=1)

st.title('Top-TieR Global HUB AI')
st.write('Welcome to the Streamlit UI!')
