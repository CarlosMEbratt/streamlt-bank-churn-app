import time
import streamlit as st
from datetime import datetime
import pandas as pd

from dotenv import load_dotenv, find_dotenv #Used for import the function to load .env file
import os
from pymongo import MongoClient #Used to create the connection
load_dotenv(find_dotenv()) #Shorcut to load the enviroment file

#'''Streamlit settings------------------------------------------------------------------------------------------------------------- '''

# Page title
st.set_page_config(page_title='Bank Churn App', 
                   page_icon='🤖', layout="wide", 
                   initial_sidebar_state="expanded")


#'''Connect to the DB------------------------------------------------------------------------------------------------------------- '''

@st.cache_resource

def connect_db():
    password = os.environ.get("MONGODB_PWD") #This is to grab the password from the .env file
    connection_string = f"mongodb+srv://carlosmebratt:{password}@bdm1003.tnmvwtl.mongodb.net/?retryWrites=true&w=majority"
    client = MongoClient(connection_string)
    db=client["bankchurnapp"]    
    return db

#'''Login App Function------------------------------------------------------------------------------------------------------------- '''

def select_signup():
    st.session_state.form = 'signup_form'

def user_update(name, successful_login):
    st.session_state.username = name
    st.session_state.successful_login = successful_login
    
def update_successful_login(successful_login):
    st.session_state.successful_login = successful_login

def login_app():
    db = connect_db()
    credentials_db = db["credentials"]

    # Initialize Session States.
    if 'username' not in st.session_state:
        st.session_state.username = ''
    if 'successful_login' not in st.session_state:
        st.session_state.successful_login = False

    if st.session_state.username != '':
        st.sidebar.markdown(''':blue[You are logged in]''')
        logout = st.sidebar.button(label='Log Out')
        if logout:
            # Handle Logout Click
            st.session_state.username = ''  # Set username to empty string
            st.session_state.successful_login = False  # Set successful_login to False
            st.session_state.form = ''  # Reset form state
            st.sidebar.success("You have successfully logged out!")

    else:
        # Render sign-in form and button
        login_container = st.sidebar.empty()
        login_container.write("Please sign in.")
        login_form = login_container.form(key='signin_form', clear_on_submit=True)
        username = login_form.text_input(label='Enter Username')
        password = login_form.text_input(label='Enter Password', type='password')

        if credentials_db.find_one({'username': username, 'password': password}):
            login = login_form.form_submit_button(label='Sign In', on_click=user_update(username, True))
            if login:
                st.sidebar.success(f"You are logged in as {username.upper()}")
                del password
        else:
            login = login_form.form_submit_button(label='Sign In')
            if login:
                st.sidebar.error("Username or Password is incorrect. Please try again or create an account.")

        # 'Create Account' button
        signup_request = st.sidebar.button('Create Account', on_click=select_signup)

    return st.session_state.username, st.session_state.successful_login

#'''Funcionality------------------------------------------------------------------------------------------------------------- '''
def form_content(username):
    
    st.header('Input data')

    st.markdown('**1. Use custom data**')
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.dataframe(data=df, use_container_width=True)

    # Select example data
    st.markdown('**2. Use example data**')
    st.info("Coming soon...")

    # Download example data
    st.markdown('**3. Download example data**')
    st.info("Coming soon...")
    
    # Initiate the model building process
    if uploaded_file:  
        st.subheader('Model building')
        st.write('Model building in progress...')

        # Placeholder for model building process
        with st.spinner('Wait for it...'):
            time.sleep(5)

        st.write('Model building complete!')

        # Display model performance
        st.subheader('Model Processing')
        st.write('Building predictions...')

        # Placeholder for model performance metrics
        with st.spinner('Wait for it...'):
            time.sleep(3)

        st.markdown(''':blue[Customer predictions are now complete!]''')

#'''Main Function------------------------------------------------------------------------------------------------------------- '''
def main():
    # Initialize Session States.
    username, successful_login = login_app()

    st.title('Machine Learning App for Bank Churn Prediction')

    if successful_login == False:
        st.subheader("Please use the sidebar on the left to log in or create an account.")
        st.image('image1.png')
    else:
        with st.sidebar:             
            st.header(f"Welcome {username} !")
        
        form_content(username)

    with st.sidebar:
        with st.expander('About this app / Instructions'):
            st.markdown('**What can this app do?**')
            st.info('This app allows users to load a bank .csv file and use it to build a machine learning model to predict churn. The app also recommends actions to reduce churn.')

            st.markdown('**How to use the app?**')
            st.warning('To engage with the app, please login or create an account and then 1. Select a dataset and 2. Click on "Run the model". As a result, this would initiate the ML model and data processing.')

            st.markdown('**Under the hood**')
            st.markdown('Data sets:')
            st.code('''- You can upload your own dataset or use the example dataset provided in the app.''', language='markdown')

            st.markdown('Libraries used:')
            st.code('''* Pandas for data wrangling
* Scikit-learn
* XGBoost for machine learning
* Streamlit for user interface''', language='markdown')

# Call the main function
if __name__ == '__main__':
    main()
