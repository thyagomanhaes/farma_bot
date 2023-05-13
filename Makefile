unit-tests:
    ${PYTHONCMD} -m pytest --cov=mecofarma --cov-fail-under=80 --cov-report html:coverage-reports/coverage-report.html tests/unit

delete-coverage-report:
    rm -rf coverage-reports/

docker-image:
    docker build . -t=mecofarma -f=Dockerfile

docker-run-for-test: docker-image
    docker run -d -rm -p 8080:8080 --name mecofarma mecofarma