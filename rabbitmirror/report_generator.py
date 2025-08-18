from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import jinja2


class ReportGenerator:
    def __init__(self, template_dir: Optional[str] = None):
        """Initialize the report generator.

        If template_dir is provided, user templates in that directory take precedence.
        Packaged templates under rabbitmirror/templates are always available as a fallback.
        """

        loaders = []
        if template_dir:
            loaders.append(jinja2.FileSystemLoader(template_dir))
        # Packaged templates fallback
        try:
            loaders.append(jinja2.PackageLoader("rabbitmirror", "templates"))
        except Exception:
            # If package data not available (e.g., during dev), also try filesystem 'templates'
            loaders.append(jinja2.FileSystemLoader("templates"))

        self.env = jinja2.Environment(
            loader=jinja2.ChoiceLoader(loaders),
            autoescape=jinja2.select_autoescape(["html", "xml"]),
        )

    def generate_report(
        self, data: Dict[str, Any], template_name: str, output_path: str
    ):
        """Generate a report using the specified template and data."""
        template = self.env.get_template(template_name)

        # Add metadata to the report
        data["generated_at"] = datetime.now().isoformat()

        # Render the template
        output = template.render(**data)

        # Save the report
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output, encoding="utf-8")
