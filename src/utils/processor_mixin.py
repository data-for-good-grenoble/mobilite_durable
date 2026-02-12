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
    def get_input_file(cls) -> Path | None:
        return cls.input_file

    @classmethod
    def get_output_file(cls) -> Path | None:
        return cls.output_file

    @classmethod
    def run(
        cls,
        reload_pipeline: bool = False,
        fetch_api_kwargs: dict | None = None,
        fetch_input_kwargs: dict | None = None,
        fetch_output_kwargs: dict | None = None,
        preprocess_kwargs: dict | None = None,
        save_kwargs: dict | None = None,
    ) -> None:
        content = cls.fetch(
            reload_pipeline=reload_pipeline,
            fetch_api_kwargs=fetch_api_kwargs,
            fetch_input_kwargs=fetch_input_kwargs,
            fetch_output_kwargs=fetch_output_kwargs,
            preprocess_kwargs=preprocess_kwargs,
            save_kwargs=save_kwargs,
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
        preprocess_kwargs: dict | None = None,
        save_kwargs: dict | None = None,
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
        preprocess_kwargs = preprocess_kwargs or dict()
        save_kwargs = save_kwargs or dict()

        try:
            preprocessed_data = cls.get_and_save_preprocessed_data(
                fetch_api_kwargs,
                fetch_input_kwargs,
                fetch_output_kwargs,
                preprocess_kwargs,
                save_kwargs,
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
        preprocess_kwargs: dict,
        save_kwargs: dict,
        *,
        reload_pipeline: bool,
        save_input_file: bool,
        save_output_file: bool,
    ) -> Any | None:
        output_file = cls.get_output_file()
        if not reload_pipeline and output_file and output_file.exists():
            return cls.fetch_from_file(output_file, **fetch_output_kwargs)
        else:
            api_content = cls.get_and_save_raw_data(
                fetch_api_kwargs,
                fetch_input_kwargs,
                save_kwargs,
                reload_pipeline=reload_pipeline,
                save_input_file=save_input_file,
            )
            preprocessed_data = cls.pre_process(api_content, **preprocess_kwargs)
            if save_output_file and output_file:
                output_file.parent.mkdir(parents=True, exist_ok=True)
                cls.save(preprocessed_data, output_file, **save_kwargs)
            return preprocessed_data

    @classmethod
    def get_and_save_raw_data(
        cls,
        fetch_api_kwargs: dict,
        fetch_input_kwargs: dict,
        save_kwargs: dict,
        *,
        reload_pipeline: bool,
        save_input_file: bool,
    ) -> Any | None:
        input_file = cls.get_input_file()
        if (
            (cls.api_class is None or not reload_pipeline)
            and input_file
            and input_file.exists()
        ):
            return cls.fetch_from_file(input_file, **fetch_input_kwargs)
        else:
            if cls.api_class is None:
                raise ValueError("api_class is not defined")
            api_content = cls.fetch_from_api(**fetch_api_kwargs)
            if save_input_file and input_file:
                input_file.parent.mkdir(parents=True, exist_ok=True)
                cls.save(api_content, input_file, **save_kwargs)
            return api_content

    @classmethod
    def fetch_from_api(cls, **kwargs):
        raise NotImplementedError

    @classmethod
    def fetch_from_file(cls, path: Path, **kwargs):
        raise NotImplementedError

    @classmethod
    def save(cls, content: Any, path: Path, **kwargs) -> None:
        raise NotImplementedError

    @classmethod
    def pre_process(cls, content: Any | None, **kwargs) -> Any | None:
        return content

    @classmethod
    def post_process(cls, content: Any | None, **kwargs) -> Any | None:
        return content
