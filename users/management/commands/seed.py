import os
import random
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from users.models import User, Contact, Spam

class Command(BaseCommand):
    help = 'Seed the database with sample data'

    def generate_unique_phone(self, base_phone):
        count = 1
        phone = base_phone
        
        while User.objects.filter(phone=phone).exists():
            phone = f"{base_phone}{count}"
            count += 1
            
        return phone

    def handle(self, *args, **kwargs):
        spam_numbers = []

        for i in range(10):
            user_phone = self.generate_unique_phone(f"987356789{i}")
            user = User.objects.create(
                username=f"User{i}",
                phone=user_phone,
                email=f"user{i}@gmail.com",
                password=make_password(f"user{i}_pass"),
            )

            for j in range(5):
                contact_phone = self.generate_unique_phone(f"97665432{i}{j}")
                Contact.objects.create(
                    name=f"Contact{j} of User{i}",
                    phone=contact_phone,
                    user=user,
                )

                if random.random() > 0.7:
                    spam_numbers.append(contact_phone)

            if random.random() > 0.5:
                spam_numbers.append(user_phone)

        for phone in set(spam_numbers):
            Spam.objects.update_or_create(
                phone=phone,
                defaults={'count': Spam.objects.filter(phone=phone).count() + 1}
            )

        self.stdout.write(self.style.SUCCESS('Database populated successfully!'))
