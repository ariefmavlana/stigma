from django import forms
from blog.models import Category


TONE_CHOICES = [
    ("Intelligent and engaging, slightly informal", "Cerdas & Menarik / Intelligent & Engaging"),
    ("Academic and thorough, evidence-based", "Akademis & Mendalam / Academic & Thorough"),
    ("Conversational and friendly, storytelling-focused", "Santai & Bersahabat / Conversational & Friendly"),
    ("Bold and opinionated, thought-leadership style", "Berani & Tegas / Bold & Opinionated"),
    ("Technical and precise, developer-audience", "Teknis & Presisi / Technical & Precise"),
]

LANGUAGE_CHOICES = [
    ("Indonesian", "🇮🇩 Bahasa Indonesia"),
    ("English", "🇺🇸 English"),
]

class GeneratePostForm(forms.Form):
    topic = forms.CharField(
        max_length=200,
        widget=forms.TextInput(
            attrs={
                "placeholder": "contoh: Masa Depan Edge Computing di 2026",
                "class": "form-input",
                "autofocus": True,
                "id": "id_topic",
            }
        ),
        label="Topik Artikel / Post Topic",
        help_text="Semakin spesifik topik, semakin baik hasilnya. / The more specific, the better.",
    )
    target_audience = forms.CharField(
        max_length=200,
        initial="Pembaca cerdas yang tertarik dengan teknologi dan ide-ide baru",
        widget=forms.TextInput(
            attrs={
                "placeholder": "contoh: Developer, founder startup, mahasiswa",
                "class": "form-input",
                "list": "audience_list",
                "id": "id_target_audience",
            }
        ),
        label="Target Pembaca / Target Audience",
    )
    language = forms.ChoiceField(
        choices=LANGUAGE_CHOICES,
        initial="Indonesian",
        widget=forms.Select(attrs={
            "class": "form-select",
            "id": "id_language",
        }),
        label="Bahasa Output / Output Language",
    )
    tone = forms.ChoiceField(
        choices=TONE_CHOICES,
        widget=forms.Select(attrs={
            "class": "form-select",
            "id": "id_tone",
        }),
        label="Gaya Penulisan / Writing Tone",
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="— Tanpa Kategori / No Category —",
        widget=forms.Select(attrs={
            "class": "form-select",
            "id": "id_category",
        }),
        label="Kategori (opsional) / Category (optional)",
    )
