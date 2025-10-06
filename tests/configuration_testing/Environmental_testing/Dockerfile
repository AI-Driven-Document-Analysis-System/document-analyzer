ARG PYTHON_VERSION
FROM python:${PYTHON_VERSION}

WORKDIR /app
COPY requirements.txt .
COPY test_config.py .
COPY run_tests.py .

RUN pip install pytest pytest-html pillow
RUN pip install -r requirements.txt

CMD ["python", "run_tests.py"]
