from django.urls import include, path

from offers.views import JobOfferView

offers_patterns = [
    path('offers', JobOfferView.as_view()),
]

urlpatterns = [
    path('jobOffers/', include(offers_patterns)),
]
