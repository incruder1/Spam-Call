from django.urls import path
from .views import register, login, search, mark_spam

urlpatterns = [
    path('register', register, name='register'),
    path('login', login, name='login'),
    path('search/', search, name='search'),
    path('spam', mark_spam, name='mark_spam'),
]
