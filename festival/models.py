from datetime import date

from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator, FileExtensionValidator, RegexValidator
from django.db import models, transaction
from django.forms import ModelForm
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from ckeditor.fields import RichTextField
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

from . import widgets, iso3166


AUTHOR = 'a'
VISITOR = 'b'
JOURNALIST = 'c'
ROLE_CHOICES = (
    (AUTHOR, _('tvůrce')),
    (VISITOR, _('návštěvník')),
    (JOURNALIST, _('novinář')),
)

class Year(models.Model):
    vol = models.PositiveSmallIntegerField('číslo', validators=[MinValueValidator(0), MaxValueValidator(100)])
    name = models.CharField('název', max_length=50, blank=True, null=True)
    date_start = models.DateField('datum zahájení')
    date_end = models.DateField('datum ukončení')
    current = models.BooleanField('aktuální', default=False)

    class Meta:
        verbose_name = 'ročník'
        verbose_name_plural = 'ročníky'

    def __str__(self):
        return f'{ self.get_year() } vol. { self.get_vol() }'

    def save(self, *args, **kwargs):
        if self.current:
            Year.objects.filter(current=True).update(current=False)
        super().save(*args, **kwargs)

    def get_year(self):
        return self.date_start.year

    def get_vol(self):
        vol_int = self.vol
        ints = (1000, 900, 500, 400, 100, 90, 50, 40, 10,  9, 5, 4, 1)
        romans = ('M', 'CM', 'D', 'CD', 'C', 'XC', 'L', 'XL', 'X', 'IX', 'V', 'IV', 'I')
        vol_roman = []
        for i in range(len(ints)):
            count = int(vol_int / ints[i])
            vol_roman.append(romans[i] * count)
            vol_int -= ints[i] * count
        return ''.join(vol_roman)

    @classmethod
    def get_current(cls):
        return cls.objects.filter(current=True).first()


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
    max_columns = models.PositiveSmallIntegerField('maximální počet sloupečků', default=None, null=True, blank=True,
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


def MaxCurrentYearValidator(value):
    current_year = Year.get_current().get_year()
    validator = MaxValueValidator(current_year)
    return validator(value)


class Film(models.Model):
    UNPAID = 'u'
    REGISTERED = 'r'
    SELECTED = 's'
    OUT = 'o'
    STATUS_CHOICES = (
        (UNPAID, 'neuhrazený poplatek'),
        (REGISTERED, 'registrovaný'),
        (SELECTED, 'vybraný'),
        (OUT, 'vyřazený'),
    )
    FILM = 'f'
    DOCUMENTARY = 'd'
    ANIMATED = 'a'
    CATEGORY_CHOICES = (
        (FILM, _('hraný')),
        (DOCUMENTARY, _('dokumentární')),
        (ANIMATED, _('animovaný')),
    )
    ACTION = 'ac'
    DETECTIVE = 'de'
    ADVENTURE = 'ad'
    DRAMA = 'dr'
    FANTASY = 'fa'
    HISTORICAL = 'hi'
    HORROR = 'ho'
    MUSICAL = 'mu'
    COMEDY = 'co'
    CRIME = 'cr'
    FAIRY_TALE = 'ft'
    FAMILY = 'fa'
    ROMANTIC = 'ro'
    SCI_FI = 'sf'
    THRILLER = 'th'
    WAR = 'wa'
    WESTERN = 'we'
    GENRE_CHOICES = (
        (ACTION, _('akční')),
        (DETECTIVE, _('detektivní')),
        (ADVENTURE, _('dobrodružný')),
        (DRAMA, _('drama')),
        (FANTASY, _('fantasy')),
        (HISTORICAL, _('historický')),
        (HORROR, _('horor')),
        (MUSICAL, _('hudební')),
        (COMEDY, _('komedie')),
        (CRIME, _('kriminální')),
        (FAIRY_TALE, 'pohádka'),
        (FAMILY, _('rodinný')),
        (ROMANTIC, _('romantický')),
        (SCI_FI, _('sci-fi')),
        (THRILLER, ('thriller')),
        (WAR, 'válečný'),
        (WESTERN, 'western'),
    )
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message=_('Zadejte, prosím, platné telefonní číslo ve formátu +999999999'))
    first_name = models.CharField(_('jméno'), max_length=50)
    last_name = models.CharField(_('příjmení'), max_length=50)
    email = models.EmailField(_('email'))
    production = models.CharField(_('škola/produkce'), max_length=50)
    country = models.CharField(_('stát'), max_length=2, choices=iso3166.COUNTRY_CHOICES, default='CZ')
    phone = models.CharField(_('telefon'), validators=[phone_regex], max_length=17, null=True, blank=True)
    name = models.CharField(_('název'), max_length=50)
    time = models.DurationField(_('stopáž'))
    description = models.TextField(_('krátký popis'), max_length=200)
    year = models.SmallIntegerField(_('rok vzniku'), validators=[ MaxCurrentYearValidator, MinValueValidator(1980)])
    category = models.CharField(_('kategorie'), max_length=1, choices=CATEGORY_CHOICES)
    genre = models.CharField(_('žánr'), max_length=2, choices=GENRE_CHOICES)
    film_url = models.URLField(_('url stažení filmu'))
    film_password = models.CharField(_('heslo k filmu'), max_length=64, null=True, blank=True)
    trailer_url = models.URLField(_('url stažení traileru'))
    trailer_password = models.CharField(_('heslo k traileru'), max_length=64, null=True, blank=True)
    subtitles_url = models.URLField(_('url stažení titulků'))
    subtitles_password = models.CharField(_('heslo k titulkům'), max_length=64, null=True, blank=True)
    starring = models.TextField(_('herecké obsazení'), max_length=200, null=True, blank=True)
    directing = models.CharField(_('režie'), max_length=50, null=True, blank=True)
    screenplay = models.CharField(_('scénář'), max_length=50, null=True, blank=True)
    camera = models.CharField(_('kamera'), max_length=50, null=True, blank=True)
    sound = models.CharField(_('zvuk'), max_length=50, null=True, blank=True)
    cut = models.CharField(_('střih'), max_length=50, null=True, blank=True)
    others = models.TextField(_('ostatní tvůrci'), max_length=200, null=True, blank=True)
    tos = models.BooleanField('souhlas s podmínkami přihlášení', default=False)
    gdpr = models.BooleanField('souhlas se zásadami zpracování osobních údajů', default=False)
    attendance = models.BooleanField('zájem o osobní účast na festivalu', default=False)
    status = models.CharField('status', max_length=1, choices=STATUS_CHOICES, default='u')
    technical_check = models.BooleanField('technicky ok', null=True, blank=True, default=None)

    class Meta:
        verbose_name = 'film'
        verbose_name_plural = 'filmy'

    def __str__(self):
        return self.name

    def get_rating(self):
        rating = Evaluation.objects.filter(film=self).aggregate(models.Avg('like'))
        return rating['like__avg']

    get_rating.short_description ='průměrné hodnocení'


