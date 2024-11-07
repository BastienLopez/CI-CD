import os

def add_requirements(requirements_path):
    requirements = ["pytest", "pytest-cov", "flake8"]
    with open(requirements_path, 'a') as f:
        for req in requirements:
            f.write(f"{req}\n")

def create_github_workflow(docker=False):
    os.makedirs(".github/workflows", exist_ok=True)
    workflow_path = ".github/workflows/CI.yml"
    if not os.path.exists(workflow_path):
        with open(workflow_path, "w") as f:
            f.write("name: Python CI\n\n")
            f.write("on:\n")
            f.write("  push:\n    branches:\n      - '**'\n")
            f.write("  pull_request:\n    branches:\n      - '**'\n\n")
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
    else:
        print("CI workflow file already exists. Skipping creation.")

def create_test_file(filename, docker=False):
    if not os.path.exists(filename):
        with open(filename, "w") as f:
            f.write("import random\n\n")
            f.write("def test_multiply_by_two():\n")
            f.write("    for _ in range(5):\n")
            f.write("        x = random.randint(-100, 100)\n")
            f.write("        assert multiply_by_two(x) == x * 2\n")
    else:
        print(f"Test file '{filename}' already exists. Skipping creation.")

def create_readme():
    readme_path = "README_CI_CD.md"
    if not os.path.exists(readme_path):
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write("# Guide CI/CD\n\n")
            f.write("Ce fichier a été généré pour expliquer la configuration CI/CD automatique pour ce projet.\n\n")
            f.write("## Exécution des tests\n\n")
            f.write("1. Assurez-vous que toutes les dépendances sont installées :\n")
            f.write("   ```bash\n   pip install -r requirements.txt\n   ```\n\n")
            f.write("2. Lancer les tests :\n")
            f.write("   ```bash\n   pytest\n   ```\n\n")
            f.write("3. Pour exécuter le linting :\n")
            f.write("   ```bash\n   flake8 src tests\n   ```\n\n")
            f.write("## Contenu ajouté\n\n")
            f.write("- `.github/workflows/CI.yml` : fichier de workflow GitHub Actions pour CI/CD.\n")
            f.write("- `test_app_ci.py` : fichier de test CI/CD.\n")
            f.write("- `README_CI_CD.md` : documentation sur la configuration CI/CD.\n")
    else:
        print("README_CI_CD.md already exists. Skipping creation.")

def scan_project():
    docker = False
    # Détecte si le projet utilise Docker
    if os.path.exists("docker-compose.yml") or os.path.exists("Dockerfile"):
        docker = True

    # Créer le dossier `src` et ajouter un fichier de test si nécessaire
    os.makedirs("src", exist_ok=True)
    create_test_file("src/test_app.py", docker=docker)

    # Créer le dossier `tests` et ajouter un fichier de test CI/CD
    os.makedirs("tests", exist_ok=True)
    create_test_file("tests/test_app_ci.py", docker=docker)

    # Vérifier ou créer requirements.txt
    requirements_path = "requirements.txt"
    if os.path.exists(requirements_path):
        add_requirements(requirements_path)
    else:
        with open(requirements_path, "w") as f:
            f.write("pytest\npytest-cov\nflake8\n")

    # Créer le workflow GitHub Actions
    create_github_workflow(docker=docker)

    # Créer un README expliquant la CI/CD
    create_readme()

if __name__ == "__main__":
    scan_project()
