
lint:
	pycodestyle .

start-simple-test-server:
	FLASK_APP=tests/contrib/flask/fixtures/single_route_apm_app/app.py flask run

test-simple-test-server:
	curl -v http://127.0.0.1:5000/

test-unit:
	nosetests tests

.PHONY: start-simple-test-server test-simple-test-server lint test-unit
