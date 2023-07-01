import json
from django.shortcuts import render
#from gaps.models import Competence
from rest_framework import status
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from zappa.asynchronous import task
from rest_framework.exceptions import ValidationError
from django.db.models import Avg
from ..models import Evaluation
from ..serializers import *
from login.serializers import *
from datetime import datetime
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import get_object_or_404
from django.db.models import F, Q
from django.db.models.functions import ExtractYear, ExtractMonth
from django.db.models.aggregates import Sum,Count   
from django.db.models import F, ExpressionWrapper, FloatField
from collections import defaultdict
from rest_framework.permissions import AllowAny
from django.core.validators import URLValidator
import pytz
from django.core.mail import EmailMultiAlternatives, send_mail
from django.conf import settings
import urllib.parse



def validate_employee_and_evaluation(employee_id, tipoEva):
    if not employee_id or not tipoEva:
        raise ValidationError("Employee's id and evaluationType are required")

    try:
        employee_id = int(employee_id)
        if employee_id <= 0:
            raise ValueError()
    except ValueError:
        raise ValidationError("Invalid value for employee_id.")

    if not isinstance(tipoEva, str) or not tipoEva.strip():
        raise ValidationError("Invalid value for tipoEva.")

def get_category_averages(evaluations):
    category_scores = EvaluationxSubCategory.objects.filter(evaluation__in=evaluations).values('subCategory__category__name').annotate(avg_score=Avg('score'))
    category_averages = {score['subCategory__category__name']: score['avg_score'] for score in category_scores}
    return category_averages
# Create your views here.
class EvaluationView(generics.ListCreateAPIView):
    queryset = Evaluation.objects.all()
    serializer_class = EvaluationSerializer
    
class PositionGenericView(generics.ListCreateAPIView):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer

class AreaGenericView(APIView):
    def get(self, request):
        area = Area.objects.all()
        area_serializado = AreaSerializer(area,many=True)
        return Response(area_serializado.data,status=status.HTTP_200_OK)

    def post(self,request):
        area_serializado = AreaSerializer(data = request.data)

        if area_serializado.is_valid():
            area_serializado.save()
            return Response(area_serializado.data,status=status.HTTP_200_OK)
        
        return Response(None,status=status.HTTP_400_BAD_REQUEST)

class CategoryGenericView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class EvaluationTypeGenericView(generics.ListCreateAPIView):
    queryset = EvaluationType.objects.all()
    serializer_class = EvaluationTypeSerializer

class SubCategoryTypeGenericView(generics.ListCreateAPIView):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer

class GetPersonasACargo(APIView):
    def post(self, request):
        supervisor_id = request.data.get("id")
        evaluation_type = request.data.get("evaluationType")
        fecha_inicio = request.data.get("fecha_inicio")
        fecha_final=request.data.get("fecha_final")
        nombre = request.data.get("nombre")
        validate_employee_and_evaluation(supervisor_id, evaluation_type)
        
        personas = Employee.objects.filter(supervisor=supervisor_id)

        if nombre:
            personas = personas.filter(
                Q(user__first_name__icontains=nombre) |
                Q(user__last_name__icontains=nombre)  |
                Q(user__username__icontains=nombre)
            )
        evaluation_type_obj = get_object_or_404(EvaluationType, name=evaluation_type)
        evaluations = Evaluation.objects.filter(evaluated__in=personas, evaluationType=evaluation_type_obj, isActive=True, isFinished=True)
        employee_data = []
        category_scores = {}

        if fecha_inicio:
            try:
                fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
                evaluations = evaluations.filter(evaluationDate__gte=fecha_inicio)
            except ValueError:
                return Response("Invalid value for fecha_inicio.", status=status.HTTP_400_BAD_REQUEST)

        if fecha_final:
            try:
                fecha_final = datetime.strptime(fecha_final, "%Y-%m-%d").date()
                evaluations = evaluations.filter(evaluationDate__lte=fecha_final)
            except ValueError:
                return Response("Invalid value for fecha_final.", status=status.HTTP_400_BAD_REQUEST)
        
        category_scores = defaultdict(list)
        category_averages = {}

        for evaluation in evaluations:
            responseQuery = EvaluationxSubCategory.objects.filter(evaluation=evaluation)
            dataSerialized = ContinuousEvaluationIntermediateSerializer(responseQuery, many=True)
            subcategories = dataSerialized.data
            for subcategory in subcategories:
                subcategory['evaluationDate'] = evaluation.evaluationDate
                # If this line is confusing, remember subcategory is a record of the EvaluationxSubCategory table
                category_id = subcategory['subCategory']['category']['name']
                score = subcategory['score']
                
                category_scores[category_id].append((score, evaluation.evaluationDate.year, evaluation.evaluationDate.month))  # Append the score, year, and month
                
        # Calculate average score for each category per year and month
        for category_id, scores in category_scores.items():
            category_averages[category_id] = {}
            year_month_scores = defaultdict(list)
            for score, year, month in scores:
                year_month_scores[(year, month)].append(score)
            for (year, month), scores in year_month_scores.items():
                average_score = sum(scores) / len(scores)
                category_averages[category_id][f"{year}-{month:02d}"] = average_score

        for persona in personas:
            # Get the latest evaluation for the specified evaluation type
            evaluation = Evaluation.objects.filter(evaluated=persona, evaluationType=evaluation_type_obj).order_by('-evaluationDate').first()
            
            # Calculate time since last evaluation
            time_since_last_evaluation = None
            dias = None
            if evaluation:
                time_since_last_evaluation = timezone.now().date() - evaluation.evaluationDate.date()
                dias = time_since_last_evaluation.days
            # Construct the desired employee data
            employee_data.append({
                'id': persona.id,
                'name': f"{persona.user.first_name} {persona.user.last_name}",
                'time_since_last_evaluation': dias,
                'area': {
                    'id': persona.area.id,
                    'name': persona.area.name
                },
                'position': {
                    'id': persona.position.id,
                    'name': persona.position.name
                },
                'email': persona.user.email
            })
            
        # for employee in employee_data:
        #     employee['CategoryAverages'] = category_averages

        return Response(employee_data, status=status.HTTP_200_OK)
    
