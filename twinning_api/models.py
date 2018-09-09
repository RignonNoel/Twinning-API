import binascii
import os
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import AbstractUser
from rest_framework.authtoken.models import Token
from .managers import ActionTokenManager, UserManager
from django.utils.html import format_html


class User(AbstractUser):
    """Abstraction of the base User model. Needed to extend in the future."""
    username = None
    email = models.EmailField(_('email address'), unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()


class TemporaryToken(Token):
    """Subclass of Token to add an expiration time."""

    class Meta:
        verbose_name = _("Temporary token")
        verbose_name_plural = _("Temporary tokens")

    expires = models.DateTimeField(
        verbose_name=_("Expiration date"),
        blank=True,
    )

    def save(self, *args, **kwargs):
        if not self.pk:
            self.expires = timezone.now() + timezone.timedelta(
                minutes=settings.REST_FRAMEWORK_TEMPORARY_TOKENS['MINUTES']
            )

        super(TemporaryToken, self).save(*args, **kwargs)

    @property
    def expired(self):
        """Returns a boolean indicating token expiration."""
        return self.expires <= timezone.now()

    def expire(self):
        """Expires a token by setting its expiration date to now."""
        self.expires = timezone.now()
        self.save()


class ActionToken(models.Model):
    """
        Class of Token to allow User to do some action.

        Generally, the token is sent by email and serves
        as a "right" to do a specific action.
    """

    ACTIONS_TYPE = [
        ('account_activation', _('Account activation')),
        ('password_change', _('Password change')),
    ]

    key = models.CharField(
        verbose_name="Key",
        max_length=40,
        primary_key=True
    )

    type = models.CharField(
        verbose_name='Type of action',
        max_length=100,
        choices=ACTIONS_TYPE,
        null=False,
    )

    user = models.ForeignKey(
        User,
        related_name='activation_token',
        on_delete=models.CASCADE,
        verbose_name="User"
    )

    created = models.DateTimeField(
        verbose_name="Creation date",
        auto_now_add=True
    )

    expires = models.DateTimeField(
        verbose_name="Expiration date",
        blank=True,
    )

    objects = ActionTokenManager()

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
            self.expires = timezone.now() + timezone.timedelta(
                minutes=settings.ACTIVATION_TOKENS['MINUTES']
            )
        return super(ActionToken, self).save(*args, **kwargs)

    @staticmethod
    def generate_key():
        """Generate a new key"""
        return binascii.hexlify(os.urandom(20)).decode()

    @property
    def expired(self):
        """Returns a boolean indicating token expiration."""
        return self.expires <= timezone.now()

    def expire(self):
        """Expires a token by setting its expiration date to now."""
        self.expires = timezone.now()
        self.save()

    def __str__(self):
        return self.key


class Organization(models.Model):
    """Organization's modal"""

    name = models.CharField(
        max_length=45,
        blank=False,
        verbose_name=_("Organization"),
    )

    logo = models.ImageField(
        _('logo'),
        blank=True,
        upload_to='organizations'
    )

    description = models.CharField(
        max_length=1500,
        blank=False,
        verbose_name=_("Description"),
    )
    godson_value = models.CharField(
        max_length=1500,
        blank=False,
        verbose_name=_("Godson value propositon"),
    )
    godfather_value = models.CharField(
        max_length=1500,
        blank=False,
        verbose_name=_("Godfather value proposition"),
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        default='',
        verbose_name=_("City"),
    )
    country = models.CharField(
        max_length=100,
        blank=True,
        default='',
        verbose_name=_("Country"),
    )

    categories = models.ManyToManyField(
        'Category',
        blank=True,
        verbose_name=_("Categories"),
        related_name='organizations',
    )

    owners = models.ManyToManyField(
        'User',
        blank=False,
        verbose_name=_("Owner"),
        related_name='organizations',
    )

    # Needed to display in the admin panel
    def logo_tag(self):
        return format_html(
            '<img href="{0}" src="{0}" height="150" />'
            .format(self.logo.url)
        )

    logo_tag.allow_tags = True
    logo_tag.short_description = 'Logo'

    def __str__(self):
        return self.name


class Category(models.Model):
    """Category's modal"""
    name = models.CharField(
        max_length=45,
        blank=False,
        verbose_name=_("Organization"),
    )

    def __str__(self):
        return self.name
