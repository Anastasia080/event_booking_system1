from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Event, Venue, Seat
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'date_time', 'venue', 'price', 'is_published']
        widgets = {
            'date_time': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'form-control'
                }
            ),
        }
        labels = {
            'title': _('Название мероприятия'),
            'description': _('Описание'),
            'date_time': _('Дата и время'),
            'venue': _('Место проведения'),
            'price': _('Цена билета'),
            'is_published': _('Опубликовать мероприятие'),
        }
        help_texts = {
            'is_published': _('Отметьте, чтобы сделать мероприятие видимым для всех'),
        }

class VenueForm(forms.ModelForm):
    class Meta:
        model = Venue
        fields = ['name', 'address', 'capacity', 'description', 'layout_image']
        labels = {
            'name': _('Название заведения'),
            'address': _('Адрес'),
            'capacity': _('Вместимость'),
            'description': _('Описание'),
            'layout_image': _('Схема зала'),
        }

class SeatForm(forms.ModelForm):
    class Meta:
        model = Seat
        fields = ['row', 'number', 'x_coord', 'y_coord']
        labels = {
            'row': _('Ряд'),
            'number': _('Номер места'),
            'category': _('Категория'),
            'x_coord': _('Координата X'),
            'y_coord': _('Координата Y'),
        }