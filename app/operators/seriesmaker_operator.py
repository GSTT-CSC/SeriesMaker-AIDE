import logging
from numpy.random import shuffle
from typing import List
from pydicom.uid import generate_uid

import monai.deploy.core as md
from monai.deploy.core import DataPath, ExecutionContext, InputContext, IOType, Operator, OutputContext
from monai.deploy.core.domain.dicom_series_selection import StudySelectedSeries
from monai.deploy.operators.dicom_utils import save_dcm_file, random_with_n_digits


@md.input("study_selected_series_list", List[StudySelectedSeries], IOType.IN_MEMORY)
@md.output("new_dicom_series", DataPath, IOType.DISK)
@md.env(pip_packages=["pydicom >= 2.4.2"])
class SeriesMakerOperator(Operator):
    """
    This operator writes a new DICOM Series based on the input DICOM Series
    """

    def compute(self, op_input: InputContext, op_output: OutputContext, context: ExecutionContext):

        logging.info(f"Begin {self.compute.__name__}")

        study_selected_series_list = op_input.get("study_selected_series_list")

        output_dir = op_output.get().path
        output_dir.mkdir(parents=True, exist_ok=True)

        logging.info("Starting new DICOM Series creation process ...")
        self.edit_and_make_new_dicom_series(study_selected_series_list, output_dir)
        logging.info("New DICOM Series created.")

        logging.info(f"End {self.compute.__name__}")

    def edit_and_make_new_dicom_series(self, study_selected_series_list, output_dir):
        """
        Takes an existing DICOM Series, edits some metadata and saves a new DICOM Series

        Function structure inspired by:
        https://github.com/Project-MONAI/monai-deploy-app-sdk/blob/main/monai/deploy/operators/dicom_series_to_volume_operator.py#L26
        and write_common_modules dicom_utils.py:
        https://github.com/Project-MONAI/monai-deploy-app-sdk/blob/978f28c62d00f653beb895176947a631c342c69b/monai/deploy/operators/dicom_utils.py#L124

        NB: currently only supports one DICOM Series within the Study
        """

        if not study_selected_series_list or len(study_selected_series_list) < 1:
            raise ValueError("Missing expected input 'study_selected_series_list'")

        logging.info("Parsing input DICOM Series ...")

        for study_selected_series in study_selected_series_list:
            if not isinstance(study_selected_series, StudySelectedSeries):
                raise ValueError("Element in input is not expected type, 'StudySelectedSeries'.")
            selected_series = study_selected_series.selected_series[0]
            dicom_series = selected_series.series

            dicom_instances = dicom_series.get_sop_instances()
            num_instances_in_series = len(dicom_instances)

            # Define new Series level DICOM tags
            new_series_instance_uid = generate_uid()
            new_series_number = str(random_with_n_digits(4))  # 4 digit number to avoid conflict
            new_series_description = "DICOM generated by SeriesMaker-AIDE - CAUTION: Not for Diagnostic Use."

            logging.info("Editing and Writing output DICOM Series ...")
            for idx, dcm_instance in enumerate(dicom_instances):

                # get pydicom Dataset object
                ds = dcm_instance.get_native_sop_instance()

                # Define new Instance level DICOM tags
                new_sop_instance_uid = generate_uid()

                logging.info(f"Writing DICOM file: {idx + 1} of {num_instances_in_series} ...")

                # Edit DICOM tags
                ds.SOPInstanceUID = new_sop_instance_uid
                ds.SeriesInstanceUID = new_series_instance_uid
                ds.SeriesNumber = new_series_number
                ds.SeriesDescription = new_series_description

                logging.info(f"New SOPInstanceUID: {ds.SOPInstanceUID}")
                logging.info(f"New SeriesInstanceUID: {ds.SeriesInstanceUID}")
                logging.info(f"New SeriesNumber: {ds.SeriesNumber}")
                logging.info(f"New InstanceNumber: {ds.InstanceNumber}")

                # Shuffle pixel_array, so obviously not diagnostic
                arr = ds.pixel_array
                shuffle(arr)
                shuffle(arr.T)
                ds.PixelData = arr.tobytes()
                logging.info("Shuffling PixelData ...")

                # Instance file name defined as the new SOPInstanceUID
                file_path = output_dir.joinpath(f"{ds.SOPInstanceUID}.dcm")
                save_dcm_file(ds, file_path)

            # Break since limited to one selected_series for now
            break
