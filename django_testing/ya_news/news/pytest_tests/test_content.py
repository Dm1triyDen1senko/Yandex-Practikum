import pytest
from django.conf import settings


@pytest.mark.django_db
def test_news_count(client, bulk_news, news_home_url):
    response = client.get(news_home_url)

    object_list = response.context['object_list']

    assert len(object_list) == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, bulk_news, news_home_url, news):
    response = client.get(news_home_url)

    object_list = response.context['object_list']

    sorted_object_list = sorted(
        object_list, key=lambda news: news.date, reverse=True
    )

    assert list(object_list) == sorted_object_list


@pytest.mark.django_db
def test_comments_order(client, bulk_news, bulk_comments, news_detail_url):
    all_dates = [comment.created for comment in
                 client.get(news_detail_url).context['news'].comment_set.all()]
    assert all_dates == sorted(all_dates)


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, author_client, news_detail_url):
    response_from_anonymous = client.get(news_detail_url)

    response_from_authorized_user = author_client.get(news_detail_url)

    assert 'form' not in response_from_anonymous.context

    assert 'form' in response_from_authorized_user.context
