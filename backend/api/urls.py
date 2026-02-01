from django.urls import path, include
from . import views

urlpatterns = [
    path('packs/', views.PackListView.as_view(), name='pack-list'),
    path('packs/<str:pack_id>/', views.PackDetailView.as_view(), name='pack-detail'),
    path('packs/<str:pack_id>/assets/', views.PackAssetsView.as_view(), name='pack-assets'),
    path('assets/<path:asset_path>', views.AssetView.as_view(), name='asset'),
    path('users/', views.UserListView.as_view(), name='user-list'),
    path('users/<str:username>/maps/', views.UserMapsView.as_view(), name='user-maps'),
    path('users/<str:username>/maps/<str:map_id>/', views.MapDetailView.as_view(), name='map-detail'),
    path('maps/public/', views.PublicMapsView.as_view(), name='public-maps'),
    path('packs/custom/upload/', views.CustomPackUploadView.as_view(), name='custom-pack-upload'),
    path('packs/custom/', views.CustomPackListView.as_view(), name='custom-pack-list'),
    path('packs/upload-zip/', views.PackZipUploadView.as_view(), name='pack-zip-upload'),
    path('packs/uploaded/', views.UploadedPackListView.as_view(), name='uploaded-pack-list'),
    path('packs/uploaded/<str:pack_id>/', views.UploadedPackDeleteView.as_view(), name='uploaded-pack-delete'),
]
