# src/utils/product.py
import os
from datetime import datetime
from uuid import uuid4

from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}


class UploadImageProduct:
    def __init__(self, description: str, user_id: int, created_at: datetime):
        self.description = description
        self.user_id = user_id
        self.created_at = created_at
        self.base_path = self.create_directory_structure()

    def create_directory_structure(self):
        year = self.created_at.strftime("%Y")
        month = self.created_at.strftime("%m")
        day = self.created_at.strftime("%d")
        base_path = os.path.join(
            "src/static/uploads",
            year,
            month,
            day,
            f"product_images_{self.description.replace(' ', '_')}",
        )
        os.makedirs(base_path, exist_ok=True)
        return base_path

    def save_image(self, image_stream):
        if not image_stream:
            raise ValueError("No image provided")

        filename = secure_filename(image_stream.filename)
        extension = filename.rsplit(".", 1)[1].lower() if "." in filename else ""
        if extension not in ALLOWED_EXTENSIONS:
            raise ValueError(
                "Invalid file extension. Only PNG, JPG, and JPEG are allowed"
            )

        unique_filename = f"{uuid4().hex}.{extension}"
        file_path = os.path.join(self.base_path, unique_filename)

        with open(file_path, "wb") as file:
            file.write(image_stream.read())

        relative_path = os.path.join(
            "static/uploads",
            self.created_at.strftime("%Y"),
            self.created_at.strftime("%m"),
            self.created_at.strftime("%d"),
            f"product_images_{self.description}",
            unique_filename,
        ).replace(os.sep, "/")
        return relative_path
