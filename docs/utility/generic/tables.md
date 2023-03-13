# Tables [+](/app/tables.py)

Utilities for the [Django tables 2](../../configuration/libraries/django_tables2.md).

## FloatColumn

Improvement of Column for Decimals to round the decimals digits.
Adds Kwargs `float_digits` to round the number to that value.

## TruncatedTextColumnMixin

Mixin to limit to x characters and add an ellipsis to a column.
Implemented for:

- **TruncatedTextColumn**
- **TruncatedEmailColumn**
- **TruncatedLinkColumn**
