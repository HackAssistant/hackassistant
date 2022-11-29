import django_tables2 as tables


class FloatColumn(tables.Column):
    def __init__(self, float_digits=None, *args, **kwargs):
        self.float_digits = float_digits
        super().__init__(*args, **kwargs)

    def render(self, value):
        if isinstance(value, float) and self.float_digits is not None:
            value = round(value, self.float_digits)
        return value
