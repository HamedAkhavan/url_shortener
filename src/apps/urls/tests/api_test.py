import pytest

from apps.urls.models import URLShortener


@pytest.fixture(scope="function")
def load_data(session):
    for i in range(10):
        URLShortener.objects.create(
            session,
            original_url=f"https://example.com/page_{i}",
            short_code=f"code_{i}",
            access_count=i * 10,
        )


def test_get_short_code(client, load_data):
    url = "/shorten"
    response = client.post(url, json={"original_url": "https://example.com/new_page"})

    assert response.status_code == 200
    assert "short_code" in response.json()


def test_redirect_to_original_url(client, load_data):
    short_code = "code_5"
    url = f"/{short_code}"
    response = client.get(url, follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "https://example.com/page_5"


def test_get_url_stats(client, load_data):
    short_code = "code_3"
    url = f"/stats/{short_code}"
    response = client.get(url)

    assert response.status_code == 200
    data = response.json()
    assert data["original_url"] == "https://example.com/page_3"
    assert data["short_code"] == short_code
    assert data["access_count"] == 30
