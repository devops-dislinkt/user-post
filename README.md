# user-post

docker build -t getting-started .

docker run -dp 3000:3000 getting-started

u docker consoli:

 * Serving Flask app 'app' (lazy loading)

 * Environment: production

 * Running on all addresses (0.0.0.0)

   WARNING: This is a development server. Do not use it in a production deployment.

 * Running on http://127.0.0.1:8080

 * Running on http://172.17.0.2:8080 (Press CTRL+C to quit)


Postman:

POST -> http://127.0.0.1:8080/add
POST -> http://172.17.0.2:8080/add
POST -> http://127.0.0.1:3000/add
POST -> http://172.17.0.2:3000/add
