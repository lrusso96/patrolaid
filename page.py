from revision import Revision


class Page:
    def __init__(self, **data):
        self.id = data['pageid']
        self.ns = data['ns']
        self.title = data['title']
        self.revisions = [Revision(self, **rev) for rev in data['revisions']]
        self.last_rev_id = self.revisions[0].id # assume to get always the last revisions!
