# awards/admin.py
from django.contrib import admin
from .models import Award, Nomination, AwardSuggestion


@admin.register(Award)
class AwardAdmin(admin.ModelAdmin):
    list_display = ("titulo", "activo", "allow_nominations")
    list_filter = ("activo", "allow_nominations")
    search_fields = ("titulo",)


@admin.register(Nomination)
class NominationAdmin(admin.ModelAdmin):
    list_display = (
        "award",
        "nominado",
        "nominado_por",
        "is_active",
        "created_at",
    )
    list_filter = ("award", "is_active")
    search_fields = ("hazana",)


@admin.register(AwardSuggestion)
class AwardSuggestionAdmin(admin.ModelAdmin):
    list_display = (
        "titulo",
        "created_by",
        "is_reviewed",
        "is_accepted",
        "created_at",
    )
    list_filter = ("is_reviewed", "is_accepted", "created_at")
    search_fields = ("titulo", "resumen", "descripcion")
    readonly_fields = ("created_by", "created_at")

    actions = [
        "aceptar_sugerencias",
        "rechazar_sugerencias",
    ]

    @admin.action(description="✅ Aceptar sugerencias seleccionadas")
    def aceptar_sugerencias(self, request, queryset):
        queryset.update(is_reviewed=True, is_accepted=True)

    @admin.action(description="❌ Rechazar sugerencias seleccionadas")
    def rechazar_sugerencias(self, request, queryset):
        queryset.update(is_reviewed=True, is_accepted=False)