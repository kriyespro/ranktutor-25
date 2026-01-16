from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from .models import Conversation, Message
from bookings.models import Booking


@login_required
def conversations_list(request):
    """List all conversations for the user"""
    # Get conversations where user is participant1 or participant2
    conversations = Conversation.objects.filter(
        Q(participant1=request.user) | Q(participant2=request.user)
    ).order_by('-updated_at')
    
    # Get unread message counts for each conversation
    for conv in conversations:
        other_user = conv.participant2 if conv.participant1 == request.user else conv.participant1
        conv.other_user = other_user
        conv.unread_count = Message.objects.filter(
            conversation=conv,
            sender=other_user,
            is_read=False,
            is_deleted=False
        ).count()
    
    context = {
        'conversations': conversations,
    }
    return render(request, 'messaging/conversations.jinja', context)


@login_required
def conversation_detail(request, conversation_id):
    """View and send messages in a conversation"""
    conversation = get_object_or_404(
        Conversation.objects.filter(
            Q(participant1=request.user) | Q(participant2=request.user)
        ),
        id=conversation_id
    )
    
    # Get the other participant
    other_user = conversation.participant2 if conversation.participant1 == request.user else conversation.participant1
    
    # Check if contact should be revealed
    contact_revealed = conversation.contact_revealed
    if not contact_revealed and conversation.booking:
        # Reveal contact if booking is accepted
        if conversation.booking.status == 'accepted':
            conversation.contact_revealed = True
            conversation.save()
            contact_revealed = True
    
    # Get messages (exclude soft-deleted)
    message_list = Message.objects.filter(
        conversation=conversation,
        is_deleted=False
    ).order_by('created_at')
    
    # Mark messages as read (only non-deleted messages)
    Message.objects.filter(
        conversation=conversation,
        sender=other_user,
        is_read=False,
        is_deleted=False
    ).update(is_read=True, read_at=timezone.now())
    
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            try:
                message = Message.objects.create(
                    conversation=conversation,
                    sender=request.user,
                    content=content
                )
                # Update conversation timestamp
                conversation.updated_at = timezone.now()
                conversation.save()
                messages.success(request, 'Message sent!')
                return redirect('messaging:conversation_detail', conversation_id=conversation_id)
            except Exception as e:
                messages.error(request, f'Error sending message: {str(e)}')
                # Continue to render the page with error
        else:
            messages.error(request, 'Message cannot be empty.')
    
    context = {
        'conversation': conversation,
        'other_user': other_user,
        'conversation_messages': message_list,  # Renamed to avoid conflict with Django messages framework
        'contact_revealed': contact_revealed,
    }
    return render(request, 'messaging/conversation_detail.jinja', context)


@login_required
def start_conversation(request, user_id):
    """Start a new conversation with a user"""
    from users.models import User
    other_user = get_object_or_404(User, id=user_id)
    
    if other_user == request.user:
        messages.error(request, 'Cannot start conversation with yourself.')
        return redirect('/')
    
    # Check if conversation already exists
    conversation = Conversation.objects.filter(
        (Q(participant1=request.user) & Q(participant2=other_user)) |
        (Q(participant1=other_user) & Q(participant2=request.user))
    ).first()
    
    if not conversation:
        # Determine participant order (smaller ID first for consistency)
        if request.user.id < other_user.id:
            conversation = Conversation.objects.create(
                participant1=request.user,
                participant2=other_user
            )
        else:
            conversation = Conversation.objects.create(
                participant1=other_user,
                participant2=request.user
            )
    
    return redirect('messaging:conversation_detail', conversation_id=conversation.id)


@login_required
def start_conversation_from_booking(request, booking_id):
    """Start conversation from a booking"""
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Check access
    if booking.student != request.user and booking.tutor != request.user:
        messages.error(request, 'Access denied.')
        return redirect('/')
    
    other_user = booking.tutor if booking.student == request.user else booking.student
    
    # Create or get conversation
    if request.user.id < other_user.id:
        participant1, participant2 = request.user, other_user
    else:
        participant1, participant2 = other_user, request.user
    
    conversation, created = Conversation.objects.get_or_create(
        participant1=participant1,
        participant2=participant2,
        defaults={'booking': booking}
    )
    
    if not created and not conversation.booking:
        conversation.booking = booking
        conversation.save()
    
    return redirect('messaging:conversation_detail', conversation_id=conversation.id)
