from django.contrib import admin

# Register your models here.
from chat.models import Invitation
admin.site.register(Invitation)
from chat.models import ChatMessage
admin.site.add_action(ChatMessage)
