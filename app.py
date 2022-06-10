from app import create_app
from opentelemetry.instrumentation.flask import FlaskInstrumentor

if __name__ == '__main__':
    app = create_app()
    FlaskInstrumentor().instrument_app(app)
    app.run(debug=True, host='0.0.0.0', port=8080)

#port = int(os.environ.get('PORT', 8080))
#if __name__ == '__main__':
#    #app.run(threaded=True, host='0.0.0.0', port=port)
#    app.run(debug=True, host='0.0.0.0', port=8080)
