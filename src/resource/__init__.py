from src.resource.company import companies_ns
from src.resource.employee import employee_ns
from src.resource.login import login_us
from src.resource.onwer import owner_ns
from src.resource.product import product_ns
from src.resource.schedule import schedule_ns
from src.resource.user import user_us


def all_namespaces():
    return [
        user_us,
        owner_ns,
        companies_ns,
        employee_ns,
        product_ns,
        schedule_ns,
        login_us,
    ]
