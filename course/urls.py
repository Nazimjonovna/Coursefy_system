from django.urls import path
from course.filters import CourseFilter, CourseFilterAdmin, PrimeMenuFilter, SubCategoryFilter
from course import views as course_views

urlpatterns = [
    path('prime-menu/', course_views.PrimeMenuList.as_view()),
    path('category/', course_views.SubCategoryList.as_view()),
    path('category-by-menu/', course_views.CategoryByMenu.as_view()),

    path('course-by-category/', course_views.CourseByCategory.as_view()),
    path('course/', course_views.CourseListView.as_view()),
    path('course/<int:pk>/', course_views.CourseDetailView.as_view()),

    path('course-by-rating/', course_views.CourseListByRating.as_view()),
    path('course/filter/', course_views.CourseFilterView.as_view()),

    path('news/', course_views.NewsListView.as_view()),
    path('news/<int:pk>/', course_views.NewsDetailView.as_view()),

    # users
    path('user/courses/list/', course_views.PupilCoursesList.as_view()),
    
    path('user/modules-by-course/<int:pk>/', course_views.ModulesByCourse.as_view()),
    path('user/lessons-by-module/<int:pk>/', course_views.LessonsByModule.as_view()),
    path('user/lessons/<int:pk>/', course_views.PupilLessonDetail.as_view()),
    path('user/lessons/pupil/answer/', course_views.PupilAnswerLessonView.as_view()),
    
    path('user/learn-statistics/', course_views.PupilLearnStatistics.as_view()),
    path('user/stopped-lessons/', course_views.StoppedLessons.as_view()),
    
    path('coures/buy/', course_views.BuyCourseList.as_view()),

    # notifications
    path('user/notification/', course_views.UserNotificationList.as_view()),
    path('user/notification/<int:pk>/', course_views.UserNotificationDetail.as_view()),
    path('user/notification/mark-as-read/', course_views.MarkingAsReadNotificationList.as_view()),
    path('user/notification/mark-as-read/<int:pk>/', course_views.MarkingAsReadNotificationDetail.as_view()),

    # filters
    path('menu/search/', PrimeMenuFilter.as_view()),
    path('subcategory/search/', SubCategoryFilter.as_view()),
    path('course/search/', CourseFilter.as_view()),
    path('admin/course/search/', CourseFilterAdmin.as_view()),

    # admin
    path('admin/course/', course_views.CourseListAdmin.as_view()),
    path('admin/course/<int:pk>/', course_views.CourseDetailAdmin.as_view()),
    path('admin/course-by-category/', course_views.CourseByCategoryAdmin.as_view()),

    path('admin/module-by-course/<int:pk>/', course_views.ModuleByCourseAdmin.as_view()),
    path('admin/lesson-by-module/<int:pk>/', course_views.LessonsByModuleAdmin.as_view()),

    path('all-categories/', course_views.AllCategoryList.as_view()),
    path('admin/module/', course_views.CourseModuleListAdmin.as_view()),
    path('admin/module/<int:pk>/', course_views.CourseModuleDetailAdmin.as_view()),
    path('admin/lesson/', course_views.LessonListAdmin.as_view()),
    path('admin/lesson/<int:pk>/', course_views.LessonDetailAdmin.as_view()),
    path('admin/lesson/video/', course_views.VideoListAdmin.as_view()),
    path('admin/lesson/video/<int:pk>/', course_views.VideoDetailAdmin.as_view()),

    path('admin/lesson/files/', course_views.LessonFileListAdmin.as_view()),
    path('admin/lesson/files/<int:pk>/', course_views.LessonFileDetailAdmin.as_view()),

    path('admin/category-news/', course_views.CategoryNewsList.as_view()),
    path('admin/news/', course_views.NewsListAdmin.as_view()),
    path('admin/news/drafts/', course_views.DraftsNewsListAdmin.as_view()),
    path('admin/news/<int:pk>/', course_views.NewsDetailAdmin.as_view()),

    path('admin/all/categories/', course_views.AllCategoryListAdmin.as_view()),
    path('admin/prime-menu/', course_views.PrimeMenuViewAdmin.as_view()),
    path('admin/prime-menu/<int:pk>/', course_views.PrimeMenuDetailAdmin.as_view()),
    path('admin/category/', course_views.SubCategoryViewAdmin.as_view()),
    path('admin/category/<int:pk>/', course_views.SubCategoryDetailAdmin.as_view()),

    path('admin/teachers/', course_views.TeacherListAdmin.as_view()),
    path('admin/pupils/', course_views.PupilListAdmin.as_view()),
    path('admin/dashboard/status/', course_views.DashboardStatusAdmin.as_view()),
    path('admin/dashboard/graphics/', course_views.GraphDashboarStatusAdmin.as_view()),
]
