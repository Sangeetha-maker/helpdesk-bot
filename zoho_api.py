import requests
import streamlit as st
from datetime import datetime, timedelta

class ZohoDeskAPI:
    def __init__(self):
        self.base_url = st.secrets.get("ZOHO_API_DOMAIN", "https://desk.zoho.in")
        self.access_token = st.secrets.get("ZOHO_ACCESS_TOKEN", "")
        self.refresh_token = st.secrets.get("ZOHO_REFRESH_TOKEN", "")
        self.client_id = st.secrets.get("ZOHO_CLIENT_ID", "")
        self.client_secret = st.secrets.get("ZOHO_CLIENT_SECRET", "")
        self.org_id = st.secrets.get("ZOHO_ORG_ID", "")
        
    def refresh_access_token(self):
        """Refresh the access token using refresh token"""
        try:
            url = "https://accounts.zoho.in/oauth/v2/token"
            params = {
                "refresh_token": self.refresh_token,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "refresh_token"
            }
            
            response = requests.post(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                return True
            else:
                return False
        except Exception as e:
            return False
    
    def get_headers(self):
        """Get headers with current access token"""
        return {
            'Authorization': f'Zoho-oauthtoken {self.access_token}',
            'orgId': self.org_id,
            'Content-Type': 'application/json'
        }
    
    def make_request(self, method, url, **kwargs):
        """Make API request with automatic token refresh"""
        headers = self.get_headers()
        
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, **kwargs)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, **kwargs)
        else:
            return None
        
        # If token is invalid, refresh and retry
        if response.status_code == 401 or "INVALID_OAUTH" in response.text:
            if self.refresh_access_token():
                headers = self.get_headers()
                if method.upper() == "GET":
                    response = requests.get(url, headers=headers, **kwargs)
                else:
                    response = requests.post(url, headers=headers, **kwargs)
        
        return response
    
    def get_ticket(self, ticket_id):
        """Fetch ticket details by ID"""
        try:
            url = f"{self.base_url}/api/v1/tickets/{ticket_id}"
            response = self.make_request("GET", url)
            
            if response and response.status_code == 200:
                return {'success': True, 'data': response.json()}
            elif response and response.status_code == 404:
                return {'success': False, 'error': 'Ticket not found'}
            else:
                error_msg = response.json() if response else "Unknown error"
                return {'success': False, 'error': f'Error: {error_msg}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def create_ticket(self, subject, description, email, priority="High"):
        """Create a new ticket"""
        try:
            url = f"{self.base_url}/api/v1/tickets"
            payload = {
                "subject": subject,
                "description": description,
                "contactId": email,
                "email": email,
                "priority": priority,
                "status": "Open",
                "channel": "Chat"
            }
            
            response = self.make_request("POST", url, json=payload)
            
            if response and response.status_code == 200:
                return {'success': True, 'data': response.json()}
            else:
                error_text = response.text if response else "No response"
                return {'success': False, 'error': f'Error: {error_text}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def add_comment(self, ticket_id, comment):
        """Add comment to ticket"""
        try:
            url = f"{self.base_url}/api/v1/tickets/{ticket_id}/comments"
            payload = {"content": comment, "isPublic": True}
            response = self.make_request("POST", url, json=payload)
            
            if response and response.status_code == 200:
                return {'success': True, 'data': response.json()}
            else:
                return {'success': False, 'error': 'Failed to add comment'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

def format_ticket_display(ticket_data):
    """Format ticket data for display"""
    ticket = ticket_data.get('data', {})
    
    status_emoji = {
        'Open': '🔴',
        'In Progress': '🟡',
        'On Hold': '🟠',
        'Closed': '🟢'
    }
    
    priority_emoji = {
        'High': '🔥',
        'Medium': '⚠️',
        'Low': '📌'
    }
    
    return f"""
### 📋 Ticket Details

**Ticket ID:** #{ticket.get('ticketNumber', 'N/A')}

**Status:** {status_emoji.get(ticket.get('status'), '⚪')} {ticket.get('status', 'Unknown')}

**Priority:** {priority_emoji.get(ticket.get('priority'), '📌')} {ticket.get('priority', 'Normal')}

**Subject:** {ticket.get('subject', 'No subject')}

**Created:** {ticket.get('createdTime', 'N/A')}

**Last Updated:** {ticket.get('modifiedTime', 'N/A')}

**Assigned To:** {ticket.get('assignee', {}).get('name', 'Unassigned')}
"""
