from django.contrib import admin
# from django.utils.safestring import mark_safe
from tests.models import (
    TestCollect, TestFile, OpenTest, ClosedTest,
    Library, Files, ResultTest
)

admin.site.register(TestCollect)
admin.site.register(TestFile)
admin.site.register(OpenTest)
admin.site.register(ClosedTest)
admin.site.register(ResultTest)

# @admin.register(ResultTest)
# class ResultTest(admin.ModelAdmin):
#     list_display = ('id', 'user', 'test_collect', 'score', 'lesson', 'created', 'updated')


# @admin.register(TestCollect)
# class TestCollectAdmin(admin.ModelAdmin):
#     list_display = (
#         'id', 'author', 'subject',
#         'title', 'image', 
#         'course', 'lesson', 'module',
#         'for_whom', 'question_file',
#         'answer_file', 'price', 'discount',
#         'dis_start_date', 'dis_end_date',
#         'score', 'test_type',  'description', 
#         'updated', 'created',
#         )
#     list_editable = (
#         'author', 'subject',
#         'title', 'image', 
#         'course', 'lesson', 'module',
#         'for_whom', 'question_file',
#         'answer_file', 'price', 'discount',
#         'dis_start_date', 'dis_end_date',
#         'score', 'test_type',  'description',
#         )
#     search_fields = ('for_whom', 'title', 'description')
#     readonly_fields = ("get_image",)

#     def get_image(self, obj):
#         return mark_safe(f'<img src={obj.image.url} width="100" height="110"')


# @admin.register(OpenTest)
# class OpenTestAdmin(admin.ModelAdmin):
#     list_display = (
#         'id', 'test_collect',
#         'question',
#         )
#     list_editable = (
#         'test_collect',
#         'question',
#         )
#     search_fields = ('question',)


# @admin.register(TestVariant)
# class TestVariantAdmin(admin.ModelAdmin):
#     list_display = ('id', 'test', 'is_correct', 'answer')
#     list_editable = ('test', 'is_correct', 'answer')
 

# @admin.register(ClosedTest)
# class ClosedTestAdmin(admin.ModelAdmin):
#     list_display = (
#         'id', 'test_collect',
#         'question', 'answer',
#         )
#     list_editable = (
#         'test_collect',
#         'question',
#         'answer',
#         )
#     search_fields = ('question', 'answer')


admin.site.register(Library)


@admin.register(Files)
class FilesAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'library',
        'size', 
        'file',
        'created_at', 
        'updated_at',
    )
    read_only_fields = ('size',)
    search_fields = ('title',)
