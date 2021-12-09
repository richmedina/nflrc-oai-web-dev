"""nflrc_oai_web URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from oaisite.views import (
    HomeView, 
    PreviousIssuesView,
    SpecialIssuesView,
    CommunityView, 
    CollectionListView, 
    CollectionView, 
    ItemView, 
    ItemViewFull,
    PageView,
    PageUpdateView,
    PostListView,
    PostView,
    PostUpdateView,
    PostViewPrivate,
    PageViewPrivate,
    SearchHaystackView,
    # KeywordBrowseView,
)

from oaiharvests.views import (
    OaiRepositoryListView, 
    OaiRepositoryCreateView, 
    OaiRepositoryUpdateView, 
    OaiRepositoryDeleteView, 
    OaiRepositoryView,
    OaiCommunityView,
    OaiCommunityCreateView,
    OaiCommunityUpdateView,
    OaiCommunityDeleteView,
    OaiCommunityHarvestView,
    OaiCollectionView,
    OaiCollectionCreateView,
    OaiCollectionUpdateView,
    OaiCollectionDeleteView,
    OaiCollectionHarvestView
)

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('previous-issues/', PreviousIssuesView.as_view(), name='previous_issues'),
    path('special-issues/', SpecialIssuesView.as_view(), name='special_issues'),
    path('community/<pk>/', CommunityView.as_view(), name='community'),
    path('collections/', CollectionListView.as_view(), name='collection_list'),
    path('collection/<pk>/', CollectionView.as_view(), name='collection'),
    path('item/<int:pk>/', ItemView.as_view(), name='item'),
    path('item-detail/<int:pk>/', ItemViewFull.as_view(), name='item_full'),
    path('page/<int:pk>/', PageView.as_view(), name='page_view'),
    path('page/edit/<int:pk>/', PageUpdateView.as_view(), name='page_update_view'),
    path('staff-page/<int:pk>/', PageViewPrivate.as_view(), name='staff_page_view'),
    path('post-archive/', PostListView.as_view(), name='post_list_view'),
    path('post/<int:pk>/', PostView.as_view(), name='post_view'),
    path('post/edit/<int:pk>/', PostUpdateView.as_view(), name='post_update_view'),
    path('staff-post/<int:pk>/', PostViewPrivate.as_view(), name='staff_post_view'),
    path('search/', SearchHaystackView.as_view(), name='haystack_search'),
    # path('keys/$', KeywordBrowseView.as_view(), name='keyword_browse_view'),

    # ---------- OAI HARVESTER VIEWS ------------- #
    # Institutional Repositories #
    path('oaiharvester/', OaiRepositoryListView.as_view(),
     name='oai_repository_list'),
    path('oaiharvester/repository/add/',
     OaiRepositoryCreateView.as_view(
     ), name='oai_repository_add'),
    path('oaiharvester/repository/edit/<int:pk>',
     OaiRepositoryUpdateView.as_view(
     ), name='oai_repository_edit'),
    path('oaiharvester/repository/delete/<int:pk>',
     OaiRepositoryDeleteView.as_view(
     ), name='oai_repository_delete'),
    path('oaiharvester/repository/<int:pk>',
     OaiRepositoryView.as_view(), name='oai_repository'),

    # Community Collections #
    path('oaiharvester/community/<pk>',
     OaiCommunityView.as_view(), name='oai_community'),
    path('oaiharvester/community/add/<pk>',
     OaiCommunityCreateView.as_view(
     ), name='oai_community_add'),
    path('oaiharvester/community/edit/<pk>',
     OaiCommunityUpdateView.as_view(
     ), name='oai_community_edit'),
    path('oaiharvester/community/delete/<pk>',
     OaiCommunityDeleteView.as_view(
     ), name='oai_community_delete'),
    path('oaiharvester/community/harvest/<pk>',
     OaiCommunityHarvestView.as_view(
     ), name='oai_harvest_community'),

    # Collections #
    path('oaiharvester/collection/<str:pk>',
     OaiCollectionView.as_view(), name='oai_collection'),
    path('oaiharvester/collection/add/<str:community>',
     OaiCollectionCreateView.as_view(
     ), name='oai_collection_add'),
    path('oaiharvester/collection/edit/<str:pk>',
     OaiCollectionUpdateView.as_view(
     ), name='oai_collection_edit'),
    path('oaiharvester/collection/delete/<str:pk>',
     OaiCollectionDeleteView.as_view(
     ), name='oai_collection_delete'),
    path('oaiharvester/collection/harvest/<str:pk>',
     OaiCollectionHarvestView.as_view(
     ), name='oai_harvest_collection'),

    path('admin/', admin.site.urls),

    path('<slug>/', PageView.as_view(), name='page_slug_view'),
]
