from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import PrimeMenu, SubCategory, Course, \
    Lesson, Video, News, Language, UserNotification, \
    PupilOfCourse, CourseModule, LessonFiles, CategoryNews

admin.site.register(PrimeMenu)
admin.site.register(SubCategory)
admin.site.register(Course)

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'course', 'module', 'score')
    list_editable = ('title', 'course', 'module', 'score')

admin.site.register(Video)
admin.site.register(News)
admin.site.register(Language)
admin.site.register(UserNotification)
# admin.site.register(PupilOfCourse)
admin.site.register(CourseModule)
admin.site.register(LessonFiles)
admin.site.register(CategoryNews)


# @admin.register(Notification)
# class NotificationAdmin(admin.ModelAdmin):
#     list_display = ('id', 'draft', 'course', 'text')


# @admin.register(UserNotification)
# class UserNotificationAdmin(admin.ModelAdmin):
#     list_display = ('id', 'user', 'notification', 'is_read')
#     list_editable = ('notification', 'is_read')


@admin.register(PupilOfCourse)
class PupilOfCourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'pupil', 'course', 'is_paid', 'created_at')
    list_editable = ('is_paid',)


# @admin.register(Courses)
# class CoursesAdmin(admin.ModelAdmin):
#     list_display = ['id', 'title', 'img', 'video', 'price', 'discount', 'avg_rating']
#     list_editable = ['title', 'img', 'video', 'price', 'discount']


# @admin.register(LessonVideo)
# class LessonVideoAdmin(admin.ModelAdmin):
#     list_display = ('id', 'title', 'video', 'module')


# @admin.register(News)
# class NewsAdmin(admin.ModelAdmin):
#     list_display = ('id', 'title', 'text', 'img')
#     list_editable = ('title', 'text', 'img')
#     readonly_fields = ("get_image",)

#     def get_image(self, obj):
#         return mark_safe(f'<img src={obj.img.url} width="100" height="110"')


# admin.site.register(CourseModule)
# admin.site.register(LanguageChoice)
