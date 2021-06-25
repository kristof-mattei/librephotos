
from api.views.serializers_serpy import PigPhotoSerilizer, GroupedPhotosSerializer
from api.views.pagination import HugeResultsSetPagination
from rest_framework import viewsets
from django.db.models import Q
from rest_framework_extensions.cache.decorators import cache_response
from api.views.caching import CustomListKeyConstructor, CustomObjectKeyConstructor, CACHE_TTL
from api.models import Photo
from rest_framework.response import Response
from api.views.PhotosGroupedByDate import get_photos_ordered_by_date

class RecentlyAddedPhotoListViewSet(viewsets.ModelViewSet):
    serializer_class = PigPhotoSerilizer 
    pagination_class = HugeResultsSetPagination

    def get_queryset(self):
        latestDate = Photo.visible.filter(Q(owner=self.request.user)).only('added_on').order_by('-added_on').first().added_on
        queryset = Photo.visible.filter(Q(owner=self.request.user) & Q(added_on__year=latestDate.year, added_on__month=latestDate.month, added_on__day=latestDate.day)).only(
            'image_hash', 'exif_timestamp', 'favorited', 'public','added_on',
            'hidden').order_by('-added_on')
        return queryset

    @cache_response(CACHE_TTL, key_func=CustomListKeyConstructor())
    def list(self, *args, **kwargs):
        return super(RecentlyAddedPhotoListViewSet, self).list(*args, **kwargs)

class FavoritePhotoListViewset(viewsets.ModelViewSet):
    serializer_class = PigPhotoSerilizer
    pagination_class = HugeResultsSetPagination

    def get_queryset(self):
        return Photo.objects.filter(
            Q(favorited=True) & Q(hidden=False) & Q(owner=self.request.user)).only(
                'image_hash', 'exif_timestamp', 'favorited', 'public',
                'hidden').order_by('-exif_timestamp')

    @cache_response(CACHE_TTL, key_func=CustomObjectKeyConstructor())
    def retrieve(self, *args, **kwargs):
        return super(FavoritePhotoListViewset, self).retrieve(*args, **kwargs)

    def list(self, request):
        queryset = Photo.objects.filter(
            Q(favorited=True) & Q(hidden=False) & Q(owner=self.request.user)).only(
                'image_hash', 'exif_timestamp', 'favorited', 'public',
                'hidden').order_by('exif_timestamp')
        grouped_photos = get_photos_ordered_by_date(queryset)
        serializer = GroupedPhotosSerializer(grouped_photos, many=True)
        return Response({'results': serializer.data})

class HiddenPhotoListViewset(viewsets.ModelViewSet):
    serializer_class = PigPhotoSerilizer
    pagination_class = HugeResultsSetPagination

    def get_queryset(self):
        return Photo.objects.filter(
            Q(hidden=True) & Q(owner=self.request.user)).only(
                'image_hash', 'exif_timestamp', 'favorited', 'public',
                'hidden').order_by('exif_timestamp')

    @cache_response(CACHE_TTL, key_func=CustomObjectKeyConstructor())
    def retrieve(self, *args, **kwargs):
        return super(HiddenPhotoListViewset, self).retrieve(*args, **kwargs)

    @cache_response(CACHE_TTL, key_func=CustomListKeyConstructor())
    def list(self, request):
        queryset = Photo.objects.filter(
            Q(hidden=True) & Q(owner=self.request.user)).only(
                'image_hash', 'exif_timestamp', 'favorited', 'public',
                'hidden').order_by('exif_timestamp')
        grouped_photos = get_photos_ordered_by_date(queryset)
        serializer = GroupedPhotosSerializer(grouped_photos, many=True)
        return Response({'results': serializer.data})