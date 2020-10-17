import logging
import time
from typing import Iterator, List, Tuple, cast

from typing_extensions import Literal

import pendulum

import requests
import lxml.etree
import lxml.html

from nrk_nynorsk.models import Article
from nrk_nynorsk.models import RSSFeed

logger = logging.getLogger(__name__)

feed_urls = [
    "https://www.nrk.no/toppsaker.rss",
    "https://www.nrk.no/nyheter/siste.rss",
    "https://www.nrk.no/norge/toppsaker.rss",
    "https://www.nrk.no/urix/toppsaker.rss",
    "https://www.nrk.no/sapmi/oddasat.rss",
    "https://www.nrk.no/sport/toppsaker.rss",
    "https://www.nrk.no/kultur/toppsaker.rss",
    "https://www.nrk.no/livsstil/toppsaker.rss",
    "https://www.nrk.no/viten/toppsaker.rss",
    "https://www.nrk.no/fordypning/toppsaker.rss",
    "https://www.nrk.no/dokumentar/toppsaker.rss",
    "https://www.nrk.no/ytring/toppsaker.rss",
    "https://www.nrk.no/innlandet/toppsaker.rss",
    "https://www.nrk.no/innlandet/siste.rss",
    "https://www.nrk.no/osloogviken/toppsaker.rss",
    "https://www.nrk.no/osloogviken/siste.rss",
    "https://www.nrk.no/mr/toppsaker.rss",
    "https://www.nrk.no/mr/siste.rss",
    "https://www.nrk.no/nordland/toppsaker.rss",
    "https://www.nrk.no/nordland/siste.rss",
    "https://www.nrk.no/rogaland/toppsaker.rss",
    "https://www.nrk.no/rogaland/siste.rss",
    "https://www.nrk.no/sorlandet/toppsaker.rss",
    "https://www.nrk.no/sorlandet/siste.rss",
    "https://www.nrk.no/tromsogfinnmark/toppsaker.rss",
    "https://www.nrk.no/tromsogfinnmark/siste.rss",
    "https://www.nrk.no/trondelag/toppsaker.rss",
    "https://www.nrk.no/trondelag/siste.rss",
    "https://www.nrk.no/vestfoldogtelemark/toppsaker.rss",
    "https://www.nrk.no/vestfold/siste.rss",
    "https://www.nrk.no/vestland/toppsaker.rss",
    "https://www.nrk.no/vestland/siste.rss",
    "https://www.nrk.no/17mai/toppsaker.rss",
    "https://www.nrk.no/finnmarkslopet/toppsaker.rss",
    "https://www.nrk.no/sport/fotball/toppsaker.rss",
    "https://www.nrk.no/klassequizen/toppsaker.rss",
    "https://www.nrk.no/kultur/litteratur/toppsaker.rss",
    "https://www.nrk.no/mat/aktuelt.rss",
    "https://www.nrk.no/mgp/toppsaker.rss",
]


def main() -> None:
    for feed_url in feed_urls:
        RSSFeed.objects.get_or_create(url=feed_url)

    with requests.Session() as session:
        session.headers.update({"User-Agent": "nrk_nynorsk_scraper"})
        for feed in RSSFeed.objects.iterator():
            check_feed(feed, session)


def check_feed(feed: RSSFeed, session: requests.Session) -> None:
    logger.debug("Checking feed %s (last checked %s)", feed.url, feed.last_checked)
    tree = get_tree(feed.url, "xml", session)
    last_checked = None
    for item in get_feed_items(tree):
        try:
            title, description, url, date = extract_item(item)
        except IndexError:
            logger.debug("Missing metadata")
            continue
        if feed.last_checked and date <= feed.last_checked:
            logger.debug("Reached already checked article")
            break
        if last_checked is None:
            last_checked = date
        time.sleep(1)
        logger.debug("Checking article %s", url)
        tree = get_tree(url, "html", session)
        if not is_full_article(tree):
            logger.debug("Not a full article")
            continue
        if not is_in_nynorsk(tree):
            logger.debug("Not in Nynorsk")
            continue
        _, created = Article.objects.update_or_create(
            url=url,
            defaults={
                "title": title,
                "description": description,
                "publication_date": date,
            },
        )
        if created:
            logger.debug("Created article")
        else:
            logger.debug("Updated article")
    if last_checked is not None:
        feed.last_checked = last_checked
        feed.save()
    logger.debug("Done checking feed")


def get_tree(
    url: str, type: Literal["xml", "html"], session: requests.Session
) -> lxml.etree._Element:
    response = session.get(url)
    response.raise_for_status()
    if type == "xml":
        return lxml.etree.fromstring(response.content)
    elif type == "html":
        return lxml.html.fromstring(response.content)
    raise ValueError("Invalid type")


def get_feed_items(tree: lxml.etree._Element) -> Iterator[lxml.etree._Element]:
    for item in cast(List[lxml.etree._Element], tree.xpath("/rss/channel/item")):
        yield item


def extract_item(item: lxml.etree._Element) -> Tuple[str, str, str, pendulum.Date]:
    title = cast(List[str], item.xpath("title/text()"))[0]
    description = cast(List[str], item.xpath("description/text()"))[0]
    url = cast(List[str], item.xpath("link/text()"))[0]
    date = cast(
        pendulum.Date,
        pendulum.parse(cast(List[str], item.xpath("pubDate/text()"))[0], strict=False),
    )
    return title, description, url, date


def is_full_article(tree: lxml.etree._Element) -> bool:
    return bool(
        tree.xpath("/html/head/meta[@property='og:type' and @content='article']")
        and tree.xpath(
            "//article[@role='main' and (contains(@class, 'article') or contains(@class, 'article-feature'))]"
        )
    )


def is_in_nynorsk(tree: lxml.etree._Element) -> bool:
    return tree.xpath("/html/@lang")[0] == "nn-NO"  # type: ignore[index]


if __name__ == "__main__":
    main()
