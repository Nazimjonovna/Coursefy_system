from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from course.models import Course
from rating.models import Rating
from rating.serializers import RatingSerializer
from rest_framework import permissions, status, parsers


class RatingList(CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    parser_classes = [parsers.MultiPartParser]
    my_tags = ['rating']

    def post(self, request):
        course, user = request.data['course'], request.user
        rate_objs = self.queryset.filter(user=user, course=course)

        if rate_objs.exists():
            return Response({'msg': 'The user has already rated this course'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            course = Course.objects.get(id=course)
            request.data._mutable = True
            request.data['course'] = course.id
            request.data['user'] = user.id
            rating = request.data
            
            serializer = RatingSerializer(data=rating)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            else:
                return Response(serializer.errors)
        
        except Course.DoesNotExist as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        
        
