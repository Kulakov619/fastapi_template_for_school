from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.db.models import Count
from datetime import timedelta
from .models import Author, Genre, Book, BookInstance, Reader, BorrowHistory


# --- Inline-модели (вложенные списки) ---

class BookInstanceInline(admin.TabularInline):
    """Позволяет видеть экземпляры книги прямо в карточке Книги"""
    model = BookInstance
    extra = 0
    readonly_fields = ('id',)
    can_delete = False


class BorrowHistoryInline(admin.TabularInline):
    """История выдачи в карточке Читателя (только для чтения)"""
    model = BorrowHistory
    extra = 0
    fields = ('book_instance', 'borrow_date', 'due_date', 'return_date', 'was_returned_late_display')
    readonly_fields = ('borrow_date', 'return_date', 'was_returned_late_display')
    can_delete = False

    def was_returned_late_display(self, obj):
        return obj.was_returned_late

    was_returned_late_display.boolean = True
    was_returned_late_display.short_description = 'Просрочено'


# --- Основные модели ---

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'books_count')
    search_fields = ('last_name', 'first_name')
    ordering = ('last_name',)

    def get_queryset(self, request):
        # Оптимизация: считаем книги сразу в запросе
        qs = super().get_queryset(request)
        return qs.annotate(books_count=Count('books'))

    @admin.display(description='Кол-во книг', ordering='books_count')
    def books_count(self, obj):
        return obj.books_count


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('get_cover', 'title', 'get_authors', 'publication_date', 'isbn', 'language')
    list_filter = ('genres', 'language', 'publication_date')
    search_fields = ('title', 'isbn', 'authors__last_name')
    filter_horizontal = ('authors', 'genres')  # Удобный выбор для M2M
    inlines = [BookInstanceInline]
    readonly_fields = ('get_cover_large',)

    fieldsets = (
        ('Основная информация', {
            'fields': (('title', 'isbn'), 'authors', 'genres', 'language')
        }),
        ('Детали', {
            'fields': ('publication_date', 'pages', 'summary')
        }),
        ('Обложка', {
            'fields': ('cover_image', 'get_cover_large')
        }),
    )

    @admin.display(description='Обложка')
    def get_cover(self, obj):
        if obj.cover_image:
            return format_html('<img src="{}" style="width: 50px; height: auto;" />', obj.cover_image.url)
        return "-"

    @admin.display(description='Предпросмотр')
    def get_cover_large(self, obj):
        if obj.cover_image:
            return format_html('<img src="{}" style="max-height: 300px;" />', obj.cover_image.url)
        return "-"

    @admin.display(description='Авторы')
    def get_authors(self, obj):
        return ", ".join([a.last_name for a in obj.authors.all()])


# --- Кастомный фильтр для просроченных книг ---

class OverdueFilter(admin.SimpleListFilter):
    title = 'Просрочка'
    parameter_name = 'is_overdue'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Просроченные'),
            ('no', 'В срок'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            # Просрочена: есть дата возврата, она в прошлом и статус "Выдана"
            return queryset.filter(due_back__lt=timezone.localdate(), status='o')
        if self.value() == 'no':
            return queryset.filter(due_back__gte=timezone.localdate())


@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    list_display = ('inventory_number', 'book_link', 'status_colored', 'due_back', 'borrower_link', 'is_overdue_icon')
    list_filter = ('status', OverdueFilter, 'due_back')
    search_fields = ('inventory_number', 'book__title', 'id')
    autocomplete_fields = ('book', 'borrower')  # Чтобы не грузить выпадающий список из 1000 читателей
    actions = ['renew_two_weeks', 'mark_as_available']

    fieldsets = (
        (None, {
            'fields': ('book', 'inventory_number', 'imprint', 'id')
        }),
        ('Статус и Выдача', {
            'fields': ('status', 'due_back', 'borrower')
        }),
    )

    @admin.display(description='Книга', ordering='book__title')
    def book_link(self, obj):
        # Ссылка на редактирование самой книги
        from django.urls import reverse
        url = reverse("admin:app_book_change", args=[obj.book.id])  # Замени 'app' на название твоего приложения
        return format_html('<a href="{}">{}</a>', url, obj.book.title)

    @admin.display(description='Читатель', ordering='borrower__user__last_name')
    def borrower_link(self, obj):
        if obj.borrower:
            return f"{obj.borrower.user.get_full_name()} ({obj.borrower.card_number})"
        return "-"

    @admin.display(description='Статус', ordering='status')
    def status_colored(self, obj):
        colors = {
            'a': 'green',  # Доступна
            'o': 'orange',  # Выдана
            'r': 'purple',  # Зарезервирована
            'm': 'red',  # На обслуживании
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.status, 'black'),
            obj.get_status_display()
        )

    @admin.display(description='!', boolean=True)
    def is_overdue_icon(self, obj):
        return obj.is_overdue

    @admin.action(description='Продлить на 2 недели')
    def renew_two_weeks(self, request, queryset):
        updated_count = 0
        for instance in queryset:
            if instance.due_back:
                instance.due_back += timedelta(days=14)
                instance.save()
                updated_count += 1
        self.message_user(request, f'Продлено книг: {updated_count}')

    @admin.action(description='Вернуть (статус "Доступна")')
    def mark_as_available(self, request, queryset):
        queryset.update(status='a', due_back=None, borrower=None)


@admin.register(Reader)
class ReaderAdmin(admin.ModelAdmin):
    list_display = ('get_photo', 'card_number', 'full_name', 'category', 'phone', 'is_active_colored')
    list_filter = ('category', 'is_active', 'registration_date')
    search_fields = ('card_number', 'user__first_name', 'user__last_name', 'phone')
    list_select_related = ('user',)  # JOIN таблицы пользователя для скорости
    inlines = [BorrowHistoryInline]
    readonly_fields = ('registration_date',)

    fieldsets = (
        ('Пользователь', {
            'fields': ('user', 'photo', 'card_number', 'is_active')
        }),
        ('Личные данные', {
            'fields': ('category', 'date_of_birth', 'phone', 'address')
        }),
        ('Даты', {
            'fields': ('registration_date', 'card_expiry_date')
        }),
    )

    @admin.display(description='ФИО', ordering='user__last_name')
    def full_name(self, obj):
        return obj.user.get_full_name()

    @admin.display(description='Активен')
    def is_active_colored(self, obj):
        color = 'green' if obj.is_active else 'red'
        icon = '✔' if obj.is_active else '✘'
        return format_html('<span style="color: {};">{}</span>', color, icon)

    @admin.display(description='Фото')
    def get_photo(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" style="width: 40px; height: 40px; border-radius: 50%; object-fit: cover;" />',
                obj.photo.url)
        return "👤"


@admin.register(BorrowHistory)
class BorrowHistoryAdmin(admin.ModelAdmin):
    list_display = ('book_instance', 'reader', 'borrow_date', 'due_date', 'return_date', 'was_returned_late')
    list_filter = ('borrow_date', 'return_date')
    date_hierarchy = 'borrow_date'  # Удобная навигация по датам наверху
    autocomplete_fields = ('book_instance', 'reader')  # Быстрый поиск при создании записи
