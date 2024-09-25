import streamlit as st
import pandas as pd
import plotly.express as px
import os
import json

# Load user data from JSON file
if os.path.exists('users.json'):
    with open('users.json', 'r') as f:
        user_data = json.load(f)
else:
    user_data = {}

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'email' not in st.session_state:
    st.session_state.email = ''
if 'page' not in st.session_state:
    st.session_state.page = 'Login'

# Sidebar navigation
st.sidebar.title("Navigation")
if st.session_state.logged_in:
    # Show only the relevant pages after login
    page = st.sidebar.radio("Go to", ["Marks Entry", "Reports"])
else:
    # Show Sign Up and Login options if not logged in
    page = st.sidebar.radio("Go to", ["Sign Up", "Login"])

# Sign Up Page
if page == "Sign Up":
    st.title("Sign Up Page")
    name = st.text_input("Name")
    phone = st.text_input("Phone")
    dob = st.date_input("DOB")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Sign Up"):
        if email in user_data:
            st.error("User with this email already exists. Please log in.")
        else:
            user_data[email] = {"name": name, "phone": phone, "dob": str(dob), "password": password, "marks": []}
            with open('users.json', 'w') as f:
                json.dump(user_data, f)
            os.makedirs(email, exist_ok=True)  # Create a folder for the user
            st.success("Account created successfully. Please log in.")
            st.session_state.logged_in = True
            st.session_state.email = email
            st.session_state.page = 'Marks Entry'
            st.experimental_rerun()  # Rerun to redirect to the Marks Entry page

# Login Page
if page == "Login" and not st.session_state.logged_in:
    st.title("Login Page")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if email in user_data and user_data[email]['password'] == password:
            st.success(f"Welcome {user_data[email]['name']}!")
            st.session_state.logged_in = True
            st.session_state.email = email
            st.session_state.page = 'Marks Entry'
            st.experimental_rerun()  # Rerun to redirect to the Marks Entry page
        else:
            st.error("Invalid email or password. Please try again.")

# Marks Entry Page (only accessible if logged in)
if st.session_state.logged_in and st.session_state.page == "Marks Entry":
    st.title("Marks Entry Page")
    email = st.session_state.email

    st.write("Enter your marks for the subjects:")
    subjects = ["Maths", "Science", "English", "History", "Geography", "Physics", "Chemistry"]
    marks = []

    for subject in subjects:
        marks.append(st.slider(f"Choose your marks for {subject}", 0, 100, 50))

    if st.button("Submit"):
        user_data[email]['marks'] = marks
        with open('users.json', 'w') as f:
            json.dump(user_data, f)

        # Save marks to CSV
        marks_df = pd.DataFrame({
            'Subject': subjects,
            'Marks': marks
        })
        marks_df.to_csv(f"{email}/marks.csv", index=False)
        st.success("Marks saved successfully!")

# Reports Page (only accessible if logged in)
if st.session_state.logged_in and page == "Reports":
    st.title("Your Reports are Ready!")
    email = st.session_state.email

    if os.path.exists(f"{email}/marks.csv"):
        marks_df = pd.read_csv(f"{email}/marks.csv")

        # Average Marks Chart - Bar Graph
        avg_marks = marks_df['Marks'].mean()
        st.write("Average Marks Chart")
        fig_bar = px.bar(marks_df, x='Subject', y='Marks', title="Marks per Subject")
        st.plotly_chart(fig_bar)

        # Marks as per each subject - Line Graph
        st.write("Marks as per each subject - Line Graph")
        fig_line = px.line(marks_df, x='Subject', y='Marks', title="Marks per Subject (Line Graph)")
        st.plotly_chart(fig_line)

        # Marks as per each subject - Pie Chart
        st.write("Marks as per each subject - Pie Chart")
        fig_pie = px.pie(marks_df, names='Subject', values='Marks', title="Marks Distribution")
        st.plotly_chart(fig_pie)
    else:
        st.warning("No marks data found. Please enter marks first.")

# If not logged in, restrict access to Marks Entry and Reports
if not st.session_state.logged_in and (page == "Marks Entry" or page == "Reports"):
    st.warning("Please log in to access this page.")