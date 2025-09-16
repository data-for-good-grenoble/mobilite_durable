import logging
from pathlib import Path
from typing import Any, Type

logger = logging.getLogger(__name__)


class ProcessorMixin:
    """
    api_class est la classe de l'API
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
    def run(
        cls,
        reload_pipeline: bool = False,
        fetch_api_kwargs: dict | None = None,
        fetch_input_kwargs: dict | None = None,
        fetch_output_kwargs: dict | None = None,
    ) -> None:
        content = cls.fetch(
            reload_pipeline=reload_pipeline,
            fetch_api_kwargs=fetch_api_kwargs,
            fetch_input_kwargs=fetch_input_kwargs,
            fetch_output_kwargs=fetch_output_kwargs,
        )
        if content is None:
            logger.warning(f"{cls.__name__}: have no content")

    @classmethod
    def fetch(
        cls,
        reload_pipeline: bool = False,
        fetch_api_kwargs: dict | None = None,
        fetch_input_kwargs: dict | None = None,
        fetch_output_kwargs: dict | None = None,
    ) -> Any:
        """
        Récupère la donnée et la sauvegarde si besoin
        Il existe 3 niveaux d'informations : celle de l'api, celle de l'input_file et celle de l'output_file
        Lors d'un process où `reload_pipeline` is False (cas par défaut) :
            - on va regarder l'output_file, s'il n'existe pas ou s'il n'est pas configuré
            - on va regarder l'input_file, que l'on va procésser, s'il n'existe pas ou s'il n'est pas configuré
            - on va regarder l'api_class, pour télécharger la donnée et la sauvegarder
        Lors d'un process où `reload_pipeline` is True, le process est inversé
        """
        fetch_api_kwargs = fetch_api_kwargs or dict()
        fetch_input_kwargs = fetch_input_kwargs or dict()
        fetch_output_kwargs = fetch_output_kwargs or dict()

        if reload_pipeline:
            api_content = cls.fetch_and_save_from_api(**fetch_api_kwargs)
            input_content = cls.fetch_and_save_from_input_file(
                api_content, **fetch_input_kwargs
            )
            output_content = cls.fetch_from_output_file(input_content, **fetch_output_kwargs)
        else:
            output_content = cls.fetch_from_output_file(**fetch_output_kwargs)
            if output_content is None:
                input_content = cls.fetch_and_save_from_input_file(**fetch_input_kwargs)
                if input_content is None:
                    api_content = cls.fetch_and_save_from_api(**fetch_api_kwargs)
                    input_content = cls.fetch_and_save_from_input_file(
                        api_content, **fetch_input_kwargs
                    )
                output_content = cls.fetch_from_output_file(
                    input_content, **fetch_output_kwargs
                )
        return output_content

    @classmethod
    def fetch_and_save_from_api(cls, content=None, save: bool = True):
        if content is None and cls.api_class:
            content = cls.fetch_from_api()

        if save and cls.input_file:
            cls.save(content, cls.input_file)
        return content

    @classmethod
    def fetch_and_save_from_input_file(cls, content=None, save: bool = True):
        if content is None and cls.input_file:
            content = cls.fetch_from_file(cls.input_file)

        processed = cls.pre_process(content)
        if save and cls.output_file:
            cls.save(processed, cls.output_file)
        return processed

    @classmethod
    def fetch_from_output_file(cls, content=None):
        if content is None and cls.output_file:
            content = cls.fetch_from_file(cls.output_file)

        return cls.post_process(content)

    @classmethod
    def fetch_from_api(cls, **kwargs):
        raise NotImplementedError

    @classmethod
    def fetch_from_file(cls, path: Path, **kwargs):
        if not path.exists():
            logger.warning(f"{cls.__name__}: {path} does not exist")
            return
        # TODO: logic

    @classmethod
    def save(cls, content, path: Path) -> None:
        if content is None:
            logger.error(f"{cls.__name__}: cannot save because `content` attribute is None")
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        # TODO: logic

    @classmethod
    def pre_process(cls, content, **kwargs):
        return content

    @classmethod
    def post_process(cls, content, **kwargs):
        return content
