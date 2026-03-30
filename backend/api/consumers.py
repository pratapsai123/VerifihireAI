import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from django.core.cache import cache
from .models import InterviewInvitation

logger = logging.getLogger(__name__)

# Replaced in-memory cache with Redis distributed cache
async def get_screen_share_state(session_id):
    state = await database_sync_to_async(cache.get)(f"interview_{session_id}_screen_share")
    return state or {'locked': False, 'holder': None}

async def set_screen_share_state(session_id, state):
    await database_sync_to_async(cache.set)(f"interview_{session_id}_screen_share", state, timeout=86400)


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
        
        try:
            # 🔥 1. Validate session FIRST
            is_valid, error_reason = await self.validate_session()
            
            if not is_valid:
                logger.warning(f"WebSocket connection rejected: {error_reason} for session {self.session_id}")
                await self.accept()
                
                messages = {
                    'invalid': 'Invalid session ID. Please check your interview link.',
                    'expired': 'This interview session has expired or ended.',
                    'completed': 'This interview session has already been completed.',
                    'not_started': 'This interview session has not started yet.'
                }
                
                await self.send(text_data=json.dumps({
                    'type': 'session_expired',
                    'reason': error_reason,
                    'message': messages.get(error_reason, 'Invalid session.')
                }))
                await self.close(code=4003)
                return

            # 🔥 2. Handle presence and duplicate connections
            presence_key = f"interview_{self.session_id}_presence_{self.role}"
            old_channel = await database_sync_to_async(cache.get)(presence_key)
            
            if old_channel and old_channel != self.channel_name:
                logger.info(f"Replacing old connection for {self.role} in {self.session_id}")

            # Register current connection
            await database_sync_to_async(cache.set)(presence_key, self.channel_name, timeout=86400)

            # Mark as joined in DB
            await self.update_invitation_usage(has_joined=True)

            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            
            await self.accept()
            logger.info(f"WebSocket connected: {self.role} for session {self.session_id}")
            
            # Send current screen share state to new connection
            session_state = await get_screen_share_state(self.session_id)
            if session_state.get('locked'):
                await self.send(text_data=json.dumps({
                    'type': 'screen_share_lock',
                    'active': True,
                    'holder': session_state.get('holder'),
                }))
            
            # Initialize or get start time for synchronization
            start_time_key = f"interview_{self.session_id}_start_time"
            start_time = await database_sync_to_async(cache.get)(start_time_key)
            if not start_time:
                start_time = timezone.now().isoformat()
                await database_sync_to_async(cache.set)(start_time_key, start_time, timeout=86400)
            
            # Send session info including start time to the connecting client
            await self.send(text_data=json.dumps({
                'type': 'session_info',
                'start_time': start_time,
                'role': self.role
            }))
            
            # Reconnection Sync: notify others
            msg_type = 'user_rejoined' if old_channel else 'user_joined'
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': msg_type,
                    'user': self.role.capitalize(),
                    'session_id': self.session_id,
                }
            )
        except Exception as e:
            logger.error(f"Error in WebSocket connect: {str(e)}", exc_info=True)
            try:
                await self.close(code=4000)
            except:
                pass

    
    async def disconnect(self, close_code):
        """
        Called when WebSocket connection is closed.
        """
        try:
            # Release screen share if this user was sharing
            session_state = await get_screen_share_state(self.session_id)
            if session_state.get('holder') == self.role:
                session_state['locked'] = False
                session_state['holder'] = None
                await set_screen_share_state(self.session_id, session_state)
                
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'screen_share_lock',
                        'active': False,
                        'holder': None,
                    }
                )
            
            # Prevent firing user_left if this disconnecting channel is replaced
            presence_key = f"interview_{self.session_id}_presence_{self.role}"
            current_channel = await database_sync_to_async(cache.get)(presence_key)
            
            if current_channel == self.channel_name:
                # Notify others that this user left (only if they are the primary)
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'user_left',
                        'user': self.role.capitalize(),
                        'session_id': self.session_id,
                    }
                )

                # 🔥 Check if this was the last user to leave
                await self.check_and_finalize_interview()

            # Leave room group
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            
            logger.info(f"WebSocket disconnected: {self.role} for session {self.session_id} (code: {close_code})")
        except Exception as e:
            logger.error(f"Error in WebSocket disconnect: {str(e)}", exc_info=True)
    
    async def receive(self, text_data):
        """
        Called when message is received from WebSocket.
        """
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            logger.debug(f"Received message type: {message_type} from {self.role}")
            
            # Handle different message types
            if message_type == 'client_ping':
                # Heartbeat - acknowledge to keep connection alive
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
                session_state = await get_screen_share_state(self.session_id)
                
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
                    await set_screen_share_state(self.session_id, session_state)
                    
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
                session_state = await get_screen_share_state(self.session_id)
                if data.get('active', False):
                    session_state['locked'] = True
                    session_state['holder'] = self.role
                    await set_screen_share_state(self.session_id, session_state)
                else:
                    if session_state.get('holder') == self.role:
                        session_state['locked'] = False
                        session_state['holder'] = None
                        await set_screen_share_state(self.session_id, session_state)
                
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
                session_state = await get_screen_share_state(self.session_id)
                if session_state.get('holder') == self.role:
                    session_state['locked'] = False
                    session_state['holder'] = None
                    await set_screen_share_state(self.session_id, session_state)
                    
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
                # Mark as completed in DB
                await self.update_invitation_usage(is_completed=True)
                
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
    
    async def disconnect_duplicate(self, event):
        """Disconnect this WebSocket due to a newer connection taking its place."""
        close_code = event.get('close_code', 4001)
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': 'Duplicate connection detected. Your session was opened in another tab.'
        }))
        await self.close(code=close_code)
    
    async def user_joined(self, event):
        """Send user joined notification to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'user_joined',
            'user': event['user'],
        }))
        
    async def user_rejoined(self, event):
        """Send user rejoined synchronization to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'user_rejoined',
            'user': event['user'],
            'message': 'User has reconnected.'
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
        # Send to all participants (including sender)
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
    def validate_session(self):
        """
        Check if interview session exists, is active, and is within valid time bounds.
        Returns: (is_valid, error_reason_string)
        """
        try:
            invitation = InterviewInvitation.objects.filter(token=self.session_id).first()
            if not invitation:
                return False, 'invalid'
            
            if invitation.is_completed:
                return False, 'completed'

            # Backward compatibility
            if invitation.status == 'completed':
                return False, 'completed'

            now = timezone.now()
            if invitation.start_time and now < invitation.start_time:
                return False, 'not_started'
                
            if invitation.end_time and now > invitation.end_time:
                return False, 'expired'
            
            return True, None
        except Exception as e:
            logger.error(f"Error validating session: {e}", exc_info=True)
            return False, 'invalid'

    @database_sync_to_async
    def update_invitation_usage(self, has_joined=None, is_completed=None):
        """Update invitation tracking fields."""
        try:
            invitation = InterviewInvitation.objects.filter(token=self.session_id).first()
            if invitation:
                if has_joined is not None:
                    invitation.has_joined = has_joined
                if is_completed is not None:
                    invitation.is_completed = is_completed
                    invitation.status = 'completed' if is_completed else invitation.status
                invitation.save()
        except Exception as e:
            logger.error(f"Error updating invitation usage: {e}")

    async def check_and_finalize_interview(self):
        """Check if all participants have left and mark as completed if so."""
        try:
            # Check presence for both roles
            roles = ['interviewer', 'candidate']
            any_present = False
            for r in roles:
                presence_key = f"interview_{self.session_id}_presence_{r}"
                if await database_sync_to_async(cache.get)(presence_key):
                    any_present = True
                    break
            
            if not any_present:
                # Everyone has left, check if session was ever 'active' (has_joined=True)
                # and mark as completed to prevent re-use of link.
                invitation = await database_sync_to_async(lambda: InterviewInvitation.objects.filter(token=self.session_id).first())()
                if invitation and invitation.has_joined:
                    logger.info(f"All participants left session {self.session_id}. Marking as completed.")
                    await self.update_invitation_usage(is_completed=True)
        except Exception as e:
            logger.error(f"Error finalizing interview: {e}")

    @database_sync_to_async
    def check_session_expired(self):
        """Check if interview session is expired (legacy helper)"""
        try:
            invitation = InterviewInvitation.objects.filter(token=self.session_id).first()
            if invitation:
                if invitation.status == 'completed':
                    return True
                if invitation.end_time and timezone.now() > invitation.end_time:
                    return True
                return False
            return True # If not found, treat as expired/invalid
        except Exception as e:
            logger.error(f"Error checking session expiry: {e}")
            return False
