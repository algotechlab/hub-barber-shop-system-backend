import os

from fastapi import APIRouter

v1_router = APIRouter(prefix='/v1')
v1_tags_metadata = []
current_dir = os.path.dirname(os.path.abspath(__file__))
routes_dir = os.path.join(current_dir, 'routes')

for filename in os.listdir(routes_dir):
    if filename.endswith('.py') and filename != '__init__.py':
        module_name = filename[:-3]
        try:
            module = __import__(
                f'src.interface.api.v1.routes.{module_name}',
                fromlist=['router', 'tags_metadata'],
            )
            if hasattr(module, 'tags_metadata'):
                v1_tags_metadata.append(module.tags_metadata)
            if hasattr(module, 'router'):
                v1_router.include_router(module.router)
            else:
                print(f"Arquivo {filename} não possui um atributo 'router'")
        except ImportError as e:
            print(f'Erro ao importar {filename}: {e}')
        except Exception as e:
            print(f'Erro ao processar {filename}: {e}')

__all__ = ['v1_router', 'v1_tags_metadata']
