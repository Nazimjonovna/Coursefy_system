from modeltranslation.translator import register, TranslationOptions
from course.models import MenuCategory, ScienceCategory, Courses, CourseVideo, News, ScoreOfStudent


@register(MenuCategory)
class MenuTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(ScienceCategory)
class ScienceTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(Courses)
class CoursesTranslationOptions(TranslationOptions):
    fields = ('title',)


@register(CourseVideo)
class CourseVideoTranslationOptions(TranslationOptions):
    fields = ('title',)


@register(News)
class RegionTranslationOptions(TranslationOptions):
    fields = ('title', 'text',)


@register(ScoreOfStudent)
class ScoreStudentTranslationOptions(TranslationOptions):
    fields = ('score',)
