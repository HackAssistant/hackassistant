from stats import base


class UserStats(base.BaseStats):
    date_joined = base.Chart(base.Chart.TIMESERIES, order=1)
    diet = base.Chart(base.Chart.DONUT, order=2)
    gender = base.Chart(base.Chart.DONUT, order=3)
    tshirt_size = base.Chart(base.Chart.DONUT, order=4)


class ApplicationStats(base.BaseStats):
    submission_date = base.Chart(base.Chart.TIMESERIES, order=1)
    type = base.Chart(base.Chart.DONUT, value_getter='name', order=2)
    status = base.Chart(base.Chart.DONUT, order=3)
    country = base.ApplicationFormChart(base.Chart.BAR, order=4, top=10)
    first_timer = base.ApplicationFormChart(base.Chart.DONUT, order=5)
    graduation_year = base.ApplicationFormChart(base.Chart.DONUT, order=6)
    university = base.ApplicationFormChart(base.Chart.BAR, order=7, top=10)
    degree = base.ApplicationFormChart(base.Chart.BAR, order=8, top=10)
    attendance = base.ApplicationFormChart(base.Chart.BAR, order=13)
    first_time_volunteering = base.ApplicationFormChart(base.Chart.DONUT, order=9)
    which_hack = base.ApplicationFormChart(base.Chart.DONUT, order=10, value_getter='name')
    night_shifts = base.ApplicationFormChart(base.Chart.DONUT, order=11)
    english_level = base.ApplicationFormChart(base.Chart.DONUT, order=12)
    study_work = base.ApplicationFormChart(base.Chart.DONUT, order=13)
    previous_roles = base.ApplicationFormChart(base.Chart.DONUT, order=13)
    company = base.ApplicationFormChart(base.Chart.BAR, order=13)
