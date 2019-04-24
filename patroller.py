import logging
import os
import requests
from requests_oauthlib import OAuth1


class Patroller:

    def __init__(self):
        consumer_token = os.environ['CONSUMER_TOKEN']
        consumer_secret = os.environ['CONSUMER_SECRET']
        access_token = os.environ['ACCESS_TOKEN']
        access_secret = os.environ['ACCESS_SECRET']
        logging.info('initializing OAuth1...')
        self._auth = OAuth1(consumer_token, consumer_secret, access_token, access_secret)
        self._endpoint = 'https://it.wikipedia.org/w/api.php'

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
            logging.error('%s: %s\n%s', error.get('code'), error.get('info'), error.get('*'))
        return error is None

    def parse(self, page):
        logging.info('requesting parse of page %s', page)
        data = {'action': 'parse', 'page': page}
        r = self.__mw_post__(**data)
        # print(r.json())

    def __get_token__(self, *args):
        """Get tokens required by data-modifying actions.

        For each action, you need a specific type of token. For example: if you want to login to a wiki site via the
        Action API, you would need a token of type “login” to proceed.

            >>> from tokens import Token
            >>> self.__get_token__(Token.LOGIN)

        It is possible to request more than one token, for example:

            >>> self.__get_token__(Token.LOGIN, Token.CREATE_ACCOUNT, ...)

        Args:
            *args: list of tokens of type Token. The default value is 'csrf'

        Returns:
            the token(s) requested

        Raises:

        """
        data = {'action': 'query', 'meta': 'tokens'}
        if len(args):
            data['type'] = '|'.join(list(map(lambda x: x.value, args)))
        r = self.__mw_get__(**data)
        # print(r.json())

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
