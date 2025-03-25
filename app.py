import streamlit as st
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from datetime import datetime
import re

# Set page configuration
st.set_page_config(page_title="Arkali-Labs", layout="centered")

# Initialize session state variables
if 'step' not in st.session_state:
    st.session_state.step = 'form'
if 'form_data' not in st.session_state:
    st.session_state.form_data = None

# Set up Google Sheets and Drive API
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
#creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
#client = gspread.authorize(creds)
# Retrieve credentials from secrets
creds_dict = st.secrets["gcp_service_account"]

# Create credentials from the dictionary
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)

# Authorize gspread client for Google Sheets
client = gspread.authorize(creds)

# Build the Drive API service
drive_service = build('drive', 'v3', credentials=creds)

# Google Sheets setup
try:
    sheet = client.open('Resumes').sheet1
except gspread.exceptions.SpreadsheetNotFound:
    st.error("Spreadsheet 'Resumes' not found. Please check the name or share it with the service account.")
    st.stop()

# Google Drive folder ID (replace with your actual folder ID)
FOLDER_ID = '1yROMWTu3ntmV9P0ehjKLnTq3ZlJ1xZbN'  # Update this with your Google Drive folder ID

# Custom CSS for styling and button alignment
st.markdown(
    """
    <style>
    /* Background gradient */
    .stApp {
        background: linear-gradient(to right, #e0f7fa, #80deea);
    }
    /* Center the title container */
    .title-container {
        text-align: center;
        margin: 20px 0;
    }
    /* Main title styling */
    .main-title {
        font-size: 24px;
        font-weight: 600;
        color: #1a1a1a;
        margin-bottom: 10px;
        line-height: 1.2;
    }
    /* Highlighted section */
    .highlight {
        font-size: 36px;
        font-weight: 700;
        color: #1a1a1a;
        margin-bottom: 10px;
        line-height: 1.2;
    }
    /* Subtitle styling */
    .subtitle {
        font-size: 16px;
        color: #4a4a4a;
        margin-bottom: 20px;
    }
    /* Responsive adjustments for title */
    @media (max-width: 600px) {
        .main-title {
            font-size: 18px;
        }
        .highlight {
            font-size: 28px;
        }
        .subtitle {
            font-size: 14px;
        }
    }
    @media (min-width: 1200px) {
        .main-title {
            font-size: 28px;
        }
        .highlight {
            font-size: 40px;
        }
    }
    /* Style the form container */
    .stForm {
        background-color: #ffffff;
        padding: 40px;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        max-width: 1000px;
        width: 90%;
        margin: 0 auto;
    }
    /* Style form inputs */
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 1px solid #d1d5db;
        padding: 12px;
        font-size: 16px;
        width: 100%;
    }
    /* Style form labels */
    .stTextInput > label, .stFileUploader > label {
        font-size: 16px;
        font-weight: 500;
        color: #1a1a1a;
        margin-bottom: 8px;
    }
    /* Style file uploader */
    .stFileUploader > div > div {
        border-radius: 8px;
        border: 1px dashed #d1d5db;
        padding: 30px;
        background-color: #f9fafb;
        font-size: 16px;
        width: 100%;
    }
    /* Style buttons generally */
    .stButton > button {
        background-color: #00796b;
        color: white;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 500;
        font-size: 16px;
        width: 100%;
        border: none;
    }
    .stButton > button:hover {
        background-color: #005a4f;
    }
    /* Responsive form adjustments */
    @media (max-width: 768px) {
        .stForm {
            padding: 25px;
            width: 95%;
        }
        .stTextInput > div > div > input {
            padding: 10px;
            font-size: 14px;
        }
        .stFileUploader > div > div {
            padding: 20px;
            font-size: 14px;
        }
        .stButton > button {
            padding: 10px 20px;
            font-size: 14px;
        }
    }
    @media (max-width: 480px) {
        .stForm {
            padding: 20px;
            width: 98%;
        }
    }
    /* Footer styling */
    .footer {
        text-align: center;
        padding: 20px 0;
        border-radius: 15px;
        background-color: rgba(255, 255, 255, 0.9);
        color: #4a4a4a;
        font-size: 14px;
        margin-top: auto;
        width: 100%;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Custom title and subtitle
st.markdown(
    """
    <div class="title-container">
        <div class="highlight">Unlock Your Career Potential! <br> AI Screening, Stand Out and Get Noticed by Top Employers!</div>
        <div class="main-title">Submit Your Resume for AI Screening <br> Get Noticed, Get Hired!</div>
        <div class="subtitle">Please fill in your details and upload your resume.</div>
    </div>
    """,
    unsafe_allow_html=True
)

# Create a container to manage display
container = st.container()

# Render the current step
def render_step():
    if st.session_state.step == 'form':
        with container:
            with st.form(key='user_form', clear_on_submit=True):
                name = st.text_input("Name", placeholder="Enter your full name", key='name')
                email = st.text_input("Email", placeholder="Enter your email address", key='email')
                location = st.text_input("Preferred Job Location", placeholder="e.g., New York, Remote", key='location')
                languages = st.text_input("Languages Known", placeholder="e.g., English, Spanish", help="Separate languages with commas.", key='languages')
                resume = st.file_uploader("Upload Resume", type=['pdf', 'docx', 'doc'], help="Accepted formats: PDF, DOCX, DOC", key='resume')

                submit = st.form_submit_button('Submit')

                if submit:
                    if all([name, email, location, languages, resume]):
                        if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                            st.error('Please enter a valid email address.')
                        else:
                            # Generate a unique file name
                            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                            file_extension = resume.name.split('.')[-1]
                            file_name = f"{name.replace(' ', '_')}_{timestamp}.{file_extension}"
                            temp_file_path = f"temp_{file_name}"

                            # Save file temporarily to disk
                            with open(temp_file_path, 'wb') as f:
                                f.write(resume.getbuffer())

                            try:
                                with st.spinner('Uploading to Google Drive and updating...'):
                                    # Upload to Google Drive
                                    file_metadata = {
                                        'name': file_name,
                                        'parents': [FOLDER_ID]
                                    }
                                    media = MediaFileUpload(temp_file_path)
                                    uploaded_file = drive_service.files().create(
                                        body=file_metadata,
                                        media_body=media,
                                        fields='id, webViewLink'
                                    ).execute()
                                    file_url = uploaded_file.get('webViewLink')

                                    # Update Google Sheet
                                    sheet.append_row([name, email, location, languages, file_url])

                                # Store form data and advance step
                                st.session_state.form_data = {
                                    'name': name,
                                    'email': email,
                                    'location': location,
                                    'languages': languages,
                                    'resume_url': file_url
                                }
                                st.session_state.step = 'submitted'
                                st.rerun()  # Rerun to update UI immediately
                            except Exception as e:
                                st.error(f'An error occurred: {e}')
                            finally:
                                if os.path.exists(temp_file_path):
                                    os.remove(temp_file_path)
                    else:
                        st.error('Please fill all fields and upload a resume.')

    elif st.session_state.step == 'submitted':
        with container:
            st.success('Resume submitted successfully! ')
            st.warning('Get AI insights to enhance your resume and increase your chances of getting hired! $3.99 only')
            if st.button('Get AI Insights(Paid) - Coming soon'):
                #st.session_state.step = 'payment_prompt' ##uncomment to enable payment prompt
                st.rerun()  # Rerun to update UI immediately
            if st.button('Submit Another'):
                st.session_state.step = 'form'
                st.session_state.form_data = None
                st.rerun()  # Rerun to update UI immediately

    elif st.session_state.step == 'payment_prompt':
        with container:
            st.write("This is a paid service. Please proceed to payment to complete your transaction. ")
            st.write("The cost for this service is $3.99. ")
            st.markdown("**Payment Instructions:**")
            st.markdown("1. Click the 'Proceed to Payment' button below.")
            st.markdown("2. You will be redirected to a secure payment gateway.")
            st.markdown("3. Complete the payment process.")
            st.markdown("4. Your AI insights will be emailed.")
            st.warning("If you have any questions or need assistance with the payment process, feel free to contact our support team. Your purchase will be processed securely, and you'll receive a confirmation email once the transaction is complete.")
            if st.button("Proceed to Payment"):
                st.session_state.step = 'payment_simulation'
                st.rerun()  # Rerun to update UI immediately

    elif st.session_state.step == 'payment_simulation':
        with container:
            st.write("**Payment Gateway Simulation**")
            st.write("Imagine this as a secure payment page (e.g., Stripe or PayPal).")
            if st.button("Pay Now"):
                st.session_state.step = 'payment_success'
                st.rerun()  # Rerun to update UI immediately

    elif st.session_state.step == 'payment_success':
        with container:
            st.write("**Payment Successful!**")
            st.write("Here are your AI insights: [Placeholder for AI-generated insights based on your input]")
            if st.button("Back to Form"):
                st.session_state.step = 'form'
                st.session_state.form_data = None
                st.rerun()  # Rerun to update UI immediately

# Render the current step
render_step()

# Footer
st.markdown(
    """
    <div class="footer">
        © 2025 Arkali-Labs. All rights reserved.
    </div>
    """,
    unsafe_allow_html=True
)
