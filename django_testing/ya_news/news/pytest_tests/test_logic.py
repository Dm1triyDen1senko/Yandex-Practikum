from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError

from news.forms import WARNING
from news.models import Comment


@pytest.mark.django_db
def test_user_can_add_comment(
    author_client, comment_form_data, news_detail_url
):
    response = author_client.post(news_detail_url, data=comment_form_data)

    assert response.status_code == HTTPStatus.FOUND

    assert Comment.objects.count() == 1


@pytest.mark.django_db
def test_anonymous_cant_add_comment(
    client, comment_form_data, news_detail_url
):
    response = client.post(news_detail_url, data=comment_form_data)

    assert response.status_code == HTTPStatus.FOUND

    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_author_can_edit_comment(
    author_client, news_edit_url, new_comment_form_data, comment
):
    response = author_client.post(news_edit_url, new_comment_form_data)

    comment.refresh_from_db()

    assert response.status_code == HTTPStatus.FOUND

    assert comment.text == new_comment_form_data['text']


@pytest.mark.django_db
def test_author_can_delete_comment(author_client, news_delete_url,):
    response = author_client.post(news_delete_url)

    assert response.status_code == HTTPStatus.FOUND

    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_cant_edit_another_user_comment(
    reader_client, news_edit_url, new_comment_form_data, comment
):
    response = reader_client.post(news_edit_url, new_comment_form_data)

    comment.refresh_from_db()

    assert response.status_code == HTTPStatus.NOT_FOUND

    assert comment.text == comment.text


@pytest.mark.django_db
def test_user_cant_delete_another_user_comment(reader_client, news_delete_url):
    response = reader_client.post(news_delete_url)

    assert response.status_code == HTTPStatus.NOT_FOUND

    assert Comment.objects.count() == 1


@pytest.mark.django_db
def test_anonymous_cant_delete_another_user_comment(client, news_delete_url):
    response = client.post(news_delete_url)

    assert response.status_code == HTTPStatus.FOUND

    assert Comment.objects.count() == 1


@pytest.mark.django_db
def test_user_cant_use_bad_words(
    author_client, bad_comment_form_data, news_detail_url
):
    response = author_client.post(news_detail_url, data=bad_comment_form_data)

    assertFormError(
        response, form='form', field='text', errors=WARNING,
    )

    assert response.status_code == HTTPStatus.OK

    assert Comment.objects.count() == 0
