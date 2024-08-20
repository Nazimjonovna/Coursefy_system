from rest_framework.parsers import MultiPartParser, FileUploadParser
from rest_framework import status, permissions, generics, pagination
from tests import models as test_models, views as test_views
from django.db.models.functions import ExtractWeekDay
from datetime import datetime as d, timedelta, date
from tests.models import BuyerOfTest, ResultTest
from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from django.db.models import Avg, Count, Sum
from payment import models as payment_models
from django.http.response import Http404
from rest_framework.views import APIView
from drf_yasg import openapi
from course.models import CategoryNews, Course, CourseModule, Lesson, PrimeMenu, PupilOfCourse,\
                             SubCategory, UserNotification, Video, LessonFiles, News
from course.serializers import AllCategorySerializer, BuyCourseSerializer, CategoryNewsSerializer, CategorySerializer, CourseModuleListSerializer, CourseSerializer,\
                CourseListSerializer, CourseModuleSerializer, LessonSerializer, LessonListSerializer, LessonVideoSerializer, \
                LessonFileSerializer, ModuleByCourseSerializer, NewsSerializer, NewsListSerializer, AllCourseListSerializer, \
                PrimeMenuSerializer, PupilCoursesListSerializer,\
                PupilModulesListSerializer, UploadAnswerSerializer, UserNotificationSerializer, \
                PupilLearnStatisticsSerializer, ContinueCourseFromStopped, \
                LessonVideoListSerializer, UsersListSerializer




User = get_user_model()


class CustomPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


def is_teacher(user):
    return user.groups.filter(name='Teacher').exists()

def is_assistant(user):
    return user.groups.filter(name='Assistant').exists()

def is_pupil(user):
    return user.groups.filter(name='Pupil').exists()


class CourseListAdmin(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPagination
    queryset = Course.objects.all()
    serializer_class = CourseListSerializer
    my_tags = ['admin']

    def get_queryset(self):
        try:
            courses = self.queryset.filter(user=self.request.user)
            return courses
        except:
            pass

    def post(self, request, *args, **kwargs):
        serializer = CourseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=self.request.user)
        # return super().post(request, *args, serializer.data) #<-- bunda course ni ikki marta yarataypti || manimcha perform create ni ishlatish uchun qilingan
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # def perform_create(self, serializer):
    #     serializer.save(user=self.request.user)


