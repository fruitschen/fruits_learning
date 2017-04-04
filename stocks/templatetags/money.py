# -*- encoding: utf-8 -*-
from __future__ import unicode_literals

import re
from datetime import date, datetime
from decimal import Decimal

from django import template
from django.conf import settings
from django.template import defaultfilters
from django.utils.encoding import force_text
from django.utils.formats import number_format
from django.utils.safestring import mark_safe
from django.utils.timezone import is_aware, utc
from django.utils.translation import pgettext, ugettext as _, ungettext

register = template.Library()

# A tuple of standard large number to their converters
# 1,809,379,782.37
#
intword_converters = (
    (12, lambda number: (
        ungettext('%(value).3f 万亿', '%(value).3f 万亿', number),
        ungettext('%(value)s 万亿', '%(value)s 万亿', number),
    )),
    (8, lambda number: (
        ungettext('%(value).3f 亿', '%(value).3f 亿', number),
        ungettext('%(value)s 亿', '%(value)s 亿', number),
    )),
    (7, lambda number: (
        ungettext('%(value).3f 千万', '%(value).3f 千万', number),
        ungettext('%(value)s 千万', '%(value)s 千万', number),
    )),
    (6, lambda number: (
        ungettext('%(value).3f 百万', '%(value).3f 百万', number),
        ungettext('%(value)s 百万', '%(value)s 百万', number),
    )),
    (4, lambda number: (
        ungettext('%(value).3f 万', '%(value).3f 万', number),
        ungettext('%(value)s 万', '%(value)s 万', number),
    )),
)


@register.filter(is_safe=False)
def money_display(value):
    """
    Converts a large integer to a friendly text representation. Works best
    for numbers over 1 million. For example, 1000000 becomes '1.0 million',
    1200000 becomes '1.2 million' and '1200000000' becomes '1.2 billion'.
    """
    original_value = value

    if value:
        abs_value = abs(value)
        value = Decimal(value)
        if abs_value < 10000:
            if '.' in str(value) and len(str(value).split('.')[-1]) > 3:
                value = value.quantize(Decimal('0.001'))
            return value

    try:
        value = int(value)
    except (TypeError, ValueError):
        return value

    if abs(value) < 10000:
        return original_value

    def _check_for_i18n(value, float_formatted, string_formatted):
        """
        Use the i18n enabled defaultfilters.floatformat if possible
        """
        if settings.USE_L10N:
            value = defaultfilters.floatformat(value, 3)
            template = string_formatted
        else:
            template = float_formatted
        return template % {'value': value}

    for exponent, converters in intword_converters:
        large_number = 10 ** exponent
        if abs(value) > large_number:
            new_value = value / float(large_number)
            return _check_for_i18n(new_value, *converters(new_value))
    return value

