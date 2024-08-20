from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from django.db.models import Sum, Avg
from rest_framework import serializers
from django.dispatch import receiver
from tests.models import ResultTest, TestCollect
from course.models import Course, CourseModule, Lesson, PrimeMenu, \
    SubCategory, Video, LessonFiles, News, PupilOfCourse, UserNotification, CategoryNews
from tinytag import TinyTag

from accounts.serializers import CourseTitleSerializer


User = get_user_model()


def is_teacher(user):
    return user.groups.filter(name='Teacher').exists()


def is_assistant(user):
    return user.groups.filter(name='Assistant').exists()


def is_pupil(user):
    return user.groups.filter(name='Pupil').exists()


class UsersListSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id',)

    def to_representation(self, instance):
        representation = super(UsersListSerializer,
                               self).to_representation(instance)
        profile = instance.profile
        if profile.birth_date:
            representation['birth_date'] = instance.profile.birth_date
        fio = ""
        if instance.profile.last_name:
            fio += instance.profile.last_name
        if instance.profile.first_name:
            fio += ' ' + instance.profile.first_name
        if instance.profile.middle_name:
            fio += ' ' + instance.profile.middle_name
        representation['fio'] = fio
        if is_teacher(instance):
            data = CourseTitleSerializer(
                instance.courses.all(), many=True).data
            representation['teacher_courses'] = data
        if is_pupil(instance):
            pupil_courses = Course.objects.filter(
                course_pupils__pupil=instance)
            data = CourseTitleSerializer(pupil_courses, many=True).data
            representation['pupil_courses'] = data
        return representation


class AllCourseListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = (
            'id', 'image', 'title',
            'author', 'price', 'discount',
            'about_course', 'about_teacher',
            'outline', 'free_video',
        )

    def to_representation(self, instance):
        representation = super(AllCourseListSerializer,
                               self).to_representation(instance)
        representation['avg_rating'] = instance.ratings.aggregate(Avg('rate'))[
            'rate__avg']
        representation['count_rating'] = instance.ratings.count()
        representation['count_pupil'] = instance.course_pupils.count()
        return representation


class CourseListSerializer(serializers.ModelSerializer):

    category = serializers.SerializerMethodField()

    def get_category(self, obj):
        if obj.category:
            return obj.category.name_uz

    class Meta:
        model = Course
        fields = ('id', 'title', 'category')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['modules/lessons'] = f"{instance.modules.count()}/{instance.lessons.count()}"
        representation['pupils'] = instance.course_pupils.count()
        return representation


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ('id', 'title', 'author', 'image',
                  'assistants', 'category', 'language')


class ModuleByCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseModule
        fields = ('id', 'name')


class CourseModuleListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseModule
        fields = ('id', 'name', 'course', 'duration', 'description',
                  'is_discount', 'discount', 'discount_start_date', 'discount_end_date')
        extra_kwargs = {
            'is_discount': {'required': False},
            'discount_end_date': {'required': False},
            'discount_start_date': {'required': False},
            'description': {'required': False},
            'discount': {'required': False}
        }

    def to_representation(self, instance):
        representation = super(CourseModuleListSerializer,
                               self).to_representation(instance)
        representation['lessons'] = str(instance.lessons.count())
        return representation


class CourseModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseModule
        exclude = ('created_at', 'updated_at')

    def validate(self, attrs):
        course = attrs.get('course', False)
        is_discount = attrs.get('is_discount', False)
        if is_discount:
            if not attrs.get('discount', False):
                raise serializers.ValidationError({'discount': f"""
                                    You have chosen the is_discount, now you have to write down the amount of the discount or set is_discount to false
                                    """})
        if course:
            if course.user != self.context['request'].user:
                raise serializers.ValidationError(
                    {'course': f"Invalid pk \"{course.id}\" object does not exist."})
        return super().validate(attrs)


class LessonListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Lesson
        fields = ('id', 'title')
    

class LessonVideoSerializer(serializers.ModelSerializer):
    duration = serializers.SerializerMethodField()
    class Meta:
        model = Video
        fields = (
            'id',
            'video',
            'duration'
        )
        # exclude = ('created_at', 'updated_at')

    def validate(self, attrs):
        lesson = attrs.get('lesson')
        if lesson.course.user != self.context['request'].user:
            raise serializers.ValidationError(
                {'lesson': f"Invalid pk \"{lesson.id}\". You cannot add a video to this lesson because this lesson is not relevant to you"})
        return super().validate(attrs)

    def get_duration(self, obj):
        tag = TinyTag.get(obj.video.url[1:len(obj.video.url)])
        seconds = int(str(tag.duration).split(".")[0])

        keys = [
            "hour",
            "minute"
        ]

        secs = {
            "hour":3600,
            "minute":60,
        }
        
        def calc(seconds, dict, keys):
            val = 0
            for i in keys:
                val = seconds // dict[i]
                seconds = seconds%dict[i]
                dict[i] = val
            dict["second"] = seconds

            return dict

        return calc(seconds, secs, keys)


class VideoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Video
        fields = (
            'id',
            'video',
        )
        extra_kwargs = {
            'video': {'required': True},
        }


class LessonFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonFiles
        fields = (
            'id',
            'lesson',
            'file',
            'mode',
            'text',
        )


class FileOfLessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonFiles
        fields = (
            'id',
            'file',
            'title',
            'text',
            'created_at',
            'updated_at'
        )


class LessonSerializer(serializers.ModelSerializer):
    videos = VideoSerializer(many=True, required=False)
    lectures = FileOfLessonSerializer(many=True, required=False)
    additionals = FileOfLessonSerializer(many=True, required=False)
    tasks = FileOfLessonSerializer(many=True, required=False)
    answer = FileOfLessonSerializer(many=True, required=False)
    text = LessonFileSerializer(required=False)
    deleted_files = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )
    deleted_videos = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )

    class Meta:
        model = Lesson
        fields = (
            'id', 'title', 'course', 'module', 'score',
            'videos', 'lectures', 'tasks', 'additionals', 'answer', 'text',
            'deleted_files', 'deleted_videos'
        )

    def to_representation(self, instance):
        representation = super(
            LessonSerializer, self).to_representation(instance)
        representation['lesson_videos'] = VideoSerializer(
            instance.lesson_videos.all(), many=True).data
        representation['lecture_files'] = FileOfLessonSerializer(
            instance.lesson_files.filter(mode='lecture'), many=True).data
        representation['task_files'] = FileOfLessonSerializer(
            instance.lesson_files.filter(mode='task'), many=True).data
        representation['additional_files'] = FileOfLessonSerializer(
            instance.lesson_files.filter(mode='additional'), many=True).data
        representation['answer_files'] = FileOfLessonSerializer(
            instance.lesson_files.filter(mode='answer'), many=True).data
        representation['test_ids'] = [{'id':i.id, 'title':i.title, 'created_at':i.created_at} for i in instance.test_collects.all()]
            
        return representation

    def validate(self, attrs):
        instance = self.instance
        course = attrs.get('course', False)
        module = attrs.get('module', False)
        if instance is None:
            files = self.context.get('files', False)
            if files:
                if not files.get('videos', False):
                    raise serializers.ValidationError(
                        {'videos': "This field is required"})
            else:
                raise serializers.ValidationError(
                    {'videos': "This field is required"})
        if instance:
            deleted_files = attrs.get('deleted_files', False)
            deleted_videos = attrs.get('deleted_videos', False)
            if deleted_files:
                for id in deleted_files:
                    file_or_video = instance.lesson_files.filter(id=id)
                    if not file_or_video.exists():
                        raise serializers.ValidationError(
                            {'deleted_files': f"Invalid pk \"{id}\" object does not exist."})
            if deleted_videos:
                for id in deleted_videos:
                    videos = instance.lesson_videos.filter(id=id)
                    if not videos.exists():
                        raise serializers.ValidationError(
                            {'deleted_videos': f"Invalid pk \"{id}\" object does not exist."})
        if course.user != self.context['user']:
            raise serializers.ValidationError(
                {'course': f"Invalid pk \"{course.id}\" object does not exist."})
        if module.course != course:
            raise serializers.ValidationError(
                {'module': f"Invalid pk \"{module.id}\". This module is not the selected course."})
        return super().validate(attrs)

    def create(self, validated_data):
        try:
            files = self.context['files']
            videos = files.pop('videos', False)
            lectures = files.pop('lectures', False)
            tasks = files.pop('tasks', False)
            additionals = files.pop('additionals', False)
            lesson = super().create(validated_data)
            lesson_videos = [Video(lesson=lesson, video=v) for v in videos]
            Video.objects.bulk_create(lesson_videos)
            if lectures:
                mode = 'lecture'
                lectures = [LessonFiles(
                    lesson=lesson, mode=mode, file=l) for l in lectures]
                LessonFiles.objects.bulk_create(lectures)
            if tasks:
                mode = 'task'
                tasks = [LessonFiles(lesson=lesson, mode=mode, file=t)
                         for t in tasks]
                LessonFiles.objects.bulk_create(tasks)
            if additionals:
                mode = 'additional'
                additionals = [LessonFiles(
                    lesson=lesson, mode=mode, file=a) for a in additionals]
                LessonFiles.objects.bulk_create(additionals)
            return lesson
        except Exception as e:
            print(f"\n[ERROR] error in lesson create {e}\n")
            return {'error': 'internal server error'}

    def update(self, instance, validated_data):
        try:
            super().update(instance, validated_data)
            deleted_files = validated_data.get('deleted_files', False)
            deleted_videos = validated_data.get('deleted_videos', False)
            print(deleted_videos)
            if deleted_files:
                files = instance.lesson_files.filter(id__in=deleted_files)
                if files:
                    files.delete()
            if deleted_videos:
                videos = instance.lesson_videos.filter(id__in=deleted_videos)
                if videos:
                    videos.delete()
            files = self.context.get('files', False)
            if files:
                videos = files.pop('videos', False)
                lectures = files.pop('lectures', False)
                tasks = files.pop('tasks', False)
                additionals = files.pop('additionals', False)
                lesson_videos = [Video(lesson=instance, video=v)
                                 for v in videos]
                Video.objects.bulk_create(lesson_videos)
                if lectures:
                    mode = 'lecture'
                    lectures = [LessonFiles(
                        lesson=instance, mode=mode, file=l) for l in lectures]
                    LessonFiles.objects.bulk_create(lectures)
                if tasks:
                    mode = 'task'
                    tasks = [LessonFiles(
                        lesson=instance, mode=mode, file=t) for t in tasks]
                    LessonFiles.objects.bulk_create(tasks)
                if additionals:
                    mode = 'additional'
                    additionals = [LessonFiles(
                        lesson=instance, mode=mode, file=a) for a in additionals]
                    LessonFiles.objects.bulk_create(additionals)
            return instance
        except Exception as e:
            print(f"\n[ERROR] error in lesson update {e}\n")
            return {'error': 'internal server error'}