class CourseDetailAdmin(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    my_tags = ['admin']

    def get_queryset(self):
        try:
            return self.queryset.filter(user=self.request.user)
        except:
            pass


class CourseModuleListAdmin(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CourseModuleListSerializer
    pagination_class = CustomPagination
    queryset = CourseModule.objects.all()
    my_tags = ['admin']

    def get_queryset(self):
        try:
            return self.queryset.filter(course__user=self.request.user)
        except:
            pass

class CourseModuleDetailAdmin(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = CourseModule.objects.all()
    serializer_class = CourseModuleSerializer
    my_tags = ['admin']

    def get_queryset(self):
        try:
            return self.queryset.filter(course__user=self.request.user)
        except:
            pass


class ModuleByCourseAdmin(generics.ListAPIView):
    queryset = CourseModule.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ModuleByCourseSerializer
    my_tags = ['admin']

    def get(self, request, pk):
        modules = self.queryset.filter(course=pk)
        serializer = self.serializer_class(modules, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LessonsByModuleAdmin(generics.ListAPIView):
    queryset = Lesson.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LessonListSerializer
    my_tags = ['admin']

    def get(self, request, pk):
        lessons = self.queryset.filter(module=pk)
        serializer = self.serializer_class(lessons, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LessonListAdmin(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    pagination_class = CustomPagination
    parser_classes = (MultiPartParser, FileUploadParser)
    my_tags = ['admin']

    def get_queryset(self):
        try:
            return self.queryset.filter(course__user=self.request.user)
        except:
            pass

    def post(self, request):
        serializer = LessonSerializer(data=request.data, context={'user': request.user, 'files': request.FILES})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_parsers(self):
        if getattr(self, 'swagger_fake_view', False):
            return []
        return super().get_parsers()


class LessonDetailAdmin(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    parser_classes = (MultiPartParser, FileUploadParser)
    my_tags = ['admin']

    def put(self, request, pk):
        try:
            lesson = self.queryset.get(id=pk)
        except Lesson.DoesNotExist:
            raise Http404
        serializer = self.serializer_class(instance=lesson, data=request.data, context={'user': request.user, 'files': request.FILES})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    def patch(self, request, pk):
        return self.put(request, pk)

    def get_parsers(self):
        if getattr(self, 'swagger_fake_view', False):
            return []
        return super().get_parsers()


class VideoListAdmin(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Video.objects.all()
    pagination_class = CustomPagination
    serializer_class = LessonVideoSerializer
    my_tags = ['admin']


class VideoDetailAdmin(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Video.objects.all()
    serializer_class = LessonVideoSerializer
    my_tags = ['admin']

    def get_parsers(self):
        if getattr(self, 'swagger_fake_view', False):
            return []
        return super().get_parsers()


class LessonFileListAdmin(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPagination
    queryset = LessonFiles.objects.all()
    serializer_class = LessonFileSerializer
    my_tags = ['admin']


class LessonFileDetailAdmin(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = LessonFiles.objects.all()
    serializer_class = LessonFileSerializer
    my_tags = ['admin']

    def get_parsers(self):
        if getattr(self, 'swagger_fake_view', False):
            return []
        return super().get_parsers()


class CategoryNewsList(generics.ListAPIView):
    serializer_class = CategoryNewsSerializer
    permission_classes = [permissions.AllowAny]
    queryset = CategoryNews.objects.all()
    my_tags = ['admin']


class NewsListAdmin(generics.ListCreateAPIView):
    pagination_class = CustomPagination
    permission_classes = [permissions.IsAuthenticated]
    queryset = News.objects.filter(draft=False)
    serializer_class = NewsSerializer
    my_tags = ['admin']

    def get_queryset(self):
        try:
            # if self.request.user.is_superuser:
            #     return self.queryset.all()
            # else:
                # return self.queryset.filter(author=self.request.user)
            return self.queryset.filter(author=self.request.user)
        except:
            pass
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class DraftsNewsListAdmin(generics.ListAPIView):
    pagination_class = CustomPagination
    permission_classes = [permissions.IsAuthenticated]
    queryset = News.objects.filter(draft=True)
    serializer_class = NewsSerializer
    my_tags = ['admin']

    def get_queryset(self):
        try:
            # if self.request.user.is_superuser:
            #     return self.queryset.all()
            # else:
            #     return self.queryset.filter(author=self.request.user)
            return self.queryset.filter(author=self.request.user)
        except:
            pass


class NewsDetailAdmin(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    my_tags = ['admin']

    def get_queryset(self):
        user = self.request.user
        try:
            if user.is_superuser:
                return self.queryset.all()
            else:
                return self.queryset.filter(author=self.request.user)
        except:
            pass
    
    def get_parsers(self):
        if getattr(self, 'swagger_fake_view', False):
            return []
        return super().get_parsers()


class PrimeMenuViewAdmin(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = PrimeMenu.objects.all()
    serializer_class = PrimeMenuSerializer
    my_tags = ['admin']


class PrimeMenuDetailAdmin(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = PrimeMenu.objects.all()
    serializer_class = PrimeMenuSerializer
    my_tags = ['admin']

    def get_parsers(self):
        if getattr(self, 'swagger_fake_view', False):
            return []
        return super().get_parsers()


class SubCategoryViewAdmin(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = SubCategory.objects.all()
    serializer_class = CategorySerializer
    my_tags = ['admin']


class SubCategoryDetailAdmin(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = SubCategory.objects.all()
    serializer_class = CategorySerializer
    my_tags = ['admin']

    def get_parsers(self):
        if getattr(self, 'swagger_fake_view', False):
            return []
        return super().get_parsers()


class AllCategoryListAdmin(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = PrimeMenuSerializer
    queryset = PrimeMenu.objects.all()
    my_tags = ['admin']

    def get(self, request):
        prime_categories = PrimeMenu.objects.all()
        pr_serializer = PrimeMenuSerializer(prime_categories, many=True)
        sub_categories = SubCategory.objects.all()
        sub_serializer = CategorySerializer(sub_categories, many=True)
        categories = sub_serializer.data + pr_serializer.data
        return Response(categories, status=status.HTTP_200_OK)


class TeacherListAdmin(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = User.objects.all()
    pagination_class = CustomPagination
    serializer_class = UsersListSerializer
    my_tags = ['admin']

    def get_queryset(self):
        return User.objects.filter(groups__name='Teacher')


class PupilListAdmin(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()
    pagination_class = CustomPagination
    serializer_class = UsersListSerializer
    my_tags = ['admin']

    def get(self, request, *args, **kwargs):
        user = request.user
        if not user.is_superuser or not is_teacher(user):
            return Response({'error': "You aren't teacher"})
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        try:
            user = self.request.user
            if user.is_superuser:
                pupils = User.objects.filter(groups__name='Pupil')
                return pupils
            elif is_teacher(user):
                courses = self.request.user.courses.values('id')
                pupils = User.objects.filter(pupil_courses__course__in=courses)
                return pupils
        except:
            pass


class DashboardStatusAdmin(APIView):
    permission_classes = [permissions.IsAdminUser]
    my_tags = ['admin']

    def get(self, request):
        total_pupils = User.objects.filter(groups__name='Pupil').count()
        total_views = ResultTest.objects.filter(lesson__isnull=False, is_first=True).count()
        total_sold_courses = PupilOfCourse.objects.filter(is_paid=True).count()
        total_sold_tests = BuyerOfTest.objects.filter(is_paid=True).count()
        return Response({
                            'total_pupils': total_pupils,
                            'total_views': total_views,
                            'total_sold_course': total_sold_courses,
                            'total_sold_tests': total_sold_tests
                        })


def num2name(object_list):
    WEEK_DAYS = {
        1: 'Sunday', 2: 'Monday', 3: 'Tuesday',
        4: 'Wednesday', 5: 'Thursday',
        6: 'Friday', 7: 'Saturday',
    }
    results = {
        'Sunday': 0,
        'Monday': 0,
        'Tuesday': 0,
        'Wednesday': 0,
        'Thursday': 0,
        'Friday': 0,
        'Saturday': 0,
    }
    for s in object_list:
        results[WEEK_DAYS[s['weekday']]] = s['count']
    return results
 
mode_id = openapi.Parameter('mode_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER)

class GraphDashboarStatusAdmin(APIView):
    """
    ### You can filter statistics through the following "**mode**"s, enter any number in the following "**mode**"s in the "input" section.
    ___
    ### Quyidagi "**mode**"lar orqali statistikalarni filter qilish mumkin, "input" qismiga yuqoridagi "**mode**"lar bo'yicha son kiriting.
    ___
    ## **mode:**
    ### **1** : pupils graphic statistics
    ### **2** : views graphic statistics
    ### **3** : solded courses graphic statistics
    ### **4** : solded tests graphic statistics
    ___
    """
    permission_classes = [permissions.IsAdminUser]
    my_tags = ['admin']

    @swagger_auto_schema(manual_parameters=[mode_id], responses={200: 'OK', 400: 'Bad Request'})
    def get(self, request):
        today = date.today()
        startday = today - timedelta(days=6)

        mode_id = int(request.GET.get('mode_id', False))
        if mode_id:
            if mode_id == 1:
                pupils = PupilOfCourse.objects.filter(is_first=True)
                week_pupils = pupils.filter(created_at__date__range=[startday, today])
                pupils_stats = week_pupils.annotate(weekday=ExtractWeekDay('created_at')).values('weekday').annotate(count=Count('id')).values('weekday', 'count')
                pupils_stats = num2name(pupils_stats)
                return Response(pupils_stats, status=status.HTTP_200_OK)
            
            if mode_id == 2:            
                test_results = test_models.ResultTest.objects.filter(lesson__isnull=True, is_first=True)
                week_results = test_results.filter(created_at__date__range=[startday, today])
                views_stats = week_results.annotate(weekday=ExtractWeekDay('created_at')).values('weekday').annotate(count=Count('id')).values('weekday', 'count')
                views_stats = num2name(views_stats)
                return Response(views_stats, status=status.HTTP_200_OK)

            elif mode_id == 3:
                solded_courses = payment_models.PaymentHistory.objects.filter(course__isnull=False)
                week_solded = solded_courses.filter(created_at__date__range=[startday, today])
                courses_stats = week_solded.annotate(weekday=ExtractWeekDay('created_at')).values('weekday').annotate(count=Count('id')).values('weekday', 'count')
                courses_stats = num2name(courses_stats)
                return Response(courses_stats, status=status.HTTP_200_OK)

            elif mode_id == 4:
                solded_tests = payment_models.PaymentHistory.objects.filter(test__isnull=False)
                week_solded = solded_tests.filter(created_at__date__range=[startday, today])
                tests_stats = week_solded.annotate(weekday=ExtractWeekDay('created_at')).values('weekday').annotate(count=Count('id')).values('weekday', 'count')
                tests_stats = num2name(tests_stats)
                return Response(tests_stats, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'incorrect "mode_id" entered!'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': '"mode_id" is required!'}, status=status.HTTP_400_BAD_REQUEST)


class CourseListView(generics.ListAPIView):
    queryset = Course.objects.all()
    serializer_class = AllCourseListSerializer
    pagination_class = CustomPagination
    permission_classes = [permissions.AllowAny]
    my_tags = ['landing-page']


class CourseDetailView(generics.RetrieveAPIView):
    queryset = Course.objects.all()
    serializer_class = AllCourseListSerializer
    permission_classes = [permissions.AllowAny]
    my_tags = ['landing-page']


class CourseListByRating(generics.ListAPIView):
    queryset = Course.objects.all()
    pagination_class = CustomPagination
    serializer_class = AllCourseListSerializer
    permission_classes = [permissions.AllowAny]
    my_tags = ['landing-page']

    def get_queryset(self):
        return self.queryset.annotate(avg_rate=Avg('ratings__rate')).order_by('-avg_rate')


class NewsListView(generics.ListAPIView):
    queryset = News.objects.filter(draft=False, for_out_of_site=True)
    serializer_class = NewsListSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = CustomPagination
    my_tags = ['landing-page']


class NewsDetailView(generics.RetrieveAPIView):
    queryset = News.objects.filter(draft=False, for_out_of_site=True)
    serializer_class = NewsListSerializer
    permission_classes = [permissions.AllowAny]
    my_tags = ['landing-page']

    def get_parsers(self):
        if getattr(self, 'swagger_fake_view', False):
            return []
        return super().get_parsers()


class AllCategoryList(generics.ListAPIView):
    serializer_class = AllCategorySerializer
    permission_classes = [permissions.AllowAny]
    queryset = PrimeMenu.objects.all()
    my_tags = ['landing-page']


class PrimeMenuList(generics.ListAPIView):
    queryset = PrimeMenu.objects.all()
    serializer_class = PrimeMenuSerializer
    permission_classes = [permissions.AllowAny]
    my_tags = ['landing-page']


class SubCategoryList(generics.ListAPIView):
    queryset = SubCategory.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    my_tags = ['landing-page']


menu_id = openapi.Parameter('menu_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER)

class CategoryByMenu(generics.ListAPIView):
    queryset = SubCategory.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    my_tags = ['landing-page']

    @swagger_auto_schema(manual_parameters=[menu_id])
    def get(self, request):
        menu_id = request.GET.get('menu_id', False)
        if menu_id:
            categories = self.queryset.filter(menu=menu_id)
            serializer = self.serializer_class(categories, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'error': '"menu_id" is required!'}, status=status.HTTP_400_BAD_REQUEST)


category_id = openapi.Parameter('category_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER)

class CourseByCategory(generics.ListAPIView):
    queryset = Course.objects.all()
    pagination_class = CustomPagination
    serializer_class = AllCourseListSerializer
    permission_classes = [permissions.AllowAny]
    my_tags = ['landing-page']

    @swagger_auto_schema(manual_parameters=[category_id])
    def get(self, request, *args, **kwargs):
        category_id = self.request.GET.get('category_id', False)
        if not category_id:
            return Response({'error': '"category_id" is required!'}, status=status.HTTP_400_BAD_REQUEST)
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        category_id = self.request.GET.get('category_id', False)
        if category_id:
            return self.queryset.filter(category=category_id)


class CourseByCategoryAdmin(generics.ListAPIView):
    queryset = Course.objects.all()
    pagination_class = CustomPagination
    serializer_class = CourseListSerializer
    permission_classes = [permissions.IsAuthenticated]
    my_tags = ['admin']

    @swagger_auto_schema(manual_parameters=[category_id])
    def get(self, request, *args, **kwargs):
        category_id = self.request.GET.get('category_id', False)
        if not category_id:
            return Response({'error': '"category_id" is required!'}, status=status.HTTP_400_BAD_REQUEST)
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        category_id = self.request.GET.get('category_id', False)
        if category_id:
            try:
                return self.queryset.filter(category=category_id, user=self.request.user)
            except:
                pass


class PupilCoursesList(generics.ListAPIView):
    queryset = Course.objects.all()
    serializer_class = PupilCoursesListSerializer
    pagination_class = CustomPagination
    permission_classes = [permissions.IsAuthenticated]
    my_tags = ['user']

    def get_queryset(self):
        try:
            user = self.request.user
            return self.queryset.filter(course_pupils__pupil=user)
        except:
            pass

    def get_serializer_context(self):
        return {'user': self.request.user}

class StoppedLessons(generics.ListAPIView):
    queryset = Course.objects.all()
    serializer_class = ContinueCourseFromStopped
    permission_classes = [permissions.IsAuthenticated]
    my_tags = ['user']

    def get(self, request, *args, **kwargs):
        user = request.user
        print(user)
        pupil_courses = user.pupil_courses.all()
        courses = self.queryset.filter(id__in=pupil_courses.values('course'))
        serializer = self.serializer_class(courses, many=True, context=request)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PupilLearnStatistics(generics.ListAPIView):
    queryset = Course.objects.all()
    serializer_class = PupilLearnStatisticsSerializer
    permission_classes = [permissions.IsAuthenticated]
    my_tags = ['user']

    def get(self, request):
        user = request.user
        courses = self.queryset.filter(id__in=user.pupil_courses.all())
        serializer = self.serializer_class(courses, many=True, context=request)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ModulesByCourse(generics.RetrieveAPIView):
    serializer_class = PupilModulesListSerializer
    queryset = CourseModule.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    my_tags = ['user']

    @swagger_auto_schema(tags=['user'])
    def get(self, request, pk):
        courses = Course.objects.filter(id=pk)
        if courses.exists():
            course = courses.first()
        pupils = course.course_pupils.filter(pupil=request.user)
        if not pupils.exists():
            raise Http404
        modules = course.modules.all()
        serializer = self.serializer_class(modules, many=True, context={'user': request.user})
        return Response(serializer.data, status=status.HTTP_200_OK)


course_id = openapi.Parameter('course_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER)

class LessonsByModule(generics.RetrieveAPIView):
    serializer_class = LessonVideoListSerializer
    queryset = Lesson.objects.all()
    pagination_class = CustomPagination
    permission_classes = [permissions.IsAuthenticated]
    my_tags = ['user']

    def get(self, request, pk):
        try:
            module = CourseModule.objects.get(id=pk)
        except CourseModule.DoesNotExist:
            raise Http404
        pupils = module.course.course_pupils.filter(pupil=request.user)
        if not pupils.exists():
            raise Http404
        lessons = module.lessons.all()
        serializer = self.serializer_class(lessons, many=True, context=request)
        return Response(serializer.data, status=status.HTTP_200_OK)



class PupilAnswerLessonView(generics.CreateAPIView):
    serializer_class =  UploadAnswerSerializer
    permission_classes = [permissions.IsAuthenticated]
    parsers_classes = [MultiPartParser, FileUploadParser]
    my_tags = ['user']


    def post(self, request, *args, **kwargs):
        serializer = UploadAnswerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['mode'] = 'answer'
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(str(serializer.errors), status=status.HTTP_400_BAD_REQUEST)


class PupilLessonDetail(generics.RetrieveAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]
    my_tags = ['user']

    def get(self, request, pk):
        try:
            lesson = Lesson.objects.get(id=pk)
        except Lesson.DoesNotExist:
            print(f"[ERROR] Lesson does not exist")
            raise Http404
        try:
            lessons = lesson.course.lessons.all()
            pr_lesson = lessons.filter(pk__lt=lesson.id).order_by('-id').first()
            if pr_lesson:
                results = pr_lesson.result_lesson.filter(user=request.user).annotate(total_score=Sum('score')).values('total_score')
                if not results:
                    return Response({'error': 'lesson is locked, because the score of the previous lesson is not enough!'}, status=status.HTTP_200_OK)
                if results[0]['total_score'] >= lesson.score:
                    serializer = self.serializer_class(lesson)
                    return Response(serializer.data, status=status.HTTP_206_PARTIAL_CONTENT)
                else:
                    return Response({'error': 'lesson is locked, because the score of the previous lesson is not enough!'}, status=status.HTTP_200_OK)
            serializer = self.serializer_class(lesson)
            return Response(serializer.data, status=status.HTTP_206_PARTIAL_CONTENT)
        except Exception as e:
            print(f"\n[ERROR] pupil create : {e}\n")
            return Response({'error': 'internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


course_id = openapi.Parameter('course_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER)


class ModuleByCourse(generics.RetrieveAPIView):
    queryset = CourseModule.objects.all()
    serializer_class = PupilModulesListSerializer
    permission_classes = [permissions.IsAuthenticated]
    my_tags = ['user']

    def get(self, request, pk):
        perm = PupilOfCourse.objects.filter(pupil=request.user, course_id=pk)
        if perm.exists():
            try:
                course = Course.objects.get(id=pk)
            except Course.DoesNotExist:
                raise Http404
            modules = course.modules.all()
            serializer = self.serializer_class(modules, many=True)
            print(serializer.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            raise Http404


id = openapi.Parameter('id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER)

class CourseFilterView(generics.ListAPIView):
    """
    1 : "Yangilari bo'yicha"
    2 : "Reyting bo'yicha"
    3 : "Mashxurlari bo'yicha"
    """
    queryset = Course.objects.all()
    serializer_class = AllCourseListSerializer
    pagination_class = CustomPagination
    permission_classes = [permissions.AllowAny]
    my_tags = ['landing-page']

    @swagger_auto_schema(manual_parameters=[id])
    def get(self, request, *args, **kwargs):
        key = request.GET.get('id', False)
        if not key:
            return Response({'error': '"id" is required!'}, status=status.HTTP_400_BAD_REQUEST)
        if int(key) not in (1,2,3):
            return Response({'error': 'you can only enter the numbers 1, 2, 3'}, status=status.HTTP_400_BAD_REQUEST)
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        key = self.request.GET.get('id', False)
        key = int(key)
        if key == 1:
            return Course.objects.order_by('-created_at')
        elif key == 2:
            obj_list = Course.objects.annotate(rate=Avg('ratings__rate'))
            return obj_list.order_by('rate')
        elif key == 3:
            return Course.objects.annotate(total_solded=Count('course_pupils')).order_by('-total_solded')


class BuyCourseList(generics.ListCreateAPIView):
    serializer_class = BuyCourseSerializer
    queryset = PupilOfCourse.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(tags=['course'])
    def get(self, request, *args, **kwargs):
        user_courses = self.request.user.pupil_courses
        serializer = self.serializer_class(user_courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(tags=['course'])
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(instance=request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserNotificationList(generics.ListAPIView):
    serializer_class = UserNotificationSerializer
    queryset = UserNotification.objects.filter(is_read=False)
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(tags=['user'])
    def get(self, request):
        user_notifs = request.user.user_notifications.filter(is_read=False)
        serializer = self.serializer_class(user_notifs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserNotificationDetail(generics.RetrieveAPIView):
    serializer_class = UserNotificationSerializer
    queryset = UserNotification.objects.filter(is_read=False) 
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(tags=['user'])
    def get(self, request, pk):
        try:
            notif = request.user.user_notifications.filter(is_read=False).get(id=pk)
            serializer = self.serializer_class(notif)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UserNotification.DoesNotExist:
            raise Http404

    def get_parsers(self):
        if getattr(self, 'swagger_fake_view', False):
            return []
        return super().get_parsers()


class MarkingAsReadNotificationList(generics.ListAPIView):
    serializer_class = UserNotificationSerializer
    queryset = UserNotification.objects.filter(is_read=False)
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(tags=['user'])
    def get(self, request):
        notifications = UserNotification.objects.filter(user=request.user.id, is_read=False)
        if len(notifications) > 0:
            notifications.update(is_read=True)
            return Response({'message': 'All message successfully read!'}, status=status.HTTP_202_ACCEPTED)
        else:
            return Response({'message': 'All message has been already read!'}, status=status.HTTP_208_ALREADY_REPORTED)


class MarkingAsReadNotificationDetail(generics.RetrieveAPIView):
    serializer_class = UserNotificationSerializer
    queryset = UserNotification.objects.filter(is_read=False)
    permission_classes = [permissions.IsAuthenticated]
    my_tags = ['user']

    @swagger_auto_schema(tags=['user'])
    def get(self, request, pk):
        try:
            notif = UserNotification.objects.filter(user=self.request.user).get(id=pk)
            notif.is_read=True
            notif.save()
            return Response({'msg': 'This message successfully read!'}, status=status.HTTP_200_OK)
        except UserNotification.DoesNotExist:
            raise Http404

    def get_parsers(self):
        if getattr(self, 'swagger_fake_view', False):
            return []
        return super().get_parsers()
