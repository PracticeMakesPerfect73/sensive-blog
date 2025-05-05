from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models import Count, Prefetch


class PostQuerySet(models.QuerySet):
    """
    Более гибкая альтернатива annotate(comments_count=Count(...)).

    Полезно, когда:
     - Уже применены prefetch_related или другие сложные фильтры.
     - Нужно избежать лишних JOIN'ов или конфликтов в ORM.
     - Хочешь добавить поле вручную к уже полученным объектам.
    """
    
    def popular(self):
        popular_tag = self.annotate(likes_count=Count('likes')).order_by('-likes_count')
        
        return popular_tag


    def fetch_with_comments_count(self):
        posts = self
        post_ids = [post.id for post in posts]
        posts_with_comments = Post.objects.filter(id__in=post_ids) \
            .annotate(comments_count=Count('comments', distinct=True))
        ids_and_comments = posts_with_comments.values_list('id', 'comments_count')
        count_for_id = dict(ids_and_comments)
        
        for post in posts:
            post.comments_count = count_for_id[post.id]
        
        return posts
    

    def prefetch_with_tags_and_authors(self):
        return self.select_related('author').prefetch_related(
            Prefetch('tags', queryset=Tag.objects.annotate(posts_count=Count('posts')))
        )

class TagQuerySet(models.QuerySet):
    def popular(self):
        popular_tag = self.annotate(posts_count=Count('posts')).order_by('-posts_count')
        
        return popular_tag


class Post(models.Model):
    title = models.CharField('Заголовок', max_length=200)
    text = models.TextField('Текст')
    slug = models.SlugField('Название в виде url', max_length=200)
    image = models.ImageField('Картинка')
    published_at = models.DateTimeField('Дата и время публикации')

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        limit_choices_to={'is_staff': True})
    likes = models.ManyToManyField(
        User,
        related_name='liked_posts',
        verbose_name='Кто лайкнул',
        blank=True)
    tags = models.ManyToManyField(
        'Tag',
        related_name='posts',
        verbose_name='Теги')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post_detail', args={'slug': self.slug})

    class Meta:
        ordering = ['-published_at']
        verbose_name = 'пост'
        verbose_name_plural = 'посты'

    objects = PostQuerySet.as_manager()


class Tag(models.Model):
    title = models.CharField('Тег', max_length=20, unique=True)

    class Meta:
        ordering = ['title']
        verbose_name = 'тег'
        verbose_name_plural = 'теги'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('tag_filter', args={'tag_title': self.slug})

    def clean(self):
        self.title = self.title.lower()

    objects = TagQuerySet.as_manager()


class Comment(models.Model):
    post = models.ForeignKey(
        'Post',
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост, к которому написан')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор')

    text = models.TextField('Текст комментария')
    published_at = models.DateTimeField('Дата и время публикации')

    def __str__(self):
        return f'{self.author.username} under {self.post.title}'

    class Meta:
        ordering = ['published_at']
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'
