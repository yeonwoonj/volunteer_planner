# coding: utf-8
from datetime import timedelta, datetime

from django.db import models
from django.templatetags.l10n import localize
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy

from . import managers


class ScheduleTemplate(models.Model):
    name = models.CharField(max_length=256, verbose_name=_('name'))

    facility = models.ForeignKey('organizations.Facility',
                                 verbose_name=_(u'facility'),
                                 related_name='schedule_templates')

    class Meta:
        ordering = ('facility',)
        verbose_name_plural = _('schedule templates')
        verbose_name = _('schedule template')

    def __unicode__(self):
        return u'{} / {}'.format(self.name,
                                 self.facility.name)


class ShiftTemplate(models.Model):
    schedule_template = models.ForeignKey('scheduletemplates.ScheduleTemplate',
                                          verbose_name=_('schedule template'),
                                          related_name='shift_templates'
                                          )

    slots = models.IntegerField(verbose_name=_(u'number of needed volunteers'))

    task = models.ForeignKey('organizations.Task',
                             verbose_name=_(u'task'),
                             related_name='+')

    workplace = models.ForeignKey('organizations.Workplace',
                                  verbose_name=_(u'workplace'),
                                  related_name='+',
                                  null=True,
                                  blank=True)

    starting_time = models.TimeField(verbose_name=_('starting time'),
                                     db_index=True)

    ending_time = models.TimeField(verbose_name=_('ending time'),
                                   db_index=True)

    days = models.PositiveIntegerField(verbose_name=_(u'days'),
                                       default=0)

    objects = managers.ShiftTemplateManager()

    @property
    def duration(self):
        today = datetime.today()
        days = timedelta(days=self.days)
        start = datetime.combine(today, self.starting_time)
        end = datetime.combine(today + days, self.ending_time)
        difference = (end - start) if (end > start) else (start - end)
        return difference

    @property
    def localized_display_ending_time(self):
        days_fmt = ungettext_lazy(u'the next day',
                                  u'after {number_of_days} days', self.days)
        days_str = days_fmt.format(
            number_of_days=self.days) if self.days else u''
        return u'{time} {days}'.format(time=localize(self.ending_time),
                                       days=days_str).strip()

    def __unicode__(self):
        return u'{}: {} x {}{} from {} to {}'.format(self.schedule_template,
                                                     self.slots,
                                                     self.task.name,
                                                     self.workplace and u'/{}'.format(
                                                         self.workplace.name) or u'',
                                                     self.starting_time,
                                                     self.localized_display_ending_time)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.days == 0 and self.starting_time >= self.ending_time:
            self.days = 1
        super(ShiftTemplate, self).save(force_insert=force_insert,
                                        force_update=force_update,
                                        using=using,
                                        update_fields=update_fields)
