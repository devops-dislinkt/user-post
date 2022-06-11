FROM python:3.7
WORKDIR /code
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
# COPY . .
EXPOSE 8070
CMD ["python", "./app.py"]