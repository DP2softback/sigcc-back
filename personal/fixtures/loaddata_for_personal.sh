python manage.py loaddata ./personal/fixtures/001demoroles.json
python manage.py loaddata ./personal/fixtures/002demousers.json
python manage.py loaddata ./personal/fixtures/003demouserxrole.json

python manage.py loaddata ./personal/fixtures/004demoarea.json
python manage.py loaddata ./personal/fixtures/005demoposition.json
python manage.py loaddata ./personal/fixtures/006demoareaxposition.json

python manage.py loaddata ./personal/fixtures/007demofunction.json

python manage.py loaddata ./personal/fixtures/008demotrainingtype.json
python manage.py loaddata ./personal/fixtures/009demotraininglevel.json
python manage.py loaddata ./personal/fixtures/010demotraining.json
python manage.py loaddata ./personal/fixtures/011demotrainingxlevel.json
python manage.py loaddata ./personal/fixtures/012demotrainingxareaxposition.json

python manage.py loaddata ./personal/fixtures/013demosubcategory.json
python manage.py loaddata ./personal/fixtures/014democompetencyxareaxposition.json

python manage.py loaddata ./personal/fixtures/db.json





python manage.py dumpdata --exclude auth.permission --exclude contenttypes > ./personal/fixtures/db.json

zappa manage dev  loaddata ./personal/fixtures/db.json