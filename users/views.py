from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import User, Contact, Spam
from .serializers import UserSerializer, SpamSerializer
import jwt
from .models import User  # Import your User model
from django.db.models import Q  # For complex queries
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@api_view(['POST'])
def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return JsonResponse({"message": "User registered", "user": UserSerializer(user).data}, status=201)
    return JsonResponse(serializer.errors, status=400)

# @csrf_exempt
@api_view(['POST'])
def login(request):
    phone = request.data.get('phone')
    password = request.data.get('password')
    user = get_object_or_404(User, phone=phone)
    if user.check_password(password):
        token = jwt.encode({'user_id': user.id}, settings.SECRET_KEY, algorithm='HS256')
        response = JsonResponse({"message": "Logged in", "token": token})
        response.set_cookie(key='jwt', value=token, httponly=True)
        return response
    return JsonResponse({"message": "Invalid credentials"}, status=401)


# The search view is used to search for users by username or email
@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search(request):
    query = request.GET.get('query', '').strip()  # Get the search query from the request
    user = request.user  # Get the currently authenticated user
    
    if not query:
        return JsonResponse({'error': 'No search query provided.'}, status=400)

    # Split query into name and phone number
    if query.isdigit():  # Check if the query is a phone number
        # Search for users by phone number
        users = User.objects.filter(phone=query)
        contacts = Contact.objects.filter(phone=query)
    else:  # Treat query as a name
        # Search for users by name
        name_starting_with = User.objects.filter(username__istartswith=query)
        name_containing = User.objects.filter(username__icontains=query).exclude(username__istartswith=query)
        users = name_starting_with | name_containing

        # Get the contacts associated with the current user for the name search
        contact_numbers = Contact.objects.filter(user=user).values_list('phone', flat=True)
        contacts = Contact.objects.filter(Q(name__istartswith=query) | Q(name__icontains=query), phone__in=contact_numbers)

    # Prepare the response data
    response_data = []

    # Include registered users and their spam likelihood
    for user in users:
        spam_likelihood = Spam.objects.filter(phone=user.phone).first()
        response_data.append({
            'id': user.id,
            'name': user.username,
            'phone': user.phone,
            'spam_likelihood': spam_likelihood.count if spam_likelihood else 0,
            'email': user.email if user in contacts else None  # Include email only if user is in contacts
        })

    # Include contacts
    for contact in contacts:
        spam_likelihood = Spam.objects.filter(phone=contact.phone).first()
        response_data.append({
            'id': contact.id,  # Assuming Contact model has an ID
            'name': contact.name,
            'phone': contact.phone,
            'spam_likelihood': spam_likelihood.count if spam_likelihood else 0,
            'email': None  # Emails are not included for contacts unless specified
        })

    return JsonResponse(response_data, safe=False)


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_spam(request):
    phone = request.data.get('phone')
    spam_entry, created = Spam.objects.get_or_create(phone=phone)
    spam_entry.count += 1
    spam_entry.save()
    return JsonResponse({"message": "Marked spam", "spam": SpamSerializer(spam_entry).data})
