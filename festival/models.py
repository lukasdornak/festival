from datetime import date

from django.contrib.auth.models import User
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from ckeditor.fields import RichTextField
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

from django.core.validators import MaxValueValidator, MinValueValidator, FileExtensionValidator
from django.db.models import Avg

from . import widgets

AUTHOR = 'a'
VISITOR = 'b'
JOURNALIST = 'c'
ROLE_CHOICES = (
    (AUTHOR, _('tvůrce')),
    (VISITOR, _('návštěvník')),
    (JOURNALIST, _('novinář')),
)

class Year(models.Model):
    vol = models.PositiveSmallIntegerField('ročník číslo', validators=[MinValueValidator(0), MaxValueValidator(100)])
    name = models.CharField('název', max_length=50, blank=True, null=True)
    date_start = models.DateField('datum zahájení')
    date_end = models.DateField('datum ukončení')
    current = models.BooleanField('aktuální', default=False)

    class Meta:
        verbose_name = 'ročník'
        verbose_name_plural = 'ročníky'

    def __str__(self):
        return str(self.vol)

    def save(self, *args, **kwargs):
        if self.current:
            Year.objects.filter(current=True).update(current=False)
        super().save(*args, **kwargs)

    @classmethod
    def get_current(cls):
        return Year.objects.filter(current=True).first()


class AbstractArticle(models.Model):
    headline = models.CharField('nadpis', max_length=50)
    headline_en = models.CharField('nadpis anglicky', max_length=50)
    full_text = RichTextField('obsah', null=True, blank=True)
    full_text_en = RichTextField('obsah anglicky', null=True, blank=True)
    slug = models.SlugField(editable=False)
    slug_en = models.SlugField(editable=False)
    published = models.BooleanField('publikováno', default=False)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.slug = slugify(self.headline)
        self.slug_en = slugify(self.headline_en)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.headline


class Article(AbstractArticle):
    date = models.DateField('datum')
    short_text = models.CharField('úryvek', max_length=150)
    short_text_en = models.CharField('úryvek anglicky', max_length=150)
    photo = models.ImageField('Fotka', blank=True, null=True)
    photo_small = ImageSpecField(source='fotka', processors=[ResizeToFill(300, 300)],
                                 format='JPEG', options={'quality': 100})
    photo_large = ImageSpecField(source='fotka', processors=[ResizeToFill(1200, 800)],
                                 format='JPEG', options={'quality': 100})

    class Meta:
        verbose_name = 'Článek'
        verbose_name_plural = 'Články'


class Section(AbstractArticle):
    extra_full_text = RichTextField('extra obsah', null=True, blank=True)
    extra_full_text_en = RichTextField('extra obsah anglicky', null=True, blank=True)
    role = models.CharField('role', max_length=1, default='v', choices=ROLE_CHOICES)
    order = models.PositiveSmallIntegerField('pořadí', default=1)
    widget = models.CharField('widget', max_length=1, choices=widgets.Widget.get_choices(),
                              null=True, blank=True)
    widget_first = models.BooleanField('nejdříve widget, potom text', default=True)
    auto_headline = models.BooleanField('nadpis automaticky', default=True)
    max_columns = models.PositiveSmallIntegerField('maximální počet sloupečků', default=3, null=True, blank=True,
                                                   validators=[MinValueValidator(1), MaxValueValidator(4)])

    class Meta:
        verbose_name = 'sekce'
        verbose_name_plural = 'sekce'
        ordering = ['role','order']

    def get_widget(self):
        return widgets.Widget.get_class(self.widget)


class Guide(models.Model):
    date = models.DateField('datum')
    headline = models.CharField('nadpis', max_length=50)
    headline_en = models.CharField('nadpis', max_length=50)
    video = models.CharField('video tag', max_length=200)
    order = models.PositiveSmallIntegerField('pořadí', default=1)
    published = models.BooleanField('publikováno', default=False)

    class Meta:
        verbose_name = 'průvodce'
        verbose_name_plural = 'průvodci'

    def __str__(self):
        return self.headline


class Contact(models.Model):
    name = models.CharField('jméno', max_length=50)
    function = models.CharField('funkce', max_length=50)
    function_en = models.CharField('funkce anglicky', max_length=50)
    email = models.EmailField('e-mail')
    phone = models.DecimalField('telefon', decimal_places=0, max_digits=9)
    published = models.BooleanField('publikováno', default=False)

    class Meta:
        verbose_name = 'kontakt'
        verbose_name_plural = 'kontakty'

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField('název', max_length=50)
    name_en = models.CharField('název anglicky', max_length=50)

    class Meta:
        verbose_name = 'kategorie filmu'
        verbose_name_plural = 'kategorie filmu'

    def __str__(self):
        return self.name


