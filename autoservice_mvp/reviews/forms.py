from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4}),
            'rating': forms.RadioSelect(),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.service = kwargs.pop('service', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        review = super().save(commit=False)
        if self.user:
            review.user = self.user
        if self.service:
            review.service = self.service
        else:
            raise ValueError("ReviewForm requires 'service' to be set.")
        if commit:
            review.save()
        return review
