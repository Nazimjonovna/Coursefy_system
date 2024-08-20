from django.http import Http404
from rest_framework.generics import CreateAPIView, ListCreateAPIView, \
                    RetrieveUpdateDestroyAPIView, ListAPIView, RetrieveAPIView
from rest_framework.parsers import MultiPartParser, FileUploadParser, FormParser
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser, IsAuthenticatedOrReadOnly
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status, pagination
from django.db.models import Sum
from tests.custom_permissions import IsAllowLibrary, IsTeacher
from tests.models import ResultTest, TestCollect, Library, Files
from tests.serializers import OpenTestAnswerSerializer, OpenTestSerializer, TestCollectListAdminSerializer, TestCollectListSerializer, TestCollectDetailSerializer,\
                    ScoreTestSerializer, LibrarySerializer, FileSerializer,\
                    OpenTestCheckerSerializer, ClosedTestCheckerSerializer, AddTestSerializer
User = get_user_model()


class CustomPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class TestAdminList(ListCreateAPIView):
    serializer_class = TestCollectListAdminSerializer
    queryset = TestCollect.objects.all()
    permission_classes = [IsTeacher]
    pagination_class = CustomPagination
    parser_classes = (MultiPartParser, FileUploadParser, FormParser)
    my_tags = ['admin']

    def post(self, request):
        context = {'user': request.user,'files': request.FILES}
        serializer = AddTestSerializer(data=request.data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        try:
            user = self.request.user
            return self.queryset.filter(author=user)
        except:
            pass

    def get_parsers(self):
        if getattr(self, 'swagger_fake_view', False):
            return []
        return super().get_parsers()


class TestAdminDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = AddTestSerializer
    queryset = TestCollect.objects.all()
    permission_classes = [IsAuthenticated, IsTeacher]
    parser_classes = (MultiPartParser, FileUploadParser)
    my_tags = ['admin']

    def patch(self, request, pk):
        context = {'user': request.user, 'files': request.FILES}
        try:
            collect = self.queryset.get(id=pk)
        except TestCollect.DoesNotExist:
            raise Http404
        serializer = self.serializer_class(instance=collect, data=request.data, context=context, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    def put(self, request, pk):
        context = {'user': request.user, 'files': request.FILES}
        try:
            collect = self.queryset.get(id=pk)
        except TestCollect.DoesNotExist:
            raise Http404
        serializer = self.serializer_class(instance=collect, data=request.data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    def get_parsers(self):
        if getattr(self, 'swagger_fake_view', False):
            return []
        return super().get_parsers()


class TestCollectList(ListAPIView):
    serializer_class = TestCollectListSerializer
    queryset = TestCollect.objects.filter(for_whom='paid')
    pagination_class = CustomPagination
    permission_classes = [AllowAny]
    my_tags = ['landing-page']

    def get_parsers(self):
        if getattr(self, 'swagger_fake_view', False):
            return []
        return super().get_parsers()


category_id = openapi.Parameter('category_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER)

class TestByCategory(ListAPIView):
    serializer_class = TestCollectListSerializer
    queryset = TestCollect.objects.filter(for_whom='paid')
    permission_classes = [AllowAny]
    pagination_class = CustomPagination
    my_tags = ['landing-page']

    @swagger_auto_schema(manual_parameters=[category_id])
    def get(self, request, *args, **kwargs):
        category_id = request.GET.get('category_id', False)
        if not category_id:
            return Response({'error': '"category_id" is required!'}, status=status.HTTP_400_BAD_REQUEST)
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        category_id = self.request.GET.get('category_id', False)
        return self.queryset.filter(category=category_id)


class TestByCategoryAdmin(ListAPIView):
    serializer_class = TestCollectListAdminSerializer
    queryset = TestCollect.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    my_tags = ['admin']

    @swagger_auto_schema(manual_parameters=[category_id])
    def get(self, request, *args, **kwargs):
        category_id = request.GET.get('category_id', False)
        if not category_id:
            return Response({'error': '"category_id" is required!'}, status=status.HTTP_400_BAD_REQUEST)
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        try:
            user = self.request.user
            category_id = self.request.GET.get('category_id', False)
            return self.queryset.filter(category=category_id, author=user)
        except:
            pass


class TestCollectDetail(RetrieveAPIView):
    serializer_class = TestCollectDetailSerializer
    queryset = TestCollect.objects.filter(for_whom='paid')
    permission_classes = [IsAuthenticated]
    my_tags = ['test']

    def get_parsers(self):
        if getattr(self, 'swagger_fake_view', False):
            return []
        return super().get_parsers()


class OpenTestChecker(CreateAPIView):
    serializer_class = OpenTestCheckerSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=['test'], request_body=OpenTestCheckerSerializer)
    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            tests = request.data.get('tests', False)
            if serializer.is_valid():
                res = serializer.save()
                if res['test_collect'].lesson:
                    lesson = res['test_collect'].lesson
                    obj = ResultTest(user=request.user)
                    results = ResultTest.objects.filter(user=request.user, lesson=lesson)
                    if not results.exists():
                        obj.is_first = True
                    obj.test_collect = res['test_collect']
                    obj.lesson = lesson
                    obj.score = res['total_score']
                    obj.save()
                open_tests = OpenTestAnswerSerializer(res['test_collect'].open_tests.all(), many=True)
                return Response({'correct_answer': res['correct'],
                                'incorrect_answer': res['incorrect'],
                                'correct_answers' : open_tests.data,
                                # 'selected_answers': tests,
                                }, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"\n\n[ERROR] error in test checker {e}\n\n")
            return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ClosedTestChecker(CreateAPIView):
    serializer_class = ClosedTestCheckerSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=['test'], request_body=ClosedTestCheckerSerializer)
    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                res = serializer.save()
                obj = ResultTest(user=request.user)
                obj.test_collect = res['test_collect']
                if res['test_collect'].lesson:
                    obj.lesson = res['test_collect'].lesson
                obj.score = res['total_score']
                obj.save()
                return Response({
                                'correct_answer': res['correct'], 
                                'incorrect_answer': res['incorrect']
                                }, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"\n\n[ERROR] error in test checker {e}\n\n")
            return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LeadersBoard(ListAPIView):
    serializer_class = ScoreTestSerializer
    queryset = ResultTest.objects.filter(lesson__isnull=True)
    permission_classes = [AllowAny]
    pagination_class = CustomPagination
    my_tags = ['test']

    def get_queryset(self):
        return self.queryset.order_by('-score')


class LibraryList(ListAPIView):
    serializer_class = LibrarySerializer
    permission_classes = [AllowAny]
    queryset = Library.objects.all()
    pagination_class = CustomPagination
    my_tags = ["library"]


class LibraryDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = LibrarySerializer
    permission_classes = [IsAdminUser]
    queryset = Library.objects.all()
    my_tags = ["library"]


library_id = openapi.Parameter('library_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER)

class FileList(ListAPIView):
    serializer_class = FileSerializer
    permission_classes = [AllowAny]
    queryset = Files.objects.all()
    pagination_class = CustomPagination
    my_tags = ["library"]

    @swagger_auto_schema(manual_parameters=[library_id])
    def get(self, request, *args, **kwargs):
        category_id = request.GET.get('library_id', False)
        if not category_id:
            return Response({'library_id': 'is required!'}, status=status.HTTP_400_BAD_REQUEST)
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        library_id = self.request.GET.get('library_id', False)
        return self.queryset.filter(library=library_id)


class FileCreate(CreateAPIView):
    serializer_class = FileSerializer
    permission_classes = [IsAdminUser]
    queryset = Files.objects.all()
    my_tags = ['library']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class FileDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = FileSerializer
    permission_classes = [IsAdminUser]
    queryset = Files.objects.all()
    my_tags = ["library"]

    # def get_queryset(self):
    #     try:
    #         return self.queryset.filter(author=self.request.user)
    #     except:
    #         pass
