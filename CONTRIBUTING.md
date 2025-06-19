# Comment contribuer (WIP)

## main.py

Le fichier `main.py` est le point d'entrée temporaire de votre code.
On va éviter les éventuels `if __name__ == "__main__":` qui sont bien trop spécifiques et poseront des problèmes d'import.
Utilisez plutôt, et de la même façon, la méthode `main`:

```py
def main(**kwargs):
    …
```

Puis exécutez votre script depuis la racine grâce au fichier `main.py`.
```sh
    uv run main.py chemin/de/mon/script.py
```

Dans le `kwargs` vous trouverez les différents arguments fournis de la commande.


## pre-commit

À activer sur votre projet pour appliquer quelques règles/checks sur votre code lors de vos commits.
Actuellement, il active le linter `ruff`. Qui permet d'uniformer votre code python en facilitant la maintenance et les reviews.
S'il détecte des anomalies, il `refusera votre commit`, lintera votre code et vous pourrez/devrez alors re-commiter ces nouveaux changements.

Vous pouvez l'installer sur votre projet avec :
```
pre-commit install
```

C'est actuellement facultatif si vous utilisez déjà ruff dans votre IDE.


## Logger

Vous pouvez(devez) utiliser les loggers pour afficher les messages utiles lors de l'exécution de votre code.

```py

import logging

logger = logging.getLogger(__name__)
…

logger.warning("mon message")

```

Ces logs seront présents à 3 endroits :
1. Dans la console
2. Dans le fichier `errors.log` à la racine du projet (non versionné)
3. Dans le fichier `errors.jsonl` à la racine du projet (non versionné)

