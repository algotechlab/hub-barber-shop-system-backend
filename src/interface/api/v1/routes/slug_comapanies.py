from typing import List

from fastapi import APIRouter, status

from src.interface.api.v1.dependencies.company import CompanyRepositoryDep
from src.interface.api.v1.schema.company import CompanyOutSchema

tags_metadata = {
    'name': 'Companias por slug',
    'description': ('Modulo de companias por slug'),
}


router = APIRouter(
    prefix='/slug-companies',
    tags=[tags_metadata['name']],
)


@router.get(
    '/{slug}',
    status_code=status.HTTP_200_OK,
    response_model=List[CompanyOutSchema],
)
async def list_companies_slug(
    controller: CompanyRepositoryDep, slug: str
) -> List[CompanyOutSchema]:
    return await controller.list_companies_slug(slug)
