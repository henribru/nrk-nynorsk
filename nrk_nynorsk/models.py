from django.db import models


class Article(models.Model):
    title = models.TextField()
    description = models.TextField()
    publication_date = models.DateTimeField()
    url = models.TextField(unique=True)

    def __repr__(self) -> str:
        return f"<Article title={self.title!r}>"


class RSSFeed(models.Model):
    url = models.TextField(unique=True)
    last_checked = models.DateTimeField(null=True, default=None)

    class Meta:
        verbose_name = "RSS feed"

    def __repr__(self) -> str:
        return f"<RSSFeed url={self.url!r}>"
