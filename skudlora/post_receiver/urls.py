from django.urls import path
from post_receiver.views import handle_post_request, hex_sent_view, send_post_request_ernets, parser

urlpatterns = [
    path('post_receiver/', handle_post_request, name='post_receiver'),
    path("hex_sent/", hex_sent_view, name="hex_sent"),
    path("send_post_request_ernets/", send_post_request_ernets, name="send_post_request_ernets"),
    path('parser/', parser, name ='parser'),
]