class GetHistoricoDeEvaluaciones(APIView):
    def post(self, request):
        #request: nivel, fecha_inicio,fecha_final, tipoEva, employee_id
        employee_id = request.data.get("employee_id")
        tipoEva = request.data.get("evaluationType")
        nivel = request.data.get("nivel")
        fecha_inicio = request.data.get("fecha_inicio")
        fecha_final=request.data.get("fecha_final")  

        validate_employee_and_evaluation(employee_id, tipoEva)
        
        
        evaType = get_object_or_404(EvaluationType, name=tipoEva)
        query = Evaluation.objects.filter(evaluated_id=employee_id, evaluationType=evaType, isActive=True,finalScore__gte=1.0)
        
        if nivel:
            query = query.filter(finalScore=nivel)

        if fecha_inicio:
            try:
                fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
                query = query.filter(evaluationDate__gte=fecha_inicio)
            except ValueError:
                return Response("Invalid value for fecha_inicio.", status=status.HTTP_400_BAD_REQUEST)

        if fecha_final:
            try:
                fecha_final = datetime.strptime(fecha_final, "%Y-%m-%d").date()
                query = query.filter(evaluationDate__lte=fecha_final)
            except ValueError:
                return Response("Invalid value for fecha_final.", status=status.HTTP_400_BAD_REQUEST)

        evaluations = query.all()
        responseData = []

        #Continua
        if evaType.name.casefold() == "Evaluación Continua".casefold():
            category_scores = {}
            for evaluation in evaluations:
                responseQuery = EvaluationxSubCategory.objects.filter(evaluation=evaluation)
                dataSerialized = ContinuousEvaluationIntermediateSerializer(responseQuery, many=True)
                subcategories = dataSerialized.data
                for subcategory in subcategories:
                    subcategory['evaluationDate'] = evaluation.evaluationDate
                    #If this line is confusing, remember subcategory is a record of the EvaluationxSubCategory table
                    category_id = subcategory['subCategory']['category']['name']
                    score = subcategory['score']
                    
                    if category_id not in category_scores:
                        category_scores[category_id] = [score]
                    else:
                        category_scores[category_id].append(score)

                # Calculate average score for each category
                category_averages = {}
                for category_id, scores in category_scores.items():
                    category_averages[category_id] = sum(scores) / len(scores)

                responseData.append({
                    'EvaluationId': evaluation.id,
                    'CategoryName': category_id,
                    'evaluationDate' : evaluation.evaluationDate,
                    'score': evaluation.finalScore
                })
             # Calculate average score for each category across all evaluations
            category_averages = {}
            for category_id, scores in category_scores.items():
                category_averages[category_id] = sum(scores) / len(scores)
            # Update responseData with category averages
            for data in responseData:
                data['CategoryAverages'] = category_averages

        #Desempeño
        elif evaType.name.casefold() == "Evaluación de Desempeño".casefold():
            serializedData = PerformanceEvaluationSerializer(evaluations,many=True)
            responseData= serializedData.data
            
        return Response(responseData, status=status.HTTP_200_OK)

class EvaluationAPI(APIView):
    def get(self, request):
        area = Evaluation.objects.all()
        area_serializado = EvaluationSerializerWrite(area,many=True)
        return Response(area_serializado.data,status=status.HTTP_200_OK, many=True)


    def post(self, request):
        area_serializado = EvaluationSerializerWrite(data = request.data)
        
        if area_serializado.is_valid():
            area_serializado.save()
            return Response(area_serializado.data,status=status.HTTP_200_OK)
        
        return Response(area_serializado.errors,status=status.HTTP_400_BAD_REQUEST)
    
class EvaluationXSubcatAPI(APIView):
    def post(self, request):
        
        
        area_serializado = EvaluationxSubCategorySerializer(data = request.data, many=True)
        
        if area_serializado.is_valid():
            area_serializado.save()
            return Response(area_serializado.data,status=status.HTTP_200_OK)
        
        return Response(area_serializado.errors,status=status.HTTP_400_BAD_REQUEST)
    
class EvaluationLineChart(APIView):
    def post(self,request):

        supervisor_id = request.data.get("id")
        evaluation_type = request.data.get("evaluationType")
        fecha_inicio = request.data.get("fecha_inicio")
        fecha_final=request.data.get("fecha_final")
        nombre = request.data.get("nombre")

        if (evaluation_type.casefold() != "Evaluación Continua".casefold() and evaluation_type.casefold() != "Evaluación de Desempeño".casefold()):
            return Response("Invaled value for EvaluationType",status=status.HTTP_400_BAD_REQUEST)
        
        Datos = EvaluationxSubCategory.objects.filter(evaluation__evaluator__id = supervisor_id,evaluation__evaluationType__name=evaluation_type, evaluation__isActive = True,score__gte= 1.0,evaluation__relatedEvaluation = None)
        Datos = Datos.exclude(subCategory__category = None)

        if fecha_inicio:
            try:
                fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
                Datos = Datos.filter(evaluation__evaluationDate__gte=fecha_inicio)
            except ValueError:
                return Response("Invalid value for fecha_inicio.", status=status.HTTP_400_BAD_REQUEST)
        
        if fecha_final:
            try:
                fecha_final = datetime.strptime(fecha_final, "%Y-%m-%d").date()
                Datos = Datos.filter(evaluation__evaluationDate__lte=fecha_final)
            except ValueError:
                return Response("Invalid value for fecha_final.", status=status.HTTP_400_BAD_REQUEST)
        if nombre:
            Datos = Datos.filter(
                Q(evaluation__evaluated__user__first_name__icontains=nombre)|
                Q(evaluation__evaluated__user__last_name__icontains=nombre)|
                Q(evaluation__evaluated__user__username__icontains=nombre)
                )

        Data_serialiazada = EvaluationxSubCategoryRead(Datos,many=True,fields=('id','score','evaluation','subCategory'))
        
        
        data = Data_serialiazada.data
        #print(data)
        # Transform data into the desired format
        result = {}
        for item in data:
            evaluation_date = item['evaluation']['evaluationDate']
            year = evaluation_date.split('-')[0]
            month = evaluation_date.split('-')[1]

            category_name = item['subCategory']['category']['name']
            score_average = item['score']

            if year not in result:
                result[year] = {}

            if month not in result[year]:
                result[year][month] = {}

            if category_name not in result[year][month]:
                result[year][month][category_name] = []

            result[year][month][category_name].append(score_average)

        # Convert the result into the desired format
        transformed_data = []
        for year, year_data in result.items():
            year_entry = {'year': year, 'month': []}
            for month, month_data in year_data.items():
                month_entry = {'month': month, 'category_scores': []}
                for category_name, scores in month_data.items():
                    average_score = sum(scores) / len(scores)
                    category_entry = {'CategoryName': category_name, 'ScoreAverage': average_score}
                    month_entry['category_scores'].append(category_entry)
                year_entry['month'].append(month_entry)
            transformed_data.append(year_entry)

        # Convert the transformed data into JSON format
        transformed_json = json.dumps(transformed_data, indent=4)


        return Response(transformed_data,status=status.HTTP_200_OK)
        
