FROM python:3.9
WORKDIR /app

COPY bbuddy.backend/ .
RUN pip install -r requirements.txt && pip install firebase-admin

#COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

