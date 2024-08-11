import streamlit as st
import google.generativeai as genai
import PyPDF2 as pdf
import requests
from dotenv import load_dotenv
import os
import subprocess

st.set_page_config(page_title="HR Dashboard", layout="wide")
load_dotenv()

with st.sidebar:
    st.title("Hi, HR!")
    page = st.selectbox("", ("Home", "ChatBot Assistant", "Interview Scheduling", "Analytics Dashboard", "Leave Management"), label_visibility="collapsed")

if page == "Home":
    st.header("Dashboard")
    st.subheader("✨Welcome to Company!✨")

elif page == "ChatBot Assistant":
    OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
    OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")

    def generate_text(prompt, max_tokens=1000, temperature=0.8, top_p=0.9):
        headers = {
            "Content-Type": "application/json",
            "api-key": OPENAI_KEY
        }
        data = {
            "messages": [
                {"role": "system", "content": "You are a helpful assistant. Please provide detailed and comprehensive responses."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            "stop": None
        }
        try:
            with st.spinner("Generating detailed response..."):
                response = requests.post(f"{OPENAI_ENDPOINT}/openai/deployments/ChatbotCC/chat/completions?api-version=2023-05-15", headers=headers, json=data)
                response.raise_for_status()
                result = response.json()
                return result['choices'][0]['message']['content']
        except requests.exceptions.RequestException as e:
            st.error(f"Error: {e}")
            if response.status_code == 404:
                st.error("Deployment not found. Please check your deployment name and try again.")
            else:
                st.error(f"Detailed error: {response.text}")
            return None

    st.header("AI Chatbot Assistant")

    if 'generated_text' not in st.session_state:
        st.session_state.generated_text = ""
    if 'prompt' not in st.session_state:
        st.session_state.prompt = ""

    st.info("This chatbot is designed to provide detailed and comprehensive responses. Feel free to ask complex questions!")

    st.session_state.prompt = st.text_area("Enter your question or prompt (the more specific, the better):", height=150)

    col1, col2, col3 = st.columns(3)
    with col1:
        max_tokens = st.slider("Response Length", min_value=100, max_value=2000, value=1000, step=100, help="Higher values allow for longer responses")
    with col2:
        temperature = st.slider("Creativity", min_value=0.5, max_value=1.0, value=0.8, step=0.1, help="Higher values increase response creativity")
    with col3:
        top_p = st.slider("Focus", min_value=0.1, max_value=1.0, value=0.9, step=0.1, help="Lower values make responses more focused")

    if st.button("Generate Response") and st.session_state.prompt.strip():
        st.session_state.generated_text = generate_text(st.session_state.prompt, max_tokens, temperature, top_p)
        if st.session_state.generated_text:
            st.subheader("Generated Response:")
            st.write(st.session_state.generated_text)

            if len(st.session_state.generated_text.split()) < 50:
                if st.button("The response seems brief. Would you like me to expand on it?"):
                    expansion_prompt = f"Please provide a more detailed explanation of the following: {st.session_state.generated_text}"
                    expanded_response = generate_text(expansion_prompt, max_tokens, temperature, top_p)
                    if expanded_response:
                        st.subheader("Expanded Response:")
                        st.write(expanded_response)

    st.markdown("---")
    st.caption("This chatbot uses Azure OpenAI services to generate responses. The quality and length of responses may vary based on the input and settings.")

elif page == "Interview Scheduling":
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

    def get_ai_response(prompt, pdf_text, job_desc):
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(f"{prompt}\n\nJob Description: {job_desc}\n\nResume: {pdf_text}")
        return response.text

    def extract_pdf_text(uploaded_file):
        reader = pdf.PdfReader(uploaded_file)
        return "".join(page.extract_text() for page in reader.pages)

    st.markdown("""
    <style>
        :root {
            --background-color-light: #f8f9fa;
            --background-color-dark: #343a40;
            --text-color-light: #212529;
            --text-color-dark: #f8f9fa;
            --card-background-light: #ffffff;
            --card-background-dark: #495057;
            --card-border-light: #e9ecef;
            --card-border-dark: #343a40;
            --primary-color-light: #007bff;
            --primary-color-dark: #1a73e8;
            --primary-hover-light: #0056b3;
            --primary-hover-dark: #1558b5;
        }

        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
        
        * {
            font-family: 'Inter', sans-serif;
        }
        
        .main {
            background-color: var(--background-color-light);
            color: var(--text-color-light);
        }

        h1, h2, h3, h4, h5, h6 {
            color: var(--text-color-light);
        }

        .stButton>button {
            background-color: var(--primary-color-light);
            color: white;
            border: none;
            border-radius: 4px;
            padding: 10px 20px;
            font-weight: 600;
            transition: all 0.3s ease;
        }

        .stButton>button:hover {
            background-color: var(--primary-hover-light);
        }

        .stTextArea>div>div>textarea, .stFileUploader {
            background-color: white;
            border: 1px solid var(--card-border-light);
            border-radius: 4px;
        }

        .card {
            background-color: var(--card-background-light);
            border: 1px solid var(--card-border-light);
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }

        .result-card {
            background-color: var(--card-background-light);
            border-left: 5px solid #28a745;
            margin-top: 20px;
        }

        .analysis-sidebar {
            background-color: var(--background-color-light);
            border-right: 1px solid var(--card-border-light);
            padding: 20px;
            height: 100%;
        }

        .result-content {
            max-height: 500px;
            overflow-y: auto;
            padding: 10px;
        }

        .st-cc {
            background-color: var(--card-border-light);
            border-radius: 4px;
            padding: 2px 6px;
            margin-bottom: 5px;
        }

        .stProgress > div > div > div {
            background-color: #28a745;
        }

        @media (prefers-color-scheme: dark) {
            .main {
                background-color: var(--background-color-dark);
                color: var(--text-color-dark);
            }

            h1, h2, h3, h4, h5, h6 {
                color: var(--text-color-dark);
            }

            .stButton>button {
                background-color: var(--primary-color-dark);
            }

            .stButton>button:hover {
                background-color: var(--primary-hover-dark);
            }

            .stTextArea>div>div>textarea, .stFileUploader {
                background-color: var(--card-background-dark);
                border: 1px solid var(--card-border-dark);
            }

            .card {
                background-color: var(--card-background-dark);
                border: 1px solid var(--card-border-dark);
                box-shadow: 0 2px 5px rgba(255,255,255,0.05);
            }

            .result-card {
                background-color: var(--card-background-dark);
            }

            .analysis-sidebar {
                background-color: var(--background-color-dark);
                border-right: 1px solid var(--card-border-dark);
            }

            .st-cc {
                background-color: var(--card-border-dark);
            }
        }
    </style>
    """, unsafe_allow_html=True)

    def main():
        tab1, tab2, tab3 = st.tabs(["📄 Input", "🔍 Analysis", "ℹ️ How It Works"])
        
        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("""
                <div class="card">
                    <h3>Job Description</h3>
                    <p>Enter the job description below. This will be used to assess the candidate's resume.</p>
                </div>
                """, unsafe_allow_html=True)
                job_desc = st.text_area("Job Description", height=200)
            with col2:
                st.markdown("""
                <div class="card">
                    <h3>Resume Upload</h3>
                    <p>Upload the candidate's resume in PDF format.</p>
                </div>
                """, unsafe_allow_html=True)
                uploaded_file = st.file_uploader("Upload Resume", type="pdf")
        
        with tab2:
            if uploaded_file and job_desc.strip():
                prompt = st.text_area("AI Analysis Prompt", "Provide an analysis of the candidate's qualifications based on the job description and resume.", height=100)
                pdf_text = extract_pdf_text(uploaded_file)
                result = get_ai_response(prompt, pdf_text, job_desc)
                
                st.markdown(f"""
                <div class="result-card">
                    <h3>AI Analysis Result</h3>
                    <div class="result-content">{result}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("Please provide a job description and upload a resume to proceed with the analysis.")

        with tab3:
            st.markdown("""
            <div class="card">
                <h3>How It Works</h3>
                <p>This tool uses advanced AI to analyze resumes against job descriptions. The AI identifies key skills and experiences in the resume and compares them to the job requirements, providing an analysis of the candidate's suitability for the role.</p>
            </div>
            """, unsafe_allow_html=True)

    main()

elif page == "Analytics Dashboard":
    st.title("Analytics Dashboard")
    st.subheader("🔎 View detailed analytics here.")

elif page == "Leave Management":
    try:
        subprocess.run(["streamlit", "run", "Leave Management/app.py"], check=True)
    except subprocess.CalledProcessError as e:
        st.error(f"Error running the Leave Management app: {e}")
        st.error(f"Detailed error output: {e.output}")

        if "not found" in str(e.output).lower():
            st.error("The file 'app.py' in the 'Leave Management' directory was not found. Please check the file path.")
        elif "Permission denied" in str(e.output).lower():
            st.error("Permission denied while trying to run the app. Please check file permissions.")
        else:
            st.error("An unexpected error occurred while trying to run the Leave Management app. Please check the terminal output for more details.")
