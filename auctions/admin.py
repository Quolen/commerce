from django.contrib import admin
from .models import User, Category, Comment, Bid, Listing
# Register your models here.
admin.site.register(User)
admin.site.register(Category)
admin.site.register(Comment)
admin.site.register(Bid)
admin.site.register(Listing)