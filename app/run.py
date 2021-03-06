from app import create_app
from jaeger_client import Config
from flask_opentracing import FlaskTracing
from flask_cors import CORS, cross_origin


if __name__ == "__main__":
    app = create_app()
    cors = CORS(app)
    app.config["CORS_HEADERS"] = "Content-Type"

    config = Config(
        config={
            "sampler": {
                "type": "const",
                "param": 1,
            },
            "local_agent": {
                "reporting_host": "jaeger",  # ili u ENV dodati IP adresu kontejnera
                "reporting_port": "6831",
            },
            "logging": True,
            "service_name": "user-post",
        }
    )

    jaeger_tracer = config.initialize_tracer()
    tracing = FlaskTracing(jaeger_tracer, True, app)

    app.run(debug=True, host="0.0.0.0", port=8070)

# port = int(os.environ.get('PORT', 8080))
# if __name__ == '__main__':
#    #app.run(threaded=True, host='0.0.0.0', port=port)
#    app.run(debug=True, host='0.0.0.0', port=8080)
