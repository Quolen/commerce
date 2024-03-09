from django.urls import path

from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_listing", views.create_listing, name="create_listing"),
    path("listings/<int:listing_id>", views.listing_detail, name="listing_detail"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("categories", views.categories, name="categories"),
    path('categories/<str:category>', views.category_listings, name='category_listings'),
    path('place_bid/<int:listing_id>', views.place_bid, name="place_bid"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