@receiver(signal=post_save, sender=PupilOfCourse)
def attach_notification(sender, **kwargs):
    obj = kwargs['instance']
    news = obj.course.course_news.all()
    if len(news) > 0:
        notifs = [UserNotification(user=obj.pupil, news=n) for n in news]
        UserNotification.objects.bulk_create(notifs)


# Upload Ansewr for The Lesson
class UploadAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonFiles
        fields = ('id', 'lesson', 'file', 'mode')

class CategoryNewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryNews
        fields = ('id', 'name')


class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        exclude = ('author',)
        extra_kwargs = {
            'category': {'required': True}
        }

    def validate(self, attrs):
        for_course = attrs.get('for_course', False)
        course = attrs.get('course', False)
        if for_course:
            if not attrs.get('course', False):
                raise serializers.ValidationError(
                    {'course': 'This field is reuired, because "for_course" is selected'})
        if course:
            if not for_course:
                raise serializers.ValidationError(
                    {'for_course': 'This field is reuired, because "course" is not empty'})
        return super().validate(attrs)


class NewsListAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = (
            'id', 'title', 'draft',
            'created_at', 'updated_at',
        )


class NewsListSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = (
            'id', 'image',
            'title', 'text',
            'created_at',
        )


class PrimeMenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrimeMenu
        fields = (
            'id', 'name_uz', 'name_ru',
            'name_eng', 'name_qr',
        )


class CategorySerializer(serializers.ModelSerializer):
    count = serializers.SerializerMethodField()

    class Meta:
        model = SubCategory
        fields = (
            'id', 'menu', 'name_uz',
            'name_ru', 'name_eng', 'name_qr', 'count',
        )

    def get_count(self, obj):
        return TestCollect.objects.filter(category__id=obj.id, for_whom='paid').count()


class AllCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PrimeMenu
        fields = (
            'id', 'name_uz', 'name_ru',
            'name_eng', 'name_qr'
        )

    def to_representation(self, instance):
        representation = super(AllCategorySerializer,
                               self).to_representation(instance)
        if instance.subcategories:
            subcategories = CategorySerializer(
                instance.subcategories.all(), many=True)
            representation['subcategories'] = subcategories.data
        return representation


class OrderChoiceSerializer(serializers.Serializer):
    CHOICE = (
        (1, "Yangilari bo'yicha"),
        (2, "Reyting bo'yicha"),
        (3, "Mashxurlari bo'yicha"),
    )

    name = serializers.ChoiceField(choices=CHOICE)


class BuyCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = PupilOfCourse
        fields = ('course',)

    def create(self, instance, validated_data):
        course = validated_data.get('course')
        try:
            course = Course.objects.get(id=course)
            obj = PupilOfCourse(pupil=instance, course=course)
            obj.save()
        except Course.DoesNotExist:
            raise serializers.ValidationError(
                {'course': 'There is no such course'})
        return obj


class UserNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserNotification
        fields = (
            'id',
        )

    def to_representation(self, instance):
        representation = super(UserNotificationSerializer,
                               self).to_representation(instance)
        representation['title'] = instance.news.title
        representation['text'] = instance.news.text
        if instance.news.image:
            representation['image'] = instance.news.image.url
        representation['created_at'] = instance.news.created_at
        return representation


class ModuleListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseModule
        fields = (
            'id', 'name', 'course',
        )

    def to_representation(self, instance):
        representation = super(ModuleListSerializer,
                               self).to_representation(instance)
        representation['total_lesson'] = instance.lessons.count()
        return representation


class LessonVideoListSerializer(serializers.ModelSerializer):
    video = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = (
            'id', 'title', 'video'
        )

    def get_video(self, obj):
        videos = Video.objects.filter(lesson__id = obj.id)
        serializers = LessonVideoSerializer(videos, many = True)
        return serializers.data

    def to_representation(self, instance):
        representation = super(LessonVideoListSerializer,
                               self).to_representation(instance)
        results = ResultTest.objects.filter(
            lesson=instance, user=self.context.user)
        if results.count() > 0:
            representation['is_lock'] = False
        else:
            representation['is_lock'] = True
        return representation


class ResultLessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = (
            'id',
        )

    def to_representation(self, instance):
        representation = super(ResultLessonSerializer,
                               self).to_representation(instance)
        score = instance.result_lesson.filter(user=self.context.user).annotate(
            total_score=Sum('score')).values('total_score')
        lesson_number = Lesson.objects.filter(id__lte=instance.id).count()
        representation['lesson_number'] = lesson_number
        if score:
            representation['score'] = score[0]['total_score']
        return representation


class PupilLearnStatisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = (
            'id',
            'title',
        )

    def to_representation(self, instance):
        representation = super(
            PupilLearnStatisticsSerializer, self).to_representation(instance)
        lessons = Lesson.objects.filter(
            id__in=self.context.user.result_tests.values('lesson'), course=instance)
        representation['statistics'] = ResultLessonSerializer(
            lessons, many=True, context=self.context).data
        return representation


class PupilCoursesListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = (
            'id', 'author', 'image', 'title',
        )

    def to_representation(self, instance):
        representation = super(PupilCoursesListSerializer,
                               self).to_representation(instance)
        try:
            lessons = instance.lessons.all()
            results = self.context['user'].result_tests.filter(is_first=True)
            percent = results.count() * (lessons.count() / 100)
            representation['percent'] = round(percent)
            return representation
        except Exception as e:
            print(f"\n[ERROR] error in pupil courses serializer {e}\n")


class PupilModulesListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseModule
        fields = (
            'id',
        )

    def to_representation(self, instance):
        representation = super(PupilModulesListSerializer,
                               self).to_representation(instance)
        try:
            lessons = self.context['user'].result_tests.filter(
                is_first=True, lesson__course__id=instance.id)
            if lessons.exists():
                representation['lesson_id'] = lessons.last().id
            else:
                representation['lesson_id'] = instance.lessons.order_by(
                    '-created_at').last().id
            lessons = instance.lessons.all()
            results = self.context['user'].result_tests.filter(
                is_first=True, lesson__in=lessons)
            percent = results.count() * (lessons.count() / 100)
            representation['percent'] = round(percent)
            representation['duration'] = instance.duration
            if percent <= 0:
                representation['is_locked'] = True
            representation['is_locked'] = False
            representation['course_title'] = instance.course.title
            representation['total_lesson'] = instance.lessons.count()
            return representation
        except Exception as e:
            print(f"\n[ERROR] error in pupil modules serializer {e}\n")


class ContinueCourseFromStopped(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = (
            'id', 'title'
        )

    def to_representation(self, instance):
        lessons = self.context.user.result_tests.filter(
            is_first=True, lesson__course__id=instance.id)
        representation = super(ContinueCourseFromStopped,
                               self).to_representation(instance)
        representation['stopped_lesson'] = lessons.count()
        if lessons:
            representation['lesson_id'] = lessons.last().id
        else:
            if instance.lessons.count() > 0:
                representation['lesson_id'] = instance.lessons.first().id
            else:
                representation['lesson_id'] = "lessons are not available"
        return representation
