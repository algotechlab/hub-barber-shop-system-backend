from enum import StrEnum


class EmployeeStatus(StrEnum):
    ROLE_EMPLOYEE = "EMPLOYEE"
    
class OwnerStatus(StrEnum):
    ROLE_OWNER = "OWNER"
    
    
class UserStatus(StrEnum):
    ROLE_USER = "USER"