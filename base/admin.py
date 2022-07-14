from django.contrib import admin
from .models import Court, Room, Topic, message

admin.site.register(Room)
admin.site.register(Topic)
admin.site.register(message)
admin.site.register(Court)
