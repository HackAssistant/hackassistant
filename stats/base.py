import inspect
from datetime import datetime


class BaseStats(object):
    def __init__(self):
        for stat in inspect.getmembers(self):
            if not stat[0].startswith('_') and isinstance(stat[1], Chart):
                stat[1].set_field_name(stat[0])
                stat[1].set_stat_model(self)

    def json(self):
        return [stat[1].json() for stat in inspect.getmembers(self)
                if not stat[0].startswith('_') and isinstance(stat[1], Chart)]

    def to_json(self, instance_list):
        data = {}
        for instance in instance_list:
            for stat in inspect.getmembers(self):
                if not stat[0].startswith('_') and isinstance(stat[1], Chart):
                    value = data.get(stat[1].field_name, None)
                    value = stat[1].update_field(value, instance)
                    data[stat[1].field_name] = value
        for stat in inspect.getmembers(self):
            if not stat[0].startswith('_') and isinstance(stat[1], Chart) and stat[1].field_name in data:
                data[stat[1].field_name] = stat[1].finalize(data[stat[1].field_name])
        return data


class Chart(object):
    TIMESERIES = 'timeseries'
    BAR = 'bar'
    DONUT = 'donut'
    DEFAULT_COL = {TIMESERIES: 12, BAR: 6, DONUT: 6}

    def __init__(self, field_type, col=None, datetime_format='%Y-%m-%d', value_getter=None, order=0, top=None):
        self.datetime_format = datetime_format
        if field_type not in self.DEFAULT_COL.keys():
            raise Exception('Invalid field_type')
        self.value_getter = value_getter
        self.field_type = field_type
        self.field_name = ''
        self.stat_model = None
        self.col = col if isinstance(col, int) and 1 < col < 12 else self.DEFAULT_COL[field_type]
        self.order = order
        self.top = top

    def set_field_name(self, field_name):
        self.field_name = field_name

    def set_stat_model(self, stat_model):
        self.stat_model = stat_model

    def get_field_value(self, instance):
        if hasattr(instance, 'get_%s_display' % self.field_name):
            return getattr(instance, 'get_%s_display' % self.field_name)()
        instance_val = getattr(instance, self.field_name)
        if isinstance(instance_val, datetime):
            instance_val = instance_val.strftime(self.datetime_format)
        if self.value_getter is not None:
            instance_val = getattr(instance_val, self.value_getter)
            if callable(instance_val):
                instance_val = instance_val()
        return instance_val

    def update_default(self, value, instance):
        if value is None:
            value = {}
        instance_val = self.get_field_value(instance)
        if isinstance(instance_val, list):
            for aux in instance_val:
                counter = value.get(aux, 0) + 1
                value[aux] = counter
        elif instance_val is not None and instance_val != '':
            counter = value.get(instance_val, 0) + 1
            value[instance_val] = counter
        return value

    def update_field(self, value, instance):
        updater = getattr(self.stat_model, 'update_%s' % self.field_name, None)
        if updater is not None:
            return updater(self.stat_model, value, instance)
        return self.update_default(value, instance)

    def finalize(self, stats):
        if self.top is None:
            return stats
        return {key: value for key, value in sorted(stats.items(), key=lambda x: -x[1])[:self.top]}

    def json(self):
        return {'field_name': self.field_name, 'col': self.col, 'field_type': self.field_type, 'order': self.order,
                'top': self.top}


class ApplicationFormChart(Chart):
    DEFAULT_COL = {Chart.TIMESERIES: 12, Chart.BAR: 12, Chart.DONUT: 6}

    def get_field_value(self, instance):
        return instance.form_data.get(self.field_name)


class StatsFilterMixin:
    def filter_list(self, instance_list):
        result = []
        for instance in instance_list:
            accept = True
            for name, value in self.form.cleaned_data.items():
                filter_method = getattr(self, 'filter_' + name, None)
                if filter_method is not None and len(value) > 0:
                    if not filter_method(instance, value):
                        accept = False
            if accept:
                result.append(instance)
        return result
