import streamlit as st

st.title('RFP Aggregator')

st.write("Welcome to the RFP Aggregator! This app helps you to manage and aggregate various RFPs.")

# Example input for a RFP
st.subheader('Enter RFP Information')
rfp_name = st.text_input('RFP Name')
rfp_description = st.text_area('RFP Description')

if st.button('Submit'):
    st.success('RFP Submitted!')
    # Here, you would add functionality to save the RFP information.
