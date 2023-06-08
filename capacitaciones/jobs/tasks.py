import json
import os
import threading

from capacitaciones.utils import GenerateUdemyEvaluation
from datetime import datetime

file_lock = threading.Lock()


def process_and_manage_course(course):
    success = GenerateUdemyEvaluation(course['id_course'])

    if success:
        file_lock.acquire()
        try:
            with open(os.getenv('PATH_FILE_QUEUE'), 'r+') as file:
                courses_data = json.load(file)
                courses_data.remove(course)
                file.seek(0)
                json.dump(courses_data, file, indent=4)
                file.truncate()
        finally:
            file_lock.release()


def task_create_udemy_evaluation():
    print("Tarea programada ejecutada:", datetime.now())

    if os.path.exists(os.getenv('PATH_FILE_QUEUE')) and os.path.getsize(os.getenv('PATH_FILE_QUEUE')) > 0:
        with open(os.getenv('PATH_FILE_QUEUE')) as file:
            udemy_courses = json.load(file)
    else:
        print("No se encontró el archivo")
        return

    first_tree = udemy_courses[:3]
    num_courses = len(first_tree)

    if num_courses <= 0:
        print("No hay cursos")
        return

    threads = []

    for course in first_tree:
        print("Analizando curso: {}".format(course))
        thread = threading.Thread(target=process_and_manage_course, args=(course,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()


def upload_new_course_in_queue(curso):
    with file_lock:

        new_course = {
            'id_course': curso.pk
        }

        if not os.path.exists(os.getenv('PATH_FILE_QUEUE')):
            courses_data = []
        else:
            with open(os.getenv('PATH_FILE_QUEUE'), 'r+') as file:
                courses_data = json.load(file)

        courses_data.append(new_course)

        with open(os.getenv('PATH_FILE_QUEUE'), 'w') as file:
            json.dump(courses_data, file, indent=4)
