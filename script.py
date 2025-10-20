
import os
import json

# Criar estrutura de pastas do projeto
project_structure = {
    "backend": [
        "app.py",
        "models.py", 
        "db_init.py",
        "config.py",
        "requirements.txt",
        "import_service.py",
        "utils.py"
    ],
    "frontend": [
        "index.html",
        "app.js",
        "styles.css"
    ],
    "uploads": [],
    "scripts": ["backup.py"]
}

print("Estrutura do projeto:")
print(json.dumps(project_structure, indent=2))
