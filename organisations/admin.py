from django.contrib import admin
from .models import Organisation

# Register your models here.
@admin.register(Organisation)
class OrganisationAdmin(admin.ModelAdmin):

    list_display = ('name', 'code', 'email', 'is_active', 'created_at', 'updated_at')

    list_filter = ('is_active',)

    search_fields = ('name', 'code', 'email')

    ordering = ('name',)