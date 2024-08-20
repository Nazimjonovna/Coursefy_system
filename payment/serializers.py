from rest_framework import serializers
from payment.models import PaymentHistory


class PaycomOperationSerializer(serializers.Serializer):
    CHECK_PERFORM_TRANSACTION = 'CheckPerformTransaction'
    CREATE_TRANSACTION = 'CreateTransaction'
    PERFORM_TRANSACTION = 'PerformTransaction'
    CHECK_TRANSACTION = 'CheckTransaction'
    CANCEL_TRANSACTION = 'CancelTransaction'
    METHODS = (
        (CHECK_PERFORM_TRANSACTION, CHECK_PERFORM_TRANSACTION),
        (CREATE_TRANSACTION, CREATE_TRANSACTION),
        (PERFORM_TRANSACTION, PERFORM_TRANSACTION),
        (CHECK_TRANSACTION, CHECK_TRANSACTION),
        (CANCEL_TRANSACTION, CANCEL_TRANSACTION)
    )
    id = serializers.IntegerField()
    method = serializers.ChoiceField(choices=METHODS)
    params = serializers.JSONField()


class PaymentHistoryAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentHistory
        fields = (
            'id', 'amount', 'is_paid',
        )

    def to_representation(self, instance):
        representation = super(PaymentHistoryAdminSerializer, self).to_representation(instance)
        representation['pupil_id'] = instance.user.id
        type = ""
        if instance.test:
            if instance.test:
                type = 'test'
                representation['name'] = instance.test.title
        elif instance.course:
            if instance.course:
                type = 'course'
                representation['name'] = instance.course.title
        representation['type'] = type
        return representation


class PaymentHistoryPupilSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentHistory
        fields = (
            'id', 'amount', 'created_at'
        )

    def to_representation(self, instance):
        representation = super(PaymentHistoryPupilSerializer, self).to_representation(instance)
        if instance.course:
            representation['title'] = instance.course.title
        elif instance.test:
            representation['title'] = instance.test.title
        return representation


class PaymentCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentHistory
        fields = (
            'user',
            'course',
            'card_number',
            'exp_date',
        )
        extra_kwargs = {'course': {'required': True}}


class PaymentTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentHistory
        fields = (
            'user',
            'test',
            'card_number',
            'exp_date',
        )
        extra_kwargs = {'test': {'required': True}}