class Evaluation(models.Model):
    LIKE_CHOICES = (
        (0, 'odpad!'),
        (1, 'španý'),
        (2, 'slabší'),
        (3, 'dobrý'),
        (4, 'hodně dobrý'),
        (5, 'bombastický!'),
    )
    user = models.ForeignKey(User, verbose_name='přidal', editable=False, on_delete=models.CASCADE)
    film = models.ForeignKey(Film, verbose_name='film', on_delete=models.CASCADE)
    like = models.PositiveSmallIntegerField('líbí', choices=LIKE_CHOICES)
    verbal = models.TextField('slovně', max_length=200)
    technical = models.BooleanField('technicky ok', null=True, blank=True, default=None)


    class Meta:
        verbose_name = 'hodnocení filmu'
        verbose_name_plural = 'hodnocení filmů'

    def __str__(self):
        return self.get_like_display()


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
    GENERAL = 10
    SUPPORT = 15
    MEDIA = 20
    OTHERS = 30
    CATEGORY_CHOICES = (
        (COORG, 'spoluorganizátoři'),
        (GENERAL, 'generální'),
        (SUPPORT, 'za podpory'),
        (MEDIA, 'medialní'),
        (OTHERS, 'ostatní'),
    )
    year = models.ManyToManyField(Year, verbose_name='ročník', blank=True)
    name = models.CharField('jméno', max_length=50)
    logo = models.ImageField('logo', null=True, blank=True)
    url = models.URLField('odkaz na web', null=True, blank=True)
    category = models.PositiveSmallIntegerField('kategorie', default=30, choices=CATEGORY_CHOICES)
    order = models.PositiveSmallIntegerField('pořadí', default=1)

    class Meta:
        verbose_name = 'sponzor'
        verbose_name_plural = 'sponzoři'
        ordering = ['category', 'order']

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
        ordering = ['date_release']

    def __str__(self):
        return self.name


