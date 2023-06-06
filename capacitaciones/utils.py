import requests
import openai
import json
import os

from capacitaciones.models import CursoUdemy

''' Udemy API '''


def get_udemy_courses(course):
    url = "https://www.udemy.com/api-2.0/courses/?search={search}&ordering=relevance&page=1&page_size={page_size}".format(
        search=course, page_size=20)

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Authorization": "Basic NWtLRjJhREhqeEFyMGxUY2cyY05WR0QzSjEweHRKQkxiQU5hY3RDTDpFQWJoTXc5c1NOVjJqZ2U4WXU2NlU2Q1VUVXFqd0hpMWtWdUd5R1ZBZmpabHp3bjRIUmpkZVFxN08xWXFGODgwRjRzclU4YkpFekl6dE1ac25KUjJWVkIzT3U2U3BtVWpJRWJzVTdGdWNhaXhPSkw5OXRxSWNVMzA5cFlUeEhCWA==",
        "Content-Type": "application/json"
    }

    request = requests.get(url=url, headers=headers)
    list_courses = request.json()['results']

    return list_courses


''' Udemy API '''


def get_detail_udemy_course(course_id):
    url = "https://www.udemy.com/api-2.0/courses/{course_id}/public-curriculum-items/?page=1&page_size={page_size}".format(
        course_id=course_id, page_size=1000)

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Authorization": "Basic NWtLRjJhREhqeEFyMGxUY2cyY05WR0QzSjEweHRKQkxiQU5hY3RDTDpFQWJoTXc5c1NOVjJqZ2U4WXU2NlU2Q1VUVXFqd0hpMWtWdUd5R1ZBZmpabHp3bjRIUmpkZVFxN08xWXFGODgwRjRzclU4YkpFekl6dE1ac25KUjJWVkIzT3U2U3BtVWpJRWJzVTdGdWNhaXhPSkw5OXRxSWNVMzA5cFlUeEhCWA==",
        "Content-Type": "application/json"
    }

    request = requests.get(url=url, headers=headers)
    detail_course = request.json()['results']

    return detail_course


def clean_course_detail(course):
    list_keys = ['is_paid', 'price', 'price_detail', 'price_serve_tracking_id', 'is_practice_test_course',
                 'tracking_id', 'predictive_score', 'relevancy_score', 'input_features', 'lecture_search_result',
                 'curriculum_lectures', 'order_in_results', 'curriculum_items', 'instructor_name']

    for key in list_keys:
        del course[key]

    return course


def get_gpt_form(curso):
    openai.api_key = os.getenv('OPEN_API_KEY')

    model = "gpt-3.5-turbo"
    max_tokens = 2048
    temperature = 0.5
    n = 1
    stop = None
    prompt = "La respuesta debe ser estructurada como un arreglo de objetos JSON del tipo Array<\{question:string," \
             "options:Array<string>,answer:1|2|3|4\}>\nGenera 10 preguntas de opción múltiple. Cada pregunta debe " \
             "tener 4 opciones de respuesta y la respuesta debe ser objetiva, precisa, breve. La dificultad de las " \
             "preguntas debe ser alta. No incluyas preguntas de cálculos numéricos. Las preguntas del cuestionario se " \
             "deben construir considerando el temario del curso '" + curso + "' de Udemy "

    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_tokens=max_tokens,
        temperature=temperature,
        n=n,
        stop=stop,
    )

    result_data = json.dumps(response)
    result_json = json.loads(result_data)

    return result_json['choices'][0]['message']['content']


def GenerateUdemyEvaluation(id_course):

    course_detail = CursoUdemy.objects.filter(pk=id_course).values('course_udemy_detail').first()
    course_name = course_detail['course_udemy_detail']['title'] + ' ' + course_detail['course_udemy_detail']['headline']

    try:
        udemy_form = get_gpt_form(course_name)
    except Exception as e:
        CursoUdemy.objects.filter(pk=id_course).update(estado='2')
        return False

    CursoUdemy.objects.filter(pk=id_course).update(preguntas=transform_gpt_quiz_output(udemy_form), estado='1')
    return True


def transform_gpt_quiz_output(gtp_output):

    new_data = []
    for i, question in enumerate(gtp_output, start=1):
        new_question = {
            "id_pregunta": i,
            "pregunta": question["question"],
            "opciones": []
        }
        for j, option in enumerate(question["options"], start=1):
            new_option = {
                "id_opcion": j,
                "opcion": option,
                "es_correcta": j == question["answer"]
            }
            new_question["opciones"].append(new_option)
        new_data.append(new_question)

    return new_data
