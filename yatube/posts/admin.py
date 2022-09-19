from django.contrib import admin

from .models import Post, Group, Comment, Follow


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'text',
        'image',
        'pub_date',
        'group',
        'author'
    )
    search_fields = ('text', )
    list_filter = ('pub_date', )
    empty_value_display = '-пусто-'
    list_editable = ('group', )


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = (
        'slug',
        'title',
        'description'
    )
    search_fields = ('slug', 'title')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'post',
        'author',
        'text',
        'created',
    )
    search_fields = ('text', )
    list_filter = ('post', )
    empty_value_display = '-пусто-'


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'author',
    )
    list_filter = ('user', 'author', )
