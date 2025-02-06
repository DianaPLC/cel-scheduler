from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

class EventSeries(models.Model):
    name = models.CharField(max_length=250)
    repeating_mon = models.BooleanField("Monday")
    repeating_tue = models.BooleanField("Tuesday")
    repeating_wed = models.BooleanField("Wednesday")
    repeating_thu = models.BooleanField("Thursday")
    repeating_fri = models.BooleanField("Friday")
    repeating_sat = models.BooleanField("Saturday")
    repeating_sun = models.BooleanField("Sunday")
    has_repeats = models.BooleanField()

    def get_repeats(self):
        repeat_list = [
            self.repeating_mon,
            self.repeating_tue,
            self.repeating_wed,
            self.repeating_thu,
            self.repeating_fri,
            self.repeating_sat,
            self.repeating_sun
        ]
        return [i for i, d in enumerate(repeat_list) if d]

    def extend(self, end_date: timezone.datetime):
        if not self.has_repeats: return
        latest_event = Event.objects.filter(event_series=self).latest("start")
        if latest_event.start > end_date: return
        last_wkday = latest_event.start.weekday()
        for day in self.get_repeats():
            skip = (day - last_wkday) if day > last_wkday else (day - last_wkday + 7)
            t = latest_event.start + timezone.timedelta(days=skip)
            while t <= end_date:
                Event(
                    start = t,
                    end = t + latest_event.duration,
                    duration = latest_event.duration,
                    event_series = self
                ).save()
                t += timezone.timedelta(weeks=1)

    def clean(self, *args, **kwargs):
        super().clean(*args, **kwargs)
        self.has_repeats = bool(self.get_repeats())
    
    def save(self):
        self.full_clean()
        super().save()

class Event(models.Model):
    start = models.DateTimeField()
    end = models.DateTimeField()
    duration = models.DurationField()
    event_series = models.ForeignKey(EventSeries, on_delete=models.CASCADE)

    def clean(self, *args, **kwargs):
        super().clean(*args, **kwargs)
        if self.end <= self.start:
            raise ValidationError('The end time must be after the start time')
        conflict = Event.objects.filter(
            models.Q(start__lte=self.start, end__gte=self.start) |
            models.Q(start__gte=self.start, start__lte=self.end)
        )[:1]
        if conflict.count() > 0:
            raise ValidationError(f'This conflicts with {conflict[0].event_series.name}.')
        self.duration = self.end - self.start

    def save(self):
        self.full_clean()
        super().save()
