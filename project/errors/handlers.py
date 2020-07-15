from flask import Blueprint, render_template

errors = Blueprint('errors', __name__, template_folder = 'templates/errors' )


@errors.app_errorhandler(404)
def error_404(error):
    return render_template('404.html', error = error), 404


@errors.app_errorhandler(500)
def error_500(error):
    return render_template('500.html', error = error), 500


@errors.app_errorhandler(403)
def error_403(error):
    return render_template('403.html', error = error), 403
