from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
import uuid
from datetime import date, timedelta


class Author(models.Model):
    """Модель автора книги"""
    first_name = models.CharField('Имя', max_length=100)
    last_name = models.CharField('Фамилия', max_length=100)
    date_of_birth = models.DateField('Дата рождения', null=True, blank=True)
    date_of_death = models.DateField('Дата смерти', null=True, blank=True)
    biography = models.TextField('Биография', blank=True)

    class Meta:
        verbose_name = 'Автор'
        verbose_name_plural = 'Авторы'
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['last_name', 'first_name']),
        ]

    def __str__(self):
        return f'{self.last_name} {self.first_name}'


class Genre(models.Model):
    """Модель жанра книги"""
    name = models.CharField('Название жанра', max_length=100, unique=True)
    description = models.TextField('Описание', blank=True)

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ['name']

    def __str__(self):
        return self.name


class Publisher(models.Model):
    """Модель издательства"""
    name = models.CharField('Название', max_length=200, unique=True)
    address = models.CharField('Адрес', max_length=300, blank=True)
    website = models.URLField('Веб-сайт', blank=True)

    class Meta:
        verbose_name = 'Издательство'
        verbose_name_plural = 'Издательства'
        ordering = ['name']

    def __str__(self):
        return self.name


class Book(models.Model):
    """Модель книги (общая информация о книге)"""
    title = models.CharField('Название', max_length=300, db_index=True)
    authors = models.ManyToManyField(Author, verbose_name='Авторы', related_name='books')
    isbn = models.CharField('ISBN', max_length=13, unique=True, help_text='13-значный ISBN код')
    publisher = models.ForeignKey(Publisher, on_delete=models.SET_NULL, null=True, blank=True,
                                  verbose_name='Издательство', related_name='books')
    publication_date = models.DateField('Дата публикации', null=True, blank=True)
    genres = models.ManyToManyField(Genre, verbose_name='Жанры', related_name='books')
    language = models.CharField('Язык', max_length=50, default='Русский')
    pages = models.IntegerField('Количество страниц', validators=[MinValueValidator(1)], null=True, blank=True)
    summary = models.TextField('Краткое описание', blank=True)
    cover_image = models.ImageField('Обложка', upload_to='books/covers/', blank=True, null=True)

    class Meta:
        verbose_name = 'Книга'
        verbose_name_plural = 'Книги'
        ordering = ['title']
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['isbn']),
        ]

    def __str__(self):
        return self.title

    def get_authors_display(self):
        """Возвращает строку с именами всех авторов"""
        return ', '.join([str(author) for author in self.authors.all()])


class BookInstance(models.Model):
    """Модель экземпляра книги (физическая копия)"""
    LOAN_STATUS = (
        ('a', 'Доступна'),
        ('o', 'Выдана'),
        ('r', 'Зарезервирована'),
        ('m', 'На обслуживании'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          help_text='Уникальный ID экземпляра книги')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name='Книга',
                             related_name='instances')
    inventory_number = models.CharField('Инвентарный номер', max_length=50, unique=True)
    imprint = models.CharField('Издание', max_length=200, blank=True)
    status = models.CharField('Статус', max_length=1, choices=LOAN_STATUS,
                              default='a', help_text='Доступность книги')
    due_back = models.DateField('Дата возврата', null=True, blank=True)
    borrower = models.ForeignKey('Reader', on_delete=models.SET_NULL, null=True, blank=True,
                                 verbose_name='Читатель', related_name='borrowed_books')

    class Meta:
        verbose_name = 'Экземпляр книги'
        verbose_name_plural = 'Экземпляры книг'
        ordering = ['due_back']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['inventory_number']),
        ]

    def __str__(self):
        return f'{self.inventory_number} - {self.book.title}'

    @property
    def is_overdue(self):
        """Проверяет, просрочена ли книга"""
        return self.due_back and date.today() > self.due_back


class Reader(models.Model):
    """Модель читателя"""
    READER_CATEGORY = (
        ('adult', 'Взрослый'),
        ('child', 'Детский'),
        ('student', 'Студент'),
        ('senior', 'Пенсионер'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    card_number = models.CharField('Номер читательского билета', max_length=20, unique=True,
                                   db_index=True)
    category = models.CharField('Категория', max_length=10, choices=READER_CATEGORY,
                                default='adult')
    date_of_birth = models.DateField('Дата рождения')
    phone = models.CharField('Телефон', max_length=20)
    address = models.CharField('Адрес', max_length=300)
    registration_date = models.DateField('Дата регистрации', auto_now_add=True)
    card_expiry_date = models.DateField('Срок действия билета')
    photo = models.ImageField('Фото', upload_to='readers/photos/', blank=True, null=True)
    is_active = models.BooleanField('Активен', default=True)
    notes = models.TextField('Примечания', blank=True)

    class Meta:
        verbose_name = 'Читатель'
        verbose_name_plural = 'Читатели'
        ordering = ['user__last_name', 'user__first_name']
        indexes = [
            models.Index(fields=['card_number']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f'{self.card_number} - {self.user.get_full_name()}'

    @property
    def is_card_expired(self):
        """Проверяет, истёк ли срок действия читательского билета"""
        return date.today() > self.card_expiry_date

    def save(self, *args, **kwargs):
        """Автоматически устанавливает срок действия билета при создании"""
        if not self.card_expiry_date:
            self.card_expiry_date = date.today() + timedelta(days=365)
        super().save(*args, **kwargs)


class BorrowHistory(models.Model):
    """История выдачи книг"""
    book_instance = models.ForeignKey(BookInstance, on_delete=models.CASCADE,
                                      verbose_name='Экземпляр книги', related_name='borrow_history')
    reader = models.ForeignKey(Reader, on_delete=models.CASCADE,
                               verbose_name='Читатель', related_name='borrow_history')
    borrow_date = models.DateField('Дата выдачи', auto_now_add=True)
    due_date = models.DateField('Плановая дата возврата')
    return_date = models.DateField('Фактическая дата возврата', null=True, blank=True)
    librarian = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                  verbose_name='Библиотекарь', related_name='issued_books')
    notes = models.TextField('Примечания', blank=True)

    class Meta:
        verbose_name = 'История выдачи'
        verbose_name_plural = 'История выдач'
        ordering = ['-borrow_date']
        indexes = [
            models.Index(fields=['-borrow_date']),
            models.Index(fields=['return_date']),
        ]

    def __str__(self):
        return f'{self.reader.card_number} - {self.book_instance.book.title} ({self.borrow_date})'

    @property
    def was_returned_late(self):
        """Проверяет, была ли книга возвращена с опозданием"""
        if self.return_date:
            return self.return_date > self.due_date
        return False

