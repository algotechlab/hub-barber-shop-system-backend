from typing import Annotated
from uuid import UUID

from fastapi import Header

# Header esperado no formato: X-Owner-Id: <uuid>
OwnerIdHeaderDep = Annotated[
    UUID,
    Header(
        alias='X-Owner-Id',
        description='UUID do owner (ex.: tenant/cliente responsável pela companhia).',
    ),
]
