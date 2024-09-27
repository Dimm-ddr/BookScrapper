import sys
import logging
import importlib
from functools import wraps
import traceback
from types import ModuleType, FunctionType, MethodType
from importlib.abc import Loader, MetaPathFinder
from importlib.machinery import ModuleSpec
from typing import Sequence

print("Error handler module loaded successfully!")


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(name)s - %(filename)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def exception_handler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            full_traceback: str = traceback.format_exc()
            logging.error(f"Exception in {func.__name__}: {str(e)}\n{full_traceback}")
            raise

    return wrapper


def global_exception_handler(exc_type, exc_value, exc_traceback) -> None:
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    full_traceback: str = "".join(
        traceback.format_exception(exc_type, exc_value, exc_traceback)
    )
    logging.error(f"Uncaught exception:\n{full_traceback}")


class ErrorHandlerFinder(MetaPathFinder):
    def __init__(self, module_names) -> None:
        self.module_names = module_names

    def find_spec(
        self,
        fullname: str,
        path: Sequence[str] | None,
        target: ModuleType | None = None,
    ) -> ModuleSpec | None:
        if fullname in self.module_names:
            return ModuleSpec(fullname, ErrorHandlerLoader(fullname))
        return None


class ErrorHandlerLoader(Loader):
    def __init__(self, fullname: str) -> None:
        self.fullname: str = fullname

    def create_module(self, spec: ModuleSpec) -> ModuleType | None:
        return None  # Use default module creation

    def exec_module(self, module: ModuleType) -> None:
        original_module: ModuleType = importlib.import_module(self.fullname)
        for name, obj in original_module.__dict__.items():
            if isinstance(obj, (FunctionType, MethodType)):
                setattr(module, name, exception_handler(obj))
            else:
                setattr(module, name, obj)


def setup_error_handling(module_names) -> None:
    print(f"Setting up error handling for modules: {module_names}")
    setup_logging()
    sys.excepthook = global_exception_handler
    sys.meta_path.insert(0, ErrorHandlerFinder(module_names))
