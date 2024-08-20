import math
from tests.models import  TestCollect, OpenTest, ClosedTest, TestFile, Library, Files, ResultTest
from rest_framework import serializers
import pandas as pd


class TestFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestFile
        fields = ('id', 'file',)


def excel_to_test(file, collect):
    series = pd.read_excel(file)
    for d in series.iterrows():
        data = d[1].to_dict()
        if len(data) > 2:
            test = OpenTest(test_collect=collect)
            test.question = data.pop('savollar')
            test.answer = data.pop('javoblar')
            test.variants = data
            test.save()
        elif len(data) == 2:
            test = ClosedTest(test_collect=collect)
            test.question = data.pop('savollar')
            test.answer = data.pop('javoblar')
            test.save()


class AddTestSerializer(serializers.ModelSerializer):
    files = TestFileSerializer(many=True, required=False, write_only=True)
    TEST_DAYS = [
                (1, 'Monday'), (2, 'Tuesday'),
                (3, 'Wednesday'), (4, 'Thursday'),
                (5, 'Friday'), (6, 'Saturday'),
                (7, 'Sunday')
                 ]
    test_days = serializers.MultipleChoiceField(choices=TEST_DAYS, required=True)
    deleted_files = serializers.ListField(
        child = serializers.IntegerField(), write_only=True, required=False
    )

    class Meta:
        model = TestCollect
        fields = (
            "id", "for_whom", "title", "category", "course", "module",
            "lesson", "test_type", "test_days", "amount_test", "score",
            "duration", "start_num_mid_level", "end_num_mid_level",
            "price", "discount", "discount_start_date",
            "discount_end_date", "is_send_phone", "to_whom",
            "language", "image", "files", "deleted_files",
        )
        extra_kwargs = {
            'test_days': {'required': True,}, 
            'category': {'required': True},
        }

    def to_representation(self, instance):
        representation = super(AddTestSerializer, self).to_representation(instance)
        representation['files'] = TestFileSerializer(instance.files.all(), many=True).data
        return representation

    def validate(self, attrs):
        if not self.instance:
            test_days = attrs.get('test_days', False)
            if not test_days:
                raise serializers.ValidationError({'test_days': 'This field is required!'})
        else:
            deleted_files = attrs.get('deleted_files', False)
            if deleted_files:
                for id in deleted_files:
                    file = self.instance.files.filter(id=id)
                    if not file.exists():
                        raise serializers.ValidationError({'deleted_files' : f"Invalid pk \"{id}\" object does not exist."})
        for_whom = attrs.get('for_whom', False)
        lesson = attrs.get('lesson', False)
        module = attrs.get('module', False)
        course = attrs.get('course', False)
        price = attrs.get('price', False)
        is_send_phone = attrs.get('is_send_phone', False)
        if for_whom:
            if for_whom == 'lesson':
                if not lesson:
                    raise serializers.ValidationError({'lesson': 'This field is required!'})
            elif for_whom == 'module':
                if not module:
                    raise serializers.ValidationError({'module': 'This field is required!'})
            elif for_whom == 'course':
                if not course:
                    raise serializers.ValidationError({'course': 'This field is required!'})
            elif for_whom == "paid":
                if not price:
                    raise serializers.ValidationError({'price': 'This field is required!'})

        if is_send_phone:
            if not attrs.get('to_whom', False):
                raise serializers.ValidationError({'to_whom': 'This field is required!'})
        return super().validate(attrs)

    def create(self, validated_data):
        if validated_data.get('test_days'):
            validated_data['test_days'] = "".join(str(i) for i in validated_data['test_days'])
        user = self.context['user']
        files = self.context['files']
        validated_data['author'] = user
        collect = super().create(validated_data)
        try:
            excel_files = files.pop('files', False)
            if excel_files:
                for file in excel_files:
                    TestFile.objects.create(collect=collect, file=file)
                    excel_to_test(file, collect)
            return collect
        except Exception as e:
            print(f"\n\n[ERROR] error in test create for admin in serializer: {e}\n\n")
            collect.delete()
            raise serializers.ValidationError({'files': 'files is not valid'})

    def update(self, instance, validated_data):
        if validated_data.get('test_days'):
            validated_data['test_days'] = "".join(str(i) for i in validated_data['test_days'])
        files = self.context.get('files', False)
        collect_files = instance.files.all()
        collect = super().update(instance, validated_data)
        deleted_files = validated_data.get('deleted_files', False)
        if deleted_files:
            d_files = instance.files.filter(id__in=deleted_files)
            if d_files:
                d_files.delete()
        try:
            excel_files = files.pop('files', False)
            if excel_files:
                for file in excel_files:
                    TestFile.objects.create(collect=collect, file=file)
                    excel_to_test(file, collect)
            return collect
        except Exception as e:
            print(f"\n\n[ERROR] error in test update for admin in serializer: {e}\n\n")
            raise serializers.ValidationError({'files': 'files is not valid'})


class TestCollectListAdminSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()

    def get_category(self, obj):
        if obj.category:
            return obj.category.name_uz

    class Meta:
        model = TestCollect
        fields = (
            'id', 'title',
            'category',
            'test_type',
        )

    def to_representation(self, instance):
        representation = super(TestCollectListAdminSerializer, self).to_representation(instance)
        representation['users_of_test'] = instance.buyers.count()
        return representation


class TestCollectListSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestCollect
        fields = (
            'id', 'category', 'test_type', 'created_at',
            'title', 'price', 'discount', 'duration', 'image',
            )

    def to_representation(self, instance):
        representation =  super(TestCollectListSerializer, self).to_representation(instance)
        try:
            author_profile = instance.author.profile
            print(f"profile : {author_profile}")
            if author_profile:
                representation['author'] = f"{author_profile.first_name} {author_profile.last_name}"
        except Exception as e:
            print(f"error : {e}")
        return representation


class OpenTestAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpenTest
        fields = (
            'id', 'answer'
        )


class OpenTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpenTest
        fields = (
            'id',
            'question',
            'variants',
        )


class ClosedTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClosedTest
        fields = (
            'id',
            'question',
        )


class TestCollectDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestCollect
        fields = (
            'id', 'title', 'duration',
        )
    
    def to_representation(self, instance):
        representation =  super(TestCollectDetailSerializer, self).to_representation(instance)
        representation['open_tests'] = OpenTestSerializer(instance.open_tests.all(), many=True).data
        representation['closed_tests'] = ClosedTestSerializer(instance.closed_tests.all(), many=True).data
        return representation


def test_checker(validated_data, is_closed=False):
    test_collect = validated_data['test_collect']
    if is_closed:
        closed_tests = test_collect.closed_tests.all()
        tests = validated_data['tests']
        corrects = 0
        for t in tests:
            test = ClosedTest.objects.get(id=t['test_id'])
            if test.answer == t['answer']:
                corrects += 1
        incorrects = len(closed_tests) - corrects
        total_score = test_collect.score * corrects
    
    else:
        collect_tests = test_collect.open_tests.all()
        tests = validated_data['tests']
        corrects = 0
        for t in tests:
            test = collect_tests.get(id=t['test_id'])
            correct = test.answer
            if t['answer'].lower() == correct.lower():
                corrects += 1
        incorrects = len(collect_tests) - corrects
        total_score = test_collect.score * corrects
    return {'test_collect': test_collect, 'correct': corrects, 'incorrect': incorrects, 'total_score': total_score}


def validatation(attrs):
    try:
        TestCollect.objects.get(id=attrs['test_collect'].id)
    except TestCollect.DoesNotExist:
        raise serializers.ValidationError({'test_collect': f"Invalid pk \"{attrs['test_collect'].id}\" object does not exist."})

    test_collect = attrs['test_collect']
    ids = [t.id for t in test_collect.open_tests.all()]
    tests = attrs['tests']
    for test in tests:
        test_id = test['test_id']
        if test_id not in ids:
            raise serializers.ValidationError({'test_id': f"Invalid pk \"{test_id}\" object does not exist."})


class OneTest(serializers.Serializer):
    test_id = serializers.IntegerField(required=True)
    answer = serializers.CharField(required=True)


class OpenTestCheckerSerializer(serializers.ModelSerializer):
    tests = OneTest(many=True, required=True, write_only=True)

    class Meta:
        model = OpenTest
        fields = ('test_collect', 'tests')

    def validate(self, attrs):
        validatation(attrs)
        return super().validate(attrs)

    def create(self, validated_data):
        try:
            res = test_checker(validated_data)
            return res
        except Exception as e:
            print(f"\n\n[ERROR] error in test checker serializer {e}\n\n")
            raise serializers.ValidationError({'error': 'Program error'})


class ClosedTestCheckerSerializer(serializers.ModelSerializer):
    tests = OneTest(many=True, required=True, write_only=True)
    
    class Meta:
        model = ClosedTest
        fields = ('test_collect', 'tests',)
    
    def validate(self, attrs):
        validatation(attrs)
        return super().validate(attrs)

    def create(self, validated_data):        
        try:
            res = test_checker(validated_data, is_closed=True)
            return res
        except Exception as e:
            print(f"\n\n[ERROR] error in test checker serializer {e}\n\n")
            raise serializers.ValidationError({'error': 'Program error'})


class ScoreTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResultTest
        fields = ('id',)

    def to_representation(self, instance):
        representation = super(ScoreTestSerializer, self).to_representation(instance)
        profile = instance.user.profile
        fio = f"{profile.last_name} {profile.first_name}"
        if profile.middle_name:
            fio += f" {profile.middle_name}"
        representation['fio'] = fio
        representation['subject'] = instance.subject
        representation['score'] = instance.score
        return representation


class LibrarySerializer(serializers.ModelSerializer):
    count = serializers.SerializerMethodField()
    class Meta:
        model = Library
        fields = ('id', 'name', 'count')

    def get_count(self, instance):
        return instance.library_files.all().count()
       


def convert_size(size_bytes):
        if size_bytes == 0:
            return "0B"
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return "%s %s" % (s, size_name[i])


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Files
        fields = (
            'id', 'author', 
            'title', 'file', 
            'library', 'size',
            'created_at',
        )
        extra_kwargs = {
            'author': {'read_only': True},
            'created_at': {'read_only': True},
        }

    def to_representation(self, instance):
        representation = super(FileSerializer, self).to_representation(instance)
        representation['size'] = convert_size(instance.file.size)
        return representation
    

    