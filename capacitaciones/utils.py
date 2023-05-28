import requests


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



def clean_course_detail (course):

    list_keys = ['is_paid', 'price', 'price_detail', 'price_serve_tracking_id', 'is_practice_test_course',
                 'tracking_id', 'predictive_score', 'relevancy_score', 'input_features', 'lecture_search_result',
                 'curriculum_lectures', 'order_in_results', 'curriculum_items', 'instructor_name']

    for key in list_keys:
        del course[key]

    return course