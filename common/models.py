# coding: utf-8
from django.db import models

# Create your models here.

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
    post_date = models.DateTimeField(verbose_name=u'Время публикации записи')
    evetn_date = models.DateField(verbose_name=u'Дата события')
    text = models.TextField(verbose_name=u'Описание события')
    source = models.CharField(max_length=100, verbose_name=u'Источник')
    is_public = models.BooleanField(default=False, verbose_name=u'Из паблика ВК')
    link = models.CharField(max_length=256, verbose_name=u'Ссылка на оргинальный пост')

    class Meta:
        verbose_name = u'Событие'
        verbose_name_plural = u'События'

    def __unicode__(self):
        return u'[{}]: {}'.format(self.date, self.source)