from scrapy_djangoitem import DjangoItem

from nrk_nynorsk.models import Article


class ArticleItem(DjangoItem):
    django_model = Article
