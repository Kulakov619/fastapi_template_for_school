from functools import lru_cache
from typing import Callable, Type


def get_service(service_class: Type) -> Callable:
    @lru_cache()
    def service():
        return service_class()
    return service
