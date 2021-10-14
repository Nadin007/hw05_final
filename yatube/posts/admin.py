from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Group, Post, User


@admin.register(User)
class MyUserAdmin(UserAdmin):
    list_display = [
        'avatar_tag',
        'username',
        'first_name',
        'last_name',
        'email',
        'role',
        'is_active',
        'bio',
    ]
    list_editable = ('role', )
    fieldsets = (
        (
            None,
            {'fields': ('username', 'email', 'password', 'role', 'bio')}
        ),
        ('Permissions',
         {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (
            None,
            {'classes': ('wide',),
             'fields': (
                'username',
                'first_name',
                'last_name',
                'email',
                'password1',
                'password2',
                'is_staff',
                'is_active',
                'role',
                'bio',)
             }
        ),
    )
    ordering = ('email', )
    search_fields = ('username', 'role')
    list_filter = ('is_active', 'role')


class GroupAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'slug', 'description')
    search_fields = ('title',)
    prepopulated_fields = {"slug": ("title",)}
    empty_value_display = '-пусто-'


admin.site.register(Group, GroupAdmin,)


class PostAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text', 'pub_date', 'author')
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


admin.site.register(Post, PostAdmin,)
