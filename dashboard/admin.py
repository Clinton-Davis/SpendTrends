from django.contrib import admin
from dashboard.models import Account, Category, Transaction


class TransactionAdmin(admin.ModelAdmin):
    list_display = ("date", "category", "trans_type", "amount", "vendor")
    list_filter = ("date", "category", "trans_type", "amount", "vendor")


admin.site.register(Account)
admin.site.register(Category)
admin.site.register(Transaction, TransactionAdmin)
