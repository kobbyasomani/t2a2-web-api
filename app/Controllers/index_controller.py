from flask import Blueprint, send_file

index = Blueprint("index", __name__)


@index.get("/")
def get_index():
    return {"message": "Welcome to the AskLocal web server API! "
            "Use it to find helpful answers to questions about a local area "
            "across categories such as accommodation, transport, shopping, "
            "and more. For the full documentation, visit: /help"}


@index.get("/help")
def get_help():
    """ Return the README.md document about the API """
    try:
        return send_file("./docs/README.md")
    except FileNotFoundError as error:
        return {"error": "The help file 'README.md' could not be found."}
    except Exception as error:
        return {"error": str(error)}
