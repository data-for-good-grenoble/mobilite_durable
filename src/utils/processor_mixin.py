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
    ) -> Any | None:
        """
        Récupère la donnée et la sauvegarde si besoin
        Il existe 3 niveaux d'informations : celle de l'api, celle de l'input_file et celle de l'output_file
        Si `reload_pipeline` is `False` (cas par défaut) :
            - on va regarder l'output_file, sur lequel on va appliquer `postprocess`, s'il n'existe pas ou s'il n'est pas configuré
            - on va regarder l'input_file, sur lequel on va appliquer `preprocess`, s'il n'existe pas ou s'il n'est pas configuré
            - on va regarder la méthode `fetch_from_api`, pour télécharger la donnée et la sauvegarder
        Si `reload_pipeline` is `True`, le process est inversé
        """
        fetch_api_kwargs = fetch_api_kwargs or dict()
        fetch_input_kwargs = fetch_input_kwargs or dict()
        fetch_output_kwargs = fetch_output_kwargs or dict()

        try:
            preprocessed_data = cls.get_and_save_preprocessed_data(
                fetch_api_kwargs,
                fetch_input_kwargs,
                fetch_output_kwargs,
                reload_pipeline=reload_pipeline,
                save_input_file=fetch_input_kwargs.get("save_input_file", True),
                save_output_file=fetch_output_kwargs.get("save_output_file", True),
            )
            return cls.post_process(preprocessed_data)
        except Exception as e:
            if not reload_pipeline:
                # Input or output file can be no more compatible with code, we try reload pipeline
                logger.exception(e)
                return cls.fetch(
                    True, fetch_api_kwargs, fetch_input_kwargs, fetch_output_kwargs
                )
            else:
                # Nothing to retry, raise the exception to avoid infinite loop
                raise e

    @classmethod
    def get_and_save_preprocessed_data(
        cls,
        fetch_api_kwargs: dict,
        fetch_input_kwargs: dict,
        fetch_output_kwargs: dict,
        *,
        reload_pipeline: bool,
        save_input_file: bool,
        save_output_file: bool,
    ) -> Any | None:
        if not reload_pipeline and cls.output_file and cls.output_file.exists():
            return cls.fetch_from_file(cls.output_file, **fetch_output_kwargs)
        else:
            api_content = cls.get_and_save_raw_data(
                fetch_api_kwargs,
                fetch_input_kwargs,
                reload_pipeline=reload_pipeline,
                save_input_file=save_input_file,
            )
            preprocessed_data = cls.pre_process(api_content)
            if save_output_file and cls.output_file:
                cls.output_file.parent.mkdir(parents=True, exist_ok=True)
                cls.save(preprocessed_data, cls.output_file)
            return preprocessed_data

    @classmethod
    def get_and_save_raw_data(
        cls,
        fetch_api_kwargs: dict,
        fetch_input_kwargs: dict,
        *,
        reload_pipeline: bool,
        save_input_file: bool,
    ) -> Any | None:
        if not reload_pipeline and cls.input_file and cls.input_file.exists():
            return cls.fetch_from_file(cls.input_file, **fetch_input_kwargs)
        else:
            api_content = cls.fetch_from_api(**fetch_api_kwargs)
            if save_input_file and cls.input_file:
                cls.input_file.parent.mkdir(parents=True, exist_ok=True)
                cls.save(api_content, cls.input_file)
            return api_content

    @classmethod
    def fetch_from_api(cls, **kwargs):
        raise NotImplementedError

    @classmethod
    def fetch_from_file(cls, path: Path, **kwargs):
        raise NotImplementedError

    @classmethod
    def save(cls, content: Any, path: Path) -> None:
        raise NotImplementedError

    @classmethod
    def pre_process(cls, content: Any | None, **kwargs) -> Any | None:
        return content

    @classmethod
    def post_process(cls, content: Any | None, **kwargs) -> Any | None:
        return content
