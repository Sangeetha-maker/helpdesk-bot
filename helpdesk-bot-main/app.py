from streamlit_lottie import st_lottie
import streamlit as st
from mock_api import MockZohoDeskAPI as ZohoDeskAPI, format_ticket_display
import re
import requests

# ----- Custom THEME CSS (Dark background and accent colors) -----
st.markdown("""
    <style>
    body, [data-testid="stAppViewContainer"], [data-testid="stHeader"], .css-1d391kg {background-color: #191c24 !important;}
    h1, h2, h3, h4, h5, h6, div, code, p, span, label {
        color: #f7f7fb !important;
        font-weight: bold !important;
        letter-spacing: 0.02em;
    }
    .big-font {font-size:30px !important; color:#1598FF;text-shadow: 0 0 18px #FF914D;}
    .stButton>button, button {
        background-color: #1598FF !important;
        color: #fff !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        border: none !important;
        box-shadow: 0 0 10px #1598FF44 !important;
        transition: background 0.2s;
    }
    .stButton>button:hover, button:hover {
        background-color: #FF914D !important;
        color: #fff !important;
    }
    [data-testid="stSidebar"], section[data-testid="stSidebar"] {
        background: linear-gradient(135deg, #232534 80%, #1598FF 100%) !important;
        color: #fff !important;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] h4, [data-testid="stSidebar"] h5, [data-testid="stSidebar"] h6, 
    [data-testid="stSidebar"] div, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label {
        color: #fff !important;
        text-shadow: 0 0 4px #1598FFCC;
        font-weight: bold !important;
    }
    .glass-card {background: rgba(21,152,255,0.08); border-radius:18px; padding:26px 34px 22px 34px;
        box-shadow:0 8px 28px rgba(255,145,77,0.13); margin-bottom:22px;}
    .accent-title {color: #FF914D !important; text-shadow: 0 0 12px #1598FF;}
    .accent-hr {border: 1px solid #FF914D; border-radius: 6px; margin-bottom: 12px;}
        
    /* --- Make Priority Dropdown Options Visible in Black --- */
    [data-baseweb="select"] > div {
        color: #000 !important;
        background-color: #fff !important;
    }
    [data-baseweb="select"] div[role="option"] {
        color: #000 !important;
        background-color: #fff !important;
        font-weight: bold !important;
    }
    [data-baseweb="select"] div[role="option"]:hover {
        background-color: #e8e8e8 !important;
        color: #000 !important;
    }
    </style>
""", unsafe_allow_html=True)

# ----- Modern UI Functions -----
def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

def show_banner():
    st.markdown('<p class="big-font">Welcome to your smart helpdesk assistant!</p>', unsafe_allow_html=True)
    lottie_url = "https://assets10.lottiefiles.com/packages/lf20_jcikwtux.json"
    lottie_ticket = load_lottieurl(lottie_url)
    st_lottie(lottie_ticket, height=200, key="ticket")

def modern_section_header(icon, title):
    st.markdown(f"""
        <div style="display:flex; align-items:center; gap:12px;">
          <span style="font-size:2.4rem;">{icon}</span>
          <span class="accent-title" style="font-size:2.1rem;">{title}</span>
        </div>
        <hr class="accent-hr">
    """, unsafe_allow_html=True)

def glass_card_box(content):
    st.markdown(f"""
        <div class="glass-card">
        {content}
        </div>
    """, unsafe_allow_html=True)

def progress_meter(step:int, total:int, label:str):
    percent = int(float(step) / total * 100)
    st.markdown(f"""
        <div style="font-size:1rem; color:#FF914D; font-weight:bold;">{label}</div>
        <progress value="{percent}" max="100" style="width:94%;height:16px; accent-color:#1598FF;"></progress>
    """, unsafe_allow_html=True)

# ----- Page configuration -----
st.set_page_config(
    page_title="Helpdesk Bot",
    page_icon="🎫",
    layout="wide"
)

# ----- Initialize API -----
@st.cache_resource
def get_api():
    return ZohoDeskAPI()
zoho = get_api()

# ----- Sidebar -----
with st.sidebar:
    st.image("logo.png", width=120)  # Optional: add/remove your own logo file here
    st.title("🎫 Helpdesk Bot")
    st.markdown("---")
    menu = st.radio(
        "Navigation",
        ["💬 Chat", "🆕 Create Ticket", "🔍 Search Tickets"]
    )
    st.markdown("---")
    st.markdown("""
    <div style='background:#24272B; padding:16px; border-radius:12px; border-left:6px solid #FF6600; color:#FFF;'>
    <span style="font-size:1.08rem;color:#FF914D;font-weight: bold;">Quick Actions:</span><br>
    - Check ticket: Type ticket ID<br>
    - Create ticket: Use form<br>
    - Add comment: Use chat
    </div>
""", unsafe_allow_html=True)


# ----- Initialize session state -----
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "👋 Hello! I'm your helpdesk assistant. How can I help you today?\n\n- Check ticket status\n- Create new ticket\n- Add comments"}
    ]

