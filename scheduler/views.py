from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import render
from django.utils import timezone

from .forms import EventForm, EventSeriesForm
from .models import Event, EventSeries

def index(request):
    events = Event.objects.order_by("start")
    series_form = EventSeriesForm()
    event_form = EventForm()
    if request.method == "POST":
        time_horizon = timezone.now() + timezone.timedelta(weeks=10)
        repeating_series = EventSeries.objects.filter(has_repeats=True)
        for e in repeating_series:
            e.extend(time_horizon)
        series_form = EventSeriesForm(request.POST)
        event_form = EventForm(request.POST)
        if series_form.is_valid() and event_form.is_valid():
            series = series_form.save(commit=False)
            event = event_form.save(commit=False)
            events_valid = True
            event_list = []
            for day in series.get_repeats():
                t = event.start
                while t <= time_horizon:
                    t += timezone.timedelta(days=(7 + t.weekday() - day))
                    try:
                        e = Event(start = t, end = t + event.duration, event_series = series)
                        e.clean()
                        event_list.append(e)
                    except ValidationError as err:
                        messages.error(request, err.message)
                        events_valid = False
                        break
                if not events_valid:
                    break
            if events_valid:
                series.save()
                event.event_series = series
                event.save()
                for e in event_list:
                    e.event_series = series
                    e.save()
                messages.success(request, "Event saved!")
        else:
            messages.error(request, "There was an error adding your event.")
    context = {
        "events": events,
        "series_form": series_form,
        "event_form": event_form
    }
    return render(request, "scheduler/index.html", context)
    