class Film(models.Model):
    UNPAID = 'neuhrazený poplatek'
    REGISTERED = 'registrovaný'
    SELECTED = 'vybraný'
    STATUS_CHOICES = (
        ('u', UNPAID),
        ('r', REGISTERED),
        ('s', SELECTED),
    )
    author_name = models.CharField(_('jméno autora'), max_length=50)
    author_yob = models.PositiveSmallIntegerField(_('rok narození'), validators=[
        MaxValueValidator(2012), MinValueValidator(1900)])
    production = models.CharField(_('škola/produkce'), max_length=50)
    author_state = models.CharField(_('stát'), max_length=50)
    name = models.CharField(_('název'), max_length=50)
    time = models.TimeField(_('stopáž'))
    year = models.SmallIntegerField(_('rok vzniku'), default=2018)
    directed = models.CharField(_('režie'), max_length=50, null=True, blank=True)
    screenplay = models.CharField(_('scénář'), max_length=50, null=True, blank=True)
    camera = models.CharField(_('kamera'), max_length=50, null=True, blank=True)
    sound = models.CharField(_('zvuk'), max_length=50, null=True, blank=True)
    cut = models.CharField(_('střih'), max_length=50, null=True, blank=True)
    others = models.TextField(_('ostatní tvůrci'), max_length=200, null=True, blank=True)
    category = models.ForeignKey(Category, verbose_name=_('Kategorie'), on_delete=models.PROTECT)
    attendance = models.BooleanField(_('mám zájem o osobní účast na festivalu'))
    tos = models.BooleanField(_('souhlasím s podmínkami přihlášení'))
    status = models.CharField('status', max_length=1, choices=STATUS_CHOICES, default='u')

    class Meta:
        verbose_name = 'film'
        verbose_name_plural = 'filmy'

    def __str__(self):
        return self.name

    def get_rating(self):
        rating = Evaluation.objects.filter(film=self).aggregate(Avg('like'))
        return rating['like__avg']

    get_rating.short_description ='průměrné hodnocení'

class Evaluation(models.Model):
    UNCHECKED = 'nezkontrolováno'
    VALID = 'ok'
    INVALID = 'něco v nepořádku'
    TECHNICAL_CHOICES = (
        ('u', UNCHECKED),
        ('v', VALID),
        ('i', INVALID),
    )
    user = models.ForeignKey(User, verbose_name='přidal', editable=False, null=True, blank=True, on_delete=models.SET_NULL)
    film = models.ForeignKey(Film, verbose_name='film', on_delete=models.CASCADE)
    like = models.PositiveSmallIntegerField('líbí', validators=[MinValueValidator(0), MaxValueValidator(5)])
    verbal = models.TextField('slovně', max_length=200)
    technical = models.CharField('technicky', max_length=1, choices=TECHNICAL_CHOICES, default='u', blank=True)

    class Meta:
        verbose_name = 'hodnocení filmu'
        verbose_name_plural = 'hodnocení filmů'


class Block(models.Model):
    name = models.CharField('název', max_length=50)
    subtitle = models.CharField('název', max_length=50, null=True, blank=True)
    subtitle_en = models.CharField('název', max_length=50, null=True, blank=True)

    class Meta:
        verbose_name = 'projekční blok'
        verbose_name_plural = 'projekční bloky'

    def __str__(self):
        return self.name


class Sponsor(models.Model):
    COORG = 0
    MAIN = 10
    MEDIA = 20
    OTHERS = 30
    TYPE_CHOICES = (
        (COORG, 'spoluorganizátoři'),
        (MAIN, 'hlavní'),
        (MEDIA, 'medialní'),
        (OTHERS, 'ostatní'),
    )
    year = models.ManyToManyField(Year, verbose_name='ročník', null=True, blank=True)
    name = models.CharField('jméno', max_length=50)
    logo = models.ImageField('logo', null=True, blank=True)
    url = models.URLField('odkaz na web', null=True, blank=True)
    type = models.PositiveSmallIntegerField('kategorie', default=30, choices=TYPE_CHOICES)

    class Meta:
        verbose_name = 'sponzor'
        verbose_name_plural = 'sponzoři'
        ordering = ['type']

    def __str__(self):
        return self.name


class PressRelease(models.Model):
    file = models.FileField('soubor', upload_to='tiskovky/',
                            validators=[FileExtensionValidator(allowed_extensions=['pdf'])])
    name = models.CharField('název', max_length=50)
    date_release = models.DateField('datum zveřejnění', default=date.today)
    year = models.ForeignKey(Year, on_delete=models.SET_NULL, verbose_name='ročník', null=True)

    class Meta:
        verbose_name = 'tiskovka'
        verbose_name_plural = 'tiskovky'

    def __str__(self):
        return self.name
