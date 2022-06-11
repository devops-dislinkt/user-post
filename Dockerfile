FROM python:3.7
WORKDIR /code
COPY requirements.txt requirements.txt

RUN pip install --proxy=http://proxy.uns.ac.rs:8080 -r requirements.txt

#RUN pip install -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["python", "app.py"]
