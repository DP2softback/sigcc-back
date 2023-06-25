from django.urls import include, path
from gaps.views import *

gaps_patterns = [
    path('employeeArea', EmployeeAreaView.as_view()),
    path('employeePosition', EmployeePositionView.as_view()),

    path('competenceAreaPosition', CapacityAreaPositionView.as_view()),
    path('competenceEmployee', CapacityEmployeeView.as_view()),
    path('employeeTrainingNeed', TrainingNeedView.as_view()),

    path('competenceAreaPositionSearch', SearchCapacityAreaPositionView.as_view()),
    path('competenceEmployeeSearch', SearchCapacityEmployeeView.as_view()),
    path('employeeTrainingNeedSearch', SearchNeedView.as_view()),

    path('competenceSearch', SearchCapacityView.as_view()),
    path('competenceConsolidateSearch', SearchCapacityConsolidateView.as_view()),
    path('trainingNeedSearch', SearchTrainingNeedView.as_view()),
    path('competenceTypes', CapacityTypeView.as_view()),
    path('competenceTypesSearch/<int:pk>', SearchCapacityTypeView.as_view()),

    # path('competenceScale', CapacityScaleView.as_view()),
    # path('competenceScale/<int:id>', CompetenceScaleView.as_view()),

    path('competences', CapacityView.as_view()),
    path('competences/<int:id>', CapacityView.as_view()),

    path('jobOfferSearch', SearchJobOfferView.as_view()),
    path('trainingNeedDemand', GenerateTrainingDemandView.as_view()),
    path('trainingNeedCourse', TrainingNeedCourseView.as_view()),
    path('trainingNeedCourseSearch', SearchTrainingNeedCourseView.as_view()),

    path('saveListedEmployeeForOffer', SaveShortlistedEmployeexJobOffer.as_view()),
    path('searchJobOfferxEmployeePreRegistered', SearchJobOfferxEmployeePreRegistered.as_view())
]

urlpatterns = [
    path('gaps/', include(gaps_patterns)),
]