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

    def __str__(self):
        return self.name

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


from django.db import models
from django.utils.translation import gettext_lazy as _


class SeatCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Название категории"))
    price = models.PositiveIntegerField(verbose_name=_("Цена"))
    color = models.CharField(max_length=20, default='#4CAF50', verbose_name=_("Цвет для отображения"))

    class Meta:
        verbose_name = _("Категория мест")
        verbose_name_plural = _("Категории мест")

    def __str__(self):
        return f"{self.name} ({self.price} руб.)"


class Seat(models.Model):
    venue = models.ForeignKey(
        'Venue',
        on_delete=models.CASCADE,
        verbose_name=_("Зал"),
        related_name='seats'
    )
    row = models.PositiveIntegerField(verbose_name=_("Ряд"))
    number = models.PositiveIntegerField(verbose_name=_("Номер места"))
    x_coord = models.PositiveIntegerField(verbose_name=_("Координата X"), blank=True, null=True)
    y_coord = models.PositiveIntegerField(verbose_name=_("Координата Y"), blank=True, null=True)
    is_booked = models.BooleanField(default=False, verbose_name=_("Забронировано"))
    category = models.ForeignKey(
        SeatCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Категория места")
    )
    price = models.PositiveIntegerField(
        verbose_name=_("Цена"),
        null=True,
        blank=True,
        help_text=_("Если не указана, будет использована цена из категории или события")
    )

    class Meta:
        verbose_name = _("Место")
        verbose_name_plural = _("Места")
        unique_together = [['venue', 'row', 'number']]
        ordering = ['row', 'number']

    def __str__(self):
        return f"{_('Ряд')} {self.row}, {_('Место')} {self.number}"

    def get_price(self, event):
        """Возвращает цену места с приоритетом: место > категория > событие"""
        if self.price:
            return self.price
        if self.category and self.category.price:
            return self.category.price
        return event.price

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