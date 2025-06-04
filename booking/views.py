from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Event, Venue, Seat, Booking,SeatCategory
from .forms import EventForm, VenueForm, SeatForm
from django.http import HttpResponse
from django.shortcuts import render
from .models import Event  # Импортируем модель мероприятий
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import CustomUserCreationForm  # Кастомная форма регистрации (опционально)
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from itertools import groupby
from operator import attrgetter

# Кастомный класс для входа с дополнительными настройками
class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    form_class = AuthenticationForm
    redirect_authenticated_user = True  # Перенаправляет уже авторизованных пользователей

    def get_success_url(self):
        return reverse_lazy('booking:home')

    def form_invalid(self, form):
        # Дополнительная обработка неверных данных
        return self.render_to_response(self.get_context_data(form=form, error=True))


class CustomLogoutView(LogoutView):
    @method_decorator(require_POST)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

# Регистрация с использованием класса (более современный подход)
class RegisterView(CreateView):
    template_name = 'registration/register.html'
    form_class = UserCreationForm  # Или CustomUserCreationForm для кастомной формы
    success_url = reverse_lazy('booking:home')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)  # Автоматический вход после регистрации
        return response


# Альтернативная версия регистрации через функцию (если предпочитаете)
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('booking:home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


# Проверка на администратора
def is_admin(user):
    return user.is_staff


# Защищенное представление для обычных пользователей
@login_required
def user_profile(request):
    # Профиль пользователя
    return render(request, 'registration/profile.html', {'user': request.user})


def home(request):
    # Получаем активные мероприятия
    events = Event.objects.filter(is_published=True).order_by('date_time')[:5]

    context = {
        'title': 'Главная страница',
        'events': events,
    }
    return render(request, 'booking/home.html', context)

def about_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id, is_published=True)
    return render(request, 'booking/about_event.html', {'event': event})


def event_list(request):
    events = Event.objects.filter(is_published=True)
    return render(request, 'booking/event_list.html', {'events': events})


@login_required
def event_detail(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    seats = Seat.objects.filter(venue=event.venue).order_by('row', 'number')
    categories = SeatCategory.objects.all()
    # Группируем места по рядам
    seat_rows = []
    for row, seats_in_row in groupby(seats, key=attrgetter('row')):
        seat_rows.append(list(seats_in_row))

    return render(request, 'booking/event_detail.html', {
        'event': event,
        'seat_rows': seat_rows,
        'seat_categories': categories,
    })

@login_required
@user_passes_test(is_admin)
def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            event.save()
            messages.success(request, 'Event created successfully!')
            return redirect('event_detail', event_id=event.id)
    else:
        form = EventForm()
    return render(request, 'booking/create_event.html', {'form': form})


# views.py
@login_required
def book_seat(request, event_id, seat_id):
    event = get_object_or_404(Event, pk=event_id)
    seat = get_object_or_404(Seat, pk=seat_id)

    # Проверяем, не забронировано ли уже место
    if Booking.objects.filter(event=event, seat=seat).exists():
        messages.error(request, 'Это место уже забронировано!')
        return redirect('event_detail', event_id=event.id)

    # Создаем бронирование
    Booking.objects.create(
        event=event,
        user=request.user,
        seat=seat,
        is_confirmed=True
    )

    messages.success(request, f'Место {seat.row}-{seat.number} успешно забронировано!')
    return redirect('event_detail', event_id=event.id)

def book_seats(request, event_id):
    if not request.user.is_authenticated:
        messages.error(request, "Для бронирования необходимо войти в систему.")
        return redirect('booking:login')

    event = get_object_or_404(Event, id=event_id)

    if request.method == 'POST':
        selected_seats_ids = request.POST.get('selected_seats', '').split(',')
        selected_seats_ids = [int(id) for id in selected_seats_ids if id.isdigit()]

        if not selected_seats_ids:
            messages.error(request, "Не выбрано ни одного места.")
            return redirect('booking:event_detail', event_id=event_id)

        # Проверяем, что места еще не забронированы
        available_seats = Seat.objects.filter(
            id__in=selected_seats_ids,
            event=event,
            is_booked=False
        )

        if available_seats.count() != len(selected_seats_ids):
            messages.error(request, "Некоторые из выбранных мест уже заняты.")
            return redirect('booking:event_detail', event_id=event_id)

        # Создаем бронирование
        try:
            for seat in available_seats:
                Booking.objects.create(
                    user=request.user,
                    event=event,
                    seat=seat
                )
                seat.is_booked = True
                seat.save()

            messages.success(request, "Места успешно забронированы!")
            return redirect('booking:event_detail', event_id=event_id)

        except Exception as e:
            messages.error(request, f"Произошла ошибка при бронировании: {str(e)}")
            return redirect('booking:event_detail', event_id=event_id)

    return redirect('booking:event_detail', event_id=event_id)

@login_required
def venue_editor(request, venue_id=None):
    if venue_id:
        venue = get_object_or_404(Venue, pk=venue_id)
    else:
        venue = None

    if request.method == 'POST':
        form = VenueForm(request.POST, request.FILES, instance=venue)
        if form.is_valid():
            venue = form.save()
            messages.success(request, 'Venue saved successfully!')
            return redirect('venue_editor', venue_id=venue.id)
    else:
        form = VenueForm(instance=venue)

    seats = Seat.objects.filter(venue=venue) if venue else []

    return render(request, 'booking/venue_editor.html', {
        'form': form,
        'venue': venue,
        'seats': seats
    })


@login_required
def edit_seat(request, seat_id):
    seat = get_object_or_404(Seat, pk=seat_id)

    if request.method == 'POST':
        form = SeatForm(request.POST, instance=seat)
        if form.is_valid():
            form.save()
            messages.success(request, 'Seat updated successfully!')
            return redirect('venue_editor', venue_id=seat.venue.id)
    else:
        form = SeatForm(instance=seat)

    return render(request, 'booking/edit_seat.html', {
        'form': form,
        'seat': seat
    })