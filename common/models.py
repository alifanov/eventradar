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
