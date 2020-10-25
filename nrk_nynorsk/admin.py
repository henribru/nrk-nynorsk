from django.contrib import admin

from nrk_nynorsk.models import Article, RSSFeed


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin
                   ):
    list_display = ["title", "publication_date"]
    date_hierarchy = "publication_date"


@admin.register(RSSFeed)
class RSSFeedAdmin(admin.ModelAdmin):
    list_display = ["url",
                    "last_checked"]
    date_hierarchy = "last_checked"
