from django.db import models
from django.contrib.auth import get_user_model
from course.models import Course
from tests.models import TestCollect
from payment.utils import CVV, HUMO_UZCARD

User = get_user_model()


class Transaction(models.Model):
    PROCESSING = 'processing'
    SUCCESS = 'success'
    FAILED = 'failed'
    CANCELED = 'canceled'
    STATUS = (
        (PROCESSING, 'processing'),
        (SUCCESS, 'success'),
        (FAILED, 'failed'),
        (CANCELED, 'canceled')
    )

    _id = models.CharField(max_length=255)
    request_id = models.IntegerField()
    order_key = models.CharField(max_length=255, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    state = models.IntegerField(blank=True, null=True)
    status = models.CharField(choices=STATUS, default='processing', max_length=55)
    perform_datetime = models.CharField(null=True, max_length=255)
    cancel_datetime = models.CharField(null=True, max_length=255)
    created_datetime = models.CharField(null=True, max_length=255)
    reason = models.IntegerField(null=True)

    def __str__(self):
        return f"{self.id}"


class PaymentHistory(models.Model):
    PAYMENT_TYPES = (
        ('Uzcard', 'Uzcard'),
        ('Humo', 'Humo'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    payment_type = models.CharField(max_length=10, choices=PAYMENT_TYPES, null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    test = models.ForeignKey(TestCollect, on_delete=models.CASCADE, null=True, blank=True)
    card_number = models.CharField(max_length=16, validators=[HUMO_UZCARD])
    exp_date = models.CharField(max_length=5)
    cvv = models.CharField(max_length=3, validators=[CVV], null=True, blank=True)
    amount = models.DecimalField(max_digits=100, decimal_places=2, null=True, blank=True)
    is_paid = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.course} - {self.is_paid}"


class PaymentOfTest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    test = models.ForeignKey(TestCollect, on_delete=models.CASCADE)
    card_number = models.IntegerField()
    exp_date = models.SmallIntegerField()
    is_paid = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.test} - {self.is_paid}"
