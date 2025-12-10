from django.contrib import admin
from .models import agentModel, ConversationHistory
# Register your models here.

admin.site.register(agentModel)
admin.site.register(ConversationHistory)
