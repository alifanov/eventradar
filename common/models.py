# coding: utf-8
from django.db import models
from django.contrib.auth.models import User
import datetime

# Create your models here.

class Source(models.Model):
    name = models.CharField(max_length=500, verbose_name=u'Название источника')
    uid = models.IntegerField(default=0, verbose_name=u'UID источника', unique=True)
    users = models.ManyToManyField(User, verbose_name=u'Владельцы', related_name='s'
                                                                                 'ources')

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u'Источник'
        verbose_name_plural = u'Источники'

class Feedback(models.Model):
    """
    Модель для отзывов по обратной связи
    """
    name = models.CharField(max_length=100, verbose_name=u'Имя')
    text = models.TextField(verbose_name=u'Текст')
    created = models.DateTimeField(auto_now_add=True, verbose_name=u'Дата создания')

    class Meta:
        verbose_name = u'Отзыв'
        verbose_name_plural = u'Отзывы'

    def __unicode__(self):
        return u'[{}]: {}'.format(self.created, self.name)

class Event(models.Model):
    """
    Модель события
    """
#    users = models.ManyToManyField(User, verbose_name=u'Пользователи', related_name='events')
    owner_id = models.IntegerField(verbose_name=u'UID владельца записи')
    post_date = models.DateTimeField(verbose_name=u'Время публикации записи')
    event_date = models.DateField(verbose_name=u'Дата события')
    text = models.TextField(verbose_name=u'Описание события')
    source = models.CharField(max_length=100, verbose_name=u'Источник')
    is_public = models.BooleanField(default=False, verbose_name=u'Из паблика ВК')
    link = models.CharField(max_length=256, verbose_name=u'Ссылка на оргинальный пост', blank=True)

    class Meta:
        verbose_name = u'Событие'
        verbose_name_plural = u'События'

    def __unicode__(self):
        return u'[{}]: {}'.format(self.event_date, self.source)