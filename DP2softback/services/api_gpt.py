import logging
import os

import openai


class ChatGptService():

    @classmethod
    def chatgpt_request(cls, capacities, temp):

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=generate_tech_competencies_textual(capacities),
            temperature=temp,
        )
        logging.info(f"response")
        logging.info(f"response {response}")
        return response.choices[0].message.content


def generate_tech_competencies_textual(info):

    return [
        {"role": "system", "content": "Eres un redactor que recibe una lista de requisitos para una posicion laboral y por cada requisito redacta una versión más detallada de este requisito, únicamente un requisito en cada línea, separados por un salto de línea, sin agregar una presentación a la lista."},
        {"role": "user", "content": "Proeficiencia en React, Conocimientos de seguridad en la nube, Habilidad en técnicas de recuperación de datos"},
        {"role": "assistant", "content": "- Programador con amplias habilidades en React\n, - Debe tener un alto dominio de temas de seguridad en la nube\n, -Gran capacidad para recuperar datos\n"},
        {"role": "user", "content": info}

    ]
