# NEW-131
# inspect_i18n_libs.py

import inspect
import pkgutil
import sys
from typing import Any, List, Tuple

def inspect_module(module: Any, indent: str = "", max_depth: int = 3, current_depth: int = 0) -> None:
    """Modulning tarkibini rekursiv tekshiradi."""
    if current_depth > max_depth:
        return

    for name, obj in inspect.getmembers(module):
        if name.startswith("_"): # Ichki obyektlarni o'tkazib yuborish
            continue

        if inspect.isclass(obj):
            print(f"{indent}Class: {name}")
            if current_depth + 1 <= max_depth:
                for method_name, method_obj in inspect.getmembers(obj, inspect.isfunction):
                    if not method_name.startswith("_"):
                        try:
                            signature = inspect.signature(method_obj)
                            print(f"{indent}  Method: {method_name}{signature}")
                        except ValueError:
                            print(f"{indent}  Method: {method_name} (signature not available)")
        elif inspect.isfunction(obj):
            try:
                signature = inspect.signature(obj)
                print(f"{indent}Function: {name}{signature}")
            except ValueError:
                print(f"{indent}Function: {name} (signature not available)")
        elif inspect.ismodule(obj) and hasattr(obj, '__file__') and obj.__file__ and \
             any(lib_name in obj.__file__ for lib_name in ["fluent", "aiogram"]): # Faqat kerakli modullarni tekshirish
            print(f"{indent}Sub-module: {name}")
            inspect_module(obj, indent + "  ", max_depth, current_depth + 1)
        # else:
        #     print(f"{indent}Other: {name} ({type(obj)})")

def inspect_library(library_name: str, max_depth: int = 3) -> None:
    """Berilgan kutubxonaning tarkibini tekshiradi."""
    print(f"\n--- Kutubxona: {library_name} ---")
    try:
        __import__(library_name)
        lib_module = sys.modules[library_name]
        inspect_module(lib_module, max_depth=max_depth)
    except ImportError:
        print(f"Kutubxona '{library_name}' topilmadi.")
    except Exception as e:
        print(f"Kutubxona '{library_name}'ni tekshirishda xatolik: {e}")

if __name__ == "__main__":
    libraries_to_inspect = [
        "fluent_compiler",
        "fluent.syntax",
        "aiogram.utils.i18n"
    ]

    for lib in libraries_to_inspect:
        inspect_library(lib, max_depth=2) # Chuqurlikni oshirishingiz mumkin

