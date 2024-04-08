
import streamlit as st
from datetime import datetime
import pandas as pd

from dotenv import load_dotenv, find_dotenv #Used for import the function to load .env file
import os
from pymongo import MongoClient #Used to create the connection
load_dotenv(find_dotenv()) #Shorcut to load the enviroment file

# Page title
st.set_page_config(page_title='Bank Churn App', 
                   page_icon='🤖', layout="wide", 
                   initial_sidebar_state="expanded")

st.title('🤖 ML Bank Churn Predictor')



# Connect to the DB.
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

def user_update(name, succesful_login):
    st.session_state.username = name
    st.session_state.succesful_login=succesful_login
    
def update_succesful_login(succesful_login):
    st.session_state.succesful_login=succesful_login

def login_app():
    db = connect_db()
    credentials_db=db["credentials"]

    
    # Initialize Session States.
    if 'username' not in st.session_state:
        st.session_state.username = ''
    if 'form' not in st.session_state:
        st.session_state.form = ''

    if 'succesful_login' not in st.session_state:
        st.session_state.succesful_login = False    
            
    if st.session_state.username != '':
        st.sidebar.write(f"You are logged in as {st.session_state.username.lower()}")   
        logout = st.sidebar.button(label='Log Out')
        if logout:
            # Handle Logout Click
            st.session_state.username = ''  # Set username to empty string
            st.session_state.succesful_login = False  # Set successful_login to False
            st.session_state.form = ''  # Reset form state
            st.sidebar.success("You have successfully logged out!")

   

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

#'''Funcionality------------------------------------------------------------------------------------------------------------- '''
def form_content(username):
    
    st.header('Input data')

    st.markdown('**Use custom data**')
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file, index_col=False)
    


    

def main():
    # Initialize Session States.
    succesful_login=False
    username, succesful_login=login_app()

    if succesful_login == False:        
        st.subheader("Please use the sidebar on the left to log in or create an account.")

    else:             
        st.header(f"Welcome {username} ")

        form_content(username)



# Call the main function
if __name__ == '__main__':
    main()