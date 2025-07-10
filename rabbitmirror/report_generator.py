from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import jinja2


class ReportGenerator:
    def __init__(self, template_dir: str = "templates"):
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(template_dir),
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
