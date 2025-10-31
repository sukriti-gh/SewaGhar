from django.contrib import admin
from .models import *

admin.site.register(Appointment)
admin.site.register(Staff)
admin.site.register(VendorRequest)
admin.site.register(Feedback)
admin.site.register(UserProfile)
admin.site.register(DeletedAppointment)
admin.site.register(DeletedStaff)