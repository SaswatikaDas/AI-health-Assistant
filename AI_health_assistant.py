import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import joblib
import requests
import json
from datetime import datetime
import speech_recognition as sr
import pyttsx3
import threading
import time
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import googletrans
from googletrans import Translator

# Configure page with dark theme
st.set_page_config(
    page_title="🏥 AI Health Assistant",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark theme CSS
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Variables */
    :root {
        --primary-bg: #0a0a0a;
        --secondary-bg: #1a1a1a;
        --card-bg: #252525;
        --accent-color: #00d4ff;
        --accent-hover: #00b8e6;
        --text-primary: #ffffff;
        --text-secondary: #b3b3b3;
        --border-color: #333333;
        --success-color: #00ff88;
        --warning-color: #ffaa00;
        --error-color: #ff4444;
        --gradient-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --gradient-accent: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%);
        --shadow: 0 8px 32px rgba(0, 212, 255, 0.1);
    }
    
    /* Main App Background */
    .stApp {
        background: var(--primary-bg);
        color: var(--text-primary);
        font-family: 'Inter', sans-serif;
    }
    
    /* Sidebar Styling */
    .css-1d391kg { /* This might need adjustment based on Streamlit's internal class names */
        background: var(--secondary-bg);
        border-right: 2px solid var(--border-color);
    }
    
    /* Headers and Text */
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-primary) !important;
        font-weight: 600;
    }
    
    .stMarkdown {
        color: var(--text-primary);
    }
    
    /* Input Fields */
    .stTextInput > div > div > input {
        background: var(--card-bg) !important;
        border: 2px solid var(--border-color) !important;
        border-radius: 12px !important;
        color: var(--text-primary) !important;
        padding: 12px 16px !important;
        font-size: 16px !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: var(--accent-color) !important;
        box-shadow: 0 0 0 3px rgba(0, 212, 255, 0.1) !important;
    }
    
    /* Buttons */
    .stButton > button {
        background: var(--gradient-accent) !important;
        border: none !important;
        border-radius: 12px !important;
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        padding: 12px 24px !important;
        transition: all 0.3s ease !important;
        box-shadow: var(--shadow) !important;
        font-size: 14px !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 12px 40px rgba(0, 212, 255, 0.2) !important;
    }
    
    /* Select Boxes */
    .stSelectbox > div > div {
        background: var(--card-bg) !important;
        border: 2px solid var(--border-color) !important;
        border-radius: 12px !important;
    }
    
    /* Checkboxes */
    .stCheckbox {
        color: var(--text-primary) !important;
    }
    
    /* Main Header */
    .main-header {
        background: var(--gradient-primary);
        padding: 3rem 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: var(--shadow);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: pulse 4s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 0.5; }
        50% { opacity: 0.8; }
    }
    
    /* Chat Container */
    .chat-container {
        background: var(--secondary-bg);
        border: 2px solid var(--border-color);
        border-radius: 16px;
        padding: 20px;
        margin: 20px 0;
        max-height: 500px;
        overflow-y: auto;
        box-shadow: var(--shadow);
    }
    
    .chat-container::-webkit-scrollbar {
        width: 8px;
    }
    
    .chat-container::-webkit-scrollbar-track {
        background: var(--card-bg);
        border-radius: 4px;
    }
    
    .chat-container::-webkit-scrollbar-thumb {
        background: var(--accent-color);
        border-radius: 4px;
    }
    
    /* Chat Messages */
    .chat-message {
        padding: 16px 20px;
        border-radius: 16px;
        margin: 16px 0;
        box-shadow: 0 4px 16px rgba(0,0,0,0.3);
        animation: slideIn 0.3s ease-out;
        position: relative;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .user-message {
        background: linear-gradient(135deg, var(--accent-color) 0%, #0099cc 100%);
        margin-left: 60px;
        margin-right: 20px;
        color: white;
    }
    
    .bot-message {
        background: var(--card-bg);
        margin-right: 60px;
        margin-left: 20px;
        border: 1px solid var(--border-color);
        color: var(--text-primary);
    }
    
    /* Cards */
    .info-card {
        background: var(--card-bg);
        border: 2px solid var(--border-color);
        border-radius: 16px;
        padding: 24px;
        margin: 16px 0;
        box-shadow: var(--shadow);
        transition: all 0.3s ease;
    }
    
    .info-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(0, 212, 255, 0.15);
        border-color: var(--accent-color);
    }
    
    /* Symptom Buttons */
    .symptom-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 12px;
        margin: 20px 0;
    }
    
    .symptom-button {
        background: var(--card-bg) !important;
        border: 2px solid var(--border-color) !important;
        border-radius: 12px !important;
        padding: 12px 16px !important;
        color: var(--text-primary) !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
        text-align: center !important;
        cursor: pointer !important;
    }
    
    .symptom-button:hover {
        background: var(--accent-color) !important;
        border-color: var(--accent-color) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 24px rgba(0, 212, 255, 0.3) !important;
    }
    
    /* Emergency Section */
    .emergency-section {
        background: linear-gradient(135deg, #ff4444 0%, #cc0000 100%);
        border-radius: 16px;
        padding: 20px;
        margin: 20px 0;
        text-align: center;
        color: white;
        box-shadow: 0 8px 32px rgba(255, 68, 68, 0.2);
    }
    
    /* Success/Warning/Error Messages */
    .stSuccess {
        background: rgba(0, 255, 136, 0.1) !important;
        border: 1px solid var(--success-color) !important;
        border-radius: 12px !important;
        color: var(--success-color) !important;
    }
    
    .stWarning {
        background: rgba(255, 170, 0, 0.1) !important;
        border: 1px solid var(--warning-color) !important;
        border-radius: 12px !important;
        color: var(--warning-color) !important;
    }
    
    .stError {
        background: rgba(255, 68, 68, 0.1) !important;
        border: 1px solid var(--error-color) !important;
        border-radius: 12px !important;
        color: var(--error-color) !important;
    }
    
    /* Metrics */
    .metric-card {
        background: var(--card-bg);
        border: 2px solid var(--border-color);
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        border-color: var(--accent-color);
        transform: translateY(-2px);
    }
    
    /* Loading Spinner */
    .stSpinner {
        color: var(--accent-color) !important;
    }
    
    /* Footer */
    .footer {
        background: var(--secondary-bg);
        border-top: 2px solid var(--border-color);
        padding: 20px;
        margin-top: 40px;
        text-align: center;
        color: var(--text-secondary);
        border-radius: 16px 16px 0 0;
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .main-header {
            padding: 2rem 1rem;
        }
        
        .chat-message {
            margin-left: 10px !important;
            margin-right: 10px !important;
        }
        
        .symptom-grid {
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'model' not in st.session_state:
    st.session_state.model = None
if 'symptoms_encoder' not in st.session_state:
    st.session_state.symptoms_encoder = None
if 'current_language' not in st.session_state:
    st.session_state.current_language = 'en'
if 'user_location' not in st.session_state:
    st.session_state.user_location = None
if 'message_counter' not in st.session_state:
    st.session_state.message_counter = 0
if 'last_input' not in st.session_state:
    st.session_state.last_input = ""
if 'diagnosis_history' not in st.session_state:
    st.session_state.diagnosis_history = []
if 'conversation_state' not in st.session_state:
    st.session_state.conversation_state = 'initial_greeting' # States: 'initial_greeting', 'awaiting_symptoms', 'asking_follow_up', 'diagnosed'
if 'current_symptoms_being_analyzed' not in st.session_state:
    st.session_state.current_symptoms_being_analyzed = []
if 'follow_up_question_index' not in st.session_state:
    st.session_state.follow_up_question_index = 0
if 'predicted_disease_for_follow_up' not in st.session_state:
    st.session_state.predicted_disease_for_follow_up = None

# Language options
LANGUAGES = {
    'en': 'English 🇺🇸',
    'es': 'Español 🇪🇸', 
    'fr': 'Français 🇫🇷',
    'de': 'Deutsch 🇩🇪',
    'hi': 'हिंदी 🇮�',
    'zh': '中文 🇨🇳',
    'ar': 'العربية 🇸🇦',
    'pt': 'Português 🇵🇹',
    'ru': 'Русский 🇷🇺',
    'ja': '日本語 🇯🇵',
    'bn': 'বাংলা 🇧🇩',
    'te': 'తెలుగు 🇮🇳',
    'ta': 'தமிழ் 🇮🇳',
    'mr': 'ମରାଠୀ 🇮🇳', # Updated Marathi for consistency
    'gu': 'ગુજરાતી 🇮🇳',
    'or': 'ଓଡ଼ିଆ 🇮🇳' # Added Odia
}

# Emergency contacts
EMERGENCY_CONTACTS = {
    'en': {
        'ambulance': {'number': '108', 'name': 'Ambulance'},
        'police': {'number': '100', 'name': 'Police'},
        'fire': {'number': '101', 'name': 'Fire Department'},
        'women_helpline': {'number': '1091', 'name': 'Women Helpline'},
        'child_helpline': {'number': '1098', 'name': 'Child Helpline'},
        'senior_citizen': {'number': '14567', 'name': 'Senior Citizen Helpline'},
        'mental_health': {'number': '+91-9152987821', 'name': 'Mental Health Helpline'},
        'covid_helpline': {'number': '1075', 'name': 'COVID-19 Helpline'}
    }
}

# Medical recommendations database
MEDICAL_RECOMMENDATIONS = {
    'Fungal infection': {
        'severity': 'mild',
        'tests': ['KOH Test', 'Fungal Culture', 'Skin Scraping'],
        'medicines': ['Antifungal cream (Clotrimazole)', 'Oral antifungals if severe', 'Keep area dry'],
        'precautions': ['Maintain hygiene', 'Avoid moisture', 'Use antifungal powder'],
        'doctor_required': False,
        'follow_up_questions': [
            "How long have you had the rash?",
            "Is the rash itchy or painful?",
            "Have you used any creams or treatments for it already?"
        ]
    },
    'Allergy': {
        'severity': 'mild',
        'tests': ['Allergy Test Panel', 'IgE levels', 'Skin Prick Test'],
        'medicines': ['Antihistamines (Cetirizine)', 'Avoid allergens', 'Use air purifiers'],
        'precautions': ['Identify triggers', 'Maintain clean environment', 'Carry emergency medication'],
        'doctor_required': False,
        'follow_up_questions': [
            "What kind of allergic reaction are you experiencing (e.g., skin rash, sneezing, swelling)?",
            "When did these symptoms start, and do they occur at specific times or after exposure to certain things?",
            "Have you been exposed to any new foods, medications, or environmental factors recently?"
        ]
    },
    'GERD': {
        'severity': 'moderate',
        'tests': ['Upper GI Endoscopy', 'pH monitoring', 'Barium swallow'],
        'medicines': ['Proton pump inhibitors', 'H2 blockers', 'Antacids'],
        'precautions': ['Avoid spicy foods', 'Eat smaller meals', 'Elevate head while sleeping'],
        'doctor_required': True,
        'follow_up_questions': [
            "How often do you experience heartburn or acid reflux?",
            "Do your symptoms worsen after eating certain foods or lying down?",
            "Have you noticed any difficulty swallowing or unexplained weight loss?"
        ]
    },
    'Chronic cholestasis': {
        'severity': 'severe',
        'tests': ['Liver Function Tests', 'MRCP', 'Liver Biopsy', 'Ultrasound'],
        'medicines': ['Ursodeoxycholic acid', 'Cholestyramine', 'Fat-soluble vitamins'],
        'precautions': ['Low-fat diet', 'Regular monitoring', 'Avoid alcohol'],
        'doctor_required': True,
        'follow_up_questions': [
            "Have you experienced yellowing of your skin or eyes (jaundice)?",
            "Are you experiencing dark urine or pale stools?",
            "Do you have persistent itching, especially at night?"
        ]
    },
    'Drug Reaction': {
        'severity': 'moderate',
        'tests': ['Complete Blood Count', 'Liver Function Test', 'Allergy Testing'],
        'medicines': ['Discontinue offending drug', 'Antihistamines', 'Corticosteroids if severe'],
        'precautions': ['Identify causative drug', 'Inform all healthcare providers', 'Carry allergy card'],
        'doctor_required': True,
        'follow_up_questions': [
            "What medication did you recently take before the reaction started?",
            "How quickly did the reaction appear after taking the medication?",
            "Are you experiencing any difficulty breathing or swelling of the face/throat?"
        ]
    },
    'Peptic ulcer diseae': {
        'severity': 'moderate',
        'tests': ['H. pylori test', 'Upper GI Endoscopy', 'CT scan if complications'],
        'medicines': ['Proton pump inhibitors', 'Antibiotics for H. pylori', 'Avoid NSAIDs'],
        'precautions': ['Avoid spicy foods', 'Quit smoking', 'Limit alcohol'],
        'doctor_required': True,
        'follow_up_questions': [
            "Where exactly is the pain located in your abdomen?",
            "Does the pain improve or worsen after eating?",
            "Have you experienced black, tarry stools or vomiting blood?"
        ]
    },
    'AIDS': {
        'severity': 'severe',
        'tests': ['HIV test', 'CD4 count', 'Viral load', 'Opportunistic infection screening'],
        'medicines': ['Antiretroviral therapy (ART)', 'Prophylactic medications', 'Nutritional supplements'],
        'precautions': ['Safe practices', 'Regular monitoring', 'Healthy lifestyle'],
        'doctor_required': True,
        'follow_up_questions': [
            "Have you experienced unexplained weight loss, chronic fatigue, or persistent fever?",
            "Have you noticed swollen lymph nodes in your neck, armpits, or groin?",
            "Have you had any recent opportunistic infections like severe thrush or pneumonia?"
        ]
    },
    'Diabetes': {
        'severity': 'chronic',
        'tests': ['HbA1c', 'Fasting glucose', 'OGTT', 'Lipid profile'],
        'medicines': ['Metformin', 'Insulin if needed', 'Blood pressure medications'],
        'precautions': ['Diet control', 'Regular exercise', 'Monitor blood sugar'],
        'doctor_required': True,
        'follow_up_questions': [
            "Are you experiencing increased thirst, frequent urination, or unexplained weight loss?",
            "Do you have blurred vision, slow-healing sores, or frequent infections?",
            "Is there a family history of diabetes?"
        ]
    },
    'Gastroenteritis': {
        'severity': 'mild',
        'tests': ['Stool examination', 'Blood tests if dehydrated'],
        'medicines': ['ORS', 'Probiotics', 'Anti-diarrheal if needed'],
        'precautions': ['Stay hydrated', 'Bland diet', 'Good hygiene'],
        'doctor_required': False,
        'follow_up_questions': [
            "How many times have you had diarrhea or vomiting in the last 24 hours?",
            "Are you experiencing any fever or severe abdominal cramps?",
            "Have you consumed any suspicious food or water recently?"
        ]
    },
    'Bronchial Asthma': {
        'severity': 'chronic',
        'tests': ['Spirometry', 'Peak flow measurement', 'Chest X-ray', 'Allergy tests'],
        'medicines': ['Bronchodilators', 'Inhaled corticosteroids', 'Rescue inhalers'],
        'precautions': ['Avoid triggers', 'Use inhalers correctly', 'Regular monitoring'],
        'doctor_required': True,
        'follow_up_questions': [
            "How often do you experience shortness of breath, wheezing, or coughing?",
            "Do your symptoms worsen at night or with exercise?",
            "Have you been diagnosed with asthma before, and if so, are you using an inhaler?"
        ]
    },
    'Hypertension': {
        'severity': 'chronic',
        'tests': ['Blood pressure monitoring', 'ECG', 'Echocardiogram', 'Kidney function tests'],
        'medicines': ['ACE inhibitors', 'Beta blockers', 'Diuretics'],
        'precautions': ['Low sodium diet', 'Regular exercise', 'Weight management'],
        'doctor_required': True,
        'follow_up_questions': [
            "Have you had your blood pressure checked recently, and what were the readings?",
            "Do you experience frequent headaches, dizziness, or blurred vision?",
            "Is there a family history of high blood pressure or heart disease?"
        ]
    },
    'Migraine': {
        'severity': 'moderate',
        'tests': ['Clinical diagnosis', 'MRI if atypical', 'Blood tests to rule out other causes'],
        'medicines': ['Triptans', 'NSAIDs', 'Preventive medications'],
        'precautions': ['Identify triggers', 'Regular sleep', 'Stress management'],
        'doctor_required': True,
        'follow_up_questions': [
            "Describe the nature of your headache (e.g., throbbing, pulsating, sharp).",
            "Do you experience any aura (visual disturbances, numbness) before the headache starts?",
            "Are your headaches accompanied by nausea, vomiting, or sensitivity to light/sound?"
        ]
    },
    'Cervical spondylosis': {
        'severity': 'moderate',
        'tests': ['X-ray cervical spine', 'MRI', 'CT scan'],
        'medicines': ['NSAIDs', 'Muscle relaxants', 'Physical therapy'],
        'precautions': ['Good posture', 'Neck exercises', 'Ergonomic workplace'],
        'doctor_required': True,
        'follow_up_questions': [
            "Are you experiencing neck pain that radiates to your arms or shoulders?",
            "Do you have numbness, tingling, or weakness in your hands or arms?",
            "Does your pain worsen with certain neck movements or positions?"
        ]
    },
    'Dengue': {
        'severity': 'severe',
        'tests': ['Dengue NS1 Antigen Test', 'IgM/IgG Antibody Test', 'Complete Blood Count (CBC)'],
        'medicines': ['Paracetamol for fever', 'Fluid and electrolyte management', 'Avoid NSAIDs'],
        'precautions': ['Mosquito bite prevention', 'Rest', 'Hydration'],
        'doctor_required': True,
        'follow_up_questions': [
            "How high is your fever, and how long has it lasted?",
            "Are you experiencing severe headache, pain behind the eyes, or joint and muscle pain?",
            "Have you noticed any skin rash, easy bruising, or bleeding from the gums or nose?"
        ]
    },
    'Malaria': {
        'severity': 'severe',
        'tests': ['Peripheral Blood Smear', 'Rapid Diagnostic Test (RDT)'],
        'medicines': ['Antimalarial drugs (e.g., Artemisinin-based Combination Therapies)'],
        'precautions': ['Mosquito bite prevention', 'Complete full course of medication'],
        'doctor_required': True,
        'follow_up_questions': [
            "Do you experience recurrent cycles of fever, chills, and sweating?",
            "Have you recently traveled to a malaria-endemic area?",
            "Are you experiencing nausea, vomiting, or headache along with fever?"
        ]
    },
    'Typhoid': {
        'severity': 'moderate',
        'tests': ['Blood Culture (Widal Test)', 'Stool Culture'],
        'medicines': ['Antibiotics (e.g., Ciprofloxacin, Azithromycin)', 'Fluid and electrolyte management'],
        'precautions': ['Maintain hygiene', 'Drink safe water', 'Avoid raw foods'],
        'doctor_required': True,
        'follow_up_questions': [
            "Have you had a prolonged high fever, often gradually increasing?",
            "Are you experiencing headache, weakness, fatigue, or loss of appetite?",
            "Have you noticed any abdominal pain, constipation, or diarrhea?"
        ]
    },
    'Common Cold': {
        'severity': 'mild',
        'tests': ['Clinical diagnosis'],
        'medicines': ['Pain relievers (e.g., Ibuprofen)', 'Decongestants', 'Cough syrup'],
        'precautions': ['Rest', 'Hydration', 'Hand hygiene'],
        'doctor_required': False,
        'follow_up_questions': [
            "Are your symptoms mainly runny nose, sore throat, and sneezing?",
            "Do you have a mild cough or congestion?",
            "How long have you been experiencing these symptoms?"
        ]
    },
    'Pneumonia': {
        'severity': 'severe',
        'tests': ['Chest X-ray', 'Sputum Culture', 'Blood tests'],
        'medicines': ['Antibiotics (for bacterial pneumonia)', 'Antivirals (for viral pneumonia)', 'Oxygen therapy'],
        'precautions': ['Vaccination', 'Avoid smoking', 'Good hygiene'],
        'doctor_required': True,
        'follow_up_questions': [
            "Are you experiencing a severe cough with phlegm, shortness of breath, or chest pain?",
            "Do you have a high fever and chills?",
            "Have you been feeling unusually weak or fatigued?"
        ]
    },
    'Jaundice': {
        'severity': 'moderate',
        'tests': ['Liver Function Tests (LFTs)', 'Bilirubin levels', 'Hepatitis panel', 'Ultrasound abdomen'],
        'medicines': ['Treatment depends on underlying cause', 'Supportive care'],
        'precautions': ['Avoid alcohol', 'Healthy diet'],
        'doctor_required': True,
        'follow_up_questions': [
            "Have you noticed yellowing of your skin or the whites of your eyes?",
            "Are your urine dark and stools pale?",
            "Do you have any abdominal pain or itching?"
        ]
    },
    'Chicken pox': {
        'severity': 'moderate',
        'tests': ['Clinical diagnosis'],
        'medicines': ['Antiviral medication (Acyclovir) if severe', 'Antihistamines for itching', 'Calamine lotion'],
        'precautions': ['Isolation to prevent spread', 'Avoid scratching', 'Hydration'],
        'doctor_required': True,
        'follow_up_questions': [
            "Have you developed an itchy rash that turned into fluid-filled blisters?",
            "Did you have a fever, headache, or loss of appetite before the rash appeared?",
            "Have you been in contact with someone who has chickenpox recently?"
        ]
    },
    'Dengue fever': { # Alias for Dengue, to catch variations
        'severity': 'severe',
        'tests': ['Dengue NS1 Antigen Test', 'IgM/IgG Antibody Test', 'Complete Blood Count (CBC)'],
        'medicines': ['Paracetamol for fever', 'Fluid and electrolyte management', 'Avoid NSAIDs'],
        'precautions': ['Mosquito bite prevention', 'Rest', 'Hydration'],
        'doctor_required': True,
        'follow_up_questions': [
            "How high is your fever, and how long has it lasted?",
            "Are you experiencing severe headache, pain behind the eyes, or joint and muscle pain?",
            "Have you noticed any skin rash, easy bruising, or bleeding from the gums or nose?"
        ]
    },
    'Typhoid fever': { # Alias for Typhoid
        'severity': 'moderate',
        'tests': ['Blood Culture (Widal Test)', 'Stool Culture'],
        'medicines': ['Antibiotics (e.g., Ciprofloxacin, Azithromycin)', 'Fluid and electrolyte management'],
        'precautions': ['Maintain hygiene', 'Drink safe water', 'Avoid raw foods'],
        'doctor_required': True,
        'follow_up_questions': [
            "Have you had a prolonged high fever, often gradually increasing?",
            "Are you experiencing headache, weakness, fatigue, or loss of appetite?",
            "Have you noticed any abdominal pain, constipation, or diarrhea?"
        ]
    },
    'Hepatitis A': {
        'severity': 'moderate',
        'tests': ['Hepatitis A IgM Antibody Test', 'Liver Function Tests'],
        'medicines': ['Supportive care', 'Rest', 'Hydration'],
        'precautions': ['Hand hygiene', 'Vaccination', 'Avoid contaminated food/water'],
        'doctor_required': True,
        'follow_up_questions': [
            "Have you experienced fatigue, nausea, vomiting, or abdominal pain?",
            "Have you noticed yellowing of your skin or eyes, or dark urine?",
            "Have you consumed any potentially contaminated food or water recently?"
        ]
    },
    'Hepatitis B': {
        'severity': 'severe',
        'tests': ['Hepatitis B Surface Antigen (HBsAg)', 'Hepatitis B e-Antigen (HBeAg)', 'Liver Function Tests', 'Viral load'],
        'medicines': ['Antiviral medications (for chronic cases)', 'Liver transplant (in severe cases)'],
        'precautions': ['Vaccination', 'Safe practices', 'Regular monitoring'],
        'doctor_required': True,
        'follow_up_questions': [
            "Have you experienced fatigue, nausea, vomiting, or abdominal pain?",
            "Have you noticed yellowing of your skin or eyes, or dark urine?",
            "Do you have any risk factors for Hepatitis B exposure (e.g., unsafe injections, unprotected sex)?"
        ]
    },
    'Hepatitis C': {
        'severity': 'severe',
        'tests': ['Hepatitis C Antibody Test', 'HCV RNA Test', 'Liver Function Tests', 'Liver biopsy'],
        'medicines': ['Direct-acting antiviral (DAA) medications'],
        'precautions': ['Avoid sharing needles', 'Safe practices', 'Regular monitoring'],
        'doctor_required': True,
        'follow_up_questions': [
            "Have you experienced chronic fatigue, joint pain, or unexplained weight loss?",
            "Have you noticed any yellowing of your skin or eyes?",
            "Do you have any risk factors for Hepatitis C exposure (e.g., past intravenous drug use, blood transfusions before 1992)?"
        ]
    },
    'Tuberculosis': {
        'severity': 'severe',
        'tests': ['Chest X-ray', 'Sputum smear microscopy', 'TB culture', 'Mantoux test'],
        'medicines': ['Multi-drug regimen (e.g., Isoniazid, Rifampicin, Pyrazinamide, Ethambutol)'],
        'precautions': ['Complete full course of medication', 'Respiratory hygiene', 'Isolation if active TB'],
        'doctor_required': True,
        'follow_up_questions': [
            "Have you had a persistent cough lasting more than 3 weeks, sometimes with blood?",
            "Are you experiencing fever, night sweats, or unexplained weight loss?",
            "Have you been in contact with someone diagnosed with tuberculosis?"
        ]
    },
    'Dengue hemorrhagic fever': { # Another alias
        'severity': 'critical',
        'tests': ['Dengue NS1 Antigen Test', 'IgM/IgG Antibody Test', 'Complete Blood Count (CBC) with platelet count'],
        'medicines': ['Intravenous fluid replacement', 'Blood transfusions (if severe bleeding)', 'Strict monitoring'],
        'precautions': ['Immediate medical attention', 'Mosquito control'],
        'doctor_required': True,
        'follow_up_questions': [
            "Are you experiencing severe abdominal pain, persistent vomiting, or rapid breathing?",
            "Have you noticed any bleeding from the nose, gums, or skin (petechiae, bruising)?",
            "Are you feeling restless, lethargic, or cold and clammy?"
        ]
    },
    'Urinary tract infection': {
        'severity': 'mild',
        'tests': ['Urinalysis', 'Urine Culture'],
        'medicines': ['Antibiotics', 'Pain relievers'],
        'precautions': ['Drink plenty of water', 'Maintain hygiene', 'Urinate after intercourse'],
        'doctor_required': True,
        'follow_up_questions': [
            "Are you experiencing frequent, painful, or burning urination?",
            "Do you feel a persistent urge to urinate, even after emptying your bladder?",
            "Are you experiencing lower abdominal pain or cloudy/strong-smelling urine?"
        ]
    },
    'Varicose veins': {
        'severity': 'moderate',
        'tests': ['Physical examination', 'Duplex ultrasound'],
        'medicines': ['Compression stockings', 'Sclerotherapy', 'Laser treatment', 'Surgery'],
        'precautions': ['Regular exercise', 'Elevate legs', 'Avoid prolonged standing/sitting'],
        'doctor_required': True,
        'follow_up_questions': [
            "Do you have twisted, bulging veins, usually in your legs?",
            "Are your legs feeling achy, heavy, or swollen, especially after standing?",
            "Have you experienced itching, skin discoloration, or ulcers near the affected veins?"
        ]
    },
    'Hypothyroidism': {
        'severity': 'chronic',
        'tests': ['TSH test', 'Free T4 test'],
        'medicines': ['Levothyroxine (thyroid hormone replacement)'],
        'precautions': ['Regular medication', 'Dietary considerations (iodine, selenium)', 'Regular monitoring'],
        'doctor_required': True,
        'follow_up_questions': [
            "Are you experiencing fatigue, weight gain, or increased sensitivity to cold?",
            "Have you noticed dry skin, hair loss, or constipation?",
            "Are you experiencing muscle aches, stiffness, or depression?"
        ]
    },
    'Hyperthyroidism': {
        'severity': 'chronic',
        'tests': ['TSH test', 'Free T3 and T4 tests', 'Thyroid scan'],
        'medicines': ['Antithyroid medications', 'Radioactive iodine therapy', 'Surgery'],
        'precautions': ['Regular medication', 'Avoid iodine-rich foods (if advised)', 'Stress management'],
        'doctor_required': True,
        'follow_up_questions': [
            "Are you experiencing unexplained weight loss, rapid heartbeat, or anxiety?",
            "Do you have increased sweating, heat sensitivity, or tremors?",
            "Have you noticed changes in your menstrual cycle or difficulty sleeping?"
        ]
    },
    'Piles': { # Hemorrhoids
        'severity': 'mild',
        'tests': ['Physical examination', 'Anoscopy'],
        'medicines': ['Fiber supplements', 'Stool softeners', 'Topical creams', 'Sitz baths'],
        'precautions': ['High-fiber diet', 'Adequate hydration', 'Avoid straining during bowel movements'],
        'doctor_required': False,
        'follow_up_questions': [
            "Are you experiencing pain, itching, or swelling around the anus?",
            "Have you noticed bleeding during bowel movements (bright red blood)?",
            "Do you feel a lump or bulge near the anus?"
        ]
    },
    'Heart attack': {
        'severity': 'critical',
        'tests': ['ECG', 'Troponin test', 'Echocardiogram', 'Angiogram'],
        'medicines': ['Aspirin', 'Nitroglycerin', 'Beta-blockers', 'Statins', 'Clot-busting drugs'],
        'precautions': ['Call emergency services immediately', 'CPR if necessary', 'Lifestyle changes'],
        'doctor_required': True,
        'follow_up_questions': [
            "Are you experiencing crushing chest pain that spreads to your arms, back, neck, jaw, or stomach?",
            "Are you feeling shortness of breath, cold sweat, nausea, or lightheadedness?",
            "Do you have a family history of heart disease or risk factors like high blood pressure/diabetes?"
        ]
    },
    'Stroke': {
        'severity': 'critical',
        'tests': ['CT scan of brain', 'MRI of brain', 'Carotid ultrasound', 'Angiogram'],
        'medicines': ['Thrombolytics (clot-busting drugs)', 'Anticoagulants', 'Antiplatelet drugs', 'Blood pressure medications'],
        'precautions': ['Call emergency services immediately', 'Recognize FAST symptoms (Face drooping, Arm weakness, Speech difficulty, Time to call 911)'],
        'doctor_required': True,
        'follow_up_questions': [
            "Are you experiencing sudden numbness or weakness on one side of your body (face, arm, or leg)?",
            "Do you have sudden confusion, trouble speaking or understanding speech?",
            "Are you experiencing sudden trouble seeing in one or both eyes, or sudden severe headache with no known cause?"
        ]
    },
    'Pneumonia': {
        'severity': 'severe',
        'tests': ['Chest X-ray', 'Sputum Culture', 'Blood tests'],
        'medicines': ['Antibiotics (for bacterial pneumonia)', 'Antivirals (for viral pneumonia)', 'Oxygen therapy'],
        'precautions': ['Vaccination', 'Avoid smoking', 'Good hygiene'],
        'doctor_required': True,
        'follow_up_questions': [
            "Are you experiencing a severe cough with phlegm, shortness of breath, or chest pain?",
            "Do you have a high fever and chills?",
            "Have you been feeling unusually weak or fatigued?"
        ]
    },
    'Acne': {
        'severity': 'mild',
        'tests': ['Clinical diagnosis'],
        'medicines': ['Topical retinoids', 'Benzoyl peroxide', 'Salicylic acid', 'Oral antibiotics (for severe cases)'],
        'precautions': ['Gentle skin care', 'Avoid picking', 'Balanced diet'],
        'doctor_required': False,
        'follow_up_questions': [
            "Are you experiencing breakouts of pimples, blackheads, or whiteheads?",
            "Where on your body are the breakouts most common (face, back, chest)?",
            "Have you tried any specific treatments, and if so, how effective were they?"
        ]
    },
    'Impetigo': {
        'severity': 'mild',
        'tests': ['Clinical diagnosis', 'Bacterial culture (if severe or recurrent)'],
        'medicines': ['Topical antibiotics (Mupirocin)', 'Oral antibiotics (for widespread infection)'],
        'precautions': ['Good hygiene', 'Avoid scratching', 'Keep lesions covered'],
        'doctor_required': True, # Can become serious if untreated
        'follow_up_questions': [
            "Do you have red sores that quickly rupture and and form a honey-colored crust?",
            "Are these sores itchy or painful?",
            "Have you been in contact with someone who has similar skin lesions?"
        ]
    }
}

# Initialize translator
translator = Translator()

def translate_text(text, target_lang='en'):
    """Translate text to target language"""
    try:
        if target_lang == 'en':
            return text
        # Remove common markdown and special characters that might interfere with translation or voice
        clean_text = text.replace('**', '').replace('##', '').replace('*', '').replace('`', '').replace('•', '').replace(':', '').strip()
        translated = translator.translate(clean_text, dest=target_lang)
        return translated.text
    except Exception as e:
        return text

def translate_ui_text(text, target_lang='en'):
    """Translate UI elements"""
    if target_lang == 'en':
        return text
    try:
        translated = translator.translate(text, dest=target_lang)
        return translated.text
    except:
        return text

def load_and_train_model():
    """Load dataset and train the model"""
    try:
        # Create sample data if CSV not available
        # In production, load from the actual CSV file
        data = pd.read_csv('Testing.csv')
        
        # Prepare features and target
        X = data.drop('prognosis', axis=1)
        y = data['prognosis']
        
        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train Random Forest model
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Get feature names (symptoms)
        symptoms = X.columns.tolist()
        
        return model, symptoms, model.score(X_test, y_test)
    except Exception as e:
        st.error(f"Error loading model: {str(e)}")
        return None, None, 0

def get_user_location():
    """Get user's approximate location"""
    try:
        response = requests.get('https://ipapi.co/json/')
        data = response.json()
        return {
            'latitude': data.get('latitude'),
            'longitude': data.get('longitude'),
            'city': data.get('city'),
            'country': data.get('country_name')
        }
    except:
        return None

def find_nearby_healthcare(lat, lon, facility_type="hospital", radius=5000):
    """Find nearby healthcare facilities or pharmacies"""
    try:
        overpass_url = "http://overpass-api.de/api/interpreter"
        if facility_type == "pharmacy":
            overpass_query = f"""
            [out:json];
            (
              node["amenity"="pharmacy"]["name"](around:{radius},{lat},{lon});
              way["amenity"="pharmacy"]["name"](around:{radius},{lat},{lon});
            );
            out center;
            """
        else: # Default to general healthcare
            overpass_query = f"""
            [out:json];
            (
              node["amenity"~"hospital|clinic|doctors"]["name"](around:{radius},{lat},{lon});
              way["amenity"~"hospital|clinic|doctors"]["name"](around:{radius},{lat},{lon});
            );
            out center;
            """
        
        response = requests.get(overpass_url, params={'data': overpass_query})
        data = response.json()
        
        facilities = []
        for element in data.get('elements', []):
            if 'tags' in element and 'name' in element['tags']:
                facility = {
                    'name': element['tags']['name'],
                    'type': element['tags'].get('amenity', facility_type), # Use amenity tag if available, else default
                    'lat': element.get('lat', element.get('center', {}).get('lat')),
                    'lon': element.get('lon', element.get('center', {}).get('lon'))
                }
                facilities.append(facility)
        
        return facilities[:10]
    except Exception as e:
        st.error(f"Error finding nearby facilities: {str(e)}")
        return []

def predict_disease(detected_symptoms_from_user_input, model, all_model_symptoms_list):
    """Predict disease based on detected symptoms that match model features."""
    try:
        input_vector = [0] * len(all_model_symptoms_list)
        
        # Map the detected symptoms (which should already be in the model's format)
        # to the input vector
        for detected_symptom in detected_symptoms_from_user_input:
            if detected_symptom in all_model_symptoms_list:
                index = all_model_symptoms_list.index(detected_symptom)
                input_vector[index] = 1
        
        # Predict only if there's at least one symptom activated in the vector
        if 1 in input_vector:
            prediction = model.predict([input_vector])[0]
            probabilities = model.predict_proba([input_vector])[0]
            confidence = max(probabilities) * 100
            return prediction, confidence
        else:
            return None, 0 # No relevant symptoms detected
    except Exception as e:
        st.error(f"Prediction error: {str(e)}")
        return None, 0

def generate_medical_report(prediction, confidence, symptoms, current_lang):
    """Generate detailed medical report"""
    if prediction not in MEDICAL_RECOMMENDATIONS:
        return translate_text("Detailed analysis not available for this condition.", current_lang)
    
    rec = MEDICAL_RECOMMENDATIONS[prediction]
    
    report_parts = []
    report_parts.append(f"## 🩺 {translate_ui_text('AI HEALTH ASSESSMENT REPORT', current_lang)}")
    report_parts.append(f"**{translate_ui_text('Date', current_lang)}:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_parts.append(f"**{translate_ui_text('Patient Symptoms', current_lang)}:** {', '.join([translate_ui_text(s.replace('_', ' '), current_lang) for s in symptoms])}")
    report_parts.append(f"**{translate_ui_text('AI Diagnosis', current_lang)}:** {translate_ui_text(prediction, current_lang)}")
    report_parts.append(f"**{translate_ui_text('Confidence Level', current_lang)}:** {confidence:.1f}%")
    
    report_parts.append(f"\n### 📊 {translate_ui_text('Condition Analysis', current_lang)}")
    report_parts.append(f"**{translate_ui_text('Severity Level', current_lang)}:** {translate_ui_text(rec['severity'].upper(), current_lang)}")
    
    report_parts.append(f"\n### 🔬 {translate_ui_text('Recommended Tests', current_lang)}")
    for test in rec['tests']:
        report_parts.append(f"• {translate_ui_text(test, current_lang)}")
    
    report_parts.append(f"\n### 💊 {translate_ui_text('Treatment Recommendations', current_lang)}")
    for medicine in rec['medicines']:
        report_parts.append(f"• {translate_ui_text(medicine, current_lang)}")
    
    report_parts.append(f"\n### ⚠️ {translate_ui_text('Precautions & Lifestyle Changes', current_lang)}")
    for precaution in rec['precautions']:
        report_parts.append(f"• {translate_ui_text(precaution, current_lang)}")
    
    if rec['doctor_required']:
        report_parts.append(f"\n### 🏥 {translate_ui_text('Medical Consultation Required', current_lang)}")
        report_parts.append(f"**⚠️ {translate_ui_text('IMPORTANT', current_lang)}:** {translate_ui_text('This condition requires professional medical consultation. Please visit a qualified healthcare provider for proper diagnosis and treatment.', current_lang)}")
        report_parts.append(f"\n**{translate_ui_text('Recommended Specialists', current_lang)}:**")
        if rec['severity'] == 'chronic':
            report_parts.append(f"• {translate_ui_text('Internal Medicine Specialist', current_lang)}")
            report_parts.append(f"• {translate_ui_text('Endocrinologist (if applicable)', current_lang)}")
            report_parts.append(f"• {translate_ui_text('Cardiologist (if applicable)', current_lang)}")
        elif rec['severity'] == 'severe':
            report_parts.append(f"• {translate_ui_text('Emergency Medicine', current_lang)}")
            report_parts.append(f"• {translate_ui_text('Specialist based on condition', current_lang)}")
            report_parts.append(f"• {translate_ui_text('Hospital admission may be required', current_lang)}")
        else:
            report_parts.append(f"• {translate_ui_text('General Practitioner', current_lang)}")
            report_parts.append(f"• {translate_ui_text('Relevant Specialist', current_lang)}")
    else:
        report_parts.append(f"\n### ✅ {translate_ui_text('Self-Care Possible', current_lang)}")
        report_parts.append(translate_ui_text('This condition can often be managed with over-the-counter medications and lifestyle changes. However, consult a doctor if symptoms persist or worsen.', current_lang))
    
    report_parts.append(f"\n### 📞 {translate_ui_text('Emergency Action', current_lang)}")
    report_parts.append(f"**{translate_ui_text('Seek immediate medical attention if you experience', current_lang)}:**")
    report_parts.append(f"• {translate_ui_text('Severe worsening of symptoms', current_lang)}")
    report_parts.append(f"• {translate_ui_text('Difficulty breathing', current_lang)}")
    report_parts.append(f"• {translate_ui_text('Chest pain', current_lang)}")
    report_parts.append(f"• {translate_ui_text('Loss of consciousness', current_lang)}")
    report_parts.append(f"• {translate_ui_text('High fever (>103°F)', current_lang)}")
    report_parts.append(f"• {translate_ui_text('Severe bleeding', current_lang)}")

    report_parts.append(f"\n---\n**{translate_ui_text('Disclaimer', current_lang)}:** {translate_ui_text('This is an AI-generated assessment for informational purposes only. Always consult qualified healthcare professionals for accurate diagnosis and treatment.', current_lang)}")
    
    return "\n".join(report_parts)

def text_to_speech(text, lang='en'):
    """Convert text to speech"""
    try:
        # Remove emojis and excessive markdown for cleaner speech output
        clean_text = text
        emojis_to_remove = ['🔍', '🩺', '📊', '⚠️', '🏥', '🤖', '👤', '💬', '🎯', '📍', '🚑', '🎤', '📤', '🤒', '🤕', '😷', '😴', '🤢', '💔', '🦴', '🔴', '✅', '📋', '💾', '📄', '🌐', '🔊', '🎵', '📡', '🚨', '📞', '✨', '🌍', '❓', '🤔', '💡', '💧', '🚶‍♀️', '🥬', '🍎', '🧘‍♂️', '🧼', '💻', '👩‍⚕️', '🌟']
        for emoji in emojis_to_remove:
            clean_text = clean_text.replace(emoji, '')
        
        # Remove markdown bold/italic/headers and extra spaces
        clean_text = clean_text.replace('**', '').replace('##', '').replace('*', '').replace('---', '').replace('•', '').strip()
        clean_text = ' '.join(clean_text.split()) # Normalize spaces

        if len(clean_text) > 500: # Limit speech length to avoid long waits
            clean_text = clean_text[:500] + "... Please read the full response above for more details."
        
        engine = pyttsx3.init()
        engine.setProperty('rate', 160)
        engine.setProperty('volume', 1.0)
        
        voices = engine.getProperty('voices')
        if voices:
            # Attempt to find a voice for the specified language
            found_voice = False
            for voice in voices:
                # Check if the language code (e.g., 'en', 'es') is in the voice's language tags
                if hasattr(voice, 'languages') and any(l.lower().startswith(lang.lower()) for l in voice.languages):
                    engine.setProperty('voice', voice.id)
                    found_voice = True
                    break
            if not found_voice:
                # Fallback: Try to find a voice by name (common for some languages)
                for voice in voices:
                    if (lang == 'hi' and 'hindi' in voice.name.lower()) or \
                       (lang == 'bn' and 'bengali' in voice.name.lower()) or \
                       (lang == 'te' and 'telugu' in voice.name.lower()) or \
                       (lang == 'ta' and 'tamil' in voice.name.lower()) or \
                       (lang == 'mr' and 'marathi' in voice.name.lower()) or \
                       (lang == 'gu' and 'gujarati' in voice.name.lower()) or \
                       (lang == 'or' and ('oriya' in voice.name.lower() or 'odia' in voice.name.lower())): # Added Odia voice check
                        engine.setProperty('voice', voice.id)
                        found_voice = True
                        break
            if not found_voice:
                # Fallback to a generic English voice if no specific language voice is found
                for voice in voices:
                    if 'en' in voice.name.lower() or ('zira' in voice.name.lower() and 'en' in voice.name.lower()): # Prefer female English voice
                        engine.setProperty('voice', voice.id)
                        break
                else: # Final fallback to the first available voice
                    if voices:
                        engine.setProperty('voice', voices[0].id)
        
        engine.say(clean_text)
        engine.runAndWait()
        engine.stop()
        
    except Exception as e:
        st.error(f"Voice output error: {str(e)}")

def speech_to_text():
    """Convert speech to text"""
    try:
        r = sr.Recognizer()
        with sr.Microphone() as source:
            st.info(translate_ui_text("🎤 Listening... Speak now!", st.session_state.current_language))
            r.adjust_for_ambient_noise(source, duration=1)
            r.pause_threshold = 1
            audio = r.listen(source, timeout=10, phrase_time_limit=10)
        
        st.info(translate_ui_text("🔄 Processing speech...", st.session_state.current_language))
        text = r.recognize_google(audio, language=st.session_state.current_language) # Use current language for recognition
        return text
    except sr.UnknownValueError:
        st.warning(translate_ui_text("Could not understand audio. Please speak clearly.", st.session_state.current_language))
        return None
    except sr.RequestError as e:
        st.error(f"{translate_ui_text('Could not request results from speech service', st.session_state.current_language)}: {e}")
        return None
    except sr.WaitTimeoutError:
        st.warning(translate_ui_text("Listening timeout. Please try again.", st.session_state.current_language))
        return None
    except Exception as e:
        st.error(f"{translate_ui_text('Speech recognition error', st.session_state.current_language)}: {str(e)}")
        return None

def display_emergency_contacts(current_lang):
    """Display emergency contacts"""
    st.markdown(f"""
    <div class="emergency-section">
        <h2>🚨 {translate_ui_text('EMERGENCY CONTACTS', current_lang)} 🚨</h2>
        <p>{translate_ui_text('In case of medical emergency, call immediately!', current_lang)}</p>
    </div>
    """, unsafe_allow_html=True)
    
    contacts = EMERGENCY_CONTACTS['en'] # Using English keys, values are translated
    
    cols = st.columns(2)
    for i, (key, contact) in enumerate(contacts.items()):
        with cols[i % 2]:
            st.markdown(f"""
            <div class="info-card">
                <h4>📞 {translate_ui_text(contact['name'], current_lang)}</h4>
                <h2 style="color: var(--accent-color);">{contact['number']}</h2>
            </div>
            """, unsafe_allow_html=True)

# Main App
def main():
    current_lang = st.session_state.current_language
    
    # Header
    st.markdown(f"""
    <div class="main-header">
        <h1>🏥 {translate_ui_text('AI Health Assistant', current_lang)} 🩺</h1>
        <p>{translate_ui_text('Your intelligent healthcare companion with multilingual support', current_lang)}</p>
        <p>✨ {translate_ui_text('Advanced AI Diagnosis', current_lang)} • 🌍 {translate_ui_text('Multi-language', current_lang)} • 🚨 {translate_ui_text('Emergency Support', current_lang)} ✨</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"""
        <div class="info-card">
            <h3>🌐 {translate_ui_text('Settings', current_lang)}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Language selector
        selected_lang = st.selectbox(
            translate_ui_text("🌍 Choose Language", current_lang),
            options=list(LANGUAGES.keys()),
            format_func=lambda x: LANGUAGES[x],
            index=list(LANGUAGES.keys()).index(current_lang),
            key="language_selector"
        )
        
        if selected_lang != st.session_state.current_language:
            st.session_state.current_language = selected_lang
            st.rerun()
        
        # Voice settings
        st.markdown(f"""
        <div class="info-card">
            <h4>🔊 {translate_ui_text('Voice Features', current_lang)}</h4>
        </div>
        """, unsafe_allow_html=True)
        
        enable_voice = st.checkbox(
            translate_ui_text("🎵 Enable Voice Output", current_lang), 
            value=True, 
            key="voice_checkbox"
        )
        
        if st.button(f"🔊 {translate_ui_text('Test Voice', current_lang)}"):
            test_text = translate_ui_text("Hello! Voice output is working correctly.", current_lang)
            with st.spinner(translate_ui_text("Testing voice...", current_lang)):
                text_to_speech(test_text, current_lang)
            st.success(translate_ui_text("✅ Voice test completed!", current_lang))
        
        # Location services
        st.markdown(f"""
        <div class="info-card">
            <h4>📍 {translate_ui_text('Location Services', current_lang)}</h4>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button(f"📡 {translate_ui_text('Get My Location', current_lang)}"):
            with st.spinner(translate_ui_text("Getting your location...", current_lang)):
                location = get_user_location()
                if location:
                    st.session_state.user_location = location
                    location_text = f"📍 {location['city']}, {location['country']}"
                    st.success(location_text)
                else:
                    st.error(translate_ui_text("Could not retrieve your location. Please check your internet connection or browser permissions.", current_lang))
        
        # Model status
        if st.session_state.model:
            st.markdown(f"""
            <div class="info-card">
                <h4>🤖 {translate_ui_text('AI Model Status', current_lang)}</h4>
                <p style="color: var(--success-color);">✅ {translate_ui_text('Active & Ready', current_lang)}</p>
                <p>📊 {translate_ui_text('Accuracy', current_lang)}: High</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Emergency contacts sidebar
        st.markdown(f"""
        <div class="emergency-section">
            <h4>🚨 {translate_ui_text('Quick Emergency', current_lang)}</h4>
            <p><strong>🚑 {translate_ui_text('Ambulance', current_lang)}: 108</strong></p>
            <p><strong>👮 {translate_ui_text('Police', current_lang)}: 100</strong></p>
            <p><strong>🔥 {translate_ui_text('Fire', current_lang)}: 101</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    # Load model
    if st.session_state.model is None:
        loading_text = translate_ui_text("Loading AI Health Assistant...", current_lang)
        with st.spinner(f"🤖 {loading_text}"):
            model, symptoms, accuracy = load_and_train_model()
            if model:
                st.session_state.model = model
                st.session_state.symptoms_list = symptoms
                success_text = translate_ui_text(f"AI Model loaded! Accuracy: {accuracy:.2%}", current_lang)
                st.success(f"🎯 {success_text}")
            else:
                st.error(translate_ui_text("Failed to load AI model. Please try refreshing the page.", current_lang))
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        f"💬 {translate_ui_text('Chat Assistant', current_lang)}",
        f"📊 {translate_ui_text('Health Reports', current_lang)}",
        f"🏥 {translate_ui_text('Find Healthcare', current_lang)}",
        f"🚨 {translate_ui_text('Emergency', current_lang)}"
    ])
    
    with tab1:
        # Chat interface
        st.markdown(f"""
        <div class="info-card">
            <h3>💬 {translate_ui_text('Chat with Your AI Health Assistant', current_lang)}</h3>
            <p>{translate_ui_text('Describe your symptoms and get instant AI-powered health insights', current_lang)}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Initial greeting if no messages yet
        if not st.session_state.messages:
            initial_bot_message = translate_ui_text("Hello! I'm your AI Health Assistant. How can I help you today? Please tell me your main symptoms.", current_lang)
            st.session_state.messages.append({"role": "assistant", "content": initial_bot_message})
            st.session_state.conversation_state = 'awaiting_symptoms'
            if enable_voice:
                text_to_speech(initial_bot_message, current_lang)
        
        # Display chat messages
        if st.session_state.messages:
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            for i, message in enumerate(st.session_state.messages):
                if message["role"] == "user":
                    st.markdown(f"""
                    <div class="chat-message user-message">
                        <strong>👤 {translate_ui_text('You', current_lang)}:</strong> {message["content"]}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Content is already translated when added to messages for bot
                    st.markdown(f"""
                    <div class="chat-message bot-message">
                        <strong>🤖 {translate_ui_text('AI Assistant', current_lang)}:</strong> {message["content"]}
                    </div>
                    """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Input section
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        
        with col1:
            placeholder_text = translate_ui_text("Tell me about your symptoms...", current_lang)
            example_text = translate_ui_text("e.g., I have headache and fever", current_lang)
            user_input = st.text_input(
                "",
                placeholder=f"{placeholder_text} ({example_text})",
                key=f"user_input_{st.session_state.message_counter}"
            )
        
        with col2:
            voice_text = translate_ui_text("🎤 Voice", current_lang)
            voice_input = st.button(voice_text)
        
        with col3:
            send_text = translate_ui_text("📤 Send", current_lang)
            send_button = st.button(send_text)
        
        with col4:
            clear_text = translate_ui_text("🗑️ Clear Chat", current_lang) # Changed text for clarity
            if st.button(clear_text):
                st.session_state.messages = []
                st.session_state.message_counter = 0
                st.session_state.conversation_state = 'initial_greeting'
                st.session_state.current_symptoms_being_analyzed = []
                st.session_state.follow_up_question_index = 0
                st.session_state.predicted_disease_for_follow_up = None
                st.session_state.last_input = "" # Ensure last_input is cleared for fresh start
                st.rerun()
        
        # Handle voice input
        if voice_input:
            voice_result = speech_to_text()
            if voice_result:
                user_input = voice_result
                said_text = translate_ui_text("You said:", current_lang)
                st.info(f"🎤 {said_text} {voice_result}")
        
        # Determine the actual input to process
        input_to_process = user_input.strip()

        # Process user input (from text field)
        # Only process if there's actual input and it's different from the last processed input
        if (send_button or input_to_process) and input_to_process and input_to_process != st.session_state.last_input:
            st.session_state.last_input = input_to_process # Update last_input immediately
            st.session_state.message_counter += 1
            
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": input_to_process})
            
            response = ""
            input_to_process_lower = input_to_process.lower()

            # Check for simple conversational responses first
            negative_responses = ["no", "no more", "that's all", "i'm good", "nothing else"]
            affirmative_responses = ["yes", "more", "continue", "go on"]
            thank_you_responses = ["thank you", "thanks", "appreciate it"]

            if any(phrase in input_to_process_lower for phrase in negative_responses):
                if st.session_state.current_symptoms_being_analyzed:
                    # User explicitly said no more symptoms, proceed to diagnosis
                    if st.session_state.model:
                        prediction, confidence = predict_disease(
                            st.session_state.current_symptoms_being_analyzed, 
                            st.session_state.model, 
                            st.session_state.symptoms_list
                        )
                        
                        if prediction:
                            report = generate_medical_report(prediction, confidence, st.session_state.current_symptoms_being_analyzed, current_lang)
                            response = translate_ui_text("Understood. Here is a preliminary assessment based on the symptoms you've provided:", current_lang) + "\n\n" + report
                            
                            diagnosis_entry = {
                                'timestamp': datetime.now(),
                                'symptoms': st.session_state.current_symptoms_being_analyzed,
                                'prediction': prediction,
                                'confidence': confidence,
                                'report': report
                            }
                            st.session_state.diagnosis_history.append(diagnosis_entry)
                            
                            # Reset for a new conversation
                            st.session_state.current_symptoms_being_analyzed = []
                            st.session_state.predicted_disease_for_follow_up = None
                            st.session_state.follow_up_question_index = 0
                            st.session_state.conversation_state = 'diagnosed' # Set state to diagnosed
                        else:
                            response = translate_ui_text("I couldn't make a specific diagnosis based on the symptoms provided. Please try adding more symptoms or clarifying existing ones.", current_lang)
                    else:
                        response = translate_ui_text("AI model is not loaded. Please refresh the page.", current_lang)
                else:
                    response = translate_ui_text("Okay, if you don't have symptoms to add, how else can I assist you?", current_lang)
                    st.session_state.conversation_state = 'awaiting_symptoms' # Stay in awaiting symptoms for general questions
            elif any(phrase in input_to_process_lower for phrase in thank_you_responses):
                response = translate_ui_text("You're welcome! Is there anything else I can help you with regarding your health?", current_lang)
                st.session_state.conversation_state = 'awaiting_symptoms' # Stay in awaiting symptoms for general questions
            elif any(phrase in input_to_process_lower for phrase in affirmative_responses) and not st.session_state.current_symptoms_being_analyzed:
                # If user says "yes" but no symptoms collected yet, prompt for symptoms
                response = translate_ui_text("Great! Please tell me your symptoms.", current_lang)
                st.session_state.conversation_state = 'awaiting_symptoms'
            else:
                # Proceed with symptom detection if no special command found
                if st.session_state.model:
                    detected_symptoms_from_current_input = []
                    
                    for model_symptom in st.session_state.symptoms_list:
                        model_symptom_clean = model_symptom.replace('_', ' ').strip()
                        
                        if model_symptom_clean in input_to_process_lower:
                            detected_symptoms_from_current_input.append(model_symptom)
                            continue

                        user_words = input_to_process_lower.split()
                        model_symptom_words = model_symptom_clean.split()

                        for user_word in user_words:
                            if len(user_word) < 3:
                                continue
                            for model_word in model_symptom_words:
                                if user_word == model_word:
                                    detected_symptoms_from_current_input.append(model_symptom)
                                    break
                            if model_symptom in detected_symptoms_from_current_input:
                                break

                    st.session_state.current_symptoms_being_analyzed.extend(detected_symptoms_from_current_input)
                    st.session_state.current_symptoms_being_analyzed = list(set(st.session_state.current_symptoms_being_analyzed))

                    if st.session_state.current_symptoms_being_analyzed:
                        symptoms_display = [translate_ui_text(s.replace('_', ' '), current_lang) for s in st.session_state.current_symptoms_being_analyzed]
                        response = translate_ui_text("I've noted the following symptoms:", current_lang) + f" **{', '.join(symptoms_display)}**."
                        response += "\n\n" + translate_ui_text("Do you have any other symptoms to add? If not, please say 'no' or click 'Get Preliminary Diagnosis'.", current_lang)
                        st.session_state.conversation_state = 'awaiting_symptoms' # Keep state for more symptoms
                    else:
                        response = translate_ui_text("""
I couldn't identify specific symptoms in your last message. 
Please tell me about your symptoms. For example, you could say:
- "I have a headache and a fever."
- "I'm feeling nauseous and dizzy."  
- "I have chest pain and difficulty breathing."
What symptoms are you experiencing?
                        """, current_lang)
                        st.session_state.conversation_state = 'awaiting_symptoms' # Stay in awaiting symptoms
                else:
                    response = translate_ui_text("AI model is not loaded. Please refresh the page.", current_lang)
            
            # Add bot response to chat history (already translated)
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            # Text-to-speech
            if enable_voice:
                try:
                    with st.spinner(translate_ui_text("🔊 Speaking...", current_lang)):
                        speech_text = response
                        text_to_speech(speech_text, current_lang)
                except Exception as e:
                    st.warning(f"{translate_ui_text('Voice output failed', current_lang)}: {str(e)}")
            
            st.rerun()
        
        # Add a "Get Diagnosis" button
        if st.session_state.current_symptoms_being_analyzed:
            st.markdown("---")
            get_diagnosis_text = translate_ui_text("Get Preliminary Diagnosis", current_lang)
            if st.button(f"✨ {get_diagnosis_text}", key="get_diagnosis_button"):
                if st.session_state.model:
                    prediction, confidence = predict_disease(
                        st.session_state.current_symptoms_being_analyzed, 
                        st.session_state.model, 
                        st.session_state.symptoms_list
                    )
                    
                    if prediction:
                        report = generate_medical_report(prediction, confidence, st.session_state.current_symptoms_being_analyzed, current_lang)
                        diagnosis_response = translate_ui_text("Based on the symptoms you've provided, here is a preliminary assessment:", current_lang) + "\n\n" + report
                        
                        # Store in diagnosis history
                        diagnosis_entry = {
                            'timestamp': datetime.now(),
                            'symptoms': st.session_state.current_symptoms_being_analyzed,
                            'prediction': prediction,
                            'confidence': confidence,
                            'report': report
                        }
                        st.session_state.diagnosis_history.append(diagnosis_entry)
                        
                        st.session_state.messages.append({"role": "assistant", "content": diagnosis_response})
                        if enable_voice:
                            text_to_speech(diagnosis_response, current_lang)
                        
                        # Reset for a new conversation
                        st.session_state.current_symptoms_being_analyzed = []
                        st.session_state.predicted_disease_for_follow_up = None
                        st.session_state.follow_up_question_index = 0
                        st.session_state.last_input = "" # Clear last input to allow immediate new input
                        st.session_state.conversation_state = 'diagnosed' # Set state to diagnosed
                        st.rerun()
                    else:
                        no_prediction_response = translate_ui_text("I couldn't make a specific diagnosis based on the symptoms provided. Please try adding more symptoms or clarifying existing ones.", current_lang)
                        st.session_state.messages.append({"role": "assistant", "content": no_prediction_response})
                        if enable_voice:
                            text_to_speech(no_prediction_response, current_lang)
                        st.rerun()
                else:
                    model_not_loaded_response = translate_ui_text("AI model is not loaded. Please refresh the page.", current_lang)
                    st.session_state.messages.append({"role": "assistant", "content": model_not_loaded_response})
                    if enable_voice:
                        text_to_speech(model_not_loaded_response, current_lang)
                    st.rerun()
        
    with tab2:
        # Health Reports
        st.markdown(f"""
        <div class="info-card">
            <h3>📊 {translate_ui_text('Your Health Reports', current_lang)}</h3>
            <p>{translate_ui_text('View your AI-generated health assessments and recommendations', current_lang)}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.diagnosis_history:
            for i, diagnosis in enumerate(reversed(st.session_state.diagnosis_history)):
                with st.expander(f"📋 {translate_ui_text('Report', current_lang)} #{len(st.session_state.diagnosis_history)-i} - {translate_ui_text(diagnosis['prediction'], current_lang)} ({diagnosis['timestamp'].strftime('%Y-%m-%d %H:%M')})"):
                    st.markdown(f"**🎯 {translate_ui_text('Confidence', current_lang)}:** {diagnosis['confidence']:.1f}%")
                    st.markdown(f"**🩺 {translate_ui_text('Symptoms', current_lang)}:** {', '.join([translate_ui_text(s.replace('_', ' '), current_lang) for s in diagnosis['symptoms']])}")
                    st.markdown("---")
                    st.markdown(diagnosis['report'])
                    
                    # Download report button
                    if st.button(f"💾 {translate_ui_text('Download Report', current_lang)} #{len(st.session_state.diagnosis_history)-i}", key=f"download_{i}"):
                        st.download_button(
                            label=translate_ui_text("📄 Download as Text", current_lang),
                            data=diagnosis['report'],
                            file_name=f"health_report_{diagnosis['timestamp'].strftime('%Y%m%d_%H%M')}.txt",
                            mime="text/plain"
                        )
        else:
            st.info(translate_ui_text("No health reports generated yet. Start a conversation with the AI assistant to get your first health assessment!", current_lang))
    
    with tab3:
        # Healthcare Finder
        st.markdown(f"""
        <div class="info-card">
            <h3>🏥 {translate_ui_text('Find Healthcare Near You', current_lang)}</h3>
            <p>{translate_ui_text('Locate hospitals, clinics, pharmacies and specialists in your area', current_lang)}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.user_location:
            st.success(f"📍 {translate_ui_text('Location', current_lang)}: {st.session_state.user_location['city']}, {st.session_state.user_location['country']}")
            
            # Buttons for different facility types
            col_hosp, col_pharm = st.columns(2)
            with col_hosp:
                if st.button(f"🔍 {translate_ui_text('Find Nearby Hospitals/Clinics', current_lang)}"):
                    st.session_state.search_facility_type = "hospital"
                    st.session_state.trigger_facility_search = True
            with col_pharm:
                if st.button(f"💊 {translate_ui_text('Find Nearby Pharmacies', current_lang)}"):
                    st.session_state.search_facility_type = "pharmacy"
                    st.session_state.trigger_facility_search = True
            
            if st.session_state.get('trigger_facility_search', False):
                searching_text = translate_ui_text(f"Searching for nearby {st.session_state.search_facility_type}s...", current_lang)
                with st.spinner(searching_text):
                    facilities = find_nearby_healthcare(
                        st.session_state.user_location['latitude'],
                        st.session_state.user_location['longitude'],
                        facility_type=st.session_state.search_facility_type
                    )
                    
                    if facilities:
                        # Create map
                        m = folium.Map(
                            location=[st.session_state.user_location['latitude'], 
                                    st.session_state.user_location['longitude']], 
                            zoom_start=13
                        )
                        
                        # Add user location
                        your_location_text = translate_ui_text("Your Location", current_lang)
                        folium.Marker(
                            [st.session_state.user_location['latitude'], 
                             st.session_state.user_location['longitude']],
                            popup=your_location_text,
                            icon=folium.Icon(color='red', icon='home')
                        ).add_to(m)
                        
                        # Add facilities
                        for facility in facilities:
                            if facility['lat'] and facility['lon']:
                                icon_color = 'blue' if facility['type'] != 'pharmacy' else 'green'
                                icon_type = 'plus-sign' if facility['type'] != 'pharmacy' else 'medkit'
                                folium.Marker(
                                    [facility['lat'], facility['lon']],
                                    popup=f"{facility['name']} ({facility['type']})",
                                    icon=folium.Icon(color=icon_color, icon=icon_type)
                                ).add_to(m)
                        
                        st_folium(m, width=700, height=400)
                        
                        # List facilities
                        st.markdown(f"""
                        <div class="info-card">
                            <h4>📋 {translate_ui_text('Healthcare Facilities List', current_lang)}</h4>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        for i, facility in enumerate(facilities, 1):
                            type_text = translate_ui_text("Type", current_lang)
                            distance_text = translate_ui_text("Distance", current_lang)
                            st.markdown(f"""
                            <div class="info-card">
                                <h5>{i}. {facility['name']}</h5>
                                <p><strong>{type_text}:</strong> {translate_ui_text(facility['type'].title(), current_lang)}</p>
                                <p><strong>{distance_text}:</strong> ~{np.random.randint(1, 10)} km {translate_ui_text('away', current_lang)}</p>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        no_facilities_text = translate_ui_text(f"No {st.session_state.search_facility_type} facilities found nearby. Please try expanding your search radius.", current_lang)
                        st.info(no_facilities_text)
                st.session_state.trigger_facility_search = False # Reset trigger
        else:
            st.warning(translate_ui_text("Please enable location services in the sidebar to find nearby healthcare facilities.", current_lang))
    
    with tab4:
        # Emergency Section
        display_emergency_contacts(current_lang)
        
        # Emergency symptoms checker
        st.markdown(f"""
        <div class="info-card">
            <h3>⚠️ {translate_ui_text('Emergency Symptoms Checker', current_lang)}</h3>
            <p>{translate_ui_text('Check if your symptoms require immediate medical attention', current_lang)}</p>
        </div>
        """, unsafe_allow_html=True)
        
        emergency_symptoms = [
            "Difficulty breathing or shortness of breath",
            "Chest pain or pressure",
            "Severe abdominal pain",
            "Sudden numbness or weakness",
            "High fever (above 103°F/39.4°C)",
            "Severe bleeding",
            "Loss of consciousness",
            "Severe allergic reaction"
        ]
        
        st.markdown(f"**🚨 {translate_ui_text('Call emergency services immediately if you have', current_lang)}:**")
        for symptom in emergency_symptoms:
            translated_symptom = translate_ui_text(symptom, current_lang)
            st.markdown(f"• {translated_symptom}")
        
        # Quick emergency actions
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button(f"🚑 {translate_ui_text('Call Ambulance (108)', current_lang)}", type="primary"):
                st.error(f"🚨 {translate_ui_text('EMERGENCY CALL', current_lang)}: 108")
                st.error(translate_ui_text("This would dial emergency services in a real app", current_lang))
        
        with col2:
            if st.button(f"🏥 {translate_ui_text('Find Nearest Hospital', current_lang)}", type="secondary"):
                if st.session_state.user_location:
                    st.success(translate_ui_text("🏥 Directing to nearest hospital...", current_lang))
                    st.info(translate_ui_text("In a real app, this would show navigation to the nearest emergency room", current_lang))
                else:
                    st.warning(translate_ui_text("Please enable location services first", current_lang))
    
    # Health tips section
    st.markdown(f"""
    <div class="info-card">
        <h3>💡 {translate_ui_text('Daily Health Tips', current_lang)}</h3>
    </div>
    """, unsafe_allow_html=True)
    
    health_tips = [
        "Drink 8-10 glasses of water daily to stay hydrated 💧",
        "Take a 30-minute walk every day for better cardiovascular health 🚶‍♀️",
        "Get 7-9 hours of quality sleep each night 😴",
        "Eat 5 servings of fruits and vegetables daily 🥬🍎",
        "Practice deep breathing exercises to reduce stress 🧘‍♂️",
        "Wash your hands frequently to prevent infections 🧼",
        "Maintain good posture while working at a computer 💻",
        "Schedule regular health check-ups with your doctor 👩‍⚕️"
    ]
    
    tip_of_the_day = np.random.choice(health_tips)
    translated_tip = translate_ui_text(tip_of_the_day, current_lang)
    tip_text = translate_ui_text("Tip of the day:", current_lang)
    
    st.info(f"💡 **{tip_text}** {translated_tip}")
    
    # Footer
    st.markdown(f"""
    <div class="footer">
        <h4>🌟 {translate_ui_text('AI Health Assistant - Your Intelligent Healthcare Companion', current_lang)} 🌟</h4>
        <p>{translate_ui_text('This tool provides AI-powered health insights for informational purposes only.', current_lang)}</p>
        <p><strong>⚠️ {translate_ui_text('Always consult qualified healthcare professionals for accurate diagnosis and treatment.', current_lang)}</strong></p>
        <p>{translate_ui_text('Available in 15+ languages • Voice-enabled • Emergency support • Location-aware', current_lang)}</p>
        <hr style="border-color: var(--border-color);">
        <p style="font-size: 12px; color: var(--text-secondary);">
            {translate_ui_text('Developed with ❤️ for global healthcare accessibility', current_lang)} | 
            {translate_ui_text('Version 2.0 - Enhanced Dark UI', current_lang)}
        </p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    # Initialize session state variables for facility search if not present
    if 'search_facility_type' not in st.session_state:
        st.session_state.search_facility_type = "hospital"
    if 'trigger_facility_search' not in st.session_state:
        st.session_state.trigger_facility_search = False

    main()