class PlantillasAPI(APIView):
    def post(self,request):
        plantilla = request.data.get("id")
        evaluation_type = request.data.get("evaluationType")

        if (evaluation_type.casefold() != "Evaluación Continua".casefold() and evaluation_type.casefold() != "Evaluación de Desempeño".casefold()):
            return Response("Invaled value for EvaluationType",status=status.HTTP_400_BAD_REQUEST)
        
        Datos = PlantillaxSubCategoria.objects.filter(plantilla__id = plantilla,plantilla__evaluationType__name=evaluation_type,plantilla__isActive = True)
        Datos = Datos.exclude(subCategory__category = None)
        Datos_serializados = PlantillaxSubCategoryRead(Datos,many=True,fields=('id','plantilla','subCategory','nombre'))


        grouped_data = {}
        data = Datos_serializados.data
        for item in data:
            plantilla_id = item['plantilla']['id']
            plantilla_name = item['plantilla']['nombre']
            plantilla_image = item['plantilla']['image']
            evaluation_type = item['plantilla']['evaluationType']['name']
            category_id = item['subCategory']['category']['id']
            category_name = item['subCategory']['category']['name']
            subcategory_id = item['subCategory']['id']
            subcategory_name = item['subCategory']['name']
            
            if plantilla_id not in grouped_data:
                grouped_data[plantilla_id] = {
                    'id': plantilla_id,
                    'name': plantilla_name,
                    'evaluationType': evaluation_type,
                    'image': plantilla_image,
                    'Categories': []
                }
            
            category_exists = False
            for category in grouped_data[plantilla_id]['Categories']:
                if category['id'] == category_id:
                    category_exists = True
                    category['subcategories'].append({
                        'id': subcategory_id,
                        'name': subcategory_name
                    })
                    break
            
            if not category_exists:
                grouped_data[plantilla_id]['Categories'].append({
                    'id': category_id,
                    'name': category_name,
                    'subcategories': [{
                        'id': subcategory_id,
                        'name': subcategory_name
                    }]
                })

        grouped_data = list(grouped_data.values())

        # Datos_noCategorias = PlantillaxSubCategoria.objects.filter(plantilla__id=plantilla,plantilla__evaluationType__name=evaluation_type)
        # Datos_noCategorias_Serializados = PlantillaxSubCategoryRead(Datos_noCategorias,many=True,fields = ('id','subCategory'))
        # data = Datos_noCategorias_Serializados.data
        # subcategories_list = [item['subCategory']['id'] for item in data]
        


        # subcategories_not_in_plantilla = SubCategory.objects.exclude(id__in = subcategories_list).filter(category__id = data[0]['subCategory']['category']['id'])

        # subcategories_not_in_plantilla_serializada = SubCategorySerializerRead(subcategories_not_in_plantilla,many=True)




        # return Response(subcategories_not_in_plantilla_serializada.data,status=status.HTTP_200_OK)

        return Response(grouped_data,status=status.HTTP_200_OK)

        


class PlantillasEditarVistaAPI(APIView):
    def post(self, request):
        plantilla_id = request.data.get("id")
        evaluation_type = request.data.get("evaluationType")

        if not self.is_valid_evaluation_type(evaluation_type):
            return Response("Invalid value for EvaluationType", status=status.HTTP_400_BAD_REQUEST)

        template = self.get_template(plantilla_id)
        if not template:
            return Response("Template not found", status=status.HTTP_404_NOT_FOUND)

        categories = self.get_categories(template)
        subcategories_not_in_template = self.get_subcategories_not_in_template(template, evaluation_type)

        response_data = self.generate_response_data(template, categories, subcategories_not_in_template)
        return Response(response_data, status=status.HTTP_200_OK)

    def is_valid_evaluation_type(self, evaluation_type):
        valid_types = ["Evaluación Continua", "Evaluación de Desempeño"]
        return evaluation_type and evaluation_type.casefold() in [t.casefold() for t in valid_types]

    def get_template(self, template_id):
        try:
            return Plantilla.objects.get(id=template_id, isActive=True)
        except Plantilla.DoesNotExist:
            return None

    def get_categories(self, template):
        subcategories = PlantillaxSubCategoria.objects.filter(
            plantilla=template,
            plantilla__isActive=True,
            isActive=True
        ).select_related('subCategory__category')

        categories = {}
        for subcategory in subcategories:
            category = subcategory.subCategory.category
            if category not in categories:
                categories[category] = []

            categories[category].append(subcategory.subCategory)

        return categories

    def get_subcategories_not_in_template(self, template, evaluation_type):
        subcategories_in_template = PlantillaxSubCategoria.objects.filter(
            plantilla=template,
            plantilla__evaluationType__name=evaluation_type,
            isActive=True
        ).values_list('subCategory_id', flat=True)

        return SubCategory.objects.exclude(id__in=subcategories_in_template).filter(category__evaluationType__name=evaluation_type)

    def generate_response_data(self, template, categories, subcategories_not_in_template):
        evaluation_type = template.evaluationType.name  # Get the evaluation type from the template

        response_data = {
            'plantilla-id': template.id,
            'plantilla-nombre': template.nombre,
            'plantilla-image': template.image,
            'Categories': []
        }

        for category, subcategories in categories.items():
            if category.evaluationType.name == evaluation_type:  # Filter categories based on evaluation type
                category_data = {
                    'id': category.id,
                    'name': category.name,
                    'Category-active': category.isActive,
                    'subcategory': [
                        {
                            'id': subcategory.id,
                            'subcategory-isActive': subcategory.isActive,
                            'nombre': subcategory.name
                        }
                        for subcategory in subcategories
                    ]
                }

                response_data['Categories'].append(category_data)

        for subcategory in subcategories_not_in_template:
            category_data = next(
                (category for category in response_data['Categories'] if (category['id'] == subcategory.category.id )),
                None
            )

            if category_data is None:
                category_data = {
                    'id': subcategory.category.id,
                    'name': subcategory.category.name,
                    'Category-active': False,
                    'subcategory': []
                }
                response_data['Categories'].append(category_data)

            subcategory_data = {
                'id': subcategory.id,
                'subcategory-isActive': False,
                'nombre': subcategory.name
            }
            category_data['subcategory'].append(subcategory_data)

        return response_data



        
