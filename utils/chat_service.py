"""
Churchgate Group HRIS - Chat Service
Integrated Messaging & Collaboration System
"""

from datetime import datetime
import json

class ChatService:
    def __init__(self):
        self.channels = {}
        self.direct_messages = {}
        self.bot_responses = self._load_bot_responses()
        self._initialize_default_channels()
    
    def _initialize_default_channels(self):
        """Initialize default company channels"""
        default_channels = [
            {
                'name': 'general',
                'description': 'General company announcements and discussions',
                'members': ['all'],
                'type': 'public'
            },
            {
                'name': 'hr-announcements',
                'description': 'HR announcements and updates',
                'members': ['all'],
                'type': 'public'
            },
            {
                'name': 'technology',
                'description': 'ELV Systems and Technology discussions',
                'members': ['ELV Systems', 'IT'],
                'type': 'department'
            },
            {
                'name': 'operations',
                'description': 'Operations and Facilities Management',
                'members': ['MEP', 'Operations', 'FM'],
                'type': 'department'
            },
            {
                'name': 'leadership',
                'description': 'Leadership and Management discussions',
                'members': ['Admin', 'HR Director', 'Manager', 'Director', 'VP', 'C-Level'],
                'type': 'private'
            },
        ]
        
        for channel in default_channels:
            self.create_channel(
                channel['name'],
                channel['description'],
                channel['members'],
                channel['type']
            )
    
    def _load_bot_responses(self):
        """Load HRIS bot responses"""
        return {
            'greetings': [
                "Hello! How can I help you today?",
                "Hi there! What can I assist you with?",
                "Welcome! How may I help you?",
            ],
            'leave': [
                "You can apply for leave through the Employee Dashboard. Your current leave balance is available there.",
                "Leave requests are processed within 48 hours. Check your dashboard for status updates.",
            ],
            'performance': [
                "Your performance review is available in the Performance & OKRs section.",
                "You can set your OKRs and track progress in the Performance Management page.",
            ],
            'training': [
                "Check the Training & Development section for available courses and webinars.",
                "New training opportunities are posted weekly. Visit the Learning Hub for details.",
            ],
            'payroll': [
                "Payroll inquiries should be directed to the Finance department.",
                "Your pay stubs are available in your Employee Dashboard.",
            ],
            'default': [
                "I'm here to help! You can ask me about leave, performance, training, or general HR inquiries.",
                "For specific assistance, please contact HR at hr@churchgate.com.",
            ]
        }
    
    def create_channel(self, channel_name, description, members, channel_type='public'):
        """Create a new chat channel"""
        if channel_name not in self.channels:
            self.channels[channel_name] = {
                'name': channel_name,
                'description': description,
                'members': members,
                'type': channel_type,
                'messages': [],
                'created_at': datetime.now().isoformat(),
                'pinned_messages': []
            }
            return True, f"Channel '{channel_name}' created"
        return False, f"Channel '{channel_name}' already exists"
    
    def send_message(self, channel_name, sender_name, sender_dept, message, message_type='text'):
        """Send a message to a channel"""
        if channel_name not in self.channels:
            return False, f"Channel '{channel_name}' not found"
        
        message_obj = {
            'id': len(self.channels[channel_name]['messages']) + 1,
            'sender': sender_name,
            'department': sender_dept,
            'content': message,
            'type': message_type,
            'timestamp': datetime.now().isoformat(),
            'reactions': [],
            'replies': []
        }
        
        self.channels[channel_name]['messages'].append(message_obj)
        return True, message_obj
    
    def send_direct_message(self, from_user, to_user, message):
        """Send a direct message"""
        conversation_key = tuple(sorted([from_user, to_user]))
        
        if conversation_key not in self.direct_messages:
            self.direct_messages[conversation_key] = []
        
        message_obj = {
            'id': len(self.direct_messages[conversation_key]) + 1,
            'from': from_user,
            'to': to_user,
            'content': message,
            'timestamp': datetime.now().isoformat(),
            'read': False
        }
        
        self.direct_messages[conversation_key].append(message_obj)
        return True, message_obj
    
    def get_messages(self, channel_name, limit=50, before_timestamp=None):
        """Get messages from a channel"""
        if channel_name not in self.channels:
            return []
        
        messages = self.channels[channel_name]['messages']
        
        if before_timestamp:
            messages = [m for m in messages if m['timestamp'] < before_timestamp]
        
        return messages[-limit:]
    
    def get_direct_messages(self, user1, user2, limit=50):
        """Get direct messages between two users"""
        conversation_key = tuple(sorted([user1, user2]))
        
        if conversation_key not in self.direct_messages:
            return []
        
        return self.direct_messages[conversation_key][-limit:]
    
    def react_to_message(self, channel_name, message_id, user, reaction):
        """Add reaction to a message"""
        if channel_name not in self.channels:
            return False
        
        for msg in self.channels[channel_name]['messages']:
            if msg['id'] == message_id:
                msg['reactions'].append({
                    'user': user,
                    'reaction': reaction,
                    'timestamp': datetime.now().isoformat()
                })
                return True
        
        return False
    
    def pin_message(self, channel_name, message_id):
        """Pin a message in a channel"""
        if channel_name not in self.channels:
            return False
        
        self.channels[channel_name]['pinned_messages'].append(message_id)
        return True
    
    def get_channel_members(self, channel_name):
        """Get channel members"""
        if channel_name not in self.channels:
            return []
        return self.channels[channel_name]['members']
    
    def is_member(self, channel_name, user_dept, user_role):
        """Check if user can access a channel"""
        if channel_name not in self.channels:
            return False
        
        channel = self.channels[channel_name]
        members = channel['members']
        
        if 'all' in members:
            return True
        
        if user_dept in members or user_role in members:
            return True
        
        return False
    
    def get_bot_response(self, user_message):
        """Get HRIS bot response based on user message"""
        message_lower = user_message.lower()
        
        if any(word in message_lower for word in ['hi', 'hello', 'hey', 'greetings']):
            import random
            return random.choice(self.bot_responses['greetings'])
        
        if any(word in message_lower for word in ['leave', 'vacation', 'time off', 'holiday']):
            import random
            return random.choice(self.bot_responses['leave'])
        
        if any(word in message_lower for word in ['performance', 'review', 'appraisal', 'kpi']):
            import random
            return random.choice(self.bot_responses['performance'])
        
        if any(word in message_lower for word in ['training', 'course', 'learning', 'webinar']):
            import random
            return random.choice(self.bot_responses['training'])
        
        if any(word in message_lower for word in ['salary', 'pay', 'payroll', 'compensation']):
            import random
            return random.choice(self.bot_responses['payroll'])
        
        import random
        return random.choice(self.bot_responses['default'])
    
    def get_all_channels(self):
        """Get all channels"""
        return [
            {
                'name': ch['name'],
                'description': ch['description'],
                'type': ch['type'],
                'member_count': len(ch['members']),
                'message_count': len(ch['messages']),
                'last_activity': ch['messages'][-1]['timestamp'] if ch['messages'] else None
            }
            for ch in self.channels.values()
        ]
    
    def search_messages(self, channel_name, query):
        """Search messages in a channel"""
        if channel_name not in self.channels:
            return []
        
        results = []
        for msg in self.channels[channel_name]['messages']:
            if query.lower() in msg['content'].lower():
                results.append(msg)
        
        return results


# Test the chat service
if __name__ == "__main__":
    chat = ChatService()
    
    # Test channel creation
    chat.create_channel('test-channel', 'Test Channel', ['all'], 'public')
    
    # Test messaging
    chat.send_message('general', 'John Doe', 'Engineering', 'Hello everyone!')
    chat.send_message('general', 'Jane Smith', 'HR', 'Welcome John!')
    
    # Test bot
    response = chat.get_bot_response("I need help with my leave")
    print(f"Bot: {response}")
    
    print("✅ Chat service test complete")