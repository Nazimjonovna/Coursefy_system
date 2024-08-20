from django.urls import path
from tests import views as test_views
from tests.filter import TestCollectFilter, LibraryFilter, FileFilter, TestCollectFilterAdmin


urlpatterns = [
    path('admin/test/', test_views.TestAdminList.as_view()),
    path('admin/test-by-category/', test_views.TestByCategoryAdmin.as_view()),
    path('admin/test/<int:pk>/', test_views.TestAdminDetail.as_view()),

    path('test-by-category/', test_views.TestByCategory.as_view()),
    path('test/', test_views.TestCollectList.as_view()),
    path('test/<int:pk>/', test_views.TestCollectDetail.as_view()),

    path('open-test/checker/', test_views.OpenTestChecker.as_view()),
    path('closed-test/checker/', test_views.ClosedTestChecker.as_view()),

    path('leader-boards/', test_views.LeadersBoard.as_view()),

    # filters
    path('search-testcollect/', TestCollectFilter.as_view()),
    path('admin/search-testcollect/', TestCollectFilterAdmin.as_view()),
    path('search-library/', LibraryFilter.as_view()),
    path('search-file/', FileFilter.as_view()),

    # library
    path('library/', test_views.LibraryList.as_view()),
    path('library/<int:pk>/', test_views.LibraryDetail.as_view()),

    path('files/', test_views.FileList.as_view()),
    path('files/create/', test_views.FileCreate.as_view()),
    path('files/<int:pk>/', test_views.FileDetail.as_view()),
]
