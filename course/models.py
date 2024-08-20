from configparser import LegacyInterpolation
from django.core.validators import FileExtensionValidator
from django.db.models import Avg
from django.db.models.signals import post_save, pre_save
from django.contrib.auth import get_user_model
from ckeditor.fields import RichTextField
from django.dispatch import receiver
from django.db.models import Avg
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from django.contrib.auth.models import Group
from django.db.models import UniqueConstraint

User = get_user_model()


class BaseModel(models.Model):
    created_at = models.DateTimeField('Created date', auto_now_add=True)
    updated_at = models.DateTimeField('Updated date', auto_now=True)

    class Meta:
        abstract = True


class Language(models.Model):
    language = models.CharField(max_length=100)

    def __str__(self):
        return f"(Language ID : {self.id}) {self.language}"

    class Meta:
        verbose_name = 'Language'
        verbose_name_plural = 'Languages'


class PrimeMenu(models.Model):
    name_uz = models.CharField('Category name uz', max_length=100)
    name_ru = models.CharField('Category name ru', max_length=100)
    name_eng = models.CharField('Category name eng', max_length=100)
    name_qr = models.CharField('Category name qr', max_length=100)

    def __str__(self):
        return f"(Menu ID : {self.id}) {self.name_uz} {self.name_ru}"

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Menu category'
        verbose_name_plural = 'Menu categories'


class SubCategory(models.Model):
    menu = models.ForeignKey(
        PrimeMenu, on_delete=models.CASCADE, related_name='subcategories')
    name_uz = models.CharField(max_length=100)
    name_ru = models.CharField(max_length=100)
    name_eng = models.CharField(max_length=100)
    name_qr = models.CharField('Category name qr', max_length=100)

    def __str__(self):
        return f"(SubCategory ID : {self.id}) {self.name_uz} {self.name_ru}"

    class Meta:
        ordering = ['id']
        verbose_name = 'Subject Category'
        verbose_name_plural = 'Subject Categories'


class Course(BaseModel):
    title = models.CharField(max_length=100)
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='courses')
    author = models.CharField(max_length=300, null=True, blank=True)
    image = models.ImageField(
        upload_to="courses/images/", null=True, blank=True)
    free_video = models.FileField(upload_to='courses/lesson/videos/', null=True, blank=True,
                                  validators=[FileExtensionValidator(allowed_extensions=['MOV', 'avi', 'mp4', 'webm', 'mkv'])])
    assistants = models.ManyToManyField(User, blank=True)
    category = models.ForeignKey(
        SubCategory, on_delete=models.SET_NULL, null=True)
    price = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True)
    discount = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True)
    language = models.ForeignKey(
        Language, on_delete=models.SET_NULL, null=True, blank=True)
    about_course = RichTextField('About the course', null=True, blank=True)
    about_teacher = RichTextField('About teacher', null=True, blank=True)
    outline = RichTextField('Mundarija', null=True, blank=True)

    def __str__(self):
        return f"(Course ID : {self.id})"

    class Meta:
        ordering = ['-id']
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'

    @property
    def avg_rating(self):
        if self.ratings:
            return self.ratings.aggregate(Avg('rate'))['rate__avg']


class CourseModule(BaseModel):
    name = models.CharField(max_length=100)
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='modules')
    is_discount = models.BooleanField(default=False)
    discount = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True)
    duration = models.IntegerField('Davomiyligi')
    discount_start_date = models.DateTimeField(null=True, blank=True)
    discount_end_date = models.DateTimeField(null=True, blank=True)
    description = RichTextField()

    def __str__(self):
        return f"(Module ID : {self.id}) | Course_ID : {self.course.id}"

    class Meta:
        ordering = ['id']
        verbose_name = 'Module'
        verbose_name_plural = 'Modules'


