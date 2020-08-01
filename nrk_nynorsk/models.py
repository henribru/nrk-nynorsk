from django.db import models


class Article(models.Model):
    title = models.TextField()
    description = models.TextField()
    publication_date = models.DateField()
    url = models.TextField(unique=True)

    def __repr__(self):
        return f"<Article title={self.title}>"


class RSSFeed(models.Model):
    url = models.TextField(unique=True)
    last_checked = models.DateTimeField(null=True, default=None)

    def __repr__(self):
        return f"<RSSFeed url={self.url}>"
