import random
import string

from fastapi import FastAPI

system_random = random.SystemRandom()


def add_routers_to_app(
    routers: list[list],
    app: FastAPI,
    root_path: str,
) -> FastAPI:
    for prefix, router in routers:
        app.include_router(router, prefix=root_path + prefix)
    return app


def random_string(length=10) -> str:
    letters = string.ascii_letters
    return "".join(system_random.choice(letters) for i in range(length))