class Lesson(BaseModel):
    title = models.CharField(max_length=255)
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='lessons')
    module = models.ForeignKey(
        CourseModule, on_delete=models.CASCADE, related_name='lessons')
    score = models.SmallIntegerField('Score')

    def __str__(self):
        return f"(Lesson ID : {self.id}) | Module_ID : {self.module.id}"

    class Meta:
        ordering = ['id']
        verbose_name = 'Lesson'
        verbose_name_plural = 'Lessons'


class Video(BaseModel):
    lesson = models.ForeignKey(
        Lesson, on_delete=models.CASCADE, related_name='lesson_videos')
    video = models.FileField(upload_to='courses/lesson/videos/', null=True,
                             validators=[FileExtensionValidator(allowed_extensions=['MOV', 'avi', 'mp4', 'webm', 'mkv'])])

    def __str__(self):
        return f"(Video ID : {self.id}) {self.video}"

    class Meta:
        ordering = ['-id']
        verbose_name = 'Video'
        verbose_name_plural = 'Videos'


def task_upload_path(instance, filename):
    return f"courses/lesson/{instance.mode}/{filename}"


class LessonFiles(BaseModel):
    MODES = (
        ('additional', 'additional'),
        ('lecture', 'lecture'),
        ('task', 'task'),
        ('answer', 'answer'),
    )
    lesson = models.ForeignKey(
        Lesson, on_delete=models.CASCADE, related_name='lesson_files')
    title = models.CharField(max_length=255, null=True, blank=True)
    file = models.FileField(upload_to=task_upload_path)
    mode = models.CharField(max_length=200, choices=MODES)
    text = RichTextField(blank=True, null=True)

    def __str__(self):
        return f"(File ID : {self.id}) {self.lesson} {self.mode}"

    class Meta:
        ordering = ['-id']
        verbose_name = 'Lesson File'
        verbose_name_plural = 'Lesson Files'

    # def save(self, *args, **kwargs):
    #     lesson_file = self.file
    #     self.text = lesson_file.read()
    #     return super(LessonFiles, self).save(*args, **kwargs)


class CategoryNews(BaseModel):
    name = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.id} {self.name}"


class PupilOfCourse(BaseModel):
    pupil = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='pupil_courses')
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='course_pupils')
    is_first = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=False)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['pupil', 'course'],
                             name='course_pupils_once')
        ]
        ordering = ['id']
        verbose_name = 'Pupil of course'
        verbose_name_plural = 'Pupils of course'

    def save(self, *args, **kwargs):
        pupil_group, created = Group.objects.get_or_create(name='Pupil')
        self.pupil.groups.add(pupil_group)
        return super(PupilOfCourse, self).save(*args, **kwargs)

    def __str__(self):
        return f"(Pupil ID : {self.id}) {self.pupil}"


class News(BaseModel):
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=150)
    category = models.ForeignKey(
        CategoryNews, on_delete=models.SET_NULL, null=True)
    for_the_system = models.BooleanField(default=False)
    for_out_of_site = models.BooleanField(default=False)
    for_course = models.BooleanField(default=False)
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='course_news', null=True, blank=True)
    text = RichTextField()
    image = models.ImageField(upload_to='news/images/', null=True, blank=True)
    draft = models.BooleanField(default=False)

    def __str__(self):
        return f"(News ID : {self.id}) {self.author}"

    class Meta:
        ordering = ['id']
        verbose_name = 'News'
        verbose_name_plural = 'News'


@receiver(signal=post_save, sender=News)
def attach_notification_to_user(sender, **kwargs):
    news = kwargs['instance']
    if news.course is not None:
        if not news.draft:
            pupils = news.course.course_pupils.all()
            if len(pupils) > 0:
                n_list = [UserNotification(
                    user=pupil.pupil, news=news) for pupil in pupils]
                UserNotification.objects.bulk_create(n_list)


class UserNotification(BaseModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='user_notifications')
    news = models.ForeignKey(
        News, on_delete=models.CASCADE, related_name='notifications')
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"(User_Notification ID : {self.id}) {self.is_read} {self.user}"

    class Meta:
        ordering = ['id']
        verbose_name = 'User Notification'
        verbose_name_plural = 'User Notifications'