class VistaCategoriasSubCategorias(APIView):
    def post(self,request):
        #plantilla = request.data.get("id")
        #evaluation_type = request.data.get("evaluationType")

        #if (evaluation_type.casefold() != "Evaluación Continua".casefold() and evaluation_type.casefold() != "Evaluación de Desempeño".casefold()):
        #    return Response("Invaled value for EvaluationType",status=status.HTTP_400_BAD_REQUEST)
        
        Datos = SubCategory.objects.filter(isActive = True)
        Datos = Datos.exclude(category = None)
        Datos_serializados = SubCategorySerializerRead(Datos,many=True,fields=('id','name','category'))

        grouped_data = {}
        json_data = Datos_serializados.data
        for item in json_data:
            category_id = item['category']['id']
            category_name = item['category']['name']
            subcategory_id = item['id']
            subcategory_name = item['name']
            
            if category_id not in grouped_data:
                grouped_data[category_id] = {
                    'category-id': category_id,
                    'category-name': category_name,
                    'subcategory': []
                }
            
            grouped_data[category_id]['subcategory'].append({
                'id': subcategory_id,
                'name': subcategory_name
            })

        grouped_data = list(grouped_data.values())

        return Response(grouped_data,status=status.HTTP_200_OK)       
    
class EvaluationLineChartPersona(APIView):
    def post(self,request):

        persona_id = request.data.get("id")
        evaluation_type = request.data.get("evaluationType")
        fecha_inicio = request.data.get("fecha_inicio")
        fecha_final=request.data.get("fecha_final")


        if (evaluation_type.casefold() != "Evaluación Continua".casefold() and evaluation_type.casefold() != "Evaluación de Desempeño".casefold()):
            return Response("Invaled value for EvaluationType",status=status.HTTP_400_BAD_REQUEST)
        
        Datos = EvaluationxSubCategory.objects.filter(evaluation__evaluated__id = persona_id,evaluation__evaluationType__name=evaluation_type, evaluation__isActive = True,score__gte= 1.0,evaluation__relatedEvaluation = None)
        Datos = Datos.exclude(subCategory__category = None)
        if fecha_inicio:
            try:
                fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
                Datos = Datos.filter(evaluation__evaluationDate__gte=fecha_inicio)
            except ValueError:
                return Response("Invalid value for fecha_inicio.", status=status.HTTP_400_BAD_REQUEST)
        
        if fecha_final:
            try:
                fecha_final = datetime.strptime(fecha_final, "%Y-%m-%d").date()
                Datos = Datos.filter(evaluation__evaluationDate__lte=fecha_final)
            except ValueError:
                return Response("Invalid value for fecha_final.", status=status.HTTP_400_BAD_REQUEST)
        
        Data_serialiazada = EvaluationxSubCategoryRead(Datos,many=True,fields=('id','score','evaluation','subCategory'))
        
        
        data = Data_serialiazada.data
        
        # Transform data into the desired format
        result = {}
        for item in data:
            evaluation_date = item['evaluation']['evaluationDate']
            year = evaluation_date.split('-')[0]
            month = evaluation_date.split('-')[1]
            if(item['subCategory']['category'] is None):
                continue
            category_name = item['subCategory']['category']['name']
            score_average = item['score']

            if year not in result:
                result[year] = {}

            if month not in result[year]:
                result[year][month] = {}

            if category_name not in result[year][month]:
                result[year][month][category_name] = []

            result[year][month][category_name].append(score_average)

        # Convert the result into the desired format
        transformed_data = []
        for year, year_data in result.items():
            year_entry = {'year': year, 'month': []}
            for month, month_data in year_data.items():
                month_entry = {'month': month, 'category_scores': []}
                for category_name, scores in month_data.items():
                    average_score = sum(scores) / len(scores)
                    category_entry = {'CategoryName': category_name, 'ScoreAverage': average_score}
                    month_entry['category_scores'].append(category_entry)
                year_entry['month'].append(month_entry)
            transformed_data.append(year_entry)

        # Convert the transformed data into JSON format
        transformed_json = json.dumps(transformed_data, indent=4)


        return Response(transformed_data,status=status.HTTP_200_OK)

class PlantillasEditarAPI(APIView):
    def post(self,request):
        plantilla = request.data.get("plantilla-id")
        nuevanombre = request.data.get("plantilla-nombre")
        Plantilla_basica = Plantilla.objects.get(pk=plantilla)
        image_url = request.data.get("image")
        
        Plantilla_basica.nombre = nuevanombre
        if image_url:
            try:
                URLValidator()(image_url)
                Plantilla_basica.image = image_url
            except ValidationError:
                return Response("Invalid image URL", status=status.HTTP_400_BAD_REQUEST)

        Plantilla_basica.save()

        Datos = PlantillaxSubCategoria.objects.filter(plantilla__id = plantilla,plantilla__isActive = True,isActive=True)
        Datos_serializados = PlantillaxSubCategoryRead(Datos,many=True,fields=('id','plantilla','subCategory','nombre'))
        
        Existe = False
        for item in request.data.get("Categories"):
            for subcat in item["subcategory"]:
                    Existe = False
                    
                    
                    for DataExistente in Datos_serializados.data:
                        
                        if(DataExistente['subCategory']['id'] == subcat["id"]):
                            if(subcat["subcategory-isActive"] == True):
                                print("Sí existe categoría")
                            elif(subcat["subcategory-isActive"] == False):
                                PlantillaxSubCategoria.objects.filter(id=DataExistente['id']).update(isActive = False)
                                
                            Existe = True
                            
                            break;
                    if(Existe == False and subcat["subcategory-isActive"] == True):
                        PlantillaxSubCategoria(
                            nombre = subcat["nombre"],
                            plantilla = Plantilla.objects.get(id= request.data.get("plantilla-id")),
                            subCategory = SubCategory.objects.get(id= subcat["id"])
                        ).save()
                        
            

        return Response("Se ha actualizado correctamente",status=status.HTTP_200_OK)

