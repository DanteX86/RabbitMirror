#!/usr/bin/env python3
"""
RabbitMirror CLI entry point.
Enables running the package as: python -m rabbitmirror
"""

from .cli import cli

if __name__ == "__main__":
    cli()
