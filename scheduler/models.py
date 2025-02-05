from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

class EventSeries(models.Model):
    name = models.CharField(max_length=250)
    repeating_mon = models.BooleanField()
    repeating_tue = models.BooleanField()
    repeating_wed = models.BooleanField()
    repeating_thu = models.BooleanField()
    repeating_fri = models.BooleanField()
    repeating_sat = models.BooleanField()
    repeating_sun = models.BooleanField()

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
        repeats = self.get_repeats()
        if not repeats: return
        latest_event = Event.objects.filter(event_series=self).latest("start")
        if latest_event.start > end_date: return
        last_wkday = latest_event.start.weekday()
        for day in repeats:
            skip = (day - last_wkday) if day > last_wkday else (day - last_wkday + 7)
            t = latest_event.start + timezone.timedelta(days=skip)
            while t <= end_date:
                Event(start = t, duration = latest_event.duration, event_series = self).save()
    
    def save(self):
        self.full_clean()
        super().save()

class Event(models.Model):
    start = models.DateTimeField()
    end = models.DateTimeField()
    duration = models.DurationField()
    event_series = models.ForeignKey(EventSeries, on_delete=models.CASCADE)

    def clean(self, *args, **kwargs):
        if self.end <= self.start:
            raise ValidationError('The end time must be after the start time')
        conflict = Event.objects.filter(
            models.Q(start__lte=self.start, end__gte=self.start) |
            models.Q(start_gte=self.start, start_lte=self.end)
        )[:1]
        if conflict.count() > 0:
            raise ValidationError(f'This conflicts with {conflict[0].event_series.name}.')
        super().clean(*args, **kwargs)

    def save(self):
        self.duration = self.end - self.start
        self.full_clean()
        super().save()