class PlantillasCrearAPI(APIView):
    def post(self,request):
        
        evaltype = request.data.get("evaluationType")
        if (evaltype.casefold() != "Evaluación Continua".casefold() and evaltype.casefold() != "Evaluación de Desempeño".casefold()):
            return Response("Invaled value for EvaluationType",status=status.HTTP_400_BAD_REQUEST)
        
        obj_evalty =   EvaluationType.objects.get(name= evaltype)
        plantilla_creada = Plantilla(nombre = request.data.get('nombre'),evaluationType = obj_evalty)

        image_url = request.data.get("image")
        if image_url:
            try:
                URLValidator()(image_url)
                plantilla_creada.image = image_url
            except ValidationError:
                return Response("Invalid image URL", status=status.HTTP_400_BAD_REQUEST)
        
        plantilla_creada.save()

        if(plantilla_creada is None):
            return Response("No se ha creado correctamente el objeto plantilla",status=status.HTTP_400_BAD_REQUEST)

        for item in request.data.get("subCategories"):
            subcategoriacrear = PlantillaxSubCategoria(nombre = item["nombre"],plantilla=plantilla_creada,subCategory = SubCategory.objects.get(id = item["id"]))
            subcategoriacrear.save()
            if(subcategoriacrear is None):
                return Response("No se ha creado correctamente el objeto subcategoria",status=status.HTTP_400_BAD_REQUEST)
        
        return Response("Se creó correctamente la plantilla ",status=status.HTTP_200_OK)
    
    def delete(self,request):
        idPlantilla = request.data.get("idPlantilla")
        if( idPlantilla is None):
            return Response("No se ha dado el idPlantilla",status=status.HTTP_400_BAD_REQUEST)
            
        try:
            obj_plantilla = Plantilla.objects.get(id=idPlantilla)
            obj_plantilla.isActive = False
            obj_plantilla.save()
        except Plantilla.DoesNotExist:
            return Response("La plantilla no existe", status=status.HTTP_400_BAD_REQUEST)

    
        obj_PlantillaxSubCategoria = PlantillaxSubCategoria.objects.filter(plantilla=obj_plantilla)

        if obj_PlantillaxSubCategoria.exists():
            obj_PlantillaxSubCategoria.update(isActive=False)
                

        
        return Response("Se ha eliminado correctamente la plantilla",status=status.HTTP_200_OK)
    

class PlantillaPorTipo(APIView):
    def post(self,request):
        Data = Plantilla.objects.filter(isActive = True)
        Data_serialazada = PlantillaSerializerRead(Data,many=True,fields = ('id','nombre','evaluationType', 'image'))


        result = {}
        data = Data_serialazada.data
        for item in data:
            evaluation_type = item['evaluationType']['name']
            plantilla_id = item['id']
            plantilla_nombre = item['nombre']
            plantilla_image = item['image']
            
            if evaluation_type not in result:
                result[evaluation_type] = []
            
            result[evaluation_type].append({"plantilla-id": plantilla_id, "plantilla-nombre": plantilla_nombre, "plantilla_image": plantilla_image})


        return Response(result,status=status.HTTP_200_OK)
    
class GetAreas(APIView):
    def get(self, request):
        areas = Area.objects.values('id', 'name')
        return Response(areas)

class GetCategoriasContinuas(APIView):
    def get(self, request):
        evaluation_type = EvaluationType.objects.get(name='Evaluación Continua')
        categorias = Category.objects.values('id', 'name')
        return Response(categorias)

class GetCategoriasDesempenio(APIView):
    def get(self, request):
        evaluation_type = EvaluationType.objects.get(name='Evaluación de Desempeño')
        categorias = Category.objects.values('id', 'name')
        return Response(categorias)
    
class EvaluationLineChartReporte(APIView):
    def post(self,request):

        area_id = request.data.get("area-id")
        category_id = request.data.get("category-id")
        evaluation_type = request.data.get("evaluationType")
        fecha_inicio = request.data.get("fecha_inicio")
        fecha_final=request.data.get("fecha_final")



        if (evaluation_type.casefold() != "Evaluación Continua".casefold() and evaluation_type.casefold() != "Evaluación de Desempeño".casefold()):
            return Response("Invaled value for EvaluationType",status=status.HTTP_400_BAD_REQUEST)
        
        Datos = EvaluationxSubCategory.objects.filter(isActive = True,evaluation__evaluationType__name=evaluation_type,evaluation__isActive = True,score__gte= 1.0,evaluation__relatedEvaluation = None)
        Datos = Datos.exclude(subCategory__category = None)
        Datos = Datos.objects.filter(  subCategory__category__id = category_id)

        if(area_id is not None):
            Datos = Datos.filter(evaluation__area__id = area_id)
        

        if fecha_inicio:
            try:
                fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
                Datos = Datos.filter(evaluation__evaluationDate__gte=fecha_inicio)
            except ValueError:
                return Response("Invalid value for fecha_inicio.", status=status.HTTP_400_BAD_REQUEST)
        
        if fecha_final:
            try:
                fecha_final = datetime.strptime(fecha_final, "%Y-%m-%d").date()
                Datos = Datos.filter(evaluation__evaluationDate__lte=fecha_final)
            except ValueError:
                return Response("Invalid value for fecha_final.", status=status.HTTP_400_BAD_REQUEST)
        
        Data_serialiazada = EvaluationxSubCategoryRead(Datos,many=True,fields=('id','score','evaluation','subCategory'))
        
        
        data = Data_serialiazada.data
        
        # Transform data into the desired format
        result = {}
        for item in data:
            evaluation_date = item['evaluation']['evaluationDate']
            year = evaluation_date.split('-')[0]
            month = evaluation_date.split('-')[1]

            if(item['subCategory']['category'] is None):
                continue

            category_name = item['subCategory']['category']['name']
            score_average = item['score']

            if year not in result:
                result[year] = {}

            if month not in result[year]:
                result[year][month] = {}

            if category_name not in result[year][month]:
                result[year][month][category_name] = []

            result[year][month][category_name].append(score_average)

        # Convert the result into the desired format
        transformed_data = []
        for year, year_data in result.items():
            year_entry = {'year': year, 'month': []}
            for month, month_data in year_data.items():
                month_entry = {'month': month, 'category_scores': []}
                for category_name, scores in month_data.items():
                    average_score = sum(scores) / len(scores)
                    category_entry = {'CategoryName': category_name, 'ScoreAverage': average_score}
                    month_entry['category_scores'].append(category_entry)
                year_entry['month'].append(month_entry)
            transformed_data.append(year_entry)

        # Convert the transformed data into JSON format
        transformed_json = json.dumps(transformed_data, indent=4)


        return Response(transformed_data,status=status.HTTP_200_OK)
    
