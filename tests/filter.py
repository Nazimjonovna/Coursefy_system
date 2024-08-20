from rest_framework import filters, permissions
from tests.models import TestCollect, Library, Files
from tests.serializers import TestCollectListAdminSerializer, LibrarySerializer, FileSerializer, TestCollectListSerializer
from rest_framework.generics import ListAPIView
from tests.views import CustomPagination


class TestCollectFilter(ListAPIView):
    queryset = TestCollect.objects.filter(for_whom='paid')
    serializer_class = TestCollectListSerializer
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['title']
    my_tags = ['search']


class TestCollectFilterAdmin(ListAPIView):
    queryset = TestCollect.objects.all()
    serializer_class = TestCollectListAdminSerializer
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter]
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['title']
    my_tags = ['search', 'admin']

    def get_queryset(self):
        try:
            user = self.request.user
            return self.queryset.filter(author=user)
        except:
            pass


class LibraryFilter(ListAPIView):
    queryset = Library.objects.all()
    serializer_class = LibrarySerializer
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    my_tags = ['search']


class FileFilter(ListAPIView):
    queryset = Files.objects.all()
    serializer_class = FileSerializer
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['title']
    my_tags = ['search']
