from pydantic import BaseModel, HttpUrl


class URLShortenerRequest(BaseModel):
    original_url: HttpUrl


class URLShortenerResponse(BaseModel):
    short_code: str


class URLShortenerStatsResponse(BaseModel):
    original_url: HttpUrl
    short_code: str
    access_count: int
