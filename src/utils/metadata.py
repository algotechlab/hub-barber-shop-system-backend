import json

from flask import jsonify
from sqlalchemy.engine.row import Row
from sqlalchemy.inspection import inspect


class ModelSerializer:
    """
    Serializer for converting SQLAlchemy models and query results to Python dictionaries.
    Handles ORM instances, Row objects, tuples, and lists thereof, providing a unified
    interface to avoid repetitive conversion logic in the codebase.
    """

    def __init__(self, objects):
        """
        Initializes the serializer with the object(s) to convert.

        :param objects: A single SQLAlchemy object, Row, tuple, or a list of such items.
        """
        self.objects = objects

    def to_dict(self, obj=None):
        """
        Converts a single object to a dictionary.

        :param obj: Optional object to convert; defaults to self.objects.
        :return: Dictionary representation of the object.
        :raises ValueError: If the object cannot be serialized.
        """
        obj = obj or self.objects

        if isinstance(obj, Row):
            return dict(obj._mapping)

        if isinstance(obj, tuple):
            return {f"col_{i}": value for i, value in enumerate(obj)}

        try:
            return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}
        except Exception:
            # Fallback for models with __table__
            if hasattr(obj, "__table__"):
                return {column.name: getattr(obj, column.name) for column in obj.__table__.columns}
            raise ValueError(f"Unable to serialize object: {obj}. Type: {type(obj)}")

    def to_list(self):
        """
        Converts the objects to a list of dictionaries.

        :return: List of dictionary representations.
        """
        if isinstance(self.objects, list):
            return [self.to_dict(obj) for obj in self.objects]
        elif self.objects:
            return [self.to_dict(self.objects)]
        return []

    def to_dict_with_id(self):
        """
        Converts to a dictionary, focusing on table columns (useful for ID extraction).

        :return: Dictionary of column names to values.
        :raises ValueError: If the object lacks a __table__ attribute.
        """
        if hasattr(self.objects, "__table__"):
            return {
                column.name: getattr(self.objects, column.name)
                for column in self.objects.__table__.columns
            }
        raise ValueError("Object does not have a __table__ attribute for column extraction.")


class JsonSerializer:
    """
    Serializer for converting Python data structures to JSON strings.
    Builds on ModelSerializer for SQLAlchemy objects, handling custom serialization
    (e.g., dates via default=str) to avoid repetitive json.dumps calls.
    """

    def __init__(self, objects):
        """
        Initializes the JSON serializer.

        :param objects: Data to serialize (can be SQLAlchemy objects or plain data).
        """
        self.serializer = (
            ModelSerializer(objects) if not isinstance(objects, (dict, list)) else None
        )
        self.data = (
            objects if isinstance(objects, (dict, list)) else None
        )  # Cache for serialized data

    def to_json(self, as_list=False):
        """
        Converts the data to a JSON string.

        :param as_list: Force conversion to a list if True.
        :return: JSON string representation.
        """
        if self.data is None:
            if self.serializer:
                self.data = (
                    self.serializer.to_list()
                    if as_list or isinstance(self.serializer.objects, list)
                    else self.serializer.to_dict()
                )
            else:
                self.data = {}  # Fallback for empty data
        return json.dumps(self.data, default=str)

    def to_json_with_id(self):
        """
        Converts to a JSON string, focusing on table columns.

        :return: JSON string representation.
        """
        if self.serializer:
            data = self.serializer.to_dict_with_id()
            return json.dumps(data, default=str)
        raise ValueError("No ModelSerializer available for ID-focused serialization.")


class ApiResponse:
    """
    Builder for standardized API responses in Flask applications.
    Handles status codes, messages, errors, data serialization (via ModelSerializer),
    and optional extras (e.g., metadata, tokens). Returns a ready-to-use Flask response.
    """

    def __init__(
        self,
        status_code=200,
        data=None,
        message_id=None,
        error=False,
        **kwargs,  # e.g., metadata, access_token
    ):
        """
        Initializes the API response builder.

        :param status_code: HTTP status code (default: 200).
        :param data: Response data (can be SQLAlchemy objects or plain dict/list).
        :param message_id: Optional message identifier for localization/logging.
        :param error: Boolean indicating if this is an error response.
        :param kwargs: Additional fields to include in the response (e.g., metadata).
        """
        self.status_code = status_code
        self.data = data
        self.message_id = message_id
        self.error = error
        self.extra = kwargs

    def _build_dict(self):
        """
        Internal method to build the response dictionary, serializing data if needed.

        :return: Dictionary ready for JSON serialization.
        """
        resp = {"status_code": self.status_code}
        if self.message_id:
            resp["message_id"] = self.message_id
        if self.error is not None:
            resp["error"] = self.error

        if self.data is not None:
            # Serialize data if it's not already a dict/list
            if not isinstance(self.data, (dict, list)):
                serializer = ModelSerializer(self.data)
                self.data = (
                    serializer.to_list()
                    if isinstance(self.data, (list, tuple))
                    else serializer.to_dict()
                )
            resp["data"] = self.data

        # Add extra fields
        resp.update(self.extra)

        return resp

    def to_response(self):
        """
        Generates the final Flask response.

        :return: Tuple of (jsonify(response_dict), status_code).
        """
        response_dict = self._build_dict()
        return jsonify(response_dict), self.status_code
