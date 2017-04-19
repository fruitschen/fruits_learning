# -*- coding: UTF-8 -*-
from django.core.cache import cache
import pytest
pytestmark = pytest.mark.django_db


def test_with_client(client):
    response = client.get('/')
    assert 'fruitschen' in response.content


def test_cache_is_working():
    cache.clear()
    result = cache.get('cache.key')
    assert result is None
    cache.set('cache.key', 'something')
    result = cache.get('cache.key')
    assert result == 'something'
    cache.delete('cache.key')
    result = cache.get('cache.key')
    assert result is None
