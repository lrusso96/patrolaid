from enum import Enum


class Template(Enum):
    """This class is an Enumeration for basic patrol templates.
    Most of them are self explaining.

    """

    VANDAL = 'vandalismo'
    YC = 'yc'
    TEST = 'test'
    PROMO = 'promo'
    CONTENT_REMOVAL = 'rimozioneContenuti'

    def generate(self, page):
        return '{{%s|%s}} ~~~~' % (self.value, page.title)