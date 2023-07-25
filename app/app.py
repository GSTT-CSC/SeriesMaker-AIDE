"""
SeriesMaker-AIDE

app.py - constructs app workflow
"""
import json
import logging
from pathlib import Path
import monai.deploy.core as md

from monai.deploy.core import Application, resource
from monai.deploy.operators import (
    DICOMDataLoaderOperator,
    DICOMSeriesSelectorOperator,
    DICOMSeriesToVolumeOperator,
)
from operators.seriesmaker_operator import SeriesMakerOperator


config = json.load(
    open(Path(__file__).resolve().parent / "app_config.json")
)
requirements_file = (
    Path(__file__).resolve().parent / "requirements.txt"
)


@resource(
    cpu=config["resources"]["cpu"],
    gpu=config["resources"]["gpu"],
    memory=config["resources"]["memory"],
)
@md.env(pip_packages=requirements_file.as_posix())
class SeriesMakerApp(Application):
    """
    This class defines the application.
    """

    def __init__(self, *args, **kwargs):
        """Creates an application instance."""
        super().__init__(*args, **kwargs)

        self._logger = logging.getLogger("{}.{}".format(__name__, type(self).__name__))

        self.name = config["info"]["name"]
        self.description = config["info"]["description"]
        self.application_version = config["info"]["application_version"]

    def compose(self):
        """
        Construct operators workflow
        """

        logging.info(f"Begin {self.compose.__name__}")

        study_loader_op = DICOMDataLoaderOperator()
        series_selector_op = DICOMSeriesSelectorOperator()
        series_to_vol_op = DICOMSeriesToVolumeOperator()
        new_series_op = SeriesMakerOperator()

        self.add_flow(
            study_loader_op,
            series_selector_op,
            {"dicom_study_list": "dicom_study_list"})
        self.add_flow(
            series_selector_op,
            new_series_op,
            {"study_selected_series_list": "study_selected_series_list"}
        )

        logging.info(f"End {self.compose.__name__}")


if __name__ == "__main__":
    SeriesMakerApp(do_run=True)
