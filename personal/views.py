import numpy
from django.conf import settings
from django.core.mail import send_mail
from django.core.serializers import serialize
from django.db import transaction
from django.shortcuts import render
from DP2softback.constants import messages
from DP2softback.services.api_gpt import ChatGptService
from evaluations_and_promotions.models import *
from flask import Flask, redirect, render_template, request, url_for
from gaps.models import *
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import *
from .serializers import *


class HiringProcessView(APIView):
    @transaction.atomic
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        hps = HiringProcess.objects.all()  # should be just active ones and may be by some extra criteria...like user
        hps_serializer = HiringProcessSerializer(hps, many=True)

        for hps in hps_serializer.data:
            position_id = hps['position']
            # area
            areasxposition = AreaxPosicion.objects.get(id=position_id)
            hps['areaxpositiondetail'] = AreaxPositionSerializer(areasxposition).data
            # Get the current process stage for the hiring process
            hp_instance = HiringProcess.objects.get(id=hps['id'])
            current_stage = hp_instance.get_current_process_stage()
            if current_stage:
                hps['current_process_stage'] = ProcessStageSerializer(current_stage).data
            else:
                hps['current_process_stage'] = None

        return Response(hps_serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        hp_serializer = HiringProcessSerializer(data=request.data, context=request.data)
        if not hp_serializer.is_valid():
            return Response(hp_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        hiring_process = hp_serializer.save()

        employees_data = request.data.get('employees', [])
        employee_x_hiring_process_serializer = EmployeeXHiringProcessSerializer(data=employees_data, many=True)
        for employee_data in employees_data:
            employee_data['hiring_process'] = hiring_process.id
        if not employee_x_hiring_process_serializer.is_valid():  # If it fails here, atomicity is compromised :(
            return Response(employee_x_hiring_process_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        employee_x_hiring_process_serializer.save()

        process_stages_data = request.data.get('process_stages', [])
        process_stage_serializer = ProcessStageSerializer(data=process_stages_data, many=True)
        for stage_data in process_stages_data:
            stage_data['hiring_process'] = hiring_process.id
        if not process_stage_serializer.is_valid():  # If it fails here, atomicity is compromised :(
            return Response(process_stage_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        process_stage_serializer.save()

        return Response(hp_serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, pk):
        hiring_process = HiringProcess.objects.filter(id=pk).first()
        if not hiring_process:
            return Response({'message': 'HiringProcess not found'}, status=status.HTTP_404_NOT_FOUND)

        hp_serializer = HiringProcessSerializer(hiring_process, data=request.data, context=request.data)
        if not hp_serializer.is_valid():
            return Response(hp_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        updated_hiring_process = hp_serializer.save()

        process_stages_data = request.data.get('process_stages', [])
        existing_process_stages = updated_hiring_process.process_stages.all()
        existing_process_stages_mapping = {stage.id: stage for stage in existing_process_stages}
        updated_process_stages = []
        created_process_stages = []

        for stage_data in process_stages_data:
            stage_id = stage_data.get('id')
            if stage_id:
                # Update existing process stage
                if stage_id in existing_process_stages_mapping:
                    stage_instance = existing_process_stages_mapping[stage_id]
                    stage_serializer = ProcessStageSerializer(
                        instance=stage_instance,
                        data=stage_data,
                        partial=True
                    )
                    if stage_serializer.is_valid():
                        updated_stage = stage_serializer.save()
                        updated_process_stages.append(updated_stage)
                    else:
                        return Response(stage_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'message': f"ProcessStage with id '{stage_id}' does not exist"},
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                # Create new process stage
                stage_data['hiring_process'] = updated_hiring_process.id
                stage_serializer = ProcessStageSerializer(data=stage_data)
                if stage_serializer.is_valid():
                    created_stage = stage_serializer.save()
                    created_process_stages.append(created_stage)
                else:
                    return Response(stage_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Delete any existing process stages that were not included in the request data
        existing_stage_ids = existing_process_stages_mapping.keys()
        stages_to_delete = set(existing_stage_ids) - set([stage.id for stage in updated_process_stages])
        ProcessStage.objects.filter(id__in=stages_to_delete).delete()

        # TODO: Update assigned employees
        return Response({'message': 'HiringProcess and ProcessStages updated successfully'},
                        status=status.HTTP_200_OK)


class StageTypeView(APIView):
    def get(self, request):
        sts = StageType.objects.all()
        st_serializer = StageTypeSerializer(sts, many=True)

        return Response(st_serializer.data, status=status.HTTP_200_OK)

    def post(self, request, id=0):
        st_serializer = StageTypeSerializer(data=request.data, context=request.data)
        if st_serializer.is_valid():
            st_serializer.save()
            return Response(st_serializer.data, status=status.HTTP_201_CREATED)
        return Response(st_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProcessStageView(APIView):
    def get(self, request):
        hiring_process_id = request.GET.get('hiring_process_id')

        if hiring_process_id:
            process_stages = ProcessStage.objects.filter(hiring_process_id=hiring_process_id)
        else:
            process_stages = ProcessStage.objects.all()

        process_stage_serializer = ProcessStageSerializer(process_stages, many=True)
        return Response(process_stage_serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):  # "cerrar etapa"

        try:
            current_date = timezone.now().date()
            hp_instance = HiringProcess.objects.get(process_stages__id=pk)
            current_stage = hp_instance.get_current_process_stage()

            if current_stage and current_stage.id == pk and current_stage.end_date >= current_date:
                current_stage.end_date = current_date
                current_stage.save()

                # TODO: For the email, it is necessary to define from where the successful and unsuccessful applicants will be retrieved
                applicants = []  # Table.objects.filter(hiring_process=hp_instance)
                successful_applicants = []  # maybe get from somewhere
                unsuccessful_applicants = []  # maybe get from somewhere
                for applicant in applicants:
                    if applicant_passed_stage(applicant):  # this is not necessary if applicants who passed are already saved...
                        successful_applicants.append(applicant)
                    else:
                        unsuccessful_applicants.append(applicant)

                next_stage = ProcessStage.objects.filter(hiring_process=hp_instance, start_date__gt=current_stage.end_date).order_by('start_date').first()
                if next_stage:
                    next_stage.start_date = current_date
                    next_stage.save()
                    send_emails(next_stage, successful_applicants, unsuccessful_applicants)
                else:
                    send_emails(None, successful_applicants, unsuccessful_applicants)
                return Response(status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)
        except HiringProcess.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


def applicant_passed_stage(applicant):
    # Marco's TODO (?)
    return True


def send_emails(next_stage, successful_applicants, unsuccessful_applicants):
    if next_stage is not None:
        successful_subject = '¡Felicidades! Has pasado la siguiente etapa'
        successful_body = 'Estimado solicitante, has pasado con éxito la siguiente etapa del proceso de contratación: ' + next_stage
    else:
        successful_subject = '¡Felicidades! Has sido seleccionado'
        successful_body = 'Estimado solicitante, has pasado con éxito todas las etapas del proceso de contratación. Nos estaremos comunicando con usted lo más pronto posible.'

    unsuccessful_subject = 'Actualización sobre tu solicitud'
    unsuccessful_body = 'Estimado solicitante, lamentamos informarte que no has pasado la siguiente etapa del proceso de contratación.'

    for applicant in successful_applicants:
        send_mail(
            successful_subject,
            successful_body,
            settings.EMAIL_HOST_USER,
            [applicant.user.email],
            fail_silently=False
        )

    for applicant in unsuccessful_applicants:
        send_mail(
            unsuccessful_subject,
            unsuccessful_body,
            settings.EMAIL_HOST_USER,
            [applicant.user.email],
            fail_silently=False
        )


class JobOfferView(APIView):
    def get(self, request):

        queryset = JobOffer.objects.all()
        serializer_class = JobOfferSerializerRead(queryset, many=True)
        return Response(serializer_class.data, status=status.HTTP_200_OK)

    def post(self, request):

        try:

            hiring_process_id = request.data.get('hiring_process_id')
            hiring_process = HiringProcess.objects.get(id=hiring_process_id)
            areaxposition = AreaxPosicion.objects.get(id=hiring_process.position.id)
            responsabilities = areaxposition.functions_set.all()
            print(responsabilities)
            responsabilities_introduction = ''
            for res in responsabilities:
                responsabilities_introduction += res.description + '\n'
            print(responsabilities_introduction)
            introduction = messages.COMPANY_INTRODUCTION
            offer_introduction = request.data.get('offer_introduction')
            tech = CompetencyxAreaxPosition.objects.filter(
                areaxposition=areaxposition,
                competency__type=SubCategory.Type.TECNICA
            ).values_list('competency__name', flat=True)
            tech_capacities = ','.join(list(tech))
            human = CompetencyxAreaxPosition.objects.filter(
                areaxposition=areaxposition,
                competency__type=SubCategory.Type.BLANDA
            ).values_list('competency__name', flat=True)
            human_capacities = ','.join(list(human))

            capacities_introduction = messages.TECH_INTRODUCTION + ChatGptService.chatgpt_request(tech_capacities, 1.4)

            # for tc in tech: capacities_introduction+='\t'+tc+'\n'
            capacities_introduction += '\n\n' + messages.HUMAN_INTRODUCTION + ChatGptService.chatgpt_request(human_capacities, 1.4)

            # for hc in human: capacities_introduction+='\t'+hc+'\n'
            print(capacities_introduction)

            beneficies_introduction = messages.BENEFICIES_INTRODUCTION
            location = request.data.get('location')
            salary_range = request.data.get('salary_range')

            jobOffer = JobOffer.objects.create(
                hiring_process=hiring_process,
                introduction=introduction,
                offer_introduction=offer_introduction,
                responsabilities_introduction=responsabilities_introduction,
                capacities_introduction=capacities_introduction,
                beneficies_introduction=beneficies_introduction,
                location=location,
                salary_range=salary_range
            )
            jobOffer.save()

            jo_serialized = JobOfferSerializerRead(jobOffer)

            return Response(status=status.HTTP_200_OK,
                            data={
                                'message': 'Job offer sucessfully created',
                                'jobOffer': jo_serialized.data
                            },)

        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class AreaxPositionView(APIView):
    def get(self, request):
        axp = AreaxPosicion.objects.all()
        axp_serializer = AreaxPositionSerializer(axp, many=True)
        return Response(axp_serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        '''
        La posicion se registra con:
        Nombre..
        Descripcion..
        id del Area a la que pertenece..
        job_modality (presencial, remoto, hibrido)..
        workday_type (Tiempo completo, medio tiempo)..
        competencies (arreglo de ids de competencias)..
        training (arreglo de ids de estudios)..
        responsabilities (arreglo de responsabilidades)..
        '''
        print(request.user)
        print(request.data)

        try:
            area = request.data["area"]
            a_position = request.data["position"]
        except:
            a_position = None

        # check if all data exits
        try:
            if a_position:
                position = Position.objects.get(id=a_position)
                type_creation = f"Using the existing position with id: {position.id}"
            else:
                name = request.data["name"]
                description = request.data["description"]
                job_modality = request.data["job_modality"]
                workday_type = request.data["workday_type"]

                # insert position
                position = Position(
                    name=name,
                    description=description,
                    modalidadTrabajo=job_modality,
                    tipoJornada=workday_type,
                )
                position.save()
                type_creation = f"Inserting a new position with id: {position.id}"

            competencies = request.data["competencies"]
            training = request.data["training"]
            functions = request.data["responsabilities"]

            area = Area.objects.get(id=area)
            # saving every competence, capacity and training
            competency_list = []
            training_list = []
            for com in competencies:
                competencyobj = SubCategory.objects.get(id=com)
                print(f"Competence: {competencyobj.name}")
                competency_list.append(competencyobj)
            for tr in training:
                trainingobj = TrainingxLevel.objects.get(id=tr)
                print(f"Training: {trainingobj.training.name}")
                training_list.append(trainingobj)

        except Exception as e:
            return Response(data=f"Exception: {e}", status=status.HTTP_404_NOT_FOUND)

        # linking position with Area
        areaxposition = AreaxPosicion(area=area, position=position)
        areaxposition.save()

        # saving functions
        for function in functions:
            functionobj = Functions.objects.create(
                areaxposition=areaxposition,
                description=function
            )
            functionobj.save()

        # linking competencies and training with position
        for com in competency_list:
            obj = CompetencyxAreaxPosition(
                competency=com,
                areaxposition=areaxposition
            )
            obj.save()
        for tr in training_list:
            obj = TrainingxAreaxPosition(
                training=tr,
                areaxposition=areaxposition
            )
            obj.save()

        axp_serialized = AreaxPositionSerializer(areaxposition)

        return Response(status=status.HTTP_200_OK,
                        data={
                            'message': 'AreaxPosition registered',
                            'type_creation': type_creation,
                            'areaxposition': axp_serialized.data
                        },)


class AllPositionView(APIView):
    def get(self, request):
        p = Position.objects.all()
        serializer = PositionSerializer(p, many=True)

        for position_data in serializer.data:
            position_id = position_data['id']
            # area
            areasxposition = AreaxPosicion.objects.filter(position_id=position_id)
            print(areasxposition)
            areas = []
            for axp in areasxposition:
                areas.append((axp.area.id, axp.area.name))
            print(areas)
            position_data['areas'] = dict(areas)

        return Response(serializer.data, status=status.HTTP_200_OK)


class PositionView(APIView):
    def get(self, request, pk):
        if pk:
            positions = Position.objects.filter(id=pk)
        else:
            positions = Position.objects.all()
        serializer = PositionSerializer(positions, many=True)

        for position_data in serializer.data:
            position_id = position_data['id']
            # area
            areasxposition = AreaxPosicion.objects.filter(position_id=position_id)
            print(areasxposition)
            areas = []
            for axp in areasxposition:
                areas.append((axp.area.id, axp.area.name))
            print(areas)
            position_data['areas'] = dict(areas)

        return Response(serializer.data)

    def put(self, request, pk):
        position = Position.objects.filter(pk=pk).first()
        if not position:
            return Response({"error": "Position not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = PositionSerializer(position, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FunctionsView(APIView):
    def get(self, request):
        functions = Functions.objects.all()
        serializer = FunctionsSerializer(functions, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = FunctionsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        function = Functions.objects.filter(pk=pk).first()
        if not function:
            return Response({"error": "Function not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = FunctionsSerializer(function, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TrainingxLevelView(APIView):
    def get(self, request):
        training = TrainingxLevel.objects.all()
        serializer = TrainingxLevelSerializer(training, many=True)
        return Response(serializer.data)


###


class ApplicationxInfoView(APIView):
    def get(self, request, pk):
        try:
            applicant = Applicant.objects.get(id=pk)
            applicant_info = ApplicantSerializerRead(applicant, many=False)

            competencies = CompetencyxApplicant.objects.filter(applicant=applicant)
            training = TrainingxApplicant.objects.filter(applicant=applicant)
            experience = Experience.objects.filter(applicant=applicant)

            application_info = {}
            training = TrainingxApplicantSerializerRead(training, many=True)
            application_info['training'] = training.data if training else {}
            experience = ExperienceSerializerRead(experience, many=True)
            application_info['experience'] = experience.data if experience else {}

            ch = []
            ct = []
            for c in competencies:
                if c.competency.type == 0:
                    ct.append(c)
                else:
                    ch.append(c)

            application_info['competency_t'] = CompetencyxApplicantSerializerRead(ct, many=True).data
            application_info['competency_h'] = CompetencyxApplicantSerializerRead(ch, many=True).data

            return Response(status=status.HTTP_200_OK,
                            data={
                                'applicant': applicant_info.data,
                                'applicationinfo': application_info
                            },)

        except Exception as e:
            return Response(data=f"Exception: {e}", status=status.HTTP_404_NOT_FOUND)

    def post(self, request):

        print(request.user)
        print(request.data)

        # check if all data exits
        try:
            applicant_id = request.data["applicant"]
            applicant = Applicant.objects.get(id=applicant_id)

            competencies = request.data["competencies"]
            training = request.data["training"]
            experience = request.data["experience"]

            competency_list = []
            training_list = []
            for com in competencies:
                competencyobj = SubCategory.objects.get(id=com)
                print(f"Competence: {competencyobj.name}")
                competency_list.append(competencyobj)
            for tr in training:
                trainingobj = TrainingxLevel.objects.get(id=tr)
                print(f"Training: {trainingobj.training.name}")
                training_list.append(trainingobj)

            # delete previous info
            exp = Experience.objects.filter(applicant=applicant)
            if exp:
                exp.delete()
            com = CompetencyxApplicant.objects.filter(applicant=applicant)
            if com:
                com.delete()
            tra = TrainingxApplicant.objects.filter(applicant=applicant)
            if tra:
                tra.delete()

            experienceobj = Experience.objects.update_or_create(
                applicant=applicant,
                description=experience
            )

            # linking competencies and training with applicant
            for com in competency_list:
                obj = CompetencyxApplicant.objects.update_or_create(
                    competency=com,
                    applicant=applicant
                )

            for tr in training_list:
                obj = TrainingxApplicant.objects.update_or_create(
                    trainingxlevel=tr,
                    applicant=applicant
                )

            applicant_s = ApplicantSerializerRead(applicant, many=False)

            return Response(status=status.HTTP_200_OK,
                            data={
                                'message': 'Applicant detail registered',
                                'applicant': applicant_s.data
                            },)

        except Exception as e:
            print(e)
            return Response(data=f"Exception: {e}", status=status.HTTP_404_NOT_FOUND)


class AllApplicationxInfoView(APIView):
    def get(self, request):
        try:
            applicants = Applicant.objects.all()

            applicants_list = []
            for applicant in applicants:
                print(applicant)
                applicant_info = ApplicantSerializerRead(applicant, many=False)
                # print(applicant_info.data)
                competencies = CompetencyxApplicant.objects.filter(applicant=applicant)
                training = TrainingxApplicant.objects.filter(applicant=applicant)
                experience = Experience.objects.filter(applicant=applicant)

                application_info = {}
                training = TrainingxApplicantSerializerRead(training, many=True)
                application_info['training'] = training.data if training else {}
                experience = ExperienceSerializerRead(experience, many=True)
                application_info['experience'] = experience.data if experience else {}

                ch = []
                ct = []
                for c in competencies:
                    if c.competency.type == 0:
                        ct.append(c)
                    else:
                        ch.append(c)

                application_info['competency_t'] = CompetencyxApplicantSerializerRead(ct, many=True).data
                application_info['competency_h'] = CompetencyxApplicantSerializerRead(ch, many=True).data

                # print(applicant_info.data)
                print(application_info)

                # my_dict = {"applicant":applicant_info.data}
                my_dict = {"applicant": applicant_info.data, "applicationinfo": application_info}

                # print(my_dict)

                applicants_list.append(my_dict)

            # print(applicants_list)

            return Response(status=status.HTTP_200_OK,
                            data=applicants_list,)

        except Exception as e:
            print(e)
            return Response(data=f"Exception: {e}", status=status.HTTP_404_NOT_FOUND)


class ApplicantView(APIView):
    def get(self, request, pk):
        try:
            a = Applicant.objects.get(id=pk)
            a_serializer = ApplicantSerializerRead(a, many=False)

            return Response(a_serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(data=f"Exception: {e}", status=status.HTTP_404_NOT_FOUND)


class AllApplicantView(APIView):
    def get(self, request):
        a = Applicant.objects.all()
        a_serializer = ApplicantSerializerRead(a, many=True)

        return Response(a_serializer.data, status=status.HTTP_200_OK)


class FilterFirstStepView(APIView):
    def post(self, request):

        # tomar hiring process
        try:
            hiring_process = request.data["hiring_process"]
            affinity = request.data["affinity"]
            mandatory = request.data["mandatory"]

            process_stage = ProcessStage.objects.get(hiring_process=hiring_process, order=1)
            applicants_ids = ApplicantxProcessStage.objects.filter(process_stage=process_stage).values_list('applicant__id')
            applicants = Applicant.objects.filter(id__in=applicants_ids)

            desired_training = TrainingxAreaxPosition.objects.filter(areaxposition=process_stage.hiring_process.position)  # training
            desired_competencies = CompetencyxAreaxPosition.objects.filter(areaxposition=process_stage.hiring_process.position)  # competency

            mandatory_training = TrainingxLevel.objects.filter(id__in=mandatory)

            print(desired_training)
            print(desired_competencies)
            print(mandatory_training)

            array_of_qualifications = []
            mult_t = 50
            mult_c = 10
            for applicant in applicants:
                score = 0
                check = 0
                total = 0
                disqualified = 0
                reason_disqualified = []
                # check training
                print("\nTraining:")
                a_t = TrainingxApplicant.objects.filter(applicant=applicant)  # trainingxlevel
                for t in desired_training:
                    total += mult_t
                    for m in mandatory_training:
                        if t.training.training.id == m.training.id:
                            disqualified += 1
                            reason_disqualified.append(t.training.id)
                            print("+ok")
                    for a in a_t:
                        if a.trainingxlevel.training.id == t.training.training.id:
                            if a.trainingxlevel.level.level >= t.training.level.level:
                                print(str(a.trainingxlevel) + " " + str(a.trainingxlevel.level.level))
                                print(str(t.training) + " " + str(t.training.level.level))
                                score += a.trainingxlevel.level.level * mult_t
                                check += mult_t

                                for m in mandatory_training:
                                    if t.training.training.id == m.training.id:
                                        disqualified -= 1
                                        print("-ok")
                                        reason_disqualified.remove(t.training.id)
                                break

                print("Competency:")
                a_c = CompetencyxApplicant.objects.filter(applicant=applicant)  # competency
                for c in desired_competencies:
                    total += mult_c
                    for a in a_c:
                        if a.competency.id == c.competency.id:
                            print(str(a.competency) + " " + str(a.scale))
                            print(str(c.competency) + " " + str(c.scale))
                            score += a.scale * mult_c
                            check += mult_c

                a_qualification = [applicant.id, round(check / total * 100, 2), score, disqualified, reason_disqualified]
                print(a_qualification)
                print()

                array_of_qualifications.append(a_qualification)

            print(array_of_qualifications)
            b = numpy.array(array_of_qualifications)
            b = b[b[:, 1].argsort()]  # sort by day
            b = b[b[:, 2].argsort(kind='mergesort')[::-1]]  # sort by month
            b = b[b[:, 3].argsort(kind='mergesort')[::-1]]  # sort by year

            array_of_qualifications = b.tolist()
            print(array_of_qualifications)

            array_of_responses = []
            for i, item in enumerate(applicants):
                reason = TrainingxLevel.objects.filter(id__in=array_of_qualifications[i][4])

                reason_serializer = TrainingxLevelSerializer(reason, many=True).data if reason else []

                a = ApplicantSerializerRead(item, many=False)

                a_response = {
                    "applicant": a.data,
                    "affinity": array_of_qualifications[i][1],
                    "score": array_of_qualifications[i][2],
                    "disqualified": array_of_qualifications[i][3],
                    "reason_of_disqualified": reason_serializer
                }

                array_of_responses.append(a_response)
                pass

            return Response(array_of_responses, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(data=f"Exception: {e}", status=status.HTTP_404_NOT_FOUND)

        # calcular

        pass
