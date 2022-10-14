from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import TokenExpiredError
import pickle
from datetime import datetime
from uuid import uuid4
from BaseApi import BaseApi
import logging

class SageApi(BaseApi):
    def __init__(self, client_id, client_secret, redirect_uri, token_uri='https://oauth.accounting.sage.com/token', authorization_uri='https://www.sageone.com/oauth2/auth/central', token_file='token.pickle', scope='readonly'):
        self._client_id = client_id
        self._client_secret = client_secret
        self._redirect_uri = redirect_uri
        self._token_uri = token_uri
        self._authorization_uri = authorization_uri
        self._scope = scope
        self._token_file = token_file
        state = uuid4()
        try:
            token = self._load_token()
        except FileNotFoundError:
            token = {}

        valid_token = False
        try: 
            expires = token['expires_at'] + token['refresh_token_expires_in'] - token['expires_in']

            refresh_expires = datetime.fromtimestamp(expires)

            valid_token = refresh_expires > datetime.now()

        except KeyError:
            pass

        extra = extra = { 'client_id': client_id, 'client_secret': client_secret}


        if valid_token:
            self._refresh_token(token)
        else:
            self._session = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=scope, auto_refresh_url=token_uri, auto_refresh_kwargs=extra, token_updater=self._save_token)
            authorization_url, state = self._session.authorization_url(authorization_uri, state=state)
            print('Please go to {} and authorize access.'.format(authorization_url))

            authorization_response = input('Enter the full callback URL: ')

            token = self._session.fetch_token(token_uri, authorization_response=authorization_response, client_secret=client_secret, state=state)

            self._save_token(token)
    
    def get(self, *args, **kwargs):
        try:
            return super().get(*args, **kwargs)
        except TokenExpiredError:
            logging.debug("Refreshing Token")
            token = self._load_token()
            self._refresh_token(token)
            return super().get(*args, **kwargs)

    def _refresh_token(self, token):
        extra = { 'client_id': self._client_id, 'client_secret': self._client_secret}
        self._session = OAuth2Session(self._client_id, token=token, auto_refresh_url=self._token_uri, auto_refresh_kwargs=extra, token_updater=self._save_token)

    def _save_token(self, token):
        with open(self._token_file, 'wb') as fh:
            pickle.dump(token, fh)
    def _load_token(self):
        with open(self._token_file, 'rb') as fh:
            return pickle.load(fh)
    
