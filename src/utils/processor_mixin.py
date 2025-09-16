import logging
from pathlib import Path
from typing import Any, Type

logger = logging.getLogger(__name__)


class ProcessorMixin:
    """
    api_class est la classe de l'API
    input_file va permettre de trouver le fichier d'entrée, sauvegarde non modifiée de l'api_class
    output_file va permettre de trouver le fichier de sortie, sauvegarde de l'input_file modifiée par `pre_process`
    la data en sortie est le contenu de l'output_file sur lequel on a appliqué `post_process`
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
            - on va regarder l'output_file, sur lequel on va appliquer `postprocess`, s'il n'existe pas ou s'il n'est pas configuré
            - on va regarder l'input_file, sur lequel on va appliquer `preprocess`, s'il n'existe pas ou s'il n'est pas configuré
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
            if content is None:
                logger.error(f"{cls.__name__}: cannot save because `content` attribute is None")
            else:
                cls.input_file.parent.mkdir(parents=True, exist_ok=True)
                cls.save(content, cls.input_file)
        return content

    @classmethod
    def fetch_and_save_from_input_file(cls, content=None, save: bool = True):
        if content is None and cls.input_file:
            if cls.input_file.exists():
                content = cls.fetch_from_file(cls.input_file)
            else:
                logger.warning(f"{cls.__name__}: {cls.input_file} does not exist")

        processed = cls.pre_process(content)
        if save and cls.output_file:
            if processed is None:
                logger.error(
                    f"{cls.__name__}: cannot save because `processed` attribute is None"
                )
            else:
                cls.output_file.parent.mkdir(parents=True, exist_ok=True)
                cls.save(processed, cls.output_file)
        return processed

    @classmethod
    def fetch_from_output_file(cls, content=None):
        if content is None and cls.output_file:
            if cls.output_file.exists():
                content = cls.fetch_from_file(cls.output_file)
            else:
                logger.warning(f"{cls.__name__}: {cls.output_file} does not exist")

        return cls.post_process(content)

    @classmethod
    def fetch_from_api(cls, **kwargs):
        raise NotImplementedError

    @classmethod
    def fetch_from_file(cls, path: Path, **kwargs):
        raise NotImplementedError

    @classmethod
    def save(cls, content, path: Path) -> None:
        raise NotImplementedError

    @classmethod
    def pre_process(cls, content, **kwargs):
        return content

    @classmethod
    def post_process(cls, content, **kwargs):
        return content
