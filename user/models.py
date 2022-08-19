from django.contrib import auth
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import PermissionsMixin, Group
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


# UserManager from default Auth Django models. This is just to get rid of username field
class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)

        user = self.model(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)

    def create_organizer(self, email=None, password=None, **extra_fields):
        user = self._create_user(email, password, **extra_fields)
        user.set_organizer()
        return user

    def with_perm(
            self, perm, is_active=True, include_superusers=True, backend=None, obj=None
    ):
        if backend is None:
            backends = auth._get_backends(return_tuples=True)
            if len(backends) == 1:
                backend, _ = backends[0]
            else:
                raise ValueError(
                    "You have multiple authentication backends configured and "
                    "therefore must provide the `backend` argument."
                )
        elif not isinstance(backend, str):
            raise TypeError(
                "backend must be a dotted import path string (got %r)." % backend
            )
        else:
            backend = auth.load_backend(backend)
        if hasattr(backend, "with_perm"):
            return backend.with_perm(
                perm,
                is_active=is_active,
                include_superusers=include_superusers,
                obj=obj,
            )
        return self.none()


class User(AbstractBaseUser, PermissionsMixin):
    GENDER_NO_ANSWER = 'NA'
    GENDER_MALE = 'M'
    GENDER_FEMALE = 'F'
    GENDER_NON_BINARY = 'NB'
    GENDER_OTHER = 'X'
    GENDERS = [
        (GENDER_NO_ANSWER, _('Prefer not to answer')),
        (GENDER_MALE, _('Male')),
        (GENDER_FEMALE, _('Female')),
        (GENDER_NON_BINARY, _('Non-binary')),
        (GENDER_OTHER, _('Prefer to self-describe')),
    ]

    DIET_NONE = 'None'
    DIET_VEGETARIAN = 'Vegetarian'
    DIET_VEGAN = 'Vegan'
    DIET_NO_PORK = 'No pork'
    DIET_GLUTEN_FREE = 'Gluten-free'
    DIET_OTHER = 'Others'

    DIETS = [
        (DIET_NONE, _('No requirements')),
        (DIET_VEGETARIAN, _('Vegetarian')),
        (DIET_VEGAN, _('Vegan')),
        (DIET_NO_PORK, _('No pork')),
        (DIET_GLUTEN_FREE, _('Gluten-free')),
        (DIET_OTHER, _('Others')),
    ]

    TSHIRT_XS = 'XS'
    TSHIRT_S = 'S'
    TSHIRT_M = 'M'
    TSHIRT_L = 'L'
    TSHIRT_XL = 'XL'
    TSHIRT_XXL = 'XXL'
    TSHIRT_XXXL = 'XXXL'

    TSHIRT_SIZES = [
        (TSHIRT_XS, "Unisex - XS"),
        (TSHIRT_S, "Unisex - S"),
        (TSHIRT_M, "Unisex - M"),
        (TSHIRT_L, "Unisex - L"),
        (TSHIRT_XL, "Unisex - XL"),
        (TSHIRT_XXL, "Unisex - XXL"),
        (TSHIRT_XXXL, "Unisex - XXXL"),
    ]

    first_name = models.CharField(_("first name"), max_length=150)
    last_name = models.CharField(_("last names"), max_length=150)
    email = models.EmailField(_("email address"), unique=True)
    email_verified = models.BooleanField(_('email verified'), default=False)
    email_subscribe = models.BooleanField(_('email subscribed'), default=False)
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    diet = models.CharField(max_length=300, choices=DIETS, default=DIET_NONE)
    other_diet = models.CharField(max_length=600, blank=True, null=True)

    tshirt_size = models.CharField(max_length=5, default=TSHIRT_M, choices=TSHIRT_SIZES)

    gender = models.CharField(max_length=23, choices=GENDERS, default=GENDER_NO_ANSWER)
    other_gender = models.CharField(max_length=50, blank=True, null=True)

    under_age = models.BooleanField(default=False)

    phone_number = models.CharField(validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$')], blank=True, max_length=20,
                                    help_text=_("Phone number must be entered in the format: +#########'. "
                                                "Up to 15 digits allowed."))

    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"  # Changed this to email
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def set_organizer(self):
        organizer_group = Group.objects.get_or_create(name='Organizer')[0]
        self.groups.add(organizer_group)

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email).lower()

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def is_organizer(self):
        return self.groups.filter(name='Organizer').exists()

    def set_unknown(self):
        self.is_active = False
        number = self.__class__.objects.filter(email__endswith='@unknown.com').count()
        self.email = 'user' + str(number) + '@unknown.com'


class LoginRequest(models.Model):
    ip = models.CharField(max_length=30)
    latest_request = models.DateTimeField()
    login_tries = models.IntegerField(default=1)

    def get_latest_request(self):
        return self.latest_request

    def set_latest_request(self, latest_request):
        self.latest_request = latest_request

    def reset_tries(self):
        self.login_tries = 1

    def increment_tries(self):
        self.login_tries += 1
