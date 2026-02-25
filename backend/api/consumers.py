import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import InterviewInvitation

logger = logging.getLogger(__name__)

# In-memory store for screen share state per session
# In production, use Redis or database for distributed systems
_screen_share_state = {}


class InterviewConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for live interview signaling.
    Handles WebRTC signaling, chat, screen sharing, and other interview features.
    """
    
    async def connect(self):
        """
        Called when WebSocket connection is established.
        URL pattern: /ws/interview/{session_id}/{role}/
        """
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.role = self.scope['url_route']['kwargs']['role']  # 'interviewer' or 'candidate'
        self.room_group_name = f'interview_{self.session_id}'
        
        # Initialize screen share state for this session if not exists
        if self.session_id not in _screen_share_state:
            _screen_share_state[self.session_id] = {
                'locked': False,
                'holder': None
            }
        
        try:
            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            
            await self.accept()
            
            logger.info(f"Γ£à WebSocket connected: {self.role} for session {self.session_id}")
            
            # Send current screen share state to new connection
            session_state = _screen_share_state.get(self.session_id, {})
            if session_state.get('locked'):
                await self.send(text_data=json.dumps({
                    'type': 'screen_share_lock',
                    'active': True,
                    'holder': session_state.get('holder'),
                }))
            
            # Notify others that this user joined
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_joined',
                    'user': self.role.capitalize(),
                    'session_id': self.session_id,
                }
            )
            
            # Check if session is expired
            is_expired = await self.check_session_expired()
            if is_expired:
                await self.send(text_data=json.dumps({
                    'type': 'session_expired',
                    'message': 'Session has already been completed.'
                }))
                await self.close()
                return

        except Exception as e:
            logger.error(f"Error in WebSocket connect: {str(e)}", exc_info=True)
            # Try to close with error code if possible, or just let it fail
            try:
                await self.close(code=4000)
            except:
                pass

    
    async def disconnect(self, close_code):
        """
        Called when WebSocket connection is closed.
        """
        # Release screen share if this user was sharing
        session_state = _screen_share_state.get(self.session_id, {'locked': False, 'holder': None})
        if session_state.get('holder') == self.role:
            session_state['locked'] = False
            session_state['holder'] = None
            _screen_share_state[self.session_id] = session_state
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'screen_share_lock',
                    'active': False,
                    'holder': None,
                }
            )
        
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        logger.info(f"≡ƒöî WebSocket disconnected: {self.role} for session {self.session_id} (code: {close_code})")
        
        # Notify others that this user left
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_left',
                'user': self.role.capitalize(),
                'session_id': self.session_id,
            }
        )
    
    async def receive(self, text_data):
        """
        Called when message is received from WebSocket.
        """
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            logger.debug(f"≡ƒô⌐ Received message type: {message_type} from {self.role}")
            
            # Handle different message types
            if message_type == 'client_ping':
                # Heartbeat - just acknowledge
                await self.send(text_data=json.dumps({
                    'type': 'server_pong',
                    'ts': data.get('ts')
                }))
                return
            
            # Forward signaling messages to the other peer
            if message_type in ['video_offer', 'video_answer', 'ice_candidate', 'request_offer']:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'forward_message',
                        'message': data,
                        'sender': self.role,
                    }
                )
            
            # Handle chat messages
            elif message_type == 'chat':
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': data.get('message', ''),
                        'sender': self.role,
                        'original_sender': data.get('sender', self.role.capitalize()),
                    }
                )
            
            # Handle media state changes
            elif message_type == 'media_state':
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'media_state_change',
                        'media': data.get('media'),
                        'enabled': data.get('enabled'),
                        'sender': self.role,
                    }
                )
            
            # Handle screen share requests
            elif message_type == 'screen_share_request':
                session_state = _screen_share_state.get(self.session_id, {'locked': False, 'holder': None})
                
                # Check if someone else is already sharing
                if session_state.get('locked') and session_state.get('holder') != self.role:
                    # Deny request - someone else is sharing
                    await self.send(text_data=json.dumps({
                        'type': 'screen_share_denied',
                        'reason': f'{session_state.get("holder")} is already sharing',
                    }))
                else:
                    # Grant request and lock
                    session_state['locked'] = True
                    session_state['holder'] = self.role
                    _screen_share_state[self.session_id] = session_state
                    
                    # Notify all participants about the lock
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'screen_share_lock',
                            'active': True,
                            'holder': self.role.capitalize(),
                        }
                    )
                    
                    # Grant to requester
                    await self.send(text_data=json.dumps({
                        'type': 'screen_share_granted',
                    }))
            
            # Handle screen share state (when someone starts/stops sharing)
            elif message_type == 'screen_share_state':
                # Update local state
                if data.get('active', False):
                    session_state = _screen_share_state.get(self.session_id, {'locked': False, 'holder': None})
                    session_state['locked'] = True
                    session_state['holder'] = self.role
                    _screen_share_state[self.session_id] = session_state
                else:
                    session_state = _screen_share_state.get(self.session_id, {'locked': False, 'holder': None})
                    if session_state.get('holder') == self.role:
                        session_state['locked'] = False
                        session_state['holder'] = None
                        _screen_share_state[self.session_id] = session_state
                
                # Broadcast state to all participants
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'screen_share_state',
                        'active': data.get('active', False),
                        'sender': self.role,
                    }
                )
            
            # Handle screen share lock
            elif message_type == 'screen_share_lock':
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'screen_share_lock',
                        'active': data.get('active', False),
                        'holder': data.get('holder'),
                    }
                )
            
            # Handle screen share release
            elif message_type == 'screen_share_release':
                # Release lock if this user was holding it
                session_state = _screen_share_state.get(self.session_id, {'locked': False, 'holder': None})
                if session_state.get('holder') == self.role:
                    session_state['locked'] = False
                    session_state['holder'] = None
                    _screen_share_state[self.session_id] = session_state
                    
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'screen_share_lock',
                            'active': False,
                            'holder': None,
                        }
                    )
                
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'screen_share_release',
                        'releaser': self.role,
                    }
                )
            
            # Handle screen share granted (response to request)
            elif message_type == 'screen_share_granted':
                # Forward grant to requester
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'screen_share_granted',
                    }
                )
            
            # Handle end interview
            elif message_type == 'end_interview':
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'end_interview',
                        'initiated_by': self.role,
                    }
                )
            
            # Handle proxy violations (from candidate)
            elif message_type == 'proxy_violation':
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'proxy_violation',
                        'violation_type': data.get('violation_type'),
                        'violation_count': data.get('violation_count'),
                        'violation_limit': data.get('violation_limit'),
                        'sender': self.role,
                    }
                )
            
            else:
                logger.warning(f"Unknown message type: {message_type}")
        
        except json.JSONDecodeError:
            logger.error("Invalid JSON received")
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
    
    # Handler methods for group messages
    
    async def user_joined(self, event):
        """Send user joined notification to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'user_joined',
            'user': event['user'],
        }))
    
    async def user_left(self, event):
        """Send user left notification to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'user_left',
            'user': event['user'],
        }))
    
    async def forward_message(self, event):
        """Forward signaling message to other peer (don't send back to sender)"""
        if event['sender'] != self.role:
            await self.send(text_data=json.dumps(event['message']))
    
    async def chat_message(self, event):
        """Send chat message to WebSocket - send to all participants"""
        # Send to all participants (including sender, so they can see it in their UI if needed)
        await self.send(text_data=json.dumps({
            'type': 'chat',
            'message': event['message'],
            'sender': event['original_sender'],
        }))
    
    async def media_state_change(self, event):
        """Send media state change to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'media_state',
            'media': event['media'],
            'enabled': event['enabled'],
            'sender': event['sender'],
        }))
    
    async def screen_share_request(self, event):
        """Handle screen share request - this is called when someone requests screen share"""
        # This handler is called for other participants when a request comes in
        # The actual grant/deny logic is handled in the receive() method
        # This is just for notification purposes
        pass
    
    async def screen_share_state(self, event):
        """Send screen share state to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'screen_share_state',
            'active': event['active'],
            'sender': event.get('sender'),
        }))
    
    async def screen_share_lock(self, event):
        """Send screen share lock to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'screen_share_lock',
            'active': event['active'],
            'holder': event.get('holder'),
        }))
    
    async def screen_share_release(self, event):
        """Handle screen share release - notify all participants"""
        await self.send(text_data=json.dumps({
            'type': 'screen_share_release',
            'releaser': event.get('releaser'),
        }))
    
    async def screen_share_granted(self, event):
        """Send screen share granted notification to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'screen_share_granted',
        }))
    
    async def end_interview(self, event):
        """Send end interview notification to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'end_interview',
            'initiated_by': event['initiated_by'],
        }))
    
    async def proxy_violation(self, event):
        """Send proxy violation notification to WebSocket (only to interviewer)"""
        if self.role == 'interviewer':
            await self.send(text_data=json.dumps({
                'type': 'proxy_violation',
                'violation_type': event['violation_type'],
                'violation_count': event['violation_count'],
                'violation_limit': event['violation_limit'],
                'sender': event['sender'],
            }))
    
    @database_sync_to_async
    def check_session_expired(self):
        """Check if interview session is expired"""
        try:
            # Try to find interview invitation by token
            invitation = InterviewInvitation.objects.filter(token=self.session_id).first()
            if invitation:
                # Check if both parties have connected before (session expired)
                # This is a simple check - you might want to add a field to track this
                return False  # For now, allow reconnection
            return False
        except Exception as e:
            logger.error(f"Error checking session expiry: {e}")
            return False
