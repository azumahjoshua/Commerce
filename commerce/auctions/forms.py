from django import forms

from .models import Listing,Bid,Comment


class ListingForm(forms.ModelForm):
    # category = forms.ChoiceField(required=True,choices=Category.CATEGORY)
    class Meta:
        model = Listing
        fields = ['title', 'description', 'starting_bid', 'category', 'image_url']

class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['bid_amount']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment_text']

