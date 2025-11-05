from src.resource.onwer import owner_ns
from src.resource.user import user_us


def all_namespaces():
    return [
        user_us,
        owner_ns,
    ]
