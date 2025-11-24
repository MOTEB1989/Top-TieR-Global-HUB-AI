from flask import Flask, request, make_response
from flask_cors import CORS


def create_app():
    app = Flask(__name__)

    # Enable CORS
    CORS(app)

    @app.after_request
    def apply_security_headers(response):
        # Security Headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'no-referrer'
        response.headers['Content-Security-Policy'] = "default-src 'self'; frame-ancestors 'none';"  
        response.headers['Strict-Transport-Security'] = 'max-age=63072000; includeSubDomains'
        response.headers['Permissions-Policy'] = 'geolocation=()'
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
