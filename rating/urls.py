from django.urls import path
from rating.views import RatingList


urlpatterns = [
    path('rating/', RatingList.as_view(), name='Rating list'),
]
