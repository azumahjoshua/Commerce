from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    # username = models.CharField(max_length=30)
    watchlist = models.ManyToManyField('Listing',related_name='watchers',blank=True) # to be completed

    def __str__(self):
        return self.username
    
    
class Listing(models.Model):
     # Categories - choices
    MOTORS = "MOT"
    FASHINON = "FAS"
    ELECTRONICS = "ELE"
    COLLECTIBLES_ARTS = "ART"
    HOME_GARDES = "HGA"
    SPORTING_GOODS = "SPO"
    TOYS = "TOY"
    BUSSINES_INDUSTRIAL = "BUS"
    MUSIC = "MUS"

    CATEGORY = [
        (MOTORS, "Motors"),
        (FASHINON, "Fashion"),
        (ELECTRONICS, "Electronics"),
        (COLLECTIBLES_ARTS, "Collectibles & Art"),
        (HOME_GARDES, "Home & Garden"),
        (SPORTING_GOODS, "Sporting Goods"),
        (TOYS, "Toys"),
        (BUSSINES_INDUSTRIAL, "Business & Industrial"),
        (MUSIC, "Music"),
    ]
    title = models.CharField(max_length=100)
    description = models.TextField()
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    current_price = models.DecimalField(max_digits=10, decimal_places=2,null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE,related_name="listings_created")
    category = models.CharField(max_length=3, choices=CATEGORY, default=MOTORS)
    image_url = models.URLField(blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    active_status = models.BooleanField(default=True)
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True,related_name="listings_won")

    def __str__(self):
        return self.title
    

class Bid(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    bid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    bid_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.bidder.username} bid ${self.bid_amount} on {self.listing.title}"
    

class Comment(models.Model):
    commenter = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    comment_text = models.TextField()
    comment_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.commenter.username} on {self.listing.title}"
