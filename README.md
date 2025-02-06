# cel-scheduler

## Running
### Install dependencies
Ensure you're running Python 3.10+.

Pull down the repo to your local machine, initialize a virtual environment with your tool of choice in the `cel-scheduler` directory, then run:
```Bash
pip freeze > requirements.txt
```

### Set up DB
This project uses the built-in SQLite3 Database. Simply run:
```Bash
python manage.py migrate
```

### Start app
```Bash
python manage.py runserver
```

## Assumptions
I made a variety of assumptions and decisions in the course of putting this together:
- Most critically, I decided to use an "end" time for events as the primary field for determining duration, both on the back-end and the front-end, as this makes querying and user input much more straightforward. Since the specifications mentioned duration specifically, I included the duration in the event list display and in the DB as a calculated field.
- To keep the list of events from immediately becoming overwhelming, I arbitrarily set a 10-week-ahead limit for how far out recurring events are scheduled. This has a known limitation, in that events that don't start until more than 10 weeks from the current date may not be fully checked for conflicts. Since I didn't fit a patch for this into the 4-hour limit, I'll just note here that I would likely fix this by setting the `time_horizon` in `views:index` to be the maximum of the current calculation or `end = datetime.strptime(request.POST["end"], '%Y-%m-%dT%H:%M')` (with some error handling since that value isn't validated yet at that point in the code).
- I assumed I should keep UI capabilities to what's strictly listed in the document, so there is no update or delete capability built-in.
- I assumed lightweight and functional was the priority  for the UI, so I focused my time on tightening backend logic and kept the front-end to a single view and just used vanilla JS and minimal CSS for the most basic visual enhancements.

## Additional notes
With another hour or so, I would focus on test coverage and adding comments; I was hoping to have at least full coverage of the model validations, but only had the a few tests half-written when time ran out, so I backed out those changes.