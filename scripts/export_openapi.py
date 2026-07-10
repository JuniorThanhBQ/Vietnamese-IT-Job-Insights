import os
import sys
import json

# Add backend directory to path so we can import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))

from app.main import app

def export_openapi():
    # Ensure docs/apis directory exists
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../docs/apis"))
    os.makedirs(output_dir, exist_ok=True)

    output_file = os.path.join(output_dir, "api_v1.json")

    # Generate the OpenAPI schema from the FastAPI app instance
    openapi_schema = app.openapi()

    # Save formatted JSON schema
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(openapi_schema, f, indent=2, ensure_ascii=False)

    print(f"Successfully exported OpenAPI schema to {output_file}")

if __name__ == "__main__":
    export_openapi()
