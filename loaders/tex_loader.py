from typing import Optional
from core.database.unit_of_work.mongo_unit_of_work import MongoUnitOfWork
from core.exceptions.database_exceptions import DatabaseError
import logging
from datetime import datetime, UTC

class TexLoader:
    """A class for loading LaTeX template files from MongoDB."""

    def __init__(self, uow: MongoUnitOfWork):
        """
        Initialize the TexLoader with a MongoDB UnitOfWork.

        Args:
            uow (MongoUnitOfWork): The unit of work for database operations.
        """
        self.uow = uow
        self.logger = logging.getLogger(__name__)
        self._cached_templates = {}

    def get_template(self, name: str) -> str:
        """
        Get a template from MongoDB by name.

        Args:
            name (str): The name of the template to retrieve.

        Returns:
            str: The content of the template.

        Raises:
            ValueError: If the template is not found.
        """
        try:
            # Use cached template if available
            if name in self._cached_templates:
                return self._cached_templates[name]

            with self.uow:
                headers = self.uow.tex_headers.get_all()
                for header in headers:
                    if header.name == name:
                        # Cache the template for future use
                        self._cached_templates[name] = header.content
                        self.uow.commit()
                        return header.content
                self.uow.commit()
                raise ValueError(f"Template '{name}' not found in the database")
        except DatabaseError as e:
            self.logger.error(f"Database error while retrieving template '{name}': {str(e)}")
            raise ValueError(f"Error retrieving template '{name}': {str(e)}")

    def safe_format_template(self, template_name: str, **kwargs) -> str:
        """
        Safely format a template with the given parameters.

        Args:
            template_name (str): The name of the template to format.
            **kwargs: The parameters to format the template with.

        Returns:
            str: The formatted template.

        Raises:
            ValueError: If the template is not found or formatting fails.
        """
        template = self.get_template(template_name)
        try:
            return template.format(**kwargs)
        except KeyError as e:
            self.logger.error(f"KeyError in template '{template_name}': {e}")
            raise ValueError(f"Missing key in template '{template_name}': {e}")
        except ValueError as e:
            self.logger.error(f"ValueError in template '{template_name}': {e}")
            raise ValueError(f"Error formatting template '{template_name}': {e}")
