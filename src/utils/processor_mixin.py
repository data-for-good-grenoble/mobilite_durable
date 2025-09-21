from pathlib import Path
from typing import Any, Type


class ProcessorMixin:
    """
    api_class va permettre d'aller récupérer la donnée en ligne
    input_file va permettre de trouver le fichier d'entrée, sauvegarde non modifiée de l'api_class
    output_file va permettre de trouver le fichier de sortie, sauvegarde modifiée de l'input_file
    """

    api_class: Type | None = None
    input_dir: Path | None = None
    input_file: Path | None = None
    output_dir: Path | None = None
    output_file: Path | None = None

    def __init__(self, *args, **kwargs):
        raise Exception("Utility class")

    @classmethod
    def run(cls, reload_pipeline: bool = False) -> None:
        content = cls.fetch(reload_pipeline=reload_pipeline)

        if cls.output_file and (reload_pipeline or not cls.output_file.exists()):
            cls.save(content, cls.output_file)

    @classmethod
    def fetch(cls, reload_pipeline: bool = False) -> Any:
        """
        Récupère la donnée et la sauvegarde si besoin
        Il existe 3 niveaux d'informations : celle de l'api, celle de l'input_file et celle de l'output_file
        Lors d'un process où `reload_pipeline` is False (cas par défaut) :
            - on va regarder l'output_file, s'il n'existe pas ou s'il n'est pas configuré
            - on va regarder l'input_file, que l'on va procésser, s'il n'existe pas ou s'il n'est pas configuré
            - on va regarder l'api_class, pour télécharger la donnée et la sauvegarder, s'il n'existe pas, une exception est levée
        Lors d'un process où `reload_pipeline` is True, le process est inversé
        """

        # TODO: fetch_from_api si le fichier de l'url a été mis à jour
        def fetch_from_api():
            if cls.api_class:
                content = cls.fetch_from_api()
                if cls.input_file:
                    cls.save(content, cls.input_file)
                return fetch_from_loaded_input_file(content)

        def fetch_from_loaded_input_file(content):
            processed = cls.pre_process(content)
            if cls.output_file:
                cls.save(processed, cls.output_file)
            return processed

        def fetch_from_input_file():
            if cls.input_file and cls.input_file.exists():
                content = cls.fetch_from_file(cls.input_file)
                return fetch_from_loaded_input_file(content)

        def fetch_from_output_file():
            if cls.output_file and cls.output_file.exists():
                return cls.fetch_from_file(cls.output_file)

        methods = [fetch_from_api, fetch_from_input_file, fetch_from_output_file]
        if not reload_pipeline:
            methods = methods[::-1]

        for method in methods:
            content = method()
            if content is not None:
                return content

        raise Exception

    @classmethod
    def fetch_from_api(cls, **kwargs):
        raise NotImplementedError

    @classmethod
    def fetch_from_file(cls, path: Path, **kwargs):
        raise NotImplementedError

    @classmethod
    def save(cls, content, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)

    @classmethod
    def pre_process(cls, content, **kwargs):
        return content
