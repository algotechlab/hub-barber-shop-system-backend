import json

from flask import jsonify
from sqlalchemy.engine.row import Row
from sqlalchemy.inspection import inspect


class ModelSerializer:

    def __init__(self, objects):
        self.objects = objects

    def to_dict(self, obj=None):
        obj = obj or self.objects

        if isinstance(obj, Row):
            return dict(obj._mapping)

        if isinstance(obj, tuple):
            return {f"col_{i}": value for i, value in enumerate(obj)}

        try:
            return {
                c.key: getattr(obj, c.key)
                for c in inspect(obj).mapper.column_attrs
            }
        except Exception:
            # Fallback for models with __table__
            if hasattr(obj, "__table__"):
                return {
                    column.name: getattr(obj, column.name)
                    for column in obj.__table__.columns
                }
            raise ValueError(
                f"Unable to serialize object: {obj}. Type: {type(obj)}"
            )

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
        Converts to a dictionary,
        focusing on table columns (useful for ID extraction).

        :return: Dictionary of column names to values.
        :raises ValueError: If the object lacks a __table__ attribute.
        """
        if hasattr(self.objects, "__table__"):
            return {
                column.name: getattr(self.objects, column.name)
                for column in self.objects.__table__.columns
            }
        raise ValueError(
            "Object does not have a __table__ attribute for column extraction."
        )


class JsonSerializer:

    def __init__(self, objects):
        self.serializer = (
            ModelSerializer(objects)
            if not isinstance(objects, (dict, list))
            else None
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
        raise ValueError(
            "No ModelSerializer available for ID-focused serialization."
        )


class ApiResponse:

    def __init__(
        self,
        status_code=200,
        data=None,
        message_id=None,
        error=False,
        **kwargs,  # e.g., metadata, access_token
    ):
        self.status_code = status_code
        self.data = data
        self.message_id = message_id
        self.error = error
        self.extra = kwargs

    def _build_dict(self):
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
