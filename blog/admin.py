from django.contrib import admin
from blog.models import Post, Tag, Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'published_at')
    raw_id_fields = ('likes',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('text', 'author', 'post', 'published_at')
    raw_id_fields = ('author', 'post')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('title',)