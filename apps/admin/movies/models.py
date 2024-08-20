import uuid

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import (
    CASCADE,
    CharField,
    DateField,
    DateTimeField,
    FloatField,
    ForeignKey,
    Index,
    ManyToManyField,
    Model,
    TextChoices,
    TextField,
    UniqueConstraint,
    UUIDField,
)
from django.utils.translation import gettext_lazy as _


class MyUserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        user = self.create_user(email, password=password)
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(verbose_name="email address", max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    # строка с именем поля модели, которая используется в качестве уникального идентификатора
    USERNAME_FIELD = "email"

    # менеджер модели
    objects = MyUserManager()

    def __str__(self):
        return f"{self.email} {self.id}"

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @staticmethod
    def is_staff():
        return True


class TimeStampedMixin(Model):
    created = DateTimeField(auto_now_add=True)
    modified = DateTimeField(auto_now=True)

    class Meta:
        # Этот параметр указывает Django, что этот класс не является представлением таблицы
        abstract = True


class UUIDMixin(Model):
    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Genre(UUIDMixin, TimeStampedMixin):
    def __str__(self):
        return self.name

    name = CharField(_("name"), max_length=255)
    description = TextField(_("description"), blank=True)

    class Meta:
        db_table = 'content"."genre'
        verbose_name = _("Жанр")
        verbose_name_plural = _("Жанры")


class Person(UUIDMixin, TimeStampedMixin):
    def __str__(self):
        return self.full_name

    full_name = CharField(_("FullName"), max_length=255)

    class Meta:
        db_table = 'content"."person'
        verbose_name = _("Персона")
        verbose_name_plural = _("Персоны")


class FilmWork(UUIDMixin, TimeStampedMixin):
    def __str__(self):
        return self.title

    class FilmType(TextChoices):
        MOVIE = "movie", _("Film")
        TV_SHOW = "tv_show", _("TV Show")

    title = CharField(_("title"), max_length=255)
    description = TextField(_("description"), blank=True)
    creation_date = DateField(_("creation_date"), null=True)
    rating = FloatField(
        _("rating"), max_length=255, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    type = CharField(_("type"), max_length=255, choices=FilmType.choices)

    genres = ManyToManyField(Genre, through="GenreFilmWork")
    persons = ManyToManyField(Person, through="PersonFilmWork")

    class Meta:
        db_table = 'content"."film_work'
        verbose_name = _("Кинопроизведение")
        verbose_name_plural = _("Кинопроизведения")
        indexes = [
            Index(fields=["creation_date"], name="film_work_creation_date_idx"),
        ]


class PersonFilmWork(UUIDMixin):
    class RoleType(TextChoices):
        ACTOR = "actor", _("Actor")
        DIRECTOR = "director", _("Director")
        WRITER = "writer", _("Writer")

    film_work = ForeignKey(FilmWork, on_delete=CASCADE)
    person = ForeignKey(Person, on_delete=CASCADE)
    role = TextField(_("role"), choices=RoleType.choices)
    created = DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'content"."person_film_work'
        constraints = [
            UniqueConstraint(fields=["film_work", "person", "role"], name="film_work_person_idx"),
        ]


class GenreFilmWork(UUIDMixin):
    film_work = ForeignKey(FilmWork, on_delete=CASCADE)
    genre = ForeignKey(Genre, on_delete=CASCADE)
    created = DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'content"."genre_film_work'
