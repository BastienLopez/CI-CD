import os
import json
import re

def add_to_file(file_path, content):
    with open(file_path, 'a', encoding="utf-8") as f:
        f.write(content)

def analyze_project_structure():
    files = {
        "routes": [],
        "models": [],
        "config_json": [],
        "other": []
    }

    for root, dirs, files_list in os.walk("."):
        for file in files_list:
            file_path = os.path.join(root, file)
            if file.endswith(".py"):
                with open(file_path, 'r', encoding="utf-8") as f:
                    content = f.read()
                    if "def " in content and ("route(" in content or "app.route" in content):
                        files["routes"].append(file_path)
                    elif "SQLAlchemy" in content or "Base.metadata" in content:
                        files["models"].append(file_path)
                    else:
                        files["other"].append(file_path)
            elif file.endswith(".json"):
                files["config_json"].append(file_path)
    
    return files

def create_route_tests(route_files):
    test_file_path = "tests/test_routes.py"
    if not os.path.exists(test_file_path):
        with open(test_file_path, 'w', encoding="utf-8") as f:
            f.write("import pytest\n\n")
            f.write("from app import app\n\n")
            f.write("@pytest.fixture\n")
            f.write("def client():\n    with app.test_client() as client:\n        yield client\n\n")

    for route_file in route_files:
        with open(route_file, 'r', encoding="utf-8") as f:
            content = f.read()
            routes = re.findall(r"@app\.route\(['\"]([^'\"]+)['\"]", content)
            for route in routes:
                add_to_file(test_file_path, f"\n\ndef test_route_{route.strip('/').replace('/', '_')}(client):\n")
                add_to_file(test_file_path, f"    response = client.get('{route}')\n")
                add_to_file(test_file_path, f"    assert response.status_code == 200\n")

def create_db_tests(model_files):
    test_file_path = "tests/test_db.py"
    if not os.path.exists(test_file_path):
        with open(test_file_path, 'w', encoding="utf-8") as f:
            f.write("import pytest\n\n")
            f.write("from app import db\n\n")
            f.write("def test_db_connection():\n")
            f.write("    assert db.engine.execute('SELECT 1')\n\n")
    
    for model_file in model_files:
        with open(model_file, 'r', encoding="utf-8") as f:
            content = f.read()
            tables = re.findall(r"class (\w+)\(db\.Model\):", content)
            for table in tables:
                add_to_file(test_file_path, f"\ndef test_{table.lower()}_table_exists():\n")
                add_to_file(test_file_path, f"    result = db.engine.execute(\"SELECT * FROM {table} LIMIT 1\")\n")
                add_to_file(test_file_path, f"    assert result is not None\n")

def create_config_tests(config_files):
    test_file_path = "tests/test_config.py"
    if not os.path.exists(test_file_path):
        with open(test_file_path, 'w', encoding="utf-8") as f:
            f.write("import json\n\n")
    
    for config_file in config_files:
        add_to_file(test_file_path, f"\n\ndef test_{os.path.basename(config_file).replace('.', '_')}():\n")
        add_to_file(test_file_path, f"    with open('{config_file}', 'r') as f:\n")
        add_to_file(test_file_path, f"        data = json.load(f)\n")
        add_to_file(test_file_path, f"        assert isinstance(data, dict)\n")

def create_integration_tests():
    test_file_path = "tests/test_integration.py"
    if not os.path.exists(test_file_path):
        with open(test_file_path, 'w', encoding="utf-8") as f:
            f.write("import pytest\n\n")
            f.write("from app import app\n\n")
            f.write("def test_integration():\n    # Placeholder for integration tests\n    pass\n")

def setup_ci_cd(docker=False):
    os.makedirs(".github/workflows", exist_ok=True)
    workflow_path = ".github/workflows/CI.yml"
    if not os.path.exists(workflow_path):
        with open(workflow_path, "w") as f:
            f.write("name: Python CI\n\n")
            f.write("on:\n  push:\n    branches:\n      - '**'\n  pull_request:\n    branches:\n      - '**'\n\n")
            f.write("jobs:\n  test:\n    runs-on: ubuntu-latest\n\n")
            f.write("    steps:\n      - name: Checkout repository\n        uses: actions/checkout@v2\n")
            if docker:
                f.write("      - name: Run tests in Docker\n        run: docker compose run test\n")
            else:
                f.write("      - name: Set up Python\n        uses: actions/setup-python@v2\n        with:\n          python-version: '3.x'\n\n")
                f.write("      - name: Install dependencies\n        run: |\n          python -m pip install --upgrade pip\n")
                f.write("          pip install -r requirements.txt\n          pip install pytest pytest-cov flake8\n")
                f.write("      - name: Lint code with flake8\n        run: flake8 src tests\n")
                f.write("      - name: Run tests\n        run: pytest --cov=src --cov-report=xml\n")

def main():
    os.makedirs("tests", exist_ok=True)
    project_files = analyze_project_structure()
    
    create_route_tests(project_files["routes"])
    create_db_tests(project_files["models"])
    create_config_tests(project_files["config_json"])
    create_integration_tests()

    setup_ci_cd(docker="docker-compose.yml" in project_files or "Dockerfile" in project_files)

if __name__ == "__main__":
    main()
