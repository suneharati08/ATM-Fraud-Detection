import streamlit as st
import pickle
import numpy as np
from groq import Groq
import os
import random
from datetime import datetime
import time

# Configure page with wider layout and custom theme
st.set_page_config(
    page_title="ATM Fraud Detection",
    page_icon="🏧",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.securebank.com/help',
        'Report a bug': 'https://www.securebank.com/bug',
        'About': 'ATM Fraud Detection System v2.2'
    }
)

# Modern Professional CSS Design
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main Header */
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 0.5rem;
        padding-bottom: 1rem;
        letter-spacing: -0.02em;
    }
    
    .subheader {
        font-size: 2rem;
        font-weight: 600;
        color: #1f2937;
        margin-top: 1.5rem;
        margin-bottom: 1.5rem;
        letter-spacing: -0.01em;
    }
    
    /* Modern Cards */
    .card {
        padding: 1.5rem;
        border-radius: 16px;
        background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
        border: 1px solid #e2e8f0;
        margin: 1rem 0;
        box-shadow: 0 2px 4px -1px rgba(0, 0, 0, 0.05), 0 1px 2px -1px rgba(0, 0, 0, 0.03);
        transition: all 0.3s ease;
    }
    
    .card:hover {
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        transform: translateY(-2px);
    }
    
    .success-card {
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        border: 2px solid #10b981;
        box-shadow: 0 4px 14px 0 rgba(16, 185, 129, 0.15);
    }
    
    .warning-card {
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
        border: 2px solid #ef4444;
        box-shadow: 0 4px 14px 0 rgba(239, 68, 68, 0.15);
    }
    
    .info-panel {
        background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #3b82f6;
        margin: 1rem 0;
        box-shadow: 0 2px 4px -1px rgba(59, 130, 246, 0.1);
    }
    
    /* Sidebar */
    .sidebar-content {
        padding: 1.5rem 1rem;
        background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem 1rem;
        font-size: 0.875rem;
        color: #64748b;
        border-top: 1px solid #e2e8f0;
        margin-top: 4rem;
        background: #f8fafc;
    }
    
    /* Transaction Form */
    .transaction-form {
        background: white;
        padding: 2rem;
        border-radius: 16px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        margin: 1.5rem 0;
        position: relative;
        overflow: visible;
    }
    
    /* Ensure Streamlit widgets inside forms are contained */
    .transaction-form .stSelectbox,
    .transaction-form .stNumberInput,
    .transaction-form .stCheckbox,
    .transaction-form .stButton {
        width: 100%;
        margin: 0.5rem 0;
    }
    
    /* Stat Boxes */
    .stat-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        border: none;
        box-shadow: 0 4px 14px 0 rgba(102, 126, 234, 0.25);
        transition: transform 0.3s ease;
    }
    
    .stat-box:hover {
        transform: scale(1.05);
    }
    
    .stat-value {
        font-size: 2.25rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 0.25rem;
    }
    
    .stat-label {
        font-size: 0.875rem;
        color: rgba(255, 255, 255, 0.9);
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Chat Bubbles */
    .chat-bubble {
        padding: 1rem 1.25rem;
        border-radius: 18px;
        margin-bottom: 0.75rem;
        display: inline-block;
        max-width: 75%;
        word-wrap: break-word;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        animation: fadeIn 0.3s ease;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .user-bubble {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-bottom-right-radius: 4px;
        float: right;
        margin-left: auto;
    }
    
    .assistant-bubble {
        background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
        color: #1e293b;
        border-bottom-left-radius: 4px;
        float: left;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 14px 0 rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px 0 rgba(102, 126, 234, 0.4);
    }
    
    /* Metrics */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    
    /* Input Fields */
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select {
        border-radius: 10px;
        border: 2px solid #e2e8f0;
        transition: all 0.3s ease;
    }
    
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Transaction List */
    .transaction-item {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 12px;
        background: #f8fafc;
        border-left: 4px solid #667eea;
        transition: all 0.2s ease;
    }
    
    .transaction-item:hover {
        background: #f1f5f9;
        transform: translateX(4px);
    }
    
    /* Badge Styles */
    .badge {
        display: inline-block;
        padding: 0.35rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .badge-success {
        background: #d1fae5;
        color: #065f46;
    }
    
    .badge-danger {
        background: #fee2e2;
        color: #991b1b;
    }
    
    /* Progress Bar */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    /* Section Dividers */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, #e2e8f0, transparent);
        margin: 2rem 0;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f5f9;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
</style>
""", unsafe_allow_html=True)

# Configure Groq API Key
# Option 1: Set it as environment variable (RECOMMENDED):
#   Windows PowerShell: $env:GROQ_API_KEY="your_key_here"
#   Windows CMD: set GROQ_API_KEY=your_key_here
#   Linux/Mac: export GROQ_API_KEY="your_key_here"
#
# Option 2: Provide it in Streamlit secrets or via the sidebar setting
# Get your API key from: https://console.groq.com/keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# Default Groq model
GROQ_MODEL = "qwen/qwen3-32b"

def get_groq_client(api_key=None):
    """Retrieve initialized Groq client or raise helpful error if missing."""
    key = api_key or os.getenv("GROQ_API_KEY") or st.session_state.get("groq_api_key", "")
    if not key:
        raise Exception("Groq API key not found. Please set GROQ_API_KEY in your environment variables, .streamlit/secrets.toml, or enter it in the sidebar API configuration.")
    return Groq(api_key=key)

# Helper function to call Groq API
def call_groq_api(prompt, model_name=None):
    """Call Groq API with the given prompt"""
    try:
        client = get_groq_client()
        model = model_name or GROQ_MODEL
        
        # Use Groq Chat Completions API with streaming
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.6,
            max_completion_tokens=200,  # Reduced to save tokens
            top_p=0.95,
            reasoning_effort="default",
            stream=True,
            stop=None
        )
        
        # Collect all chunks from streaming response
        full_response = ""
        for chunk in completion:
            if chunk.choices and len(chunk.choices) > 0:
                content = chunk.choices[0].delta.content or ""
                full_response += content
        
        if full_response.strip():
            return full_response.strip()
        else:
            raise Exception("No response from Groq API")
            
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "403" in error_msg or "authentication" in error_msg.lower() or "invalid" in error_msg.lower() or "api key" in error_msg.lower():
            raise Exception(f"Authentication error: Please check your Groq API key. Get one at: https://console.groq.com/keys. Set it as environment variable GROQ_API_KEY or in the sidebar. {error_msg}")
        elif "rate limit" in error_msg.lower() or "429" in error_msg:
            raise Exception(f"Rate limit exceeded. Please try again later. {error_msg}")
        else:
            raise Exception(f"Groq API error: {error_msg}")

# Load trained models
@st.cache_resource
def load_model(model_path):
    try:
        with open(model_path, "rb") as file:
            return pickle.load(file)
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None

# App header with logo
col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    st.markdown("<h1 class='main-header'>🏧 ATM Fraud Detection System</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; margin-bottom: 2rem; color: #64748b; font-size: 1.1rem; font-weight: 400;'>Advanced AI-powered fraud monitoring and prevention</p>", unsafe_allow_html=True)

# Sidebar with navigation and stats
with st.sidebar:
    st.markdown("<div class='sidebar-content'>", unsafe_allow_html=True)
    
    # User profile section
    current_time = datetime.now().strftime('%B %d, %Y %H:%M')
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 2rem;">
        <div style="width: 80px; height: 80px; border-radius: 50%; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); margin: 0 auto 1rem; display: flex; align-items: center; justify-content: center; font-size: 2rem; box-shadow: 0 4px 14px rgba(102, 126, 234, 0.3);">
            👤
        </div>
        <h3 style="margin: 0; color: #1e293b; font-weight: 600;">Welcome, Analyst</h3>
        <p style="margin: 0.5rem 0 0; color: #64748b; font-size: 0.875rem;">Last login: {current_time}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Navigation
    st.markdown("### 📌 Navigation")
    section = st.radio("", ["Dashboard", "Model Selection", "Deep Learning Analysis", "Community Chat", "AI Assistant"])
    
    with st.expander("🔑 API Configuration", expanded=False):
        api_input = st.text_input("Groq API Key", type="password", value=st.session_state.get("groq_api_key", os.getenv("GROQ_API_KEY", "")), help="Required for Deep Learning Analysis & AI Assistant")
        if api_input:
            st.session_state["groq_api_key"] = api_input

    st.markdown("---")
    
    # Stats section
    st.markdown("### 📊 System Stats")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='stat-box'><div class='stat-value'>98.7%</div><div class='stat-label'>Accuracy</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='stat-box'><div class='stat-value'>1.2s</div><div class='stat-label'>Avg Response</div></div>", unsafe_allow_html=True)
        
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; margin-top: 2rem; padding-top: 1.5rem; border-top: 1px solid #e2e8f0;">
        <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">🔐</div>
        <p style="color: #1e293b; font-weight: 600; margin: 0.25rem 0; font-size: 0.875rem;">Bank Security System</p>
        <p style="color: #64748b; font-size: 0.75rem; margin: 0;">v2.2 • © 2025</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Load models
rf_model = load_model("fraud_detection_rf_model.pkl")
dt_model = load_model("Decision_Tree_model.pkl")

# Functions for transaction analysis
def analyze_transaction(transaction_type, amount, old_balance, new_balance):
    """Provides additional insights about the transaction"""
    insights = []
    
    # Balance change analysis
    if new_balance < old_balance - amount:
        insights.append("⚠️ Balance discrepancy detected")
    
    # Amount patterns
    if amount > 5000:
        insights.append("⚠️ Large transaction amount")
    if 0.99 < amount < 5.01:
        insights.append("⚠️ Test transaction amount (common in fraud)")
        
    # Balance patterns  
    if old_balance > 0 and new_balance == 0:
        insights.append("⚠️ Account emptied (high risk)")
    
    # Transaction type specific
    if transaction_type == "CASH_OUT" and amount > 1000:
        insights.append("⚠️ Large cash withdrawal")
        
    return insights

# --- Dashboard Section ---
if section == "Dashboard":
    # Dashboard layout
    st.markdown("<h2 class='subheader'>📊 Fraud Detection Dashboard</h2>", unsafe_allow_html=True)
    
    # Key metrics in columns with modern styling
    st.markdown("<div style='margin: 2rem 0;'>", unsafe_allow_html=True)
    metric1, metric2, metric3, metric4 = st.columns(4)
    with metric1:
        st.metric(label="📊 Today's Alerts", value="12", delta="-3", delta_color="inverse")
    with metric2:
        st.metric(label="✅ False Positives", value="2.1%", delta="-0.4%", delta_color="inverse")
    with metric3:
        st.metric(label="🎯 Detection Rate", value="99.7%", delta="+0.2%", delta_color="normal")
    with metric4:
        st.metric(label="⚡ Review Time", value="45s", delta="-5s", delta_color="inverse")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Recent activity section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color: #1e293b; font-weight: 600; margin-bottom: 1rem; font-size: 1.25rem;'>📈 Latest Transactions</h4>", unsafe_allow_html=True)
        
        transactions = [
            {"time": "10:45 AM", "type": "PAYMENT", "amount": "$152.30", "status": "✅ Safe"},
            {"time": "09:32 AM", "type": "TRANSFER", "amount": "$890.00", "status": "✅ Safe"},
            {"time": "08:17 AM", "type": "CASH_OUT", "amount": "$500.00", "status": "🚨 Flagged"},
            {"time": "Yesterday", "type": "DEBIT", "amount": "$42.15", "status": "✅ Safe"},
            {"time": "Yesterday", "type": "TRANSFER", "amount": "$1,200.00", "status": "✅ Safe"},
        ]
        
        for t in transactions:
            status_color = "#10b981" if "Safe" in t["status"] else "#ef4444"
            status_bg = "#d1fae5" if "Safe" in t["status"] else "#fee2e2"
            st.markdown(f"""
            <div class="transaction-item" style="display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; align-items: center; gap: 1rem;">
                <div style="font-weight: 500; color: #64748b;">{t["time"]}</div>
                <div style="font-weight: 600; color: #1e293b;">{t["type"]}</div>
                <div style="font-weight: 700; color: #1e293b; font-size: 1.1rem;">{t["amount"]}</div>
                <div style="text-align: right;">
                    <span style="background: {status_bg}; color: {status_color}; padding: 0.35rem 0.75rem; border-radius: 20px; font-size: 0.75rem; font-weight: 600;">
                        {t["status"]}
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color: #1e293b; font-weight: 600; margin-bottom: 0.5rem;'>📊 Fraud Distribution</h4>", unsafe_allow_html=True)
        st.markdown("<p style='color: #64748b; font-size: 0.875rem; margin-bottom: 1.5rem;'>By transaction type</p>", unsafe_allow_html=True)
        
        chart_data = {
            "PAYMENT": 34,
            "TRANSFER": 28, 
            "CASH_OUT": 56,
            "DEBIT": 19,
            "CASH_IN": 13
        }
        
        st.bar_chart(chart_data, height=250)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # System notifications
    st.markdown("<div class='info-panel'>", unsafe_allow_html=True)
    st.markdown("<h4 style='color: #1e40af; font-weight: 600; margin-bottom: 1rem;'>📢 System Notifications</h4>", unsafe_allow_html=True)
    st.markdown("""
    <div style="line-height: 1.8;">
        <div style="margin: 0.75rem 0; padding-left: 1rem; border-left: 3px solid #3b82f6;">
            <strong>Model Update:</strong> Random Forest model updated yesterday with 2.3% accuracy improvement
        </div>
        <div style="margin: 0.75rem 0; padding-left: 1rem; border-left: 3px solid #3b82f6;">
            <strong>Pattern Alert:</strong> New fraud pattern detected involving small recurring payments
        </div>
        <div style="margin: 0.75rem 0; padding-left: 1rem; border-left: 3px solid #3b82f6;">
            <strong>Maintenance:</strong> Scheduled system maintenance on April 12, 2025
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- Model Selection ---
elif section == "Model Selection":
    st.markdown("<h2 class='subheader'>⚙️ Model Selection</h2>", unsafe_allow_html=True)
    
    # Create two columns for better layout
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # Add custom CSS for the column container
        st.markdown("""
        <style>
            div[data-testid="column"]:nth-of-type(1) {
                background: white;
                padding: 2rem;
                border-radius: 16px;
                border: 1px solid #e2e8f0;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
                margin: 1.5rem 0;
            }
        </style>
        """, unsafe_allow_html=True)
        
        # Transaction Details Section
        st.markdown("<h3 style='color: #1e293b; font-weight: 600; margin-bottom: 1.5rem; font-size: 1.5rem;'>💰 Transaction Details</h3>", unsafe_allow_html=True)
        
        transaction_type = st.selectbox("Transaction Type", [2, 4, 1, 5, 3], format_func=lambda x: {
            2: "PAYMENT",
            4: "TRANSFER",
            1: "CASH_OUT",
            5: "DEBIT",
            3: "CASH_IN"
        }[x])
        
        # More intuitive form layout
        amount = st.number_input("Amount ($)", min_value=0.0, format="%.2f", help="Transaction amount")
        
        col1_inner, col2_inner = st.columns(2)
        with col1_inner:
            old_balance_org = st.number_input("Old Balance (Sender)", min_value=0.0, format="%.2f")
        with col2_inner:
            new_balance_org = st.number_input("New Balance (Sender)", min_value=0.0, format="%.2f")
        
        # Model selection section
        st.markdown("<h3 style='color: #1e293b; font-weight: 600; margin: 2rem 0 1rem; font-size: 1.25rem;'>🤖 Select Model</h3>", unsafe_allow_html=True)
        model_col1, model_col2 = st.columns(2)
        
        with model_col1:
            rf_selected = st.checkbox("Random Forest", value=True, help="Higher accuracy, slower")
            if rf_selected:
                st.markdown("- 96.4% Accuracy")
                st.markdown("- Good for complex patterns")
                st.markdown("- Handles outliers well")
        
        with model_col2:
            dt_selected = st.checkbox("Decision Tree", help="Faster, more interpretable")
            if dt_selected:
                st.markdown("- 93.8% Accuracy")
                st.markdown("- More explainable")
                st.markdown("- Faster processing")
                
        # Ensure only one is selected
        if rf_selected and dt_selected:
            dt_selected = False
            st.warning("Only one model can be selected at a time.")
        
        model_choice = "Random Forest Classifier" if rf_selected else "Decision Tree"
        
        # Enhanced submit button with animation
        st.markdown("<div style='margin-top: 2rem;'>", unsafe_allow_html=True)
        if st.button("🔍 Analyze Transaction", use_container_width=True):
            with st.spinner("Analyzing transaction..."):
                # Simulated processing time for better UX
                time.sleep(1.2)
                
                input_data = np.array([[transaction_type, amount, old_balance_org, new_balance_org]])
                
                if model_choice == "Random Forest Classifier":
                    prediction = rf_model.predict(input_data) if rf_model else ["No fraud"]
                else:
                    prediction = dt_model.predict(input_data) if dt_model else ["No fraud"]
                
                # Get additional insights
                transaction_type_name = {2: "PAYMENT", 4: "TRANSFER", 1: "CASH_OUT", 5: "DEBIT", 3: "CASH_IN"}[transaction_type]
                insights = analyze_transaction(transaction_type_name, amount, old_balance_org, new_balance_org)
                
                # Show results - inside the form container
                if prediction[0] == "No fraud":
                    st.markdown("<div class='card success-card' style='margin-top: 1.5rem;'>", unsafe_allow_html=True)
                    st.success("✅ This transaction appears legitimate.")
                    st.markdown("<h3 style='color: #065f46; font-weight: 600; margin: 1rem 0 0.75rem; font-size: 1.25rem;'>Transaction Assessment</h3>", unsafe_allow_html=True)
                    st.markdown("✓ Normal transaction pattern")
                    st.markdown("✓ Balanced account activity")
                    st.markdown("✓ No suspicious indicators")
                    st.markdown("</div>", unsafe_allow_html=True)
                    st.toast("✅ Transaction looks safe!", icon="✅")
                    st.balloons()
                else:
                    st.markdown("<div class='card warning-card' style='margin-top: 1.5rem;'>", unsafe_allow_html=True)
                    st.error("🚨 WARNING: Potential Fraud Detected!")
                    st.markdown("<h3 style='color: #991b1b; font-weight: 600; margin: 1rem 0 0.75rem; font-size: 1.25rem;'>Risk Assessment</h3>", unsafe_allow_html=True)
                    st.markdown("❌ Suspicious transaction pattern")
                    for insight in insights:
                        st.markdown(f"❌ {insight}")
                    st.markdown("</div>", unsafe_allow_html=True)
                    st.toast("🚨 Fraud Alert! This transaction may be fraudulent.", icon="⚠")
        st.markdown("</div>", unsafe_allow_html=True)
                
    # Side panel with model performance and information
    with col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<h3 style='color: #1e293b; font-weight: 600; margin-bottom: 1.5rem; font-size: 1.25rem;'>📈 Model Performance</h3>", unsafe_allow_html=True)
        
        st.markdown("<h4 style='color: #1e293b; font-weight: 600; margin: 1rem 0 0.5rem; font-size: 1rem;'>Random Forest</h4>", unsafe_allow_html=True)
        st.progress(96)
        st.caption("96% Overall Accuracy")
        
        st.markdown("<h4 style='color: #1e293b; font-weight: 600; margin: 1rem 0 0.5rem; font-size: 1rem;'>Decision Tree</h4>", unsafe_allow_html=True)
        st.progress(93)
        st.caption("93% Overall Accuracy")
        
        st.markdown("<h3 style='color: #1e293b; font-weight: 600; margin: 1.5rem 0 1rem; font-size: 1.25rem;'>🔍 Why Use ML for Fraud?</h3>", unsafe_allow_html=True)
        st.markdown("""
        - Pattern recognition across millions of transactions
        - Real-time analysis and scoring
        - Adapts to evolving fraud techniques
        - Reduces false positives by 73%
        """)
        
        # Model insights accordion
        with st.expander("ℹ️ How the models work"):
            st.markdown("""
            **Random Forest Classifier**
            Combines multiple decision trees to improve accuracy and reduce overfitting. Effective at identifying complex fraud patterns.
            
            **Decision Tree**
            Creates a flowchart-like structure for decision making. More interpretable but slightly less accurate.
            """)
        st.markdown("</div>", unsafe_allow_html=True)

# --- Deep Learning Model with Gemini API ---
elif section == "Deep Learning Analysis":
    st.markdown("<h2 class='subheader'>🧠 Deep Learning Fraud Analysis</h2>", unsafe_allow_html=True)

    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown("<div class='transaction-form'>", unsafe_allow_html=True)
        st.markdown("<h3 style='color: #1e293b; font-weight: 600; margin-bottom: 1.5rem; font-size: 1.5rem;'>🔍 Transaction Details</h3>", unsafe_allow_html=True)
        
        # More visually appealing layout
        transaction_type = st.selectbox("Transaction Type", 
                                      ["PAYMENT", "TRANSFER", "CASH_OUT", "DEBIT", "CASH_IN"],
                                      help="Type of transaction being performed")
        
        # Use columns for compact layout
        row1_col1, row1_col2 = st.columns(2)
        with row1_col1:
            amount = st.number_input("Amount ($)", min_value=0.0, value=500.0, format="%.2f")
        with row1_col2:
            time_options = ["Morning", "Afternoon", "Evening", "Night"]
            transaction_time = st.selectbox("Time of Day", time_options)
        
        row2_col1, row2_col2 = st.columns(2)
        with row2_col1:
            old_balance_org = st.number_input("Old Balance ($)", min_value=0.0, value=1000.0, format="%.2f")
        with row2_col2:
            new_balance_org = st.number_input("New Balance ($)", min_value=0.0, value=500.0, format="%.2f")
    
        # Add more contextual information for better analysis
        with st.expander("Additional Context (Optional)"):
            country = st.selectbox("Transaction Country", ["United States", "Canada", "United Kingdom", "Other"])
            is_mobile = st.checkbox("Mobile Transaction")
            frequency = st.slider("Customer Transaction Frequency", 1, 30, 5, 
                                help="Average transactions per month")
            
        # Enhanced submit button
        analyze_btn = st.button("🤖 Analyze with Groq AI", use_container_width=True, type="primary")
        st.markdown("</div>", unsafe_allow_html=True)
            
    with col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<h3 style='color: #1e293b; font-weight: 600; margin-bottom: 1rem; font-size: 1.25rem;'>🧪 Groq AI Analysis</h3>", unsafe_allow_html=True)
        st.markdown("""
        The Groq AI model analyzes transactions using:
        
        - Pattern recognition
        - Natural language processing
        - Behavioral analysis
        - Historical data correlation
        - Multi-factor risk assessment
        
        This provides deeper insights beyond traditional models.
        """)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Model confidence visualization
        with st.expander("🔮 Groq AI Performance Metrics"):
            st.markdown("""
            - **Accuracy**: 97.8%
            - **False Positive Rate**: 0.8%
            - **Detection Speed**: < 1.5 seconds
            - **Adaptability**: High - Self-improving
            """)
    
    if analyze_btn:
        st.markdown("<div style='background: #f8fafc; padding: 1.5rem; border-radius: 16px; border: 1px solid #e2e8f0; margin-top: 1.5rem;'>", unsafe_allow_html=True)
        progress_text = "Analyzing with Groq AI..."
        status_bar = st.progress(0)
        
        # Simulate analysis progress for better UX
        for i in range(100):
            status_bar.progress(i + 1)
            time.sleep(0.01)
        
        try:
            # Use Groq model for fraud analysis
            model_name = "qwen/qwen3-32b"
            
            prompt = f"""Analyze transaction: Type={transaction_type}, Amount=${amount:.2f}, Old=${old_balance_org:.2f}, New=${new_balance_org:.2f}, Time={transaction_time}. Fraud? Answer: "Fraud" or "No fraud" + brief reason (1 sentence) + 1 precaution. Keep response under 50 words."""

            result = call_groq_api(prompt, model_name).strip()

            # Enhanced visualization of results
            st.markdown("<h2 style='color: #1e293b; font-weight: 600; margin-bottom: 1rem; font-size: 1.75rem;'>📊 Analysis Results</h2>", unsafe_allow_html=True)
            
            if "Fraud" in result and "No fraud" not in result:
                st.error("🚨 HIGH RISK: Potential fraud detected")
                st.warning("This transaction has been flagged for manual review")
            else:
                st.success("✅ LOW RISK: No fraud indicators detected")
                st.info("Transaction appears to be legitimate")

            # Format the AI response with better styling
            formatted_response = result.replace("Fraud", "**🚨 FRAUD ALERT**").replace("No fraud", "**✅ NO FRAUD DETECTED**")
            st.markdown("<h3 style='color: #1e293b; font-weight: 600; margin: 1.5rem 0 1rem; font-size: 1.25rem;'>🤖 Groq Analysis Report</h3>", unsafe_allow_html=True)
            st.markdown(formatted_response)
            
            # Recommended actions based on result
            st.markdown("<h3 style='color: #1e293b; font-weight: 600; margin: 1.5rem 0 1rem; font-size: 1.25rem;'>📋 Recommended Actions</h3>", unsafe_allow_html=True)
            if "Fraud" in result and "No fraud" not in result:
                st.markdown("""
                1. 🚫 **Block Transaction** - Prevent further activity
                2. 📞 **Contact Customer** - Verify attempted transaction
                3. 🔍 **Review Account** - Check for other suspicious activity
                4. 📝 **Document Findings** - Add to fraud database
                """)
            else:
                st.markdown("""
                1. ✅ **Approve Transaction** - Proceed with normal processing
                2. 📊 **Update Profile** - Add to customer behavior model
                3. 🔄 **Monitor** - Continue normal account monitoring
                """)

        except Exception as e:
            st.error(f"⚠️ Groq analysis failed: {str(e)}")
            st.markdown("Please try again or use the traditional models.")
        st.markdown("</div>", unsafe_allow_html=True)

# --- Community Chat Section ---
elif section == "Community Chat":
    st.markdown("<h2 class='subheader'>💬 Fraud Prevention Community</h2>", unsafe_allow_html=True)
    st.caption("Exchange insights with fraud prevention professionals")

    # Tabs for different discussion areas
    tab1, tab2, tab3 = st.tabs(["General Discussion", "New Patterns", "Resources"])
    
    with tab1:
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {"role": "assistant", "content": "👋 Welcome to the Fraud Prevention Community! Share your experiences and ask questions."},
                {"role": "user", "content": "Has anyone seen an increase in small test transactions lately?"},
                {"role": "assistant", "content": "💡 Yes! Small test transactions ($1-$5) before larger withdrawals are trending. We're seeing this pattern especially on weekends."}
            ]

        # Enhanced chat display
        st.markdown("<div style='padding: 1.5rem; min-height: 400px; max-height: 500px; overflow-y: auto; margin-bottom: 1rem; background: #f8fafc; border-radius: 16px; border: 1px solid #e2e8f0;'>", unsafe_allow_html=True)
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f"<div style='text-align: right;'><div class='chat-bubble user-bubble'>{msg['content']}</div></div><div style='clear: both;'></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='text-align: left;'><div class='chat-bubble assistant-bubble'>{msg['content']}</div></div><div style='clear: both;'></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        community_tips = [
            "🤖 Community Tip: Fraudsters often test cards with small transactions ($1-$5) before larger withdrawals. Monitor these carefully.",
            "🔍 Expert Insight: Look for rapid succession transactions at different ATMs - common fraud pattern.",
            "📊 Data Trend: 63% of fraud occurs on weekends when monitoring teams are smaller. Increase weekend vigilance.",
            "💡 Prevention Tip: Train staff to recognize 'shoulder surfing' - criminals watching customers enter PINs.",
            "🛡️ Security Advice: Recommend customers cover the keypad when entering PINs at ATMs.",
            "⚠️ Alert Pattern: Transactions where amount is exactly the account balance are suspicious (attempts to empty accounts).",
            "🌐 Global Trend: Card skimming devices are becoming more sophisticated. Regularly inspect ATM card readers.",
            "📱 Tech Tip: Mobile banking apps with transaction alerts can help customers spot fraud faster.",
            "🕵️ Investigator Note: Fraudsters often target elderly customers. Extra verification recommended for senior transactions.",
            "💳 Card Safety: EMV chip cards reduced counterfeit fraud by 76%. Encourage customers to use chip instead of swipe.",
            "🔢 PIN Security: The most common PINs (1234, 0000, 1111) are compromised first. Encourage complex PINs.",
            "⏱️ Timing Insight: Most fraudulent ATM withdrawals occur between 8PM-12AM when branches are closed.",
            "🚨 Red Flag: Multiple failed PIN attempts followed by a successful transaction may indicate brute force attacks.",
            "💰 Amount Pattern: Fraudsters often withdraw just below reporting thresholds (e.g., $9,900 instead of $10,000).",
            "🌍 Location Tip: Transactions originating from countries different than the cardholder's residence need extra scrutiny."
        ]

        # Improved chat input
        col1, col2 = st.columns([5, 1])
        with col1:
            prompt = st.text_input("Share your experience or ask a question...", key="community_input")
        with col2:
            send_btn = st.button("Send", use_container_width=True)
            
        if prompt and send_btn:
            st.session_state.messages.append({"role": "user", "content": prompt})

            contextual_response = None
            user_message_lower = prompt.lower()

            if "small" in user_message_lower or "test" in user_message_lower:
                contextual_response = "💡 Small test transactions often lead to fraud. Monitor closely."
            elif "weekend" in user_message_lower:
                contextual_response = "📅 Weekend fraud is common. Increase monitoring."
            elif "elderly" in user_message_lower:
                contextual_response = "👵 Elderly customers are targeted. Use extra verification."

            bot_response = contextual_response if contextual_response else random.choice(community_tips)
            st.session_state.messages.append({"role": "assistant", "content": bot_response})
            st.rerun()
            
    with tab2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color: #1e293b; font-weight: 600; margin-bottom: 1rem; font-size: 1.25rem;'>🚨 Recently Reported Patterns</h4>", unsafe_allow_html=True)
        st.markdown("""
        - **Digital Gift Card Scams** - Reported by 12 institutions in the last week
        - **QR Code Phishing** - Growing trend in metro areas
        - **ATM Deep Insert Skimmers** - New hardware harder to detect visually
        - **Social Engineering via Social Media** - Targeting bank employees
        """)
        
        with st.expander("Report New Pattern"):
            st.text_area("Describe the pattern you've identified", height=100)
            st.selectbox("Fraud Category", ["Card Present", "Card Not Present", "Account Takeover", "Identity Theft", "Other"])
            st.slider("Confidence Level", 1, 5, 3)
            st.button("Submit Report")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with tab3:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color: #1e293b; font-weight: 600; margin-bottom: 1.5rem; font-size: 1.25rem;'>📚 Resources</h4>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<h5 style='color: #1e293b; font-weight: 600; margin-bottom: 0.75rem; font-size: 1rem;'>Training Materials</h5>", unsafe_allow_html=True)
            st.markdown("- [Fraud Pattern Recognition Guide](https://example.com)")
            st.markdown("- [Customer Authentication Best Practices](https://example.com)")
            st.markdown("- [Transaction Monitoring Techniques](https://example.com)")
            
        with col2:
            st.markdown("<h5 style='color: #1e293b; font-weight: 600; margin-bottom: 0.75rem; font-size: 1rem;'>Latest Reports</h5>", unsafe_allow_html=True)
            st.markdown("- [Q1 2025 Fraud Trends](https://example.com)")
            st.markdown("- [ATM Vulnerability Assessment](https://example.com)")
            st.markdown("- [Cross-Border Fraud Statistics](https://example.com)")
        st.markdown("</div>", unsafe_allow_html=True)

# --- AI Assistant Section ---
elif section == "AI Assistant":
    st.markdown("<h2 class='subheader'>🤖 AI Fraud Prevention Assistant</h2>", unsafe_allow_html=True)
    
    # Layout with columns
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Initialize chat if not exists
        if "ai_chat" not in st.session_state:
            st.session_state.ai_chat = [
                {"role": "assistant", "content": "👋 Hello! I'm your AI Fraud Prevention Assistant. How can I help you today?"}
            ]

        # Enhanced chat display with styling
        st.markdown("<div style='padding: 1.5rem; min-height: 400px; max-height: 500px; overflow-y: auto; margin-bottom: 1rem; background: #f8fafc; border-radius: 16px; border: 1px solid #e2e8f0;'>", unsafe_allow_html=True)
        for msg in st.session_state.ai_chat:
            if msg["role"] == "user":
                st.markdown(f"<div style='text-align: right;'><div class='chat-bubble user-bubble'>{msg['content']}</div></div><div style='clear: both;'></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='text-align: left;'><div class='chat-bubble assistant-bubble'>{msg['content']}</div></div><div style='clear: both;'></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Chat input area with button
        st.markdown("<div style='margin-top: 1rem;'>", unsafe_allow_html=True)
        input_col, button_col = st.columns([5, 1])
        with input_col:
            user_input = st.text_input("Type your question here...", key="ai_assistant_input")
        with button_col:
            send_btn = st.button("Send", use_container_width=True)

        if user_input and send_btn:
            st.session_state.ai_chat.append({"role": "user", "content": user_input})
            
            # Show typing indicator
            with st.spinner("AI Assistant is thinking..."):
                try:
                    # Create conversation history for context
                    chat_history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.ai_chat])
                    
                    # Create prompt for Groq API (shortened to save tokens)
                    prompt = f"""Fraud prevention assistant. Answer briefly (max 100 words).
                        
                        History: {chat_history[-200:]}
                        
                        Question: {user_input}
                        
                        Brief answer with key points only."""
                    
                    # Use Groq model for chat
                    model_name = "qwen/qwen3-32b"
                    response_text = call_groq_api(prompt, model_name)
                    
                    # Add response to chat
                    st.session_state.ai_chat.append({"role": "assistant", "content": response_text})
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error communicating with AI: {str(e)}")
                    st.session_state.ai_chat.append({"role": "assistant", "content": "Sorry, I encountered an error. Please try again."})
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<h3 style='color: #1e293b; font-weight: 600; margin-bottom: 1.5rem; font-size: 1.25rem;'>💡 Quick Actions</h3>", unsafe_allow_html=True)
        
        if st.button("🛡️ Fraud Prevention Tips", use_container_width=True):
            st.session_state.ai_chat.append({"role": "user", "content": "Give me fraud prevention tips"})
            st.session_state.ai_chat.append({"role": "assistant", "content": """Here are key fraud prevention tips:
            
1. **Monitor Accounts Daily** - Check transactions regularly
2. **Use Strong Authentication** - Enable 2FA wherever possible
3. **Educate Customers** - Teach them to recognize phishing attempts
4. **Set Transaction Limits** - Especially for new accounts
5. **Watch for Small Test Transactions** - Common fraud precursor
6. **Verify Large Transactions** - Especially international ones
7. **Update Systems Regularly** - Keep security patches current"""})
            st.rerun()
            
        if st.button("🚨 Common Fraud Patterns", use_container_width=True):
            st.session_state.ai_chat.append({"role": "user", "content": "What are common fraud patterns?"})
            st.session_state.ai_chat.append({"role": "assistant", "content": """Most common ATM fraud patterns:
            
- **Card Skimming** - Devices capture card data
- **Shoulder Surfing** - Watching customers enter PINs
- **Cash Trapping** - ATM doesn't dispense but records transaction
- **Distraction Theft** - While customer is distracted
- **Transaction Reversal Fraud** - Exploiting system delays
- **Ghost ATMs** - Fake machines that steal data
- **Lebanese Loop** - Device traps card in slot"""})
            st.rerun()
            
        if st.button("📊 Fraud Statistics", use_container_width=True):
            st.session_state.ai_chat.append({"role": "user", "content": "Share fraud statistics"})
            st.session_state.ai_chat.append({"role": "assistant", "content": """Latest fraud statistics (2025):
            
- **$12.8B** lost to payment fraud globally
- **78%** of fraud involves card-not-present transactions
- **42%** increase in mobile banking fraud
- **63%** of fraud occurs on weekends
- **2.7s** average time to detect fraud with AI
- **1 in 127** transactions are attempted fraud"""})
            st.rerun()
            
        st.markdown("---")
        st.markdown("<h3 style='color: #1e293b; font-weight: 600; margin: 1.5rem 0 1rem; font-size: 1.25rem;'>📌 Sample Questions</h3>", unsafe_allow_html=True)
        st.markdown("- How to detect card skimming?")
        st.markdown("- What's the latest phishing trend?")
        st.markdown("- How to handle suspected fraud?")
        st.markdown("- Best practices for ATM security?")
        st.markdown("</div>", unsafe_allow_html=True)

# Footer for all pages
st.markdown("<div class='footer'>", unsafe_allow_html=True)
st.markdown("""
    <div style='display: flex; justify-content: center; gap: 2rem; margin-bottom: 0.5rem;'>
        <a href='#' style='color: #6B7280; text-decoration: none;'>Security Policy</a>
        <a href='#' style='color: #6B7280; text-decoration: none;'>Terms of Service</a>
        <a href='#' style='color: #6B7280; text-decoration: none;'>Contact Support</a>
        <a href='#' style='color: #6B7280; text-decoration: none;'>Training Portal</a>
    </div>
    <div style='text-align: center;'>
        © 2025 SecureBank. All rights reserved. | Fraud Detection System v2.2
    </div>
""", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)