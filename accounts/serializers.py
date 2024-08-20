from accounts.models import Profile, Verification, HistoryOfEntries
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework import serializers
from course.models import Course


User = get_user_model()


class PhoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('phone_number',)


class ChangePhoneSerializer(serializers.ModelSerializer):
    parent_phone_number = serializers.CharField(required=False, write_only=True)
    class Meta:
        model = User
        fields = (
            'phone_number',
            'parent_phone_number'
        )
        extra_kwargs = {
            "phone_number": {'required': False}
        }
    
    def to_representation(self, instance):
        representation = super(ChangePhoneSerializer, self).to_representation(instance)
        if instance.profile:
            if instance.profile.parent_phone_number:
                representation['parent_phone_number'] = str(instance.profile.parent_phone_number)
        return representation



class VerifyCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Verification
        fields = ('phone_number', 'verify_code', 'step_change_phone')
        extra_kwargs = {
            'step_change_phone': {'read_only': True}
        }

    def update(self, instance, validated_data):
        verify_code = validated_data['verify_code']
        if instance.verify_code == verify_code:
            instance.is_verified = True
            if instance.step_reset == 'send':
                instance.step_reset = 'confirmed'
            if instance.step_change_phone:
                if instance.step_change_phone == 'send':
                    instance.step_change_phone = 'confirmed'
            instance.save()
            return instance
        else:
            raise serializers.ValidationError({'error': 'Phone number or verify code incorrect'})


class RegisterUserSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(required=True, write_only=True)
    first_name = serializers.CharField(required=True, write_only=True)
    last_name = serializers.CharField(required=True, write_only=True)
    birth_date = serializers.DateField(required=False, write_only=True)
    language =  serializers.ChoiceField(choices=Profile.LANG_EXT, required=True, write_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'phone_number',
            'password', 'password2',
            'first_name', 'last_name',
            'birth_date',
            'language',
        )
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def to_representation(self, instance):
        representation = super(RegisterUserSerializer, self).to_representation(instance)
        if instance.profile:
            representation['user_id'] = instance.id
            representation['first_name'] = instance.profile.first_name
            representation['last_name'] = instance.profile.last_name
            representation['language'] = instance.profile.language
        return representation

    def validate(self, attrs):
        phone_number = attrs.get('phone_number')
        password = attrs.get('password')
        password2 = attrs.pop('password2')
        if password != password2:
            raise serializers.ValidationError({'password and password2': "The two password fields didn't match."})
        if self.context:
            if self.context['request'].user.is_superuser:
                return super().validate(attrs)
        try:
            obj = Verification.objects.get(phone_number=phone_number)
            if not obj.is_verified:
                raise serializers.ValidationError({
                    'Phone_number': 'Phone number is not verified. Please confirm your phone number then you can register'})
        except Verification.DoesNotExist:
            raise serializers.ValidationError({
                'Phone_number': 'Phone number is not verified. Please confirm your phone number then you can register'})
        return super().validate(attrs)

    def create(self, validated_data):
        phone_number, password = validated_data['phone_number'], validated_data['password']
        first_name, last_name = validated_data['first_name'], validated_data['last_name']
        # language, birth_date = validated_data['language'], validated_data['birth_date'],
        language, birth_date = validated_data['language'], validated_data.get('birth_date'),
        user = User.objects._create_user(phone_number=phone_number, password=password)
        if self.context.get('is_teacher'):
            self.add_to_group(user, is_teacher=True)
        if self.context.get('is_pupil'):
            self.add_to_group(user, is_pupil=True)
        profile = Profile(user=user, first_name=first_name, last_name=last_name)
        profile.birth_date, profile.language = birth_date, language
        profile.save()
        return user


    def add_to_group(self, user, is_pupil=None, is_teacher=None):
        if is_teacher:
            gr_name, code_name, name = 'Teacher', 'can_add_course', 'Can Add Course'
        if is_pupil:
            gr_name, code_name, name = 'Pupil', 'can_see_course', 'Can See Course'
        gr, created = Group.objects.get_or_create(name=gr_name)
        content_type = ContentType.objects.get_for_model(Course)
        perm_course, created = Permission.objects.get_or_create(
                    codename=code_name,
                    name=name,
                    content_type=content_type, 
                    )
        gr.permissions.add(perm_course)
        user.user_permissions.add(perm_course)
        user.groups.add(gr)
        return None

class CourseTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ('id', 'title')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'phone_number',
        )


class LoginUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('phone_number', 'password')
        extra_kwargs = {'password': {'write_only': True}}


class ChangePasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    re_new_password = serializers.CharField(label='Confirm Password', required=True, write_only=True)

    class Meta:
        model = User
        fields = ['old_password', 'new_password', 're_new_password']

    def validate(self, attrs):
        if attrs['new_password'] != attrs['re_new_password']:
            raise serializers.ValidationError({'passwords': "The two password fields didn't match."})
        return super().validate(attrs)

    def update(self, instance, validated_data):
        if not instance.check_password(validated_data['old_password']):
            raise serializers.ValidationError({'old_password': 'wrong password'})
        instance.password = validated_data.get('password', instance.password)

        instance.set_password(validated_data['new_password'])
        instance.save()
        return instance


class ResetPasswordSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField()
    new_password = serializers.CharField()
    re_new_password = serializers.CharField()

    class Meta:
        model = User
        fields = ('phone_number', 'new_password', 're_new_password')

    def validate(self, attrs):
        if not attrs['new_password']:
            raise serializers.ValidationError({'new_password': 'This field is required.'})

        if not attrs['re_new_password']:
            raise serializers.ValidationError({'re_new_password': 'This field is required.'})

        if attrs['new_password'] != attrs['re_new_password']:
            raise serializers.ValidationError({'passwords': "The two password fields didn't match."})

        return attrs


class HistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoryOfEntries
        fields = (
            'ip', 'device',
            'address', 'entered',
        )


class ChatUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = (
            'first_name',
            'last_name',
            'picture',
        )


class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = (
            'first_name',
            'last_name',
            'middle_name',
            'parent_phone_number',
            'picture',
            'language',
        )


class RefreshTokenSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    default_error_messages = {
        'bad_token': 'Token is invalid or expired'
    }

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            self.fail('bad_token')
