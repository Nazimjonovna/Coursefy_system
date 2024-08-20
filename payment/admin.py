from django.contrib import admin
from payment.models import PaymentHistory, Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', '_id', 'request_id', 'amount', 'state', 'status')
    list_display_links = ('id',)
    list_filter = ('status',)
    search_fields = ['request_id', 'status', 'id', '_id']


admin.site.register(PaymentHistory)
