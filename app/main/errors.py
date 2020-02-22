from flask import render_template, request, jsonify
from . import main
from app.util import isAjax


@main.errorhandler(403)
def forbidden(e):
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'forbidden'})
        response.status_code = 403
        return response
    return render_template('errors/403.html'), 403


@main.errorhandler(404)
def page_not_found(e):
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'not found'})
        response.status_code = 404
        return response
    return render_template('errors/404.html'), 404


@main.errorhandler(500)
def internal_server_error(e):
    if isAjax():
        return jsonify({'code':0,'msg':'internal server error'})
    return render_template('errors/500.html'), 500
