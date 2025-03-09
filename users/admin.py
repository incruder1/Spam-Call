from django.contrib import admin
from .models import User, Contact, Spam

admin.site.register(User)
admin.site.register(Contact)
admin.site.register(Spam)
