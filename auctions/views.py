from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from auctions.forms import ListingForm

from .models import User, Listing, Bid, Category, Comment


def index(request):
    listings = Listing.objects.all()

    return render(request, "auctions/index.html", {
        "active_listings": listings
    })

def listing_detail(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)

    return render(request, "auctions/listing_detail.html", {
        "listing": listing
    })

def categories(request):
    categories = Category.objects.all()
    return render(request, 'auctions/category_list.html', {'categories': categories})

def category_listings(request, category):
    category_obj = get_object_or_404(Category, name=category)

    listings = Listing.objects.filter(category=category_obj, is_active=True)
    return render(request, "auctions/category_listings.html", {'listings': listings, 'category': category})

def watchlist(request):
    watchlist_listings = request.user.watchlist.all()

    if request.method == 'POST':
        listing_id = request.POST.get('listing_id')
        listing = Listing.objects.get(pk=listing_id)
        action = request.POST.get('action')

        if action == 'add':
            request.user.watchlist.add(listing)
            return redirect(reverse('listing_detail', args=[listing_id]))
        elif action == 'remove':
            request.user.watchlist.remove(listing)

    return render(request, "auctions/watchlist.html", {
        'watchlist_listings': watchlist_listings
    })

def create_listing(request):
    if request.method == "GET":
        form = ListingForm()
        return render(request, "auctions/create.html", {'form': form})
    elif request.method == "POST":
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            title = form.cleaned_data['title']
            description = form.cleaned_data['desc']
            starting_bid = form.cleaned_data['bid']
            image = form.cleaned_data['image']
            category_name = form.cleaned_data['category']

            # Get or create a Category instance
            category, created = Category.objects.get_or_create(name=category_name)

            listing = Listing.objects.create(
                title=title,
                description=description,
                starting_bid=starting_bid,
                image=image,
                category=category,
                author=request.user,
                is_active=True
            )

            return redirect('index')
        else:
            return render(request, "auctions/create.html", {'form': form})




def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
