
import pytest

@pytest.mark.django_db
def test_with_client(client):
    response = client.get('/')
    assert 'wagtail' in response.content