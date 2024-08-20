from rest_framework import filters, permissions
from course.models import Course, PrimeMenu, SubCategory
from rest_framework.generics import ListAPIView
from course.serializers import AllCourseListSerializer, PrimeMenuSerializer, CategorySerializer, CourseListSerializer
from course.views import CustomPagination


class PrimeMenuFilter(ListAPIView):
    queryset = PrimeMenu.objects.all()
    serializer_class = PrimeMenuSerializer
    filter_backends = [filters.SearchFilter]
    pagination_class = CustomPagination
    search_fields = ['name_uz', 'name_ru', 'name_eng', 'name_qr']
    my_tags = ['search']


class SubCategoryFilter(ListAPIView):
    queryset = SubCategory.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter]
    pagination_class = CustomPagination
    search_fields = ['name_uz', 'name_ru', 'name_eng', 'name_qr']
    my_tags = ['search']


class CourseFilter(ListAPIView):
    queryset = Course.objects.all()
    serializer_class = AllCourseListSerializer
    filter_backends = [filters.SearchFilter]
    pagination_class = CustomPagination
    search_fields = ['title', 'author', 'about_course', 'about_teacher', 'outline']
    my_tags = ['search']


class CourseFilter(ListAPIView):
    queryset = Course.objects.all()
    serializer_class = AllCourseListSerializer
    filter_backends = [filters.SearchFilter]
    pagination_class = CustomPagination
    search_fields = ['title', 'author', 'about_course', 'about_teacher', 'outline']
    my_tags = ['search']


class CourseFilterAdmin(ListAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseListSerializer
    filter_backends = [filters.SearchFilter]
    pagination_class = CustomPagination
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['title', 'author', 'about_course', 'about_teacher', 'outline']
    my_tags = ['admin',]

    def get_queryset(self):
        try:
            return self.queryset.filter(user=self.request.user)
        except:
            pass
