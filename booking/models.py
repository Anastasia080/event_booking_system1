from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _  # Импортируем функцию перевода

class Venue(models.Model):
    name = models.CharField(_('Название заведения'), max_length=100)
    address = models.TextField(_('Адрес'))
    capacity = models.PositiveIntegerField(_('Вместимость'))
    description = models.TextField(_('Описание'), blank=True)
    layout_image = models.ImageField(
        _('Схема зала'),
        upload_to='venue_layouts/',
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = _('Место проведения')
        verbose_name_plural = _('Места проведения')

    def __str__(self):
        return self.name

class Event(models.Model):
    title = models.CharField(_('Название мероприятия'), max_length=200)
    description = models.TextField(_('Описание мероприятия'))
    date_time = models.DateTimeField(_('Дата и время проведения'))
    venue = models.ForeignKey(
        Venue,
        verbose_name=_('Место проведения'),
        on_delete=models.CASCADE
    )
    organizer = models.ForeignKey(
        User,
        verbose_name=_('Организатор'),
        on_delete=models.CASCADE
    )
    price = models.DecimalField(
        _('Цена билета'),
        max_digits=10,
        decimal_places=2
    )
    is_published = models.BooleanField(
        _('Опубликовано'),
        default=False
    )

    class Meta:
        verbose_name = _('Мероприятие')
        verbose_name_plural = _('Мероприятия')

    def __str__(self):
        return f"{self.title} ({self.venue.name})"

class Seat(models.Model):
    venue = models.ForeignKey(
        Venue,
        verbose_name=_('Место проведения'),
        on_delete=models.CASCADE
    )
    row = models.CharField(_('Ряд'), max_length=10)
    number = models.PositiveIntegerField(_('Номер места'))
    category = models.CharField(_('Категория места'), max_length=50)
    x_coord = models.PositiveIntegerField(_('Координата X'))
    y_coord = models.PositiveIntegerField(_('Координата Y'))

    class Meta:
        verbose_name = _('Место')
        verbose_name_plural = _('Места')

    def __str__(self):
        return f"{_('Ряд')} {self.row}, {_('Место')} {self.number}"

class Booking(models.Model):
    event = models.ForeignKey(
        Event,
        verbose_name=_('Мероприятие'),
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        User,
        verbose_name=_('Пользователь'),
        on_delete=models.CASCADE
    )
    seat = models.ForeignKey(
        Seat,
        verbose_name=_('Место'),
        on_delete=models.CASCADE
    )
    booking_time = models.DateTimeField(
        _('Время бронирования'),
        auto_now_add=True
    )
    is_confirmed = models.BooleanField(
        _('Подтверждено'),
        default=False
    )

    class Meta:
        verbose_name = _('Бронирование')
        verbose_name_plural = _('Бронирования')
        unique_together = ('event', 'seat')

    def __str__(self):
        return f"{self.user.username} - {self.event.title}"