# ----- Function to process chat messages -----
def process_message(user_input, api):
    ticket_match = re.search(r'\b\d{5,}\b', user_input)
    if ticket_match:
        ticket_id = ticket_match.group()
        result = api.get_ticket(ticket_id)
        if result['success']:
            return format_ticket_display(result)
        else:
            return f"❌ {result['error']}"
    elif "create" in user_input.lower() or "new ticket" in user_input.lower():
        return "Please use the '🆕 Create Ticket' option in the sidebar to create a new ticket."
    elif "help" in user_input.lower():
        return """
        I can help you with:

        <span style="color:#1598FF;font-weight:bold;">1️⃣ Check Ticket Status</span> - Just type or paste your ticket ID  
        <span style="color:#1598FF;font-weight:bold;">2️⃣ Create New Ticket</span> - Use the sidebar menu  
        <span style="color:#1598FF;font-weight:bold;">3️⃣ Search Tickets</span> - Use the search option in sidebar  
        
        Try typing a ticket ID like: <span style='color:#FF914D'>12345</span>
        """
    else:
        return "I didn't quite understand that. You can:<br>- Type a ticket ID to check status<br>- Type 'help' for more options<br>- Use the sidebar menu for other actions"

# ----------------- CHAT INTERFACE -----------------
if menu == "💬 Chat":
    modern_section_header("💬", "Smart Helpdesk Chat")
    show_banner()
    glass_card_box(
      "<b style='color:#FF914D;'>Tip:</b> Type your ticket ID or a request (e.g. 'create new ticket') below!"
    )

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"], unsafe_allow_html=True)

    # Floating chat input
    if prompt := st.chat_input("🔥 Send a message to the bot..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt, unsafe_allow_html=True)
        # Process user input
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = process_message(prompt, zoho)
                st.markdown(response, unsafe_allow_html=True)
                st.session_state.messages.append({"role": "assistant", "content": response})

# ----------------- CREATE TICKET INTERFACE -----------------
elif menu == "🆕 Create Ticket":
    modern_section_header("🆕", "Create a New Ticket")
    show_banner()
    progress_meter(1, 3, "Step 1: Enter Details")
    with st.form("create_ticket_form"):
        col1, col2 = st.columns(2)
        with col1:
            email = st.text_input("📧 Your Email *", placeholder="your@email.com")
            subject = st.text_input("📝 Subject *", placeholder="Brief description of issue")
        with col2:
            priority = st.selectbox("⚡ Priority", ["Low", "Medium", "High"])
        description = st.text_area("📄 Description *", placeholder="Describe your issue in detail...", height=150)
        submitted = st.form_submit_button("🚀 CREATE TICKET", use_container_width=True)
        if submitted:
            progress_meter(2, 3, "Step 2: Creating Ticket...")
            if not email or not subject or not description:
                st.error("❌ Please fill all required fields marked with *")
            else:
                with st.spinner("Creating ticket..."):
                    result = zoho.create_ticket(subject, description, email, priority)
                    if result['success']:
                        ticket = result['data']
                        st.success("✅ Ticket created successfully!")
                        st.balloons()
                        progress_meter(3, 3, "Step 3: Ticket Created!")
                        glass_card_box(f"""
                            <b style='color:#1598FF;'>Ticket Number:</b> <span style='color:#FF914D;'>#{ticket.get('ticketNumber')}</span><br>
                            <b style='color:#1598FF;'>Status:</b> {ticket.get('status')}<br>
                            You will receive updates via email at: <span style='color:#FF914D;'>{email}</span>
                        """)
                    else:
                        st.error(f"❌ Failed to create ticket: {result['error']}")

# ----------------- SEARCH TICKETS INTERFACE -----------------
elif menu == "🔍 Search Tickets":
    modern_section_header("🔍", "Search and Manage Tickets")
    show_banner()
    glass_card_box(
      "🔎 <span style='color:#1598FF;font-weight:bold;'>Enter a ticket ID</span> to search for status, add comments, or take action."
    )
    ticket_id = st.text_input("Enter Ticket ID:", placeholder="e.g., 12345")
    if st.button("🔍 SEARCH", use_container_width=True):
        if ticket_id:
            with st.spinner("Searching..."):
                result = zoho.get_ticket(ticket_id)
                if result['success']:
                    glass_card_box(format_ticket_display(result))
                    st.markdown("### <span class='accent-title'>Actions</span>", unsafe_allow_html=True)
                    col1, col2 = st.columns(2)
                    with col1:
                        comment = st.text_area("💬 Add Comment:", placeholder="Type your comment here...")
                    with col2:
                        st.write("")
                        st.write("")
                        if st.button("📤 SEND COMMENT", use_container_width=True):
                            if comment:
                                result = zoho.add_comment(ticket_id, comment)
                                if result['success']:
                                    st.success("✅ Comment added!")
                                else:
                                    st.error("❌ Failed to add comment")
                            else:
                                st.warning("⚠️ Please enter a comment")
                else:
                    st.error(f"❌ {result['error']}")
        else:
            st.warning("⚠️ Please enter a ticket ID")
