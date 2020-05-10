from django.template.defaultfilters import slugify as django_slugify
"""
Usage of this model is
from unique.custom_slugify import slugify
and use
as slugify("Text")
"""

alphabet = {'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo', 'ж': 'zh', 'з': 'z', 'и': 'i',
            'й': 'j', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't',
            'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch', 'ы': 'y', 'э': 'e', 'ю': 'yu',
            'я': 'ya', 'ә': 'ae', 'ғ': 'gh', 'қ': 'q', 'ң': 'ng', 'ө': 'oe', 'ұ': 'u',
            'ү': 'ue', 'і': 'i'}


def slugify(s):
    """
    Overriding django slugify that allows to use russian words as well.
    """
    return django_slugify(''.join(alphabet.get(w, w) for w in s.lower()))

#  TODO ZHAMAN SOZDERDI UDalit etu
