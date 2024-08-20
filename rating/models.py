from django.db import models
from course.models import BaseModel, Course
from django.utils.translation import gettext as _
from django.contrib.auth import get_user_model

User = get_user_model()


class Rating(BaseModel):
    STARS = (
        (1, 1), (2, 2),
        (3, 3), (4, 4),
        (5, 5),)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True)
    rate = models.SmallIntegerField(choices=STARS)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='ratings')
    feedback = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.id} {self.course} {self.rate}"

    class Meta:
        verbose_name = "rating"
        verbose_name_plural = "ratings"
