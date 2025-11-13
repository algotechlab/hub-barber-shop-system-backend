from enum import StrEnum


class PostgresErrorCode(StrEnum):
    UNIQUE_VIOLATION = "23505"
    FOREIGN_KEY_VIOLATION = "23503"
    NOT_NULL_VIOLATION = "23502"
