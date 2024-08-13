import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
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
