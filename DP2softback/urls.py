
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path 

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path("users/",include("users.urls"))
# ]

admin.site.site_header = 'SIGCC BACKk'
admin.site.index_title = 'Backend de proyecto SIGCC'

public_apis = [
    url(r'^api/v1/', include([
        url(r'', include('users.urls')),        
    ])),
]

urlpatterns = [
    url(r'^', include((public_apis, 'DP2softback'))),    
    url(r'^admin/', admin.site.urls),
] 