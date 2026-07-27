from flask import jsonify
from werkzeug.exceptions import HTTPException

def register_error_handlers(app):
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        response = e.get_response()
        response.data = jsonify({
            "code": e.code,
            "name": e.name,
            "description": e.description,
        }).data
        response.content_type = "application/json"
        return response

    @app.errorhandler(Exception)
    def handle_exception(e):
        # Handle non-HTTP exceptions
        response = jsonify({
            "code": 500,
            "name": "Internal Server Error",
            "description": str(e),
        })
        response.status_code = 500
        return response

    @app.errorhandler(404)
    def handle_404_error(e):
        response = jsonify({
            "code": 404,
            "name": "Not Found",
            "description": "The requested resource was not found.",
        })
        response.status_code = 404
        return response