"""Entry point for the calendardataviz package.
Exposes the `InspectorABC`, RichString class and
`start_app` function to the user.
"""

from calendardataviz.app import start_app
from calendardataviz.inspector_abc import InspectorABC
from calendardataviz.rich_string import RichString

__all__ = [
    "start_app",
    "InspectorABC",
    "RichString",
]
