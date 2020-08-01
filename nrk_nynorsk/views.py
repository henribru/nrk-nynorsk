import random

from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.shortcuts import redirect
from django.views.generic import ListView

from nrk_nynorsk.models import Article


class ArticleListView(ListView):
    model = Article
    paginate_by = 30
    ordering = ["-publication_date"]

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get("q")
        if query:
            vector = SearchVector("title", "description", config="norwegian")
            query = SearchQuery(query, config="norwegian", search_type="websearch")
            queryset = queryset.annotate(search=vector).filter(search=query)
        return queryset

    def get(self, request, *args, **kwargs):
        if "lucky" in request.GET:
            ids = self.get_queryset().values_list("id", flat=True)
            if not ids:
                return super().get(request, *args, **kwargs)
            random_id = random.choice(ids)
            return redirect(super().get_queryset().get(id=random_id).url)
        return super().get(request, *args, **kwargs)
