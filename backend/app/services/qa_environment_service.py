"""Fail-closed environment gate for the Sandbox QA scan capability."""
from app.core.settings import settings


QA_ALLOWED_ENVIRONMENT = "dev"


def is_sandbox_qa_dev_environment(value: object | None = None) -> bool:
    """Return true only for the explicitly configured BCSentinel DEV value.

    Do not normalize aliases: ``production``, ``test``, whitespace variants,
    missing values and unknown values must all remain denied.
    """
    environment = settings.ENV if value is None else value
    return isinstance(environment, str) and environment == QA_ALLOWED_ENVIRONMENT


def require_sandbox_qa_dev_environment() -> None:
    if not is_sandbox_qa_dev_environment():
        raise ValueError("Sandbox QA grants are available only when ENV is explicitly configured as dev.")
