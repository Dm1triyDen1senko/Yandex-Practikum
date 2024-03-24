from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects

from .constants import Urls, UserClient


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url, parametrized_client, status_code',
    ((Urls.NEWS_HOME, UserClient.ANONYMOUS, HTTPStatus.OK),
     (Urls.NEWS_DETAIL, UserClient.ANONYMOUS, HTTPStatus.OK),
     (Urls.LOGIN, UserClient.ANONYMOUS, HTTPStatus.OK),
     (Urls.LOGOUT, UserClient.ANONYMOUS, HTTPStatus.OK),
     (Urls.SIGNUP, UserClient.ANONYMOUS, HTTPStatus.OK),
     (Urls.NEWS_EDIT, UserClient.AUTHOR, HTTPStatus.OK),
     (Urls.NEWS_DELETE, UserClient.AUTHOR, HTTPStatus.OK),
     (Urls.NEWS_EDIT, UserClient.READER, HTTPStatus.NOT_FOUND),
     (Urls.NEWS_DELETE, UserClient.READER, HTTPStatus.NOT_FOUND),
     )
)
def test_pages_availability(url, parametrized_client, status_code):
    assert parametrized_client.get(url).status_code == status_code


@pytest.mark.parametrize(
    'url, expected_url',
    ((Urls.NEWS_EDIT, Urls.REDIRECT_EDIT),
     (Urls.NEWS_DELETE, Urls.REDIRECT_DELETE))
)
def test_redirect_to_login_page(client, url, expected_url):
    assertRedirects(client.get(url), expected_url)
