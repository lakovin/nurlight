from django import forms

from .phones import normalize_phone

PHONE_ERROR = "Укажите номер в формате +7 700 000 00 00"


def clean_phone_value(value: str) -> str:
    phone = normalize_phone(value)
    if phone is None:
        raise forms.ValidationError(PHONE_ERROR)
    return phone


class CheckoutForm(forms.Form):
    name = forms.CharField(label="Имя", max_length=255, widget=forms.TextInput(attrs={"placeholder": "Как к вам обращаться", "autocomplete": "name"}))
    phone = forms.CharField(label="Телефон", max_length=32, widget=forms.TextInput(attrs={"placeholder": "+7 (___) ___-__-__", "autocomplete": "tel", "inputmode": "tel"}))
    address = forms.CharField(label="Адрес", max_length=500, widget=forms.TextInput(attrs={"placeholder": "Улица, дом, квартира", "autocomplete": "street-address"}))
    comment = forms.CharField(label="Комментарий для курьера", required=False, widget=forms.Textarea(attrs={"rows": 3, "placeholder": "Код домофона, подъезд, этаж — по желанию"}))

    def clean_phone(self):
        return clean_phone_value(self.cleaned_data["phone"])


class OrderLookupForm(forms.Form):
    number = forms.CharField(label="Номер заказа", max_length=12, widget=forms.TextInput(attrs={"placeholder": "Например, 000123", "inputmode": "numeric"}))
    phone = forms.CharField(label="Телефон из заказа", max_length=32, widget=forms.TextInput(attrs={"placeholder": "+7 (___) ___-__-__", "inputmode": "tel"}))

    def clean_number(self):
        digits = self.cleaned_data["number"].strip().lstrip("№#")
        if not digits.isdigit() or int(digits) == 0:
            raise forms.ValidationError("Номер заказа — это цифры, например 000123")
        return int(digits)

    def clean_phone(self):
        return clean_phone_value(self.cleaned_data["phone"])
