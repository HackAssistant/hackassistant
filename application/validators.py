import os

import filetype
from django.core.exceptions import ValidationError
from django.conf import settings


def validate_file_extension(value):
    (_, ext) = os.path.splitext(value.name)
    valid_extensions = getattr(settings, 'SUPPORTED_RESUME_EXTENSIONS', None)
    if valid_extensions and not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension.')
    matches = [f_t for f_t in filetype.TYPES if ('.' + f_t.extension) in valid_extensions]
    if filetype.match(value.file.read(), matches) is None:
        raise ValidationError('Unsupported file type.')
