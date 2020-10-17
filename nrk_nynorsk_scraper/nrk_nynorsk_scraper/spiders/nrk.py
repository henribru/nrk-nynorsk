from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule, SitemapSpider

from nrk_nynorsk_scraper.items import ArticleItem


class NrkSpider(SitemapSpider, CrawlSpider):
    name = "nrk"
    allowed_domains = ["nrk.no"]
    start_urls = ["https://nrk.no"]
    rules = [Rule(LinkExtractor(), callback="parse_article")]
    sitemap_urls = ["https://www.nrk.no/robots.txt"]
    sitemap_rules = [("", "parse_sitemap_link")]

    def start_requests(self):
        yield from CrawlSpider.start_requests(self)
        yield from SitemapSpider.start_requests(self)

    def parse_sitemap_link(self, response):
        return self._parse_response(
            response, self.parse_article, cb_kwargs={}, follow=True
        )

    def parse_article(self, response):
        if (
            not response.xpath(
                "/html/head/meta[@property='og:type' and @content='article']"
            )
            or response.xpath("/html/@lang").extract_first() != "nn-NO"
            or not response.xpath(
                "//article[@role='main' and (contains(@class, 'article') or contains(@class, 'article-feature'))]"
            )
        ):
            return None
        publication_date = response.xpath(
            "//time[contains(@class, 'datePublished')]/@datetime"
        ).extract_first()
        if publication_date is None:
            publication_date = get_meta_tag(response, "name", "dc.date.issued")
        return ArticleItem(
            title=get_meta_tag(response, "property", "og:title"),
            description=get_meta_tag(response, "property", "og:description"),
            publication_date=publication_date,
            url=get_meta_tag(response, "property", "og:url"),
        )


def get_meta_tag(response, name_attribute, name):
    return response.xpath(
        f"/html/head/meta[@{name_attribute}='{name}']/@content"
    ).extract_first()
