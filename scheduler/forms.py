from django.forms import ModelForm, DateTimeInput
from .models import Event, EventSeries

class EventSeriesForm(ModelForm):
    class Meta:
        model = EventSeries
        fields = [
            "name",
            "repeating_mon",
            "repeating_tue",
            "repeating_wed",
            "repeating_thu",
            "repeating_fri",
            "repeating_sat",
            "repeating_sun"
        ]

class EventForm(ModelForm):
    class Meta:
        model = Event
        fields = ["start", "end"]
        localized_fields = ["start", "end"]
        widgets = {
            "start": DateTimeInput(attrs={
                "type": "datetime-local",
                "onblur": "set_min_end(this)"
            }),
            "end": DateTimeInput(attrs={
                "type": "datetime-local",
                "onblur": "this.reportValidity()"
            }),
        }