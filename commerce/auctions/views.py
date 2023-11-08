from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render,redirect,get_object_or_404
from django.urls import reverse
from django.contrib import messages

from .models import *

from .forms import *


def index(request):
    listing = Listing.objects.all()
    return render(request, "auctions/index.html",{
        "listing" : listing

})


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

def create_listing(request):
    if request.method == "POST":
        form = ListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.created_by  = User.objects.get(pk=request.user.id)
            listing.current_price  = listing.starting_bid
            listing.save()
            return redirect('listing',listing_id=listing.id)
    else:
        form = ListingForm()
    return render(request, 'auctions/create_listing.html',{'form':form})



def listing(request,listing_id):
    user = User.objects.get(pk=request.user.id)
    listing = get_object_or_404(Listing, pk=listing_id)
    bid_form = BidForm()
    comment_form = CommentForm()
    comments = Comment.objects.filter(listing=listing)
    if request.method == "POST":
        if user.is_authenticated:
            if 'add_watchlist' in request.POST:
                if user.watchlist.filter(pk=listing_id).exists():
                    messages.info(request,"This item is already in your watchlist")
                else :
                    user.watchlist.add(listing)
                    messages.success(request,"Added successfully to your watchlist") 
            elif 'remove_watchlist' in request.POST: 
                user.watchlist.remove(listing)
                messages.success(request, "Item removed from your watchlist")
            elif 'place_bid' in request.POST:
                if user != listing.created_by:
                    bid_form = BidForm(request.POST)
                    # check if bid is valid
                    if bid_form.is_valid():
                        bid_amount = bid_form.cleaned_data['bid_amount']
                        if bid_amount >= listing.starting_bid and (listing.current_price is None or bid_amount > listing.current_price):
                            bid = Bid(bidder=user,listing=listing,bid_amount=bid_amount)
                            bid.save()
                            listing.current_price = bid_amount
                            listing.save()
                            messages.success(request,"Your bid is the highest bid")
                        elif listing.active_status:
                            messages.error(request, "Your bid should be higher.")
                    else:
                        messages.error(request, "Invalid bid amount. Please try again.")
                else:
                    messages.error(request,"You cannot bid on your own listing")
            elif 'close_auction' in request.POST:
                if user == listing.created_by:
                    if listing.bid_set.exists():
                        # Determine the highest bidder
                        highest_bid = listing.bid_set.order_by('-bid_amount').first()
                        winner = highest_bid.bidder
                        listing.winner = winner
                        listing.active_status = False
                        listing.save()
                        messages.success(request, f"Auction closed and {winner} is the highest bidder.")
                    else:
                        messages.error(request,"Auction cannot be closed with no bids")
                else:
                    messages.error(request, "Only the creator can close the auction.")
        else:
             # Handle error for unauthenticated users trying to place a bid
            messages.error(request, "You must be logged in to place a bid.")
    
    if request.method == 'POST' and 'add_comment' in request.POST:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.commenter = request.user
            comment.listing = listing
            comment.save()
            # messages.success(request, "Comment added successfully.")
            return redirect('listing', listing_id=listing_id)
    # print(comments_count)
    return render(request, 'auctions/listing.html', {
        'listing': listing,
        'user': user,
        'bid_form': bid_form,
        'comment_form': comment_form,
        'comments': comments
    })

def watchlist(request):
    user = User.objects.get(pk=request.user.id)
    watchlist_items = user.watchlist.all()
    count_watchlist = watchlist_items.count()
    # print(watchlist_items)
    return render(request,'auctions/watchlist.html', 
                  {'watchlist_items': watchlist_items,
                   'user':user,
                   'count':count_watchlist
                   })