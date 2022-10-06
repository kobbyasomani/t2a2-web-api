from datetime import datetime, timezone
from flask import current_app as app
from multidict import MultiDict


def duplicate_exists(
        new_record: object, model_name: str, ignore_list: list) -> None | list:
    """ Check whether a record with identical cell values already exists """
    with app.app_context():
        # Store the new record values in MultiDict for easy filtering
        new_record_values = MultiDict(
            # For each column in the new record, generate the name=value pair
            (column.name, getattr(new_record, column.name))
            for column in new_record.__table__.columns
            # Ignore column in igonre_list
            if column.name not in ignore_list)
        found_record = model_name.query.filter_by(
            **new_record_values).first()
        return found_record


def current_datetime():
    """ Return the current datetime with UTC timezone """
    return datetime.now(timezone.utc)


def record_not_found(record_type: str):
    """ Return a 404 error when a record was not found """
    return {"error": f"The {record_type} could not be found."}, 404


def unauthorised_editor(record_type: str):
    """ Return a 403 error when a user attempts to edit a record 
    they did not author """
    return {"error": f"You aren't allowed to edit this {record_type}."}, 403
