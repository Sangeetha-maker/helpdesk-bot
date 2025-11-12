import streamlit as st
from mock_api import MockZohoDeskAPI as ZohoDeskAPI, format_ticket_display
import re

# Page configuration
st.set_page_config(
    page_title="Helpdesk Bot",
    page_icon="🎫",
    layout="wide"
)

# Initialize API
@st.cache_resource
def get_api():
    return ZohoDeskAPI()

zoho = get_api()

# Sidebar
with st.sidebar:
    st.title("🎫 Helpdesk Bot")
    st.markdown("---")
    
    menu = st.radio(
        "Navigation",
        ["💬 Chat", "🆕 Create Ticket", "🔍 Search Tickets"]
    )
    
    st.markdown("---")
    st.info("**Quick Actions:**\n- Check ticket: Type ticket ID\n- Create ticket: Use form\n- Add comment: Use chat")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "👋 Hello! I'm your helpdesk assistant. How can I help you today?\n\n- Check ticket status\n- Create new ticket\n- Add comments"}
    ]

# Function to process chat messages
def process_message(user_input, api):
    # Extract ticket ID from message
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
        
        1️⃣ **Check Ticket Status** - Just type or paste your ticket ID
        2️⃣ **Create New Ticket** - Use the sidebar menu
        3️⃣ **Search Tickets** - Use the search option in sidebar
        
        Try typing a ticket ID like: 12345
        """
    
    else:
        return "I didn't quite understand that. You can:\n- Type a ticket ID to check status\n- Type 'help' for more options\n- Use the sidebar menu for other actions"

# CHAT INTERFACE
if menu == "💬 Chat":
    st.title("💬 Chat Support")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Type your message..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Process user input
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = process_message(prompt, zoho)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

# CREATE TICKET INTERFACE
elif menu == "🆕 Create Ticket":
    st.title("🆕 Create New Ticket")
    
    with st.form("create_ticket_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            email = st.text_input("📧 Your Email *", placeholder="your@email.com")
            subject = st.text_input("📝 Subject *", placeholder="Brief description of issue")
        
        with col2:
            priority = st.selectbox("⚡ Priority", ["Low", "Medium", "High"])
        
        description = st.text_area("📄 Description *", placeholder="Describe your issue in detail...", height=150)
        
        submitted = st.form_submit_button("🚀 Create Ticket", use_container_width=True)
        
        if submitted:
            if not email or not subject or not description:
                st.error("❌ Please fill all required fields marked with *")
            else:
                with st.spinner("Creating ticket..."):
                    result = zoho.create_ticket(subject, description, email, priority)
                    
                    if result['success']:
                        ticket = result['data']
                        st.success(f"✅ Ticket created successfully!")
                        st.balloons()
                        
                        st.info(f"""
                        **Ticket Number:** #{ticket.get('ticketNumber')}
                        
                        **Status:** {ticket.get('status')}
                        
                        You will receive updates via email at: {email}
                        """)
                    else:
                        st.error(f"❌ Failed to create ticket: {result['error']}")

# SEARCH TICKETS INTERFACE
elif menu == "🔍 Search Tickets":
    st.title("🔍 Search Tickets")
    
    ticket_id = st.text_input("Enter Ticket ID:", placeholder="e.g., 12345")
    
    if st.button("🔍 Search", use_container_width=True):
        if ticket_id:
            with st.spinner("Searching..."):
                result = zoho.get_ticket(ticket_id)
                
                if result['success']:
                    st.markdown(format_ticket_display(result))
                    
                    # Action buttons
                    st.markdown("### Actions")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        comment = st.text_area("💬 Add Comment:", placeholder="Type your comment here...")
                    
                    with col2:
                        st.write("")
                        st.write("")
                        if st.button("📤 Send Comment", use_container_width=True):
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
