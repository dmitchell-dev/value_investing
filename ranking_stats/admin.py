from django.contrib import admin
from .models import RankingStats


class RankingStatsAdmin(admin.ModelAdmin):
    fields = ["company_name", "param_name", "value", "timestamp"]


admin.site.register(RankingStats, RankingStatsAdmin)