class ListAllCategories(APIView):
    def post(self,request):
        Categorias = Category.objects.filter(isActive = True)
        Categorias_serializada = CategorySerializerRead2(Categorias, many=True,fields=('id','name','code','description'))
        return Response(Categorias_serializada.data, status=status.HTTP_200_OK)



class RegistrarEvaluacionDesempen(APIView):
    def post(self,request):

        evaluador = request.data.get("evaluatorId")
        evaluado = request.data.get("evaluatedId")
        proyectoOb = request.data.get("associatedProject")
        terminado = request.data.get("isFinished")
        evaltype = request.data.get("evaluationType")


        if (evaltype.casefold() != "Evaluación Continua".casefold() and evaltype.casefold() != "Evaluación de Desempeño".casefold()):
            return Response("Invaled value for EvaluationType",status=status.HTTP_400_BAD_REQUEST)

        obj_evalty =   EvaluationType.objects.get(name= evaltype)
        obj_evaluado = Employee.objects.get(id=evaluado)
        obj_evaluador = Employee.objects.get(id=evaluador)
        obj_area = Area.objects.get(id=obj_evaluador.area.id)
        obj_position = Position.objects.get(id=obj_evaluado.position.id)

        scores=[]
        for item in request.data.get("categories"):
            for item2 in item["subcategories"]:
                scores.append(item2["score"])

        finalPuntaje = sum(scores)/len(scores)
        evaluacion_creada = Evaluation(evaluationDate = datetime.now(),finalScore = finalPuntaje,proyecto =proyectoOb ,evaluator = obj_evaluador, evaluated = obj_evaluado,evaluationType = obj_evalty,area = obj_area, position=obj_position,isFinished = terminado,hasComment=request.data.get("hasComment"))

        evaluacion_creada.save()

        if(evaluacion_creada is None):
            return Response("No se ha creado correctamente el objeto evaluacion",status=status.HTTP_400_BAD_REQUEST)
        
        if(obj_evalty.id==2):
            evaluacion_creada_related = Evaluation(evaluationDate = datetime.now(),finalScore = 0,proyecto =proyectoOb ,evaluator = obj_evaluado, evaluated = obj_evaluado,evaluationType = obj_evalty,area = obj_area, position=obj_position, relatedEvaluation = evaluacion_creada,isFinished=False,hasComment=request.data.get("hasComment"))  
            evaluacion_creada_related.save()
            if(evaluacion_creada_related is None):
                return Response("No se ha creado correctamente el objeto evaluacion relacionada",status=status.HTTP_400_BAD_REQUEST)
            employee_user = getattr(obj_evaluado, 'user', None)
            user_email  = getattr(employee_user, 'email', None)
            name = "{} {}".format(getattr(employee_user, 'first_name', ''), getattr(employee_user, 'last_name', ''))
            encoded_name = urllib.parse.quote(name)
            url = "{}/skill-management/auto-evaluation?id={}&name={}&evaluationId={}".format(
                settings.CLIENT_URL,
                obj_evaluado.id,
                encoded_name,
                evaluacion_creada_related.id
            )
            send_mail(
            "Su autoevaluación está lista",
            "Su autoevaluación está lista para ser llenada. Por favor llenela ingresando a {}".format(url),
            settings.EMAIL_HOST_USER,
            [user_email],
            fail_silently=False,
        )


        for item in request.data.get("categories"):
            for item2 in item["subcategories"]:
                
                subcategoriacrear_evaluacion = EvaluationxSubCategory(score=item2["score"],comment=item2["comment"],subCategory = SubCategory.objects.get(id = item2["id"]),evaluation=evaluacion_creada)
                subcategoriacrear_evaluacion.save()
                if(subcategoriacrear_evaluacion is None):
                    return Response("No se ha creado correctamente el objeto subcategoria",status=status.HTTP_400_BAD_REQUEST)
                
                if(obj_evalty.id==2):
                    subcat = SubCategory.objects.get(id = item2["id"])
                    subcategoriacrear_evaluacion_related= EvaluationxSubCategory(subCategory = subcat,evaluation=evaluacion_creada_related,score=0)
                    subcategoriacrear_evaluacion_related.save()
                    if(subcategoriacrear_evaluacion_related is None):
                        return Response("No se ha creado correctamente el objeto subcategoria related ",status=status.HTTP_400_BAD_REQUEST)

        return Response("Se creó correctamente las evaluaciones ",status=status.HTTP_200_OK)
    
    def put(self,request):
        evaluationId = request.data.get("evaluationId")


        try:
            obj_evaluation = Evaluation.objects.get(id=evaluationId)
        except Evaluation.DoesNotExist:
            return Response("No existe la evaluación de desempeño",status=status.HTTP_400_BAD_REQUEST)
        
        
    
        scores=[]
        for item in request.data.get("categories"):
            for item2 in item["subcategories"]:
                scores.append(item2["score"])

        finalPuntaje = sum(scores)/len(scores)
        obj_evaluation.finalScore = finalPuntaje
        obj_evaluation.evaluationDate = datetime.now()
        


        for item in request.data.get("categories"):
            for item2 in item["subcategories"]:
                
                subcategoriaactualizar_evaluacion = EvaluationxSubCategory.objects.get(subCategory__id =  item2["id"],evaluation__id=evaluationId)

                if(subcategoriaactualizar_evaluacion is None):
                    return Response("No se ha ubicado la subcategoria para esta evaluacion",status=status.HTTP_400_BAD_REQUEST)
            
                subcategoriaactualizar_evaluacion.score = item2["score"]
                subcategoriaactualizar_evaluacion.save()

        obj_evaluation.isFinished = True

        obj_evaluation.save()


        print(obj_evaluation.relatedEvaluation.id)
        Evaluation.objects.filter(id=obj_evaluation.relatedEvaluation.id).update(isFinished=True)

 

        
        
                
                
        return Response("Se envió correcatamente la evaluación de desempeño",status=status.HTTP_200_OK)
    
