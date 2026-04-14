from django import forms
from blog.models import Category


TONE_CHOICES = [
    ("Intelligent and engaging, slightly informal", "Intelligent & Engaging"),
    ("Academic and thorough, evidence-based", "Academic & Thorough"),
    ("Conversational and friendly, storytelling-focused", "Conversational & Friendly"),
    ("Bold and opinionated, thought-leadership style", "Bold & Opinionated"),
    ("Technical and precise, developer-audience", "Technical & Precise"),
]


class GeneratePostForm(forms.Form):
    topic = forms.CharField(
        max_length=200,
        widget=forms.TextInput(
            attrs={
                "placeholder": "e.g. The Rise of Edge Computing in 2025",
                "class": "form-input",
                "autofocus": True,
            }
        ),
        label="Post Topic",
        help_text="Be specific. The more precise the topic, the better the output.",
    )
    target_audience = forms.CharField(
        max_length=200,
        initial="Curious, intelligent readers interested in technology and ideas",
        widget=forms.TextInput(
            attrs={
                "placeholder": "e.g. Software developers, startup founders",
                "class": "form-input",
            }
        ),
        label="Target Audience",
    )
    tone = forms.ChoiceField(
        choices=TONE_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Writing Tone",
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="— No category —",
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Assign Category (optional)",
    )