class Ticket(models.Model):
    pass


class ThepayPayment(models.Model):
    OK = 2
    CANCELED = 3
    ERROR = 4
    UNDERPAID = 6
    WAITING = 7
    CARD_DEPOSIT = 9
    STATUS_CHOICES = (
        (OK , 'úspěšně zaplaceno'),
        (CANCELED , 'platba byla zrušena zákazníkem'),
        (ERROR , 'při platbě došlo k chybě.'),
        (UNDERPAID , 'zákazník zaplatil nižší než požadovanou částku.'),
        (WAITING , 'zákazník platbu provedl, ale je nutné počkat na potvrzení'),
        (CARD_DEPOSIT , 'částka je blokována na účtu zákazníka'),
    )
    FILM = 'f'
    TICKETS = 't'
    TYPE_CHOICES = (
        (FILM, _('registrační poplatek')),
        (TICKETS, _('prodej vstupenek')),
    )
    value = models.DecimalField('částka', decimal_places=2, max_digits=10)
    currency = models.CharField('měna', max_length=3)
    methodId = models.PositiveSmallIntegerField('id platební metody')
    merchantData = models.CharField(max_length=150)
    status = models.PositiveSmallIntegerField('status', choices=STATUS_CHOICES)
    paymentId = models.PositiveIntegerField('id platby', unique=True)
    isOffline = models.BooleanField('offline', null=True)
    type = models.CharField('typ', max_length=1, choices=TYPE_CHOICES)
    datetime = models.DateTimeField('datum a čas', auto_now_add=True)
    valid_signature = models.BooleanField('validní podpis', default=False)
    film = models.OneToOneField('Film', on_delete=models.SET_NULL, null=True, blank=True)
    ticket = models.OneToOneField('Ticket', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = 'thepay platba'
        verbose_name_plural = 'thepay platby'

    def save(self, **kwargs):
        if self._state.adding and self.valid_signature and self.status == self.OK:
            if self.type == self.FILM:
                with transaction.atomic():
                    self.film.status = Film.REGISTERED
                    self.film.save(update_fields=['status'])
                    super().save(**kwargs)
        else:
            super().save(**kwargs)


class ThepayPaymentForm(ModelForm):

    class Meta:
        model = ThepayPayment
        exclude = []


class FilmRegistrationForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['attendance'].label = _('Mám zájem o osobní účast na festivalu.')
        self.fields['tos'].label = _('Souhlasím s podmínkami přihlášení.')
#        self.fields['gdpr'].label = _('Souhlasím se zásadami zpracování osobních údajů.')
        self.fields['tos'].required = True
#        self.fields['gdpr'].required = True
        self.fields['time'].widget.attrs['placeholder'] = 'mm:ss'
        self.fields['phone'].widget.attrs['placeholder'] = '+420 111 222 333'

    class Meta:
        model = Film
        exclude = ('status', 'technical_check', 'gdpr')
