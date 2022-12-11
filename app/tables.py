import django_tables2 as tables


class FloatColumn(tables.Column):
    def __init__(self, float_digits=None, *args, **kwargs):
        self.float_digits = float_digits
        super().__init__(*args, **kwargs)

    def render(self, value):
        if isinstance(value, float) and self.float_digits is not None:
            value = round(value, self.float_digits)
        return value


class TruncatedTextColumnMixin:
    """A Column to limit to x characters and add an ellipsis"""
    def __init__(self, truncated_at=30, *args, **kwargs):
        self.truncated_at = truncated_at
        super().__init__(*args, **kwargs)

    def truncate_text(self, text):
        text = str(text)
        if len(text) > self.truncated_at:
            text = text[:(self.truncated_at - 3)] + '...'
        return text


class TruncatedTextColumn(TruncatedTextColumnMixin, tables.Column):
    def render(self, value):
        return super().render(self.truncate_text(value))


class TruncatedEmailColumn(TruncatedTextColumnMixin, tables.EmailColumn):
    def text_value(self, record, value):
        return super().text_value(record, self.truncate_text(value))


class TruncatedLinkColumn(TruncatedTextColumnMixin, tables.LinkColumn):
    def text_value(self, record, value):
        return super().text_value(record, self.truncate_text(value))
