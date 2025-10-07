"""
Container Instance - Singleton instance of the DI container
Prevents circular imports by keeping container in a separate module
"""
from .container import Container

# Single instance of the container used throughout the application
container = Container()
