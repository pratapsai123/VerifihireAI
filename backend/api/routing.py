"""
WebSocket URL routing for interview signaling.
"""
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/interview/(?P<session_id>[^/]+)/(?P<role>interviewer|candidate)/?$', consumers.InterviewConsumer.as_asgi()),
    re_path(r'ws/interview/p/(?P<participant_token>[^/]+)/?$', consumers.InterviewConsumer.as_asgi()),
]
