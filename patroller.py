import logging
import os
import requests
from requests_oauthlib import OAuth1
from dotenv import load_dotenv

from page import Page
from tokens import Token
from templates import Template


class Patroller:
    """Models a it.wikipedia patroller. Needs consumer and access tokens to work properly.

    """

    def __init__(self):
        load_dotenv()
        consumer_token = os.getenv('CONSUMER_TOKEN')
        consumer_secret = os.environ['CONSUMER_SECRET']
        access_token = os.environ['ACCESS_TOKEN']
        access_secret = os.environ['ACCESS_SECRET']
        logging.info('initializing OAuth1...')
        self._auth = OAuth1(consumer_token, consumer_secret,
                            access_token, access_secret)
        self._endpoint = 'https://it.wikipedia.org/w/api.php'
        self.redirect_wl = os.environ['REDIRECT_WL']
        self.tokens = {}

    def authenticate(self):
        """Authenticate current patroller.

        Checks whether the current configuration is correct or not, using OAuth1 protocol.
        Any error (e.g. 'invalid-authorization') is logged, with a code and a brief summary.
        It is not strictly required to call this before other methods, prefer instead add the assert=user parameter
        to all requests that should be made by a logged-in user.
        See https://www.mediawiki.org/wiki/API:Assert for details

        Examples:
            >>> patroller = Patroller()
            >>> if patroller.authenticate():
            >>>     print(...)

        Args:

        Returns:
            True if successful, else False

        Raises:

        """
        logging.info('initializing authentication...')
        data = {'action': 'query', 'assert': 'user'}
        r = self.__mw_post__(**data)
        error = r.json().get('error')
        if error:
            logging.error('%s: %s\n%s', error.get('code'),
                          error.get('info'), error.get('*'))
        return error is None

    def parse(self, page):
        # logging.info('requesting parse of page %s', page)
        # data = {'action': 'parse', 'page': page}
        # r = self.__mw_post__(**data)
        # print(r.json())
        pass

    def edit(self, page, text, summary):
        # TODO wrap edit calls, like restore, warn_user, etc
        # TODO handle errors here too.
        pass

    def get_last_revisions(self, title, limit=5):
        """Retrieves last revisions (at most 'limit') of a page, given its title.

        Examples:
            >>> pt = Patroller()
            >>> revs = pt.get_last_revisions('Main page', limit=20)
            >>> page = revs[0].page # retrieve corresponding page object
            >>> for rev in revs:
            >>>     # do stuff...

        Args:
            title: the title of page
            limit: max number of revisions to load. Default value is 5.

        Returns:
            the list of revisions.

        Raises:

        """
        data = {'action': 'query', "prop": "revisions",
                "titles": title,
                "rvprop": "user|comment|ids",
                "rvslots": "main",
                'rvlimit': limit,
                "formatversion": "2"}
        r = self.__mw_get__(**data)
        pages = r.json()['query']['pages'][0]
        page = Page(**pages)
        return page.revisions

    def __get_token__(self, *tokens):
        """Get tokens required by data-modifying actions.

        For each action, you need a specific type of token. For example: if you want to login to a wiki site via the
        Action API, you would need a token of type “login” to proceed.

        NOTE: does not (yet) handle cache!

            >>> self.__get_token__(Token.LOGIN)
            >>> Token.LOGIN.value in self.tokens
            >>> True

        It is also possible to request more than one token, for example:

            >>> self.__get_token__(Token.LOGIN, Token.CREATE_ACCOUNT, ...)

        Args:
            *tokens: list of tokens of type Token. The default value is 'csrf'

        Returns:
            None. The tokens are stored in self.tokens.

        Raises:

        """
        data = {'action': 'query', 'meta': 'tokens'}
        if len(tokens):
            data['type'] = '|'.join(list(map(lambda x: x.value, tokens)))
        r = self.__mw_get__(**data)
        ret = r.json()['query']['tokens']
        for token in ret:
            self.tokens[token.replace('token', '')] = ret[token]

    def __mw_post__(self, **kwargs):
        """Wraps a request.post call, with a basic configuration.

        In particular, json format is used for output.
        Any call is authenticated with OAuth1 protocol.

            >>> args = {'action': 'query', ...}
            >>> self.__mw_post__(args) # do oauth, use json...

        Args:
            **kwargs: dictionary of parameters for the POST call.

        Returns:
            a Response object.
        """
        args = {'format': 'json'}
        kwargs.update(args)
        return requests.post(url=self._endpoint, data=kwargs, auth=self._auth)

    def __mw_get__(self, **kwargs):
        """Wraps a request.get call, with a basic configuration.

        In particular, json format is used for output.
        Any call is authenticated with OAuth1 protocol.

            >>> args = {'action': 'query', ...}
            >>> self.__mw_get__(args) # do oauth, use json...

        Args:
            **kwargs: dictionary of parameters for the GET call.

        Returns:
            a Response object.
        """
        args = {'format': 'json'}
        kwargs.update(args)
        return requests.get(url=self._endpoint, params=kwargs, auth=self._auth)

    def restore(self, revision, summary='rb'):
        """Restores a revision.
        NOTE: does not (yet) handle errors!

        Example:


        Args:
            revision: the one to be restored
            summary: the description of the restore action. Default is 'rb'.

        Returns:

        Raises:

        """
        if Token.CSRF.value not in self.tokens:
            self.__get_token__(Token.CSRF)
        token = self.tokens[Token.CSRF.value]
        summary = f"{self.redirect_wl}:  {summary}"
        data = {'action': 'edit', 'pageid': revision.page.id, 'summary': summary, 'undo': revision.page.last_rev_id,
                'undoafter': revision.id, 'token': token}
        r = self.__mw_post__(**data).json()
        # just to debug
        if r['edit']['result'].lower() == "success":
            print('restore rev id', revision.id, 'for page', revision.page.id)
        else:
            print("error...", r)

    def warn_user(self, page, user, template=Template.VANDAL, summary='avviso'):
        """Puts a warning template on talk page of user.
        NOTE: does not (yet) handle errors!

        Example:


        Args:
            page: which page the user has 'improperly' modified.
            user: who has to made the improper edit(s).
            template: a Template type, to be used depending on the kind of edit.
            summary: the description of this edit. Default is 'avviso'.

        Returns:

        Raises:

        """
        if Token.CSRF.value not in self.tokens:
            self.__get_token__(Token.CSRF)
        token = self.tokens[Token.CSRF.value]
        text = template.generate(page)
        summary = f"{self.redirect_wl}: {summary}"
        data = {'action': 'edit', 'title': f"Discussioni utente: {user}", 'summary': summary,
                'section': 'new', 'sectiontitle': 'Avviso', 'text': text, 'token': token}
        r = self.__mw_post__(**data).json()
        # just to debug
        if r['edit']['result'].lower() == "success":
            print('ok')
        else:
            print("error...", r)