class ActualizarCategorias(APIView):
    def post(self, request):

        idCategoria = request.data.get("idCategoria")
        nameCategoria = request.data.get("nameCategoria")

        if(idCategoria is None):
            return Response("No se ha especificado el idCategoria",status=status.HTTP_400_BAD_REQUEST)
        if(nameCategoria is None):
            return Response("No se ha especificado el nameCategoria",status=status.HTTP_400_BAD_REQUEST)
        
        try:
            obj_categoria = Category.objects.get(id=idCategoria)
        except Category.DoesNotExist:
            return Response("La categoria no existe", status=status.HTTP_400_BAD_REQUEST)
        
        obj_categorias = Category.objects.filter(name=obj_categoria.name)

        if obj_categorias.exists():
            obj_categorias.update(name=nameCategoria)
        

        obj_categoria_serializado = CategorySerializerRead(obj_categorias,fields=('id','name'),many=True)

    
        
        return Response("Se ha actualizado correctamente la categoria",status=status.HTTP_200_OK)
    
    def delete(self, request):
        idCategoria = request.data.get("idCategoria")
        idSubCategoria = request.data.get("idSubCategoria")
        peruTz = pytz.timezone('America/Lima')
        now=datetime.now(peruTz)

        if(idCategoria is None):
            return Response("No se ha especificado el idCategoria",status=status.HTTP_400_BAD_REQUEST)
        if(idSubCategoria is None):
            return Response("No se ha especificado el idSubCategoria",status=status.HTTP_400_BAD_REQUEST)
        
        try:
            obj_subcategoria = SubCategory.objects.get(id=idSubCategoria,category__id=idCategoria)
            
        except SubCategory.DoesNotExist:
            return Response("La subCategory no existe", status=status.HTTP_400_BAD_REQUEST)
        
        obj_categorias = SubCategory.objects.filter(name=obj_subcategoria.name)

        if obj_categorias.exists():
            obj_categorias.update(category = None, modifiedDate= now )
        

        

    
        
        return Response("Se ha eliminado la subcategoria correctamente de la categoria",status=status.HTTP_200_OK)
    
