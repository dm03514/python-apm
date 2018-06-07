
lint:
	pycodestyle .

start-simple-test-server:
	FLASK_APP=tests/contrib/flask/fixtures/single_route_apm_app/app.py flask run

start-service-test-stack:
	# for a full project would use docker-compose here
	FLASK_APP=tests/contrib/flask/fixtures/single_route_apm_app/app.py flask run &

test-simple-test-server:
	curl -v http://127.0.0.1:5000/

test-unit:
	nosetests tests

test-service:
	./bin/amd64/flaskapmtest -cmd wait-ready
	./bin/amd64/flaskapmtest -cmd http-surfacer-metrics-correct

.PHONY: start-simple-test-server test-simple-test-server lint test-unit
