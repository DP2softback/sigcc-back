from django.urls import include, path

from users.views import UsersView

dashboard_patterns = [
    path('users', UsersView.as_view()),
]

urlpatterns = [
    path('dashboard/', include(dashboard_patterns)),
]

# urlpatterns = [
#     path('users', UsersView.as_view()),
# ]