from django import forms
from .models import Comment


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["author_name", "author_email", "body"]
        widgets = {
            "author_name": forms.TextInput(
                attrs={"placeholder": "Your name", "class": "form-input"}
            ),
            "author_email": forms.EmailInput(
                attrs={"placeholder": "your@email.com", "class": "form-input"}
            ),
            "body": forms.Textarea(
                attrs={
                    "placeholder": "Share your thoughts…",
                    "class": "form-textarea",
                    "rows": 5,
                }
            ),
        }
        labels = {
            "author_name": "Name",
            "author_email": "Email",
            "body": "Comment",
        }
