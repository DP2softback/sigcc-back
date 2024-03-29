from django.urls import path

from .views import *

urlpatterns = [
    path('hiring-processes', HiringProcessView.as_view()),
    path('hiring-processes/employees', HiringProcessView.as_view()),
    path('hiring-processes/<int:pk>', HiringProcessView.as_view()),
    path('stage-types', StageTypeView.as_view()),
    path('process-stages', ProcessStageView.as_view()),
    path('process-stages/<int:pk>', ProcessStageView.as_view()),
    path('job-offers', JobOfferView.as_view()),
    path('apply-to-offer', ApplyToOffer.as_view()),
    path('apply-to-process-stage', ApplyToProcessStage.as_view()),

    path('positions', AllPositionView.as_view()),
    path('positions/<int:pk>', PositionView.as_view()),
    path('areaxposition', AreaxPositionView.as_view()),
    path('functions', FunctionsView.as_view()),
    path('functions/<int:pk>', FunctionsView.as_view()),
    path('training', TrainingxLevelView.as_view()),

    path('applicants', AllApplicantView.as_view()),
    path('applicants/<int:pk>', ApplicantView.as_view()),
    path('applicants-info', AllApplicationxInfoView.as_view()),
    path('applicants-info/<int:pk>', ApplicationxInfoView.as_view()),
    path('register-applicants-info', ApplicationxInfoView.as_view()),

    path('filter-first-step', FilterFirstStepView.as_view()),
    path('dummy-first-step', DummyFirstStepView.as_view()),
    path('filter-second-step', FilterSecondStepView.as_view()),
    path('dummy-second-step', DummySecondStepView.as_view()),
    path('filter-third-step', FilterThirdStepView.as_view()),
    path('dummy-third-step', DummyThirdStepView.as_view()),
    path('filter-fourth-step', FilterFourthStepView.as_view()),
    
    path('update-competency-x-applicant', UpdateCompetencyxApplicantView.as_view()),

    path('single-application-status/<int:pk>', SingleApplicationStatusView.as_view()),
    path('all-application-status', AllApplicationStatusView.as_view()),



]
