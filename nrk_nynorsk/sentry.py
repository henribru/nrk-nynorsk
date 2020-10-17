import os

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration


def init_sentry() -> None:
    if "SENTRY_DSN" not in os.environ:
        return

    sentry_sdk.init(dsn=os.environ["SENTRY_DSN"], integrations=[DjangoIntegration()])
