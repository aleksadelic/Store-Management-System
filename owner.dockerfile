FROM python:3

RUN mkdir -p /opt/src/applications
WORKDIR /opt/src/applications

COPY applications/application_owner.py ./application.py
COPY applications/configuration.py ./configuration.py
COPY applications/models.py ./models.py
COPY applications/requirements.txt ./requirements.txt
COPY applications/role_check_decorator.py ./role_check_decorator.py

RUN pip install -r ./requirements.txt

ENV PYTHONPATH = "/opt/src/applications"

ENTRYPOINT ["python", "./application.py"]
