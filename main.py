import argparse
import logging
import sys
from datetime import datetime
from importlib.util import module_from_spec, spec_from_file_location

from src.utils.logger import setup_logger

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Lance un script")
    parser.add_argument(
        "filename",
        type=str,
        help="Chemin vers le fichier de script, format python",
    )
    args = parser.parse_args()

    spec = spec_from_file_location(args.filename, args.filename)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)

    logger = setup_logger(level=logging.INFO)

    start = datetime.now()

    if hasattr(module, "main"):
        module.main(**args.__dict__)
    else:
        logger.error("Erreur : le script n'a pas de méthode main")
        sys.exit(1)

    end = datetime.now()
    logger.info(f"Duration: {end - start}s")
