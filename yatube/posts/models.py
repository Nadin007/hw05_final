from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.db.models import UniqueConstraint
from django.db.models import Q
from django.contrib.postgres.fields import ArrayField


class ROLE_CHOICES(models.TextChoices):
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'


class User(AbstractUser):
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text='Please enter up to 150 characters',
        validators=[username_validator],
        error_messages={
            'unique': 'User with the same username already exists'})
    first_name = models.CharField(_('first name'), max_length=150, blank=True)
    last_name = models.CharField(_('lasr_name'), max_length=150, blank=True)
    email = models.EmailField(
        _('email'), blank=False,
        unique=True, max_length=250)
    bio = models.TextField(
        _('A few words about yourself'), blank=True)
    role = models.CharField(
        _('user`s role'),
        choices=ROLE_CHOICES.choices, default=ROLE_CHOICES.USER,
        null=False, max_length=60)
    is_active = models.BooleanField(
        _('active'), default=False,
        help_text='Determines if this user is considered active or not')
    avatar = models.ImageField(
        _('avatar'),
        upload_to='avatars/',
        help_text='Choose the avatar',
        blank=True, null=True)
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
        constraints = [
            models.CheckConstraint(
                check=~Q(username='username'),
                name='User can not be called \'username\'!'
            )
        ]

    def __str__(self) -> str:
        return f'{self.username} is a {self.role}'

    def save(
            self, *args, **kwargs) -> None:
        if self.is_superuser:
            self.role = ROLE_CHOICES.ADMIN
            self.is_active = True
        return super().save()

    def get_avatar(self):
        if self.avatar:
            return self.avatar.url
        return '/media/avatars/default-1.png'

    def avatar_tag(self):
        return mark_safe(
            '<img src="%s" width="50" height="50" />' % self.get_avatar())
    avatar_tag.short_description = 'avatar'


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(max_length=500)

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField('date published', auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='posts')
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, blank=True,
                              null=True, related_name='posts')
    image = models.ImageField(upload_to='posts/', blank=True, null=True)
    counter = models.IntegerField(default=0)

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='comments')
    text = models.TextField(max_length=500)
    created = models.DateTimeField('date published', auto_now_add=True)
    path = ArrayField(models.IntegerField())

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.text[:15]

    def getoffset(self):
        level = len(self.path) - 1
        if level > 5:
            level = 5
        return level


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='follower')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='following')

    class Meta:
        constraints = [UniqueConstraint(fields=['user', 'author'],
                                        name='unique_subscription')]

    def __str__(self) -> str:
        return f"{self.user} follows {self.author}"
