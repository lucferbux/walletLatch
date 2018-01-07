### LATCH + COINBASE  ###


#### PREREQUISITES LATCH ####

* Python.

* Read API documentation (https://latch.elevenpaths.com/www/developers/doc_api).

* To get the "Application ID" and "Secret", (fundamental values for integrating Latch in any application), it’s necessary to register a developer account in Latch's website: https://latch.elevenpaths.com. On the upper right side, click on "Developer area".



#### USING THE SDK IN PYTHON ####

* Import "latch" module.
```
	import latch
```

* Create a Latch object with the "Application ID" and "Secret" previously obtained.
```
	api = latch.Latch("APP_ID_HERE", "SECRET_KEY_HERE")
```

* Optional settings:
```
	latch.Latch.set_proxy("PROXY_HOST_HERE", port)
```

* Call to Latch Server. Pairing will return an account id that you should store for future api calls
```
	response = api.pair("PAIRING_CODE_HERE")
	response = api.status("ACCOUNT_ID_HERE")
	response = api.unpair("ACCOUNT_ID_HERE")
```

* After every API call, get Latch response data and errors and handle them.
```
	responseData = response.get_data()
	responseError = response.get_error()
  ```

#### PREREQUISITES COINBASE  ####

Features
--------

- Near-100% test coverage.
- Support for both `API Key + Secret <https://developers.coinbase.com/api/v2/#api-key>`_ and `OAuth 2 <https://developers.coinbase.com/api/v2/#oauth2-coinbase-connect>`_ authentication.
- Convenient methods for making calls to the API - packs JSON for you!
- Automatic parsing of API responses into relevant Python objects.
- All objects have tab-completable methods and attributes when using `IPython <http://ipython.org>`_.


Installation
------------

``coinbase`` is available on `PYPI <https://pypi.python.org/pypi/coinbase/>`_.
Install with ``pip``:

.. code:: bash

    pip install coinbase

or with ``easy_install``:

.. code:: bash

    easy_install coinbase

The library is currently tested against Python versions 2.6.9, 2.7.10, 3.2, 3.3.6, and 3.4.3.

Documentation
-------------

The first thing you'll need to do is `sign up with Coinbase <https://coinbase.com>`_.

API Key + Secret
^^^^^^^^^^^^^^^^

If you're writing code for your own Coinbase account, `enable an API key <https://coinbase.com/settings/api>`_.

Next, create a ``Client`` object for interacting with the API:

.. code:: python

    from coinbase.wallet.client import Client
    client = Client(api_key, api_secret)

OAuth2
^^^^^^

If you're writing code that will act on behalf of another user, start by `creating a new OAuth 2 application from the API settings page <https://coinbase.com/settings/api>`_.
You will need to do some work to obtain OAuth credentials for your users; while outside the scope of this document, please refer to our `OAuth 2 flow documentation <https://developers.coinbase.com/docs/wallet/coinbase-connect>`_.
Once you have these credentials (an ``access_token`` and ``refresh_token``), create a client:

.. code:: python

    from coinbase.wallet.client import OAuthClient
    client = OAuthClient(access_token, refresh_token)

Making API Calls
^^^^^^^^^^^^^^^^

Both the ``Client`` and ``OAuthClient`` support all of the same API calls.
We've included some examples below, but in general the library has Python classes for each of the objects described in our `REST API documentation <https://developers.coinbase.com/api/v2>`_.
These classes each have methods for making the relevant API calls; for instance, ``coinbase.wallet.model.Order.refund`` maps to `the "refund order" API endpoint <https://developers.coinbase.com/api/v2#refund-an-order>`_.
The docstring of each method in the code references the endpoint it implements.

Every method supports the passing of arbitrary parameters via keyword.
These keyword arguments will be sent directly to the relevant endpoint.
If a required parameter is not supplied, the relevant error will be raised.

Each API method returns an ``APIObject`` (a subclass of ``dict``) representing the JSON response from the API, with some niceties like pretty-printing and attr-style item access (``response.foo`` is equivalent to ``response['foo']``). All of the models are dumpable with JSON:

.. code:: python

    user = client.get_current_user()
    user_as_json_string = json.dumps(user)


And, when the response data is parsed into Python objects, the appropriate ``APIObject`` subclasses will be used automatically.
See the code in ``coinbase.wallet.model`` for all of the relevant classes, or the examples below.
API methods that return lists of objects (for instance, ``client.get_accounts()`` return ``APIObject`` instances with nice wrappers around the ``data`` of the response body. These objects support direct indexing and slicing of the list referenced by ``data``.

.. code:: python

    accounts = client.get_accounts()
    assert isinstance(accounts.data, list)
    assert accounts[0] is accounts.data[0]
    assert len(accounts[::]) == len(accounts.data)

But, the ``APIObject`` is not actually a list (it's a subclass of ``dict``) so you cannot iterate through the items of ``data`` directly.
Simple slicing and index access are provided to make common uses easier, but to access the actual list you must reference the ``data`` attribute.

Refreshing
""""""""""
All the objects returned by API methods are subclasses of the ``APIObject`` and support being "refreshed" from the server.
This will update their attributes and all nested data by making a fresh ``GET`` request to the relevant API endpoint:

.. code:: python

    accounts = client.get_accounts()
    # Create a new account via the web UI
    accounts.refresh()
    # Now, the new account is present in the list


Warnings
""""""""
The API V2 `will return relevant *warnings* along with the response data <https://developers.coinbase.com/api/v2#warnings>`_.
In a successful API response, any warnings will be present as a list on the returned ``APIObject``:

.. code:: python

    accounts = client.get_accounts()
    assert (accounts.warnings is None) or isinstance(accounts.warnings, list)

All warning messages will also be alerted using the `Python stdlib warnings module <https://docs.python.org/2/library/warnings.html>`_.

Pagination
""""""""""
Several of the API V2 endpoints `are paginated <https://developers.coinbase.com/api/v2#pagination>`_.
By default, only the first page of data is returned. All pagination data will be present under the ``pagination`` attribute of the returned ``APIObject``:

.. code:: python

    accounts = client.get_accounts()
    assert (accounts.pagination is None) or isinstance(accounts.pagination, dict)


Error Handling
^^^^^^^^^^^^^^

All errors occuring during interaction with the API will be raised as exceptions.
These exceptions will be subclasses of ``coinbase.wallet.error.CoinbaseError``.
When the error involves an API request and/or response, the error will be a subclass of ``coinbase.error.APIError``, and include ``request`` and ``response`` attributes with more information about the failed interaction.
For full details of error responses, please refer `to the relevant API documentation <https://developers.coinbase.com/api/v2#errors>`_.

=============================  ================
Error                          HTTP Status Code
=============================  ================
APIError                       *
TwoFactorRequiredError         402
ParamRequiredError             400
ValidationError                422
InvalidRequestError            400
PersonalDetailsRequiredError   400
AuthenticationError            401
UnverifiedEmailError           401
InvalidTokenError              401
RevokedTokenError              401
ExpiredTokenError              401
InvalidScopeError              403
NotFoundError                  404
RateLimitExceededError         429
InternalServerError            500
ServiceUnavailableError        503
=============================  ================


OAuth Client
^^^^^^^^^^^^

The OAuth client provides a few extra methods to refresh and revoke the access token.

.. code:: python

    # exchange the current access_token and refresh_token for a new pair
    oauth_client.refresh()

This method will update the values stored in the client and return a ``dict`` containing information from the token endpoint so that you can update your records.

.. code:: python

    # revoke the current access_token and refresh_token
    oauth_client.revoke()

*Protip*: You can test OAuth2 authentication easily with Developer Access Tokens which can be created `in your OAuth2 application settings <https://www.coinbase.com/settings/api>`_. These are short lived tokens which authenticate but don't require full OAuth2 handshake to obtain.

Two Factor Authentication
^^^^^^^^^^^^^^^^^^^^^^^^^
Sending money may require the user to supply a 2FA token `in certain situations <https://developers.coinbase.com/docs/wallet/coinbase-connect#two-factor-authentication>`_.
If this is the case, a ``TwoFactorRequiredError`` will be raised:

.. code:: python

    from coinbase.wallet.client import Client
    from coinbase.wallet.error import TwoFactorRequiredError

    client = Client(api_key, api_secret)
    account = client.get_primary_account()
    try:
      tx = account.send_money(to='test@test.com', amount='1', currency='BTC')
    except TwoFactorRequiredError:
      # Show 2FA dialog to user and collect 2FA token
      # two_factor_token = ...
      # Re-try call with the `two_factor_token` parameter
      tx = account.send_money(to='test@test.com', amount='1', currency='BTC', two_factor_token="123456")

`Notifications/Callbacks <https://developers.coinbase.com/docs/wallet/notifications>`_
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Verify notification authenticity**

.. code:: python

    client.verify_callback(request.body, request.META['CB-SIGNATURE']) # true/false

