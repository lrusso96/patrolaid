class Revision:
    def __init__(self, page, **kwargs):
        self.page = page
        self.id = kwargs['revid']
        self.user = kwargs['user']
        self.comment = kwargs['comment']