class EvaluationLineChartReporte2(APIView):
    def post(self,request):

        area_id = request.data.get("area-id")
        category_id = request.data.get("category-id")
        evaluation_type = request.data.get("evaluationType")
        fecha_inicio = request.data.get("fecha_inicio")
        fecha_final=request.data.get("fecha_fin")

        if (evaluation_type.casefold() != "Evaluación Continua".casefold() and evaluation_type.casefold() != "Evaluación de Desempeño".casefold()):
            return Response("Invaled value for EvaluationType",status=status.HTTP_400_BAD_REQUEST)
        
        Datos = EvaluationxSubCategory.objects.filter(evaluation__evaluationType__name=evaluation_type,evaluation__isActive = True,score__gte= 1.0,evaluation__relatedEvaluation = None)
        Datos = Datos.exclude(subCategory__category = None)

        if fecha_inicio:
            try:
                fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
                Datos = Datos.filter(evaluation__evaluationDate__gte=fecha_inicio)
            except ValueError:
                return Response("Invalid value for fecha_inicio.", status=status.HTTP_400_BAD_REQUEST)
        
        if fecha_final:
            try:
                fecha_final = datetime.strptime(fecha_final, "%Y-%m-%d").date()
                Datos = Datos.filter(evaluation__evaluationDate__lte=fecha_final)
            except ValueError:
                return Response("Invalid value for fecha_final.", status=status.HTTP_400_BAD_REQUEST)

        if(category_id is not None):
            Datos = Datos.filter(subCategory__category__id= category_id)
            
        if(area_id is not None):
            Datos = Datos.filter(evaluation__area__id = area_id)

        Data_serialiazada = EvaluationxSubCategoryRead2(Datos,many=True,fields=('id','score','evaluation','subCategory'))
        
        
        data = Data_serialiazada.data

        json1 = Data_serialiazada.data
        json2=[]
        json_data=json1
        result = []



        if(category_id is not None and area_id is None):
            result = []
            for data in json_data:
                area_name = data["evaluation"]["area"]["name"]
                evaluation_date = datetime.fromisoformat(data["evaluation"]["evaluationDate"])
                year = str(evaluation_date.year)
                month = str(evaluation_date.month).zfill(2)

                # Check if the area and year already exist in the result dictionary
                area_exists = False
                for area_data in result:
                    if area_data["Area"] == area_name and area_data["Year"] == year:
                        area_exists = True
                        month_exists = False

                        # Check if the month already exists in the area
                        for month_data in area_data["Month"]:
                            if month_data["month"] == month:
                                month_exists = True

                                # Check if the subcategory already exists in the month
                                subcategory_exists = False
                                for subcategory_score in month_data["subCategory_scores"]:
                                    if subcategory_score["SubCategory"] == data["subCategory"]["name"]:
                                        subcategory_exists = True
                                        subcategory_score["ScoreAverage"] = (
                                            subcategory_score["ScoreAverage"]
                                            + data["score"]
                                        ) 
                                        subcategory_score["Quantity"] += 1
                                        break

                                # If the subcategory doesn't exist, add it to the month
                                if not subcategory_exists:
                                    month_data["subCategory_scores"].append(
                                        {
                                            "SubCategory": data["subCategory"]["name"],
                                            "ScoreAverage": data["score"],
                                            "Quantity":1
                                        }
                                    )
                                break

                        # If the month doesn't exist, add it to the area
                        if not month_exists:
                            area_data["Month"].append(
                                {
                                    "month": month,
                                    "subCategory_scores": [
                                        {
                                            "SubCategory": data["subCategory"]["name"],
                                            "ScoreAverage": data["score"],
                                            "Quantity":1
                                        }
                                    ],
                                }
                            )
                        break

                # If the area doesn't exist, create a new entry
                if not area_exists:
                    result.append(
                        {
                            "Area": area_name,
                            "Year": year,
                            "Month": [
                                {
                                    "month": month,
                                    "subCategory_scores": [
                                        {
                                            "SubCategory": data["subCategory"]["name"],
                                            "ScoreAverage": data["score"],
                                            "Quantity":1
                                        }
                                    ],
                                }
                            ],
                        }
                    )


            for item in result:
                for month in item["Month"]:
                    for subcat in month["subCategory_scores"]:
                        subcat["ScoreAverage"] /= subcat["Quantity"]
                        del subcat["Quantity"]    
            return Response(result,status=status.HTTP_200_OK)
        elif(category_id is None and area_id is not None):    
            for data in json_data:
                category_name = data["subCategory"]["category"]["name"]
                evaluation_date = datetime.fromisoformat(data["evaluation"]["evaluationDate"])
                year = str(evaluation_date.year)
                month = str(evaluation_date.month).zfill(2)

                # Check if the category and year already exist in the result dictionary
                category_exists = False
                for category_data in result:
                    if category_data["Category"] == category_name and category_data["Year"] == year:
                        category_exists = True
                        month_exists = False

                        # Check if the month already exists in the category
                        for month_data in category_data["Month"]:
                            if month_data["month"] == month:
                                month_exists = True

                                # Check if the subcategory already exists in the month
                                subcategory_exists = False
                                for subcategory_score in month_data["subCategory_scores"]:
                                    if subcategory_score["SubCategory"] == data["subCategory"]["name"]:
                                        subcategory_exists = True
                                        subcategory_score["ScoreAverage"] = (
                                            subcategory_score["ScoreAverage"]
                                            + data["score"]
                                        )
                                        subcategory_score["Quantity"] += 1
                                        break

                                # If the subcategory doesn't exist, add it to the month
                                if not subcategory_exists:
                                    month_data["subCategory_scores"].append(
                                        {
                                            "SubCategory": data["subCategory"]["name"],
                                            "ScoreAverage": data["score"],
                                            "Quantity":1
                                        }
                                    )
                                break

                        # If the month doesn't exist, add it to the category
                        if not month_exists:
                            category_data["Month"].append(
                                {
                                    "month": month,
                                    "subCategory_scores": [
                                        {
                                            "SubCategory": data["subCategory"]["name"],
                                            "ScoreAverage": data["score"],
                                            "Quantity":1
                                        }
                                    ],
                                }
                            )
                        break

                # If the category doesn't exist, create a new entry
                if not category_exists:
                    result.append(
                        {
                            "Category": category_name,
                            "Year": year,
                            "Month": [
                                {
                                    "month": month,
                                    "subCategory_scores": [
                                        {
                                            "SubCategory": data["subCategory"]["name"],
                                            "ScoreAverage": data["score"],
                                            "Quantity":1
                                        }
                                    ],
                                }
                            ],
                        }
                    )
            for item in result:
                for month in item["Month"]:
                    for subcat in month["subCategory_scores"]:
                        subcat["ScoreAverage"] /= subcat["Quantity"]
                        del subcat["Quantity"]
                        

            return Response(result,status=status.HTTP_200_OK)
        elif(category_id is not None and area_id is not None):
            for data in json_data:
                evaluation_date = datetime.fromisoformat(data["evaluation"]["evaluationDate"])
                year = str(evaluation_date.year)
                month = str(evaluation_date.month).zfill(2)

                # Check if the year already exists in the result dictionary
                year_exists = False
                for year_data in result:
                    if year_data["Year"] == year:
                        year_exists = True
                        month_exists = False

                        # Check if the month already exists in the year
                        for month_data in year_data["Month"]:
                            if month_data["month"] == month:
                                month_exists = True

                                # Check if the subcategory already exists in the month
                                subcategory_exists = False
                                for subcategory_score in month_data["subCategory_scores"]:
                                    if subcategory_score["SubCategory"] == data["subCategory"]["name"]:
                                        subcategory_exists = True
                                        subcategory_score["ScoreAverage"] = (
                                            subcategory_score["ScoreAverage"]
                                            + data["score"]
                                        ) 
                                        subcategory_score["Quantity"] += 1
                                        break

                                # If the subcategory doesn't exist, add it to the month
                                if not subcategory_exists:
                                    month_data["subCategory_scores"].append(
                                        {
                                            "SubCategory": data["subCategory"]["name"],
                                            "ScoreAverage": data["score"],
                                            "Quantity":1
                                        }
                                    )
                                break

                        # If the month doesn't exist, add it to the year
                        if not month_exists:
                            year_data["Month"].append(
                                {
                                    "month": month,
                                    "subCategory_scores": [
                                        {
                                            "SubCategory": data["subCategory"]["name"],
                                            "ScoreAverage": data["score"],
                                            "Quantity":1
                                        }
                                    ],
                                }
                            )
                        break

                # If the year doesn't exist, create a new entry
                if not year_exists:
                    result.append(
                        {
                            "Year": year,
                            "Month": [
                                {
                                    "month": month,
                                    "subCategory_scores": [
                                        {
                                            "SubCategory": data["subCategory"]["name"],
                                            "ScoreAverage": data["score"],
                                            "Quantity":1
                                        }
                                    ],
                                }
                            ],
                        }
                    )
            for item in result:

                for month in item["Month"]:
                    for subcat in month["subCategory_scores"]:
                        subcat["ScoreAverage"] /= subcat["Quantity"]
                        del subcat["Quantity"]
            return Response(result,status=status.HTTP_200_OK)
        else:
            return Response("No se ha brindado correctamente los parametros",status=status.HTTP_400_BAD_REQUEST)
