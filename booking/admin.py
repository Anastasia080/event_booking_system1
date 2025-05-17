from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Venue, Event, Seat, Booking


class SeatInline(admin.TabularInline):
    model = Seat
    extra = 1
    verbose_name = _('Место')
    verbose_name_plural = _('Места')
    fields = ('row', 'number', 'category', 'x_coord', 'y_coord')


class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'capacity')
    list_display_links = ('name',)
    search_fields = ('name', 'address')
    inlines = [SeatInline]
    fieldsets = (
        (None, {
            'fields': ('name', 'address')
        }),
        (_('Дополнительная информация'), {
            'fields': ('capacity', 'description', 'layout_image'),
            'classes': ('collapse',)
        }),
    )


class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'venue', 'date_time', 'price', 'is_published')
    list_editable = ('is_published',)
    list_filter = ('is_published', 'venue')
    search_fields = ('title', 'description', 'venue__name')
    date_hierarchy = 'date_time'
    raw_id_fields = ('organizer',)
    ordering = ('-date_time',)
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'venue')
        }),
        (_('Дата и цена'), {
            'fields': ('date_time', 'price')
        }),
        (_('Публикация'), {
            'fields': ('is_published', 'organizer'),
            'classes': ('collapse',)
        }),
    )


class BookingAdmin(admin.ModelAdmin):
    list_display = ('event', 'user', 'seat', 'formatted_booking_time', 'is_confirmed')
    list_filter = ('is_confirmed', 'event__venue')
    search_fields = ('user__username', 'event__title')
    date_hierarchy = 'booking_time'
    list_select_related = ('event', 'user', 'seat')

    @admin.display(description=_('Время бронирования'))
    def formatted_booking_time(self, obj):
        return obj.booking_time.strftime("%d.%m.%Y %H:%M")


# Регистрация моделей
admin.site.register(Venue, VenueAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Booking, BookingAdmin)

# Настройки админ-панели
admin.site.site_header = _("Администрирование системы бронирования мероприятий")
admin.site.site_title = _("Система бронирования")
admin.site.index_title = _("Панель управления")