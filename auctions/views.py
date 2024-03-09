from pyexpat.errors import messages
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

def close_auction(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    highest_bid = listing.bids.order_by('-amount').first()
    
    listing.winner = highest_bid.bidder
    listing.is_active = False
    listing.save() 

    return redirect('listing_detail', listing_id)

def place_bid(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    error_message = None

    if request.method == "POST":
        bid_amount = request.POST.get('bid_amount')

        if bid_amount:
            try:
                bid_amount = float(bid_amount)
            except ValueError:
                error_message = "Invalid bid amount. Please enter a valid number."
            else:
                if request.user == listing.author:
                    error_message = "You cannot bid on your own listing."
                elif bid_amount >= listing.starting_bid and bid_amount > listing.current_bid_amount():
                    bid = Bid.objects.create(listing=listing, bidder=request.user, amount=bid_amount)
                else:
                    error_message = "Invalid bid. Please make sure it's at least as large as the starting bid and greater than any other bids placed."
        else:
            error_message = "Bid amount is required."

    highest_bid = listing.bids.order_by('-amount').first()

    return render(request, 'auctions/listing_detail.html', {'listing': listing, 'highest_bid': highest_bid, 'error_message': error_message})


def listing_detail(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)

    highest_bid = None
    if listing.bids.exists():
        highest_bid = listing.bids.order_by('-amount').first()

    return render(request, 'auctions/listing_detail.html', {'listing': listing, 'highest_bid': highest_bid})

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
