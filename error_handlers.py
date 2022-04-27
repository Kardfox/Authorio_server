#local
import werkzeug
from main import app

@app.errorhandler(werkzeug.exceptions.BadRequest)
def bar_request(error):
    return "BAD_REQUEST", 400

@app.errorhandler(werkzeug.exceptions.BadRequest)
def not_found(error):
    return "NOT_FOUND", 404

@app.errorhandler(werkzeug.exceptions.BadRequest)
def method_not_allowed(error):
    return "METHOD_NOT_ALLOWED", 405

@app.errorhandler(werkzeug.exceptions.BadRequest)
def server_error(error):
    return "SERVER_ERROR", 500

app.register_error_handler(400, bar_request)
app.register_error_handler(404, not_found)
app.register_error_handler(405, method_not_allowed)
app.register_error_handler(500, server_error)