import os

import filetype
from django.core.exceptions import ValidationError


def validate_file_extension(valid_extensions, type_check=True):
    def wrapper(value):
        (_, ext) = os.path.splitext(value.name)
        if valid_extensions and not ext.lower() in valid_extensions:
            raise ValidationError('Unsupported file extension.')
        if type_check:
            matches = [f_t for f_t in filetype.TYPES if ('.' + f_t.extension) in valid_extensions]
            if filetype.match(value.file.read(), matches) is None:
                raise ValidationError('Unsupported file type.')
    return wrapper
