from importlib import import_module
import streamlit as st
import os
from pymongo import MongoClient
from datetime import datetime


# Page title
st.set_page_config(page_title='Bank Churn App', 
                   page_icon='🤖', layout="wide", 
                   initial_sidebar_state="expanded")

st.title('🤖 ML Bank Churn Predictor + Recomendations')


# Connect to the DB.
@st.cache_resource

def connect_db():
    #password = os.environ.get("MONGODB_PWD") #This is to grab the password from the .env file
    #connection_string = f"mongodb+srv://carlosmebratt:{password}@bdm1003.tnmvwtl.mongodb.net/?retryWrites=true&w=majority"

    # connection_string = f"mongodb+srv://carlosmebratt:ebratt1986@bdm1003.tnmvwtl.mongodb.net/?retryWrites=true&w=majority"
    # client = MongoClient(connection_string)
    # db=client["bankchurnapp"]

   

    try:
        from pathlib import Path
        config_path = Path(".streamlit/secrets.toml")  # Replace with the actual path
        secrets = import_module(config_path.name)
    except ModuleNotFoundError:
        st.error("Error: Could not find secrets.toml file. Please create one with your MongoDB credentials.")
        exit()

    mongo_username = secrets.mongo_username
    mongo_password = secrets.mongo_password
    mongo_cluster_name = secrets.mongo_cluster_name

    connection_string = f"mongodb+srv://{mongo_username}:{mongo_password}@{mongo_cluster_name}.mongodb.net/?retryWrites=true&w=majority" 

    try:
        client = MongoClient(connection_string)
        db = client.your_database_name  # Replace with your database name
        st.success("Connected to MongoDB successfully!")
    except Exception as e:
        st.error(f"Error connecting to MongoDB: {e}")
        exit()

    return db


def select_signup():
    st.session_state.form = 'signup_form'

def user_update(name, succesful_login):
    st.session_state.username = name
    st.session_state.succesful_login=succesful_login
    
def update_succesful_login(succesful_login):
    st.session_state.succesful_login=succesful_login

def login_app():
    db = connect_db()
    credentials_db=db["credentials"]

    #st.session_state.succesful_login=False
    # Initialize Session States.
    if 'username' not in st.session_state:
        st.session_state.username = ''
    if 'form' not in st.session_state:
        st.session_state.form = ''

    if 'succesful_login' not in st.session_state:
        st.session_state.succesful_login = False    
            
    if st.session_state.username != '':
        st.sidebar.write(f"You are logged in as {st.session_state.username.lower()}")
        

   

    # Initialize Sing In or Sign Up forms
    if st.session_state.form == 'signup_form' and st.session_state.username == '':
    
        signup_form = st.sidebar.form(key='signup_form', clear_on_submit=True)
        new_username = signup_form.text_input(label='Enter Username*')
        new_user_email = signup_form.text_input(label='Enter Email Address*')
        new_user_pas = signup_form.text_input(label='Enter Password*', type='password')
        user_pas_conf = signup_form.text_input(label='Confirm Password*', type='password')
        note = signup_form.markdown('**required fields*')
        signup = signup_form.form_submit_button(label='Sign Up')
        
        if signup:
            if '' in [new_username, new_user_email, new_user_pas]:
                st.sidebar.error('Some fields are missing')
            else:
                if credentials_db.find_one({'username' : new_username}):
                    st.sidebar.error('This username already exists')
                if credentials_db.find_one({'email' : new_user_email}):
                    st.sidebar.error('This e-mail is already registered')
                else:
                    if new_user_pas != user_pas_conf:
                        st.sidebar.error('Passwords do not match')
                    else:
                        user_update(new_username,True)
                        credentials_db.insert_one({'username' : new_username, 
                                                'email' : new_user_email, 
                                                'password' : new_user_pas,
                                                "creation_time":datetime.now()})
                        st.sidebar.success('You have successfully registered!')
                        #st.sidebar.success(f"You are logged in as {new_username.upper()}")
                        
                        login_form = st.sidebar.form(key='signin_form', clear_on_submit=True)
                        username = login_form.text_input(label='Enter Username')
                        password = login_form.text_input(label='Enter Password', type='password')
                        
                        del new_user_pas, user_pas_conf
                        
    
    
    elif st.session_state.username == '':
        login_form = st.sidebar.form(key='signin_form', clear_on_submit=True)
        username = login_form.text_input(label='Enter Username')
        password = login_form.text_input(label='Enter Password', type='password')
        
        

        if credentials_db.find_one({'username' : username, 'password' : password}):
            login = login_form.form_submit_button(label='Sign In', on_click=user_update(username,True))
            if login:
                st.sidebar.success(f"You are logged in as {username.upper()}")
                
                
                del password
        else:
            login = login_form.form_submit_button(label='Sign In')
            if login:
                st.sidebar.error("Username or Password is incorrect. Please try again or create an account.")

        
    else:
        logout = st.sidebar.button(label='Log Out')
        if logout:
            user_update('',False)
            st.session_state.form = ''

       

    # 'Create Account' button
    if st.session_state.username == "" and st.session_state.form != 'signup_form':
        signup_request = st.sidebar.button('Create Account', on_click=select_signup)
    
    

    return st.session_state.username, st.session_state.succesful_login




def main():
    # Initialize Session States.
    succesful_login=False
    username, succesful_login=login_app()

    if succesful_login ==False:
        
        st.title("Hello user. If you haven't log in yet, please use the sidebar on the left to do so")

    else:     
        
        st.title(f"Welcome {username} to your personal dashboard ")

        

if __name__ == '__main__':
    main()
