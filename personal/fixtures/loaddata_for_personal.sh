python manage.py loaddata ./personal/fixtures/db.json

python manage.py dumpdata --exclude auth.permission --exclude contenttypes > ./personal/fixtures/db.json


python manage.py loaddata login_user.json personal_area.json personal_position.json personal_areaxposicion.json login_employee.json evaluations_and_promotions_evaluationType.json evaluations_and_promotions_category.json evaluations_and_promotions_subcategory.json evaluations_and_promotions_evaluation.json evaluations_and_promotions_evaluationxsubcategory.json evaluations_and_promotions_plantilla.json evaluations_and_promotions_plantillaxsubcategoria.json

python manage.py loaddata ./personal/fixtures/personal_login.role.json

python manage.py loaddata ./personal/fixtures/personal_personal.trainingtype.json
python manage.py loaddata ./personal/fixtures/personal_personal.traininglevel.json
python manage.py loaddata ./personal/fixtures/personal_personal.training.json
python manage.py loaddata ./personal/fixtures/personal_personal.trainingxlevel.json



zappa manage dev  loaddata ./personal/fixtures/db.json