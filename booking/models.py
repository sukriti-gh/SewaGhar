from django.db import models
from datetime import datetime
from django.contrib.auth.models import User

SERVICE_CHOICES = (
    ("Electrician", "Electrician"),
    ("Plumber", "Plumber"),
)

class VendorRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    business_name = models.CharField(max_length=255)
    business_address = models.TextField()
    contact_number = models.CharField(max_length=15)
    email = models.EmailField()
    business_description = models.TextField()
    business_category = models.CharField(max_length=255)
    experience = models.IntegerField(default='1')
    image = models.ImageField(upload_to='images', null=True, blank=True, default='/default_image.png')
    CA_image = models.ImageField(upload_to='images', null=True, blank=True, default='/default_image.png')
    CB_image = models.ImageField(upload_to='images', null=True, blank=True, default='/default_image.png')
    docs = models.FileField(upload_to='pdfs', null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} | {self.business_name} | {self.business_category}"

class Appointment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    service = models.CharField(max_length=50, choices=SERVICE_CHOICES, default="Electrician")
    day = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=200, blank=True)
    description = models.TextField(default='')
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    isFinished = models.CharField(max_length=15, default="No")
    accepted = models.BooleanField(default=False)
    rejected = models.BooleanField(default=False)
    time = models.CharField(max_length=10, null=True, blank=True)
    staff = models.CharField(max_length=50, default="Not assigned")
    payment_status = models.CharField(max_length=100, default='Cash On Delivery')
    rating = models.IntegerField(null=True, blank=True)
    rated = models.BooleanField(default=False)
    invoice_number = models.CharField(max_length=50, blank=True, null=True)
    dispute_created = models.BooleanField(default=False)
    dispute_resolved = models.BooleanField(default=False)
    tier = models.CharField(max_length=20, default="bronze")

    def update_credit_points(self):
        from sewaghar.booking.models import UserProfile  # path
        user_profile = UserProfile.objects.get(user=self.user)
        if self.isFinished == "Yes":
            user_profile.credit_points += 1
            if user_profile.credit_points > 10:
                user_profile.credit_points = 0
            user_profile.save()

# Signal to automatically update credit points when an Appointment is saved
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Appointment)
def update_credit_points(sender, instance, **kwargs):
    instance.update_credit_points()

class DeletedAppointment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service = models.CharField(max_length=50, choices=SERVICE_CHOICES, default="Electrician")
    day = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=200, blank=True)
    description = models.TextField(default='')
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    isFinished = models.CharField(max_length=15, default="No")
    accepted = models.BooleanField(default=False)
    rejected = models.BooleanField(default=False)
    time = models.CharField(max_length=10, null=True, blank=True)
    staff = models.CharField(max_length=50, default="Not assigned")
    payment_status = models.CharField(max_length=100, default='Cash On Delivery')
    rating = models.IntegerField(null=True, blank=True)
    rated = models.BooleanField(default=False)

    def update_credit_points(self):
        from sewaghar.booking.models import UserProfile  # updated path
        user_profile = UserProfile.objects.get(user=self.user)
        user_profile.credit_points -= 1
        user_profile.save()

    def __str__(self):
        return f"{self.user.username} | {self.service} | {self.day}"

@receiver(post_save, sender=DeletedAppointment)
def update_credit_points_deleted_appointment(sender, instance, **kwargs):
    instance.update_credit_points()

class Staff(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=255, unique=True, verbose_name='email address', default="")
    contact_number = models.CharField(max_length=100)
    assigned_user = models.CharField(max_length=100, default="")
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False, blank=True)
    tier = models.CharField(max_length=50, default="Not assigned")
    service = models.CharField(max_length=100)
    bio = models.TextField(default='')
    image = models.ImageField(upload_to='images', null=True, blank=True, default='/default_image.png')
    CA_image = models.ImageField(upload_to='images', null=True, blank=True, default='/default_image.png')
    CB_image = models.ImageField(upload_to='images', null=True, blank=True, default='/default_image.png')
    docs = models.FileField(upload_to='pdfs', null=True, blank=True)
    experience = models.IntegerField(default='1')
    TIER_CHOICES = [
        ('bronze', 'Bronze'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
    ]
    tier = models.CharField(max_length=10, choices=TIER_CHOICES, default='bronze')
    total_ratings = models.IntegerField(default=0)
    cumulative_rating = models.IntegerField(default=0)

    def update_rating(self, rating):
        self.total_ratings += 1
        self.cumulative_rating += rating
        self.save()

    def average_rating(self):
        if self.total_ratings == 0:
            return 0
        return self.cumulative_rating / self.total_ratings

    def __str__(self):
        return f"{self.name} | {self.tier} | {self.contact_number}" 

class Feedback(models.Model):
    date = models.DateField(auto_now=True)
    by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    message = models.CharField(max_length=500)
    acknowledged = models.BooleanField(default=False)
    TYPE_CHOICES = [
        ('complaint', 'Complaint'),
        ('feedback', 'Feedback'),
    ]
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='complaint')

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images', null=True, blank=True, default='images/default_image.png')
    contact_number = models.CharField(max_length=10, blank=True, null=True, default='')
    credit_points = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username}'s Profile"

User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])

class DeletedStaff(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=255, unique=True, verbose_name='email address', default="")

    def __str__(self):
        return f"{self.name} ({self.email})"
