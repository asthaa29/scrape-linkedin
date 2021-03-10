from .utils import *
from .ResultsObject import ResultsObject
import re
from datetime import datetime


class Activity(ResultsObject):
    """Linkedin User Profile Object"""

    attributes = ['activities']

    @property
    def activities(self):
        """Return dict of personal info about the user"""
        top_card = all_or_default(self.soup, '.occludable-update')
        information = []
        for i in top_card:
            action = text_or_default(i,'.t-12')
            if action is not None and not any(a in action for a in ['likes', 'liked', 'replied', 'commented']):
                element = {}
                element['post'] = text_or_default(i,'.feed-shared-update-v2__description-wrapper')
                element['no_of_likes'] = text_or_default(i, '.social-details-social-counts__count-value')
                element['no_of_comments'] = text_or_default(i, '.social-details-social-counts__comments')
                information.append(element)

        return information

    def to_dict(self):
        info = super(Activity, self).to_dict()
        return info
