from src.resource.company import companies_ns
from src.resource.employee import employee_ns
from src.resource.onwer import owner_ns
from src.resource.user import user_us


def all_namespaces():
    return [user_us, owner_ns, companies_ns, employee_ns]
