#!/usr/bin/env python3
"""
Simple script to check which methods in AdversarialProfiler need more test coverage
"""
import inspect
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from rabbitmirror.adversarial_profiler import AdversarialProfiler


def get_all_methods(cls):
    """Get all methods from a class"""
    methods = []
    for name, method in inspect.getmembers(cls, predicate=inspect.ismethod):
        if not name.startswith("__"):
            methods.append(name)

    # Also get unbound methods (static methods, etc.)
    for name in dir(cls):
        if not name.startswith("__"):
            attr = getattr(cls, name)
            if callable(attr) and name not in methods:
                methods.append(name)

    return sorted(methods)


def main():
    methods = get_all_methods(AdversarialProfiler)
    print("AdversarialProfiler methods:")
    for i, method in enumerate(methods, 1):
        print(f"{i:2d}. {method}")

    print(f"\nTotal methods: {len(methods)}")


if __name__ == "__main__":
    main()
