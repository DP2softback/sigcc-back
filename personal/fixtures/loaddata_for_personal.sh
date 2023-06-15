python manage.py loaddata ./personal/fixtures/demoroles.json
python manage.py loaddata ./personal/fixtures/demousers.json
python manage.py loaddata ./personal/fixtures/demouserxrole.json

python manage.py loaddata ./personal/fixtures/personal_position.json
python manage.py loaddata ./personal/fixtures/demoarea.json
python manage.py loaddata ./personal/fixtures/demofunctions.json


python manage.py loaddata ./personal/fixtures/democompetencetype.json
python manage.py loaddata ./personal/fixtures/democompetence.json
python manage.py loaddata ./personal/fixtures/democompetencescale.json

python manage.py loaddata ./personal/fixtures/demoareaxposicion.json
python manage.py loaddata ./personal/fixtures/democompetencexareaxposition.json
python manage.py loaddata ./personal/fixtures/stage_types.json
python manage.py loaddata ./gaps/fixtures/Data_tiposCompetencia.json
python manage.py loaddata ./gaps/fixtures/Data_competencias.json

zappa manage dev loaddata ./personal/fixtures/demoroles.json
zappa manage dev loaddata ./personal/fixtures/demousers.json
zappa manage dev loaddata ./personal/fixtures/demouserxrole.json

zappa manage dev loaddata ./personal/fixtures/personal_position.json
zappa manage dev loaddata ./personal/fixtures/demoarea.json
zappa manage dev loaddata ./personal/fixtures/demofunctions.json


zappa manage dev loaddata ./personal/fixtures/democompetencetype.json
zappa manage dev loaddata ./personal/fixtures/democompetence.json
zappa manage dev loaddata ./personal/fixtures/democompetencescale.json

zappa manage dev loaddata ./personal/fixtures/demoareaxposicion.json
zappa manage dev loaddata ./personal/fixtures/democompetencexareaxposition.json


zappa manage dev loaddata ./gaps/fixtures/Data_tiposCompetencia.json
zappa manage dev loaddata ./gaps/fixtures/Data_competencias.json
