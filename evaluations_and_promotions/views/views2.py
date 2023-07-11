from evaluations_and_promotions.serializers import SubCategorySerializer
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from ..models import *
from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime 
from collections import defaultdict
import pytz
from django.db.models import F
from django.db.models.functions import ExtractYear, ExtractMonth
from django.http import HttpResponse
from django.db.models import Avg
from django.http import HttpResponseBadRequest
import json
from django.http import JsonResponse
from datetime import datetime, timezone
from django.core.mail import EmailMultiAlternatives, send_mail
from django.conf import settings

class EvaluationCreateAPIView(APIView):
    @transaction.atomic

    def post(self, request):
        try:
            data = request.data
            evaluator_id = data.get('evaluatorId')
            evaluated_id = data.get('evaluatedId')
            evaluated_employee = get_object_or_404(Employee, id=evaluated_id)
            is_finished = data.get('isFinished')
            additional_comments = data.get('additionalComments')
            has_comment = bool(additional_comments)

            evaluation_type_name = data.get('evaluationType')
            evaluation_type = get_object_or_404(EvaluationType, name=evaluation_type_name)

            associated_project = data.get('associatedProject')
            category_id = data.get('categoryId')
            subcategories_data = data.get('subcategories')

            category = get_object_or_404(Category, id=category_id)
            scores = [subcategory["score"] for subcategory in subcategories_data]
            finalScore = sum(scores) / len(scores)
            evaluation = Evaluation.objects.create(
                evaluator_id=evaluator_id,
                evaluated_id=evaluated_id,
                hasComment=has_comment,
                generalComment=additional_comments,
                isFinished=is_finished,
                finalScore=finalScore,
                evaluationType=evaluation_type,
                area=evaluated_employee.area,  
                position=evaluated_employee.position,  
                proyecto=associated_project,
                evaluationDate = datetime.now()
                
            )

            evaluationxsubcategories = []
            for subcategory_data in subcategories_data:
                subcategory_id = subcategory_data.get('id')
                score = subcategory_data.get('score')
                data_comment= subcategory_data.get('comment')
                data_hasComment = subcategory_data.get('hasComment')
                comment = '' if data_comment is None else data_comment
                hasComment = False if data_hasComment is None else data_hasComment
                subcategory = get_object_or_404(SubCategory, id=subcategory_id)
                evaluationxsubcategory = EvaluationxSubCategory(
                    subCategory=subcategory,
                    evaluation=evaluation,
                    score=score,
                    comment=comment,
                    hasComment=hasComment
                )
                evaluationxsubcategories.append(evaluationxsubcategory)

            EvaluationxSubCategory.objects.bulk_create(evaluationxsubcategories)

            return Response({'message': 'Evaluation created successfully.'}, status=status.HTTP_201_CREATED)
        except EvaluationType.DoesNotExist:
            return Response({'message': 'Invalid evaluation type.'}, status=status.HTTP_400_BAD_REQUEST)
        except SubCategory.DoesNotExist:
            return Response({'message': 'Invalid subcategory.'}, status=status.HTTP_400_BAD_REQUEST)
        except Category.DoesNotExist:
            return Response({'message': 'Invalid category.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'message': 'An error occurred.', 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class getEvaluation(APIView):
    def post(self, request, evaluation_id):
        try:
            evaluation = get_object_or_404(Evaluation, id=evaluation_id)

            subcategories = EvaluationxSubCategory.objects.filter(evaluation=evaluation)
            id_rel = None
            try:
                Rela = Evaluation.objects.get(relatedEvaluation__id = evaluation_id)
                id_rel = Rela.id
            except Evaluation.DoesNotExist:
                print("No hay rela")

            
            

            category_subcategories = defaultdict(list)
            for subcategory in subcategories:
                category = subcategory.subCategory.category
                category_subcategories[category].append({
                    'id': subcategory.subCategory.id,
                    'name': subcategory.subCategory.name,
                    'score': subcategory.score,
                    'comment': subcategory.comment
                })


            request_data = {
                'evaluatorId': evaluation.evaluator_id,
                'evaluatedId': evaluation.evaluated_id,
                'associatedProject': evaluation.proyecto,
                'evaluationType': evaluation.evaluationType.name,
                'isFinished': evaluation.isFinished,
                'additionalComments': evaluation.generalComment,
                'categories': [
                    {
                        'id': category.id,
                        'name': category.name,
                        'subcategories': category_subcategories[category]
                    }
                    for category in category_subcategories.keys()
                ],
                'RelatedEvaluation': id_rel
            }

            return Response(request_data)
        except Evaluation.DoesNotExist:
            return Response({'message': 'Evaluation not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': 'An error occurred.', 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class getCategory(APIView):
    def post(self,request, categoryId):
        subcategories = SubCategory.objects.filter(category=categoryId)
        data = []
        for subcategory in subcategories:
            data.append({
                'idSubcategory': subcategory.id,
                'nameSubCategory': subcategory.name,
                'isActive': subcategory.isActive,
                'idCompetencia': '', #subcategory.category.id, 
                'nameCompetencia': '' #subcategory.category.name  
            })

        return Response(data, status=status.HTTP_200_OK)

class addSubcategory(APIView):
    @transaction.atomic
    def post(self,request, categoryId):
        data = request.data
        category = get_object_or_404(Category, id=categoryId)
        subcategories = data.get('Subcategorias', [])
        peruTz = pytz.timezone('America/Lima')
        subcats =[]
        count =  SubCategory.objects.filter(category = category).count()
        for subcategoryData in subcategories:
            count += 1
            subcategoryId = subcategoryData.get('id')
            if(subcategoryId is not None):
                subcat =SubCategory.objects.get(id= subcategoryId)
                subcat.code = category.code+str(count)
                subcat.modifiedDate = datetime.now(peruTz)
                subcat.category = category
                subcat.code = category.code+str(count)
                subcat.modifiedDate = datetime.now(peruTz)
                subcat.save()
            else:    
                subcat = SubCategory(
                    creationDate = datetime.now(peruTz),
                    code = category.code+str(count),
                    name = subcategoryData['name'],
                    description = subcategoryData['description'], 
                    category = category,
                )
                subcats.append(subcat)
            
        SubCategory.objects.bulk_create(subcats)
        return Response({'message': 'Subcategories added successfully.'}, status=status.HTTP_201_CREATED)

class addCategory(APIView):
    @transaction.atomic
    def post(self, request):
        data = request.data
        catName = data.get('nombre')
        peruTz = pytz.timezone('America/Lima')
        now=datetime.now(peruTz)
        subcategories = data.get('Subcategorias', [])

        cat = Category(
        creationDate = now,
        modifiedDate =now,
        name = catName,
        code = 'USR',
        )

        cat.save()

        subcats =[]
        count = 0 
        for subcategoryData in subcategories:
            count += 1
            subcategoryId = subcategoryData.get('id')
            
            if(subcategoryId is not None):
                subcat =SubCategory.objects.get(id= subcategoryId)
                subcat.category = cat
                subcat.code = cat.code+str(count)
                subcat.modifiedDate = datetime.now(peruTz)
                subcat.save()
            else:    
                subcat = SubCategory(
                    creationDate = datetime.now(peruTz),
                    code = cat.code+str(count),
                    name = subcategoryData['name'],
                    description = subcategoryData['description'], 
                    category = cat,
                )
                subcats.append(subcat)
        SubCategory.objects.bulk_create(subcats)
        return Response({'message': 'Category created.'}, status=status.HTTP_201_CREATED)

class getFreeCompetences(APIView):
    def get(self, request):
        competences =  SubCategory.objects.all().order_by('name').distinct('name')
        competences = [subcategory for subcategory in competences if subcategory.category is None]
        serialized = SubCategorySerializer(competences, many=True)
        return Response(serialized.data, status=status.HTTP_200_OK)

class GetReporteGeneral(APIView):
    def post(self, request):
        try:
            data = request.data
            evalType = data.get('evaluationType')
            evaluationType = get_object_or_404(EvaluationType, name=evalType)
            initDate = data.get('fecha_inicio')
            finishDate = data.get('fecha_fin')
            query = '''
                SELECT
                    id,
                    EXTRACT(YEAR FROM "evaluationDate") AS "year",
                    EXTRACT(MONTH FROM "evaluationDate") AS "month",
                    area_id,
                    AVG("finalScore") AS ScoreAverage
                FROM
                    evaluations_and_promotions_evaluation
                WHERE
                    "isActive" = True
                    AND "evaluationType_id" = {}
                    AND "evaluationDate" IS NOT NULL
                    AND "evaluationDate" >= to_date('{}', 'YYYY-MM-DD')
                    AND "evaluationDate" <= to_date('{}', 'YYYY-MM-DD')
                GROUP BY
                    "id",
                    "year",
                    "month",
                    "area_id"
                ORDER BY
                    "year", "month", "area_id"
            '''.format(evaluationType.id, initDate, finishDate)
            evaluations = Evaluation.objects.raw(query)
            result = []

            for row in evaluations:
                year = int(row.year)
                month = str(row.month).zfill(2)
                area_id = row.area_id
                score_average = row.scoreaverage  

                year_dict = next((item for item in result if item['year'] == year), None)
                if year_dict is None:
                    year_dict = {
                        'year': year,
                        'month': []
                    }
                    result.append(year_dict)

                month_dict = next((item for item in year_dict['month'] if item['month'] == month), None)
                if month_dict is None:
                    month_dict = {
                        'month': month,
                        'area_scores': []
                    }
                    year_dict['month'].append(month_dict)

                area_scores = month_dict['area_scores']
                area = Area.objects.get(id=area_id) 
                area_score = next((item for item in area_scores if item['AreaName'] == area.name), None)
                if area_score is None:
                    area_score = {
                        'AreaName': area.name,
                        'ScoreSum': score_average,
                        'Count': 1
                    }
                    area_scores.append(area_score)
                else:
                    area_score['ScoreSum'] += score_average
                    area_score['Count'] += 1
            for year_dict in result:
                for month_dict in year_dict['month']:
                    for area_score in month_dict['area_scores']:
                        area_score['ScoreAverage'] = area_score['ScoreSum'] / area_score['Count']
                        del area_score['ScoreSum']
                        del area_score['Count']

            return Response(result)

        except EvaluationType.DoesNotExist:
            return HttpResponseBadRequest("EvaluationType does not exist.")

            

