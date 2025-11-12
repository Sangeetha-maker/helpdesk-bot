import random
from datetime import datetime

class MockZohoDeskAPI:
    def __init__(self):
        self.tickets = {
            "12345": {
                "ticketNumber": "12345",
                "subject": "Login Issue - Cannot access account",
                "status": "Open",
                "priority": "High",
                "createdTime": "2025-11-10T10:30:00Z",
                "modifiedTime": "2025-11-11T14:20:00Z",
                "assignee": {"name": "John Doe"},
                "description": "User unable to login with correct credentials"
            },
            "67890": {
                "ticketNumber": "67890",
                "subject": "Payment Processing Error",
                "status": "In Progress",
                "priority": "Medium",
                "createdTime": "2025-11-09T09:15:00Z",
                "modifiedTime": "2025-11-12T11:45:00Z",
                "assignee": {"name": "Jane Smith"},
                "description": "Transaction failed during checkout"
            },
            "11111": {
                "ticketNumber": "11111",
                "subject": "Feature Request - Dark Mode",
                "status": "Closed",
                "priority": "Low",
                "createdTime": "2025-11-05T16:00:00Z",
                "modifiedTime": "2025-11-08T12:30:00Z",
                "assignee": {"name": "Mike Johnson"},
                "description": "Request for dark mode in application"
            }
        }
    
    def refresh_access_token(self):
        return True
    
    def get_ticket(self, ticket_id):
        if str(ticket_id) in self.tickets:
            return {'success': True, 'data': self.tickets[str(ticket_id)]}
        return {'success': False, 'error': 'Ticket not found'}
    
    def create_ticket(self, subject, description, email, priority="High"):
        new_id = str(random.randint(20000, 99999))
        ticket = {
            "ticketNumber": new_id,
            "subject": subject,
            "description": description,
            "email": email,
            "status": "Open",
            "priority": priority,
            "createdTime": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "modifiedTime": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "assignee": {"name": "Support Team"}
        }
        self.tickets[new_id] = ticket
        return {'success': True, 'data': ticket}
    
    def add_comment(self, ticket_id, comment):
        if str(ticket_id) in self.tickets:
            return {'success': True, 'data': {'comment': comment, 'added': True}}
        return {'success': False, 'error': 'Ticket not found'}

def format_ticket_display(ticket_data):
    ticket = ticket_data.get('data', {})
    status_emoji = {'Open': '🔴', 'In Progress': '🟡', 'On Hold': '🟠', 'Closed': '🟢'}
    priority_emoji = {'High': '🔥', 'Medium': '⚠️', 'Low': '📌'}
    
    return f"""
### 📋 Ticket Details

**Ticket ID:** #{ticket.get('ticketNumber', 'N/A')}

**Status:** {status_emoji.get(ticket.get('status'), '⚪')} {ticket.get('status', 'Unknown')}

**Priority:** {priority_emoji.get(ticket.get('priority'), '📌')} {ticket.get('priority', 'Normal')}

**Subject:** {ticket.get('subject', 'No subject')}

**Created:** {ticket.get('createdTime', 'N/A')}

**Last Updated:** {ticket.get('modifiedTime', 'N/A')}

**Assigned To:** {ticket.get('assignee', {}).get('name', 'Unassigned')}

---
"""
