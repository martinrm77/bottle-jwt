# -*- coding: utf-8 -*-
"""Unit test fixtures for `bottle_jwt.auth` module
"""
from __future__ import unicode_literals
from __future__ import print_function


import pytest
import bottle
from bottle_jwt.auth import (
    JWTProvider, JWTProviderError, JWTProviderPlugin, jwt_auth_required
)


@pytest.fixture(scope='module')
def provider(backend):
    """Fixture for `bottle_jwt.JWTProvider` class instance.
    """
    b = backend({"pav": "123", "ama": "123", "max": '456'})

    return JWTProvider(
        fields=('username', 'secret'),
        backend=b,
        secret='123',
        ttl=1
    )


@pytest.fixture(scope='module')
def provider_plugin(backend):
    """Fixture for `bottle_jwt.JWTProviderPlugin` class instance.
    """

    b = backend({"pav": "123", "ama": "123", "max": '456'})

    return JWTProviderPlugin(
        'auth',
        auth_endpoint='/auth',
        fields=('username', 'secret'),
        backend=b,
        secret='123',
        ttl=1
    )


def test_provider_authenticate(provider, request):
    """
    """

    r = request({"username": "pav", "secret": "123"})

    token = provider.authenticate(r)

    assert len(token) > 100


def test_provider_authenticate_fail(provider, request):
    """
    """

    r = request({"username": "pax", "secret": "123"})

    with pytest.raises(JWTProviderError):
        provider.authenticate(r)


def test_provider_authorize_pass(provider, request):
    """
    """
    r = request({"username": "pav", "secret": "123"})

    token = provider.authenticate(r)

    r.set_header('Authorization', 'JWT {}'.format(token.decode("utf-8")))

    data = provider.authorize(r)

    assert data


def test_provider_authorize_invalid_token_fail(provider, request):
    """
    """
    r = request({"username": "pav", "secret": "123"})

    token = provider.authenticate(r)

    r.set_header('Authorization', 'JWT {}123'.format(token.decode("utf-8")))

    with pytest.raises(JWTProviderError):
        provider.authorize(r)


def test_provider_authorize_no_token_fail(provider, request):
    """
    """
    r = request({"username": "pav", "secret": "123"})

    with pytest.raises(JWTProviderError):
        provider.authorize(r)


def test_provider_authorize_exp_fail(provider, request):
    """
    """
    r = request({"username": "pav", "secret": "123"})

    token = provider.authenticate(r)

    r.set_header('Authorization', 'JWT {}'.format(token))

    import time

    time.sleep(2)

    with pytest.raises(JWTProviderError):
        provider.authorize(r)


def test_provider_plugin_register(provider_plugin):
    """
    """
    app = bottle.Bottle()

    app.install(provider_plugin)

    @jwt_auth_required
    def app_handler():
        return 'Private Resource'

    app.get('/')(app_handler)

    assert len(app.routes) == 2
