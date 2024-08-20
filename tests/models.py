from course.models import Language, Lesson, CourseModule, Course, SubCategory, BaseModel
from django.core.validators import FileExtensionValidator
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.db import models
from django.contrib.postgres.fields import DateTimeRangeField
import os


User = get_user_model()


TYPES = [
        ('open', 'open'), ('closed', 'closed')
        ]
FOR_WHOM = [
        ('lesson', 'lesson'), ('module', 'module'),
        ('course', 'course'), ('block', 'block'),
        ('paid', 'paid'),
        ]
TEST_DAYS = [
        ('Monday', 'Monday'), ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'), ('Thursday', 'Thursday'),
        ('Friday', 'Friday'), ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday')
        ]
TO_WHOM = [
        ('to_parent', 'to_parent'), ('to_self', 'to_self'),
        ]


class TestCollect(BaseModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author_tests')
    for_whom = models.CharField(max_length=15, choices=FOR_WHOM)
    title = models.CharField(max_length=300)
    category = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, related_name='test_collects')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True, related_name='test_collects')
    module = models.ForeignKey(CourseModule, on_delete=models.CASCADE, null=True, blank=True, related_name='test_collects')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, null=True, blank=True, related_name='test_collects')
    test_type = models.CharField(max_length=10, choices=TYPES)
    test_days = models.CharField(max_length=7)
    amount_test = models.PositiveIntegerField('testlar soni')
    score = models.FloatField('har bir test uchun ball')
    duration = models.DurationField()
    start_num_mid_level = models.PositiveIntegerField()
    end_num_mid_level = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    discount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    discount_start_date = models.DateTimeField(null=True, blank=True)
    discount_end_date = models.DateTimeField(null=True, blank=True)
    is_send_phone = models.BooleanField(default=False)
    to_whom = models.CharField(max_length=50, choices=TO_WHOM, null=True, blank=True)
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True)
    image = models.ImageField(default='test.jpg', upload_to='tests/images/')

    def __str__(self):
        return f"{self.id}"

    class Meta:
        ordering= ('id',)
        verbose_name = "Test collection"
        verbose_name_plural = "Test collections"


class TestFile(BaseModel):
    collect = models.ForeignKey(TestCollect, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='test/excel-files/', validators=[FileExtensionValidator(allowed_extensions=['xlsx'])])

    class Meta:
        ordering = ('id',)
        verbose_name = 'Test File'
        verbose_name_plural = 'Test Files'


class OpenTest(models.Model):
    test_collect = models.ForeignKey(TestCollect, on_delete=models.CASCADE, related_name='open_tests')
    question = models.CharField(max_length=700)
    variants = models.JSONField()
    answer = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.id} {self.question[:30]}"

    class Meta:
        verbose_name = "Open test"
        verbose_name_plural = "Open tests"


class ClosedTest(models.Model):
    test_collect = models.ForeignKey(TestCollect, on_delete=models.CASCADE, related_name='closed_tests')
    question = models.CharField(max_length=500)
    answer = models.CharField(max_length=500)

    def __str__(self):
        return f"{self.id} {self.question[:30]}"

    class Meta:
        verbose_name = "Closed test"
        verbose_name_plural = "Closed tests"


class BuyerOfTest(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.CASCADE)
    test_collect = models.ForeignKey(TestCollect, on_delete=models.CASCADE, related_name='buyers')
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"(BuyerOfTest ID {self.id})"

    class Meta:
        verbose_name = 'Buyer of test'
        verbose_name_plural = 'Buyers of tests'


class Library(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('id',)
        verbose_name = 'Library'
        verbose_name_plural = 'Libraries'


class Files(BaseModel):
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=200, null=True, blank=True)
    file = models.FileField(upload_to='library/files/')
    library = models.ForeignKey(Library, on_delete=models.SET_NULL, null=True, blank=True, related_name='library_files')
    size = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.id} {self.title}"

    class Meta:
        ordering = ('id',)
        verbose_name = 'File'
        verbose_name_plural = 'Files'


    def clean(self):
        self.size = self.file.size


# @receiver(post_save, sender=Files)
# def my_handler(sender, **kwargs):
#     try:
#         obj = kwargs["instance"]
#         file_size = round(os.stat(obj.file.path).st_size / (1024 * 1024), 2)
#         obj.size = file_size
#         obj.save()
#     except Exception as e:
#         print(f"[ERROR] error at signal <<<{e}>>>")


class ResultTest(BaseModel):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='result_tests')
    subject = models.CharField(max_length=200)
    test_collect = models.ForeignKey(TestCollect, on_delete=models.CASCADE, related_name='result_tests')
    score = models.FloatField()
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='result_lesson', null=True, blank=True)
    is_first = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.id} {self.user} {self.score}"

    class Meta:
        verbose_name = "Result test"
        verbose_name_plural = "Results tests"
