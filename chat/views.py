from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Conversation, Chats
from django.db.models import Q

@login_required
def chat_index(request):
    context = {}
    conversations = Chats.objects.filter(Q(sender=request.user) | Q(receiver=request.user)).select_related('user1','user2')
    return render(request, 'chat_index.html', context=context)



 