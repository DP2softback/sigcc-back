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
import pytz

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
                subcategory = get_object_or_404(SubCategory, id=subcategory_id)
                evaluationxsubcategory = EvaluationxSubCategory(
                    subCategory=subcategory,
                    evaluation=evaluation,
                    score=score
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

            evaluationxsubcategories = EvaluationxSubCategory.objects.filter(evaluation=evaluation)

            categories = evaluationxsubcategories.values('subCategory__category_id', 'subCategory__category__name').distinct()

            request_data = {
                'evaluatorId': evaluation.evaluator_id,
                'evaluatedId': evaluation.evaluated_id,
                'associatedProject': evaluation.proyecto,
                'evaluationType': evaluation.evaluationType.name,
                'isFinished': evaluation.isFinished,
                'additionalComments': evaluation.generalComment,
                'categoryId': [category['subCategory__category_id'] for category in categories],
                'categoryName': [category['subCategory__category__name'] for category in categories],
                'subcategories': [
                    {
                        'id': evaluationxsubcategory.subCategory.id,
                        'name': evaluationxsubcategory.subCategory.name,
                        'score': evaluationxsubcategory.score
                    }
                    for evaluationxsubcategory in evaluationxsubcategories
                ]
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
        peru_tz = pytz.timezone('America/Lima')
        subcats =[]
        for subcategory_data in subcategories:
            subcategory_data['category'] = category
            subcat = SubCategory(
                creationDate = datetime.now(peru_tz),
                code = subcategory_data['code'],
                name = subcategory_data['name'],
                description = subcategory_data['description'], 
                category = category,
                #competence =  subcategory_data['competence']
            )
            subcats.append(subcat)
        SubCategory.objects.bulk_create(subcats)
        return Response({'message': 'Subcategories added successfully.'}, status=status.HTTP_201_CREATED)

