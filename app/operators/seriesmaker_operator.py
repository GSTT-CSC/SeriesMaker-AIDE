import logging
import monai.deploy.core as md
from monai.deploy.core import DataPath, ExecutionContext, Image, InputContext, IOType, Operator, OutputContext


@md.input("image", Image, IOType.IN_MEMORY)
@md.output("image", DataPath, IOType.DISK)
@md.env(pip_packages=["pydicom >= 2.4.2"])
class SeriesMakerOperator(Operator):
    """
    This operator writes a new DICOM Series based on the input DICOM Series
    """

    def compute(self, op_input: InputContext, op_output: OutputContext, context: ExecutionContext):

        logging.info(f"Begin {self.compute.__name__}")

        input_path = op_input.get("image")
        output_dir = op_output.get().path
        output_dir.mkdir(parents=True, exist_ok=True)

        logging.info("Creating new DICOM Series ...")
        self.edit_and_make_new_dicom_series(input_path, output_dir)
        logging.info("New DICOM Series created ...")

        logging.info(f"End {self.compute.__name__}")

    def edit_and_make_new_dicom_series(self, image, path):
        """
        Takes and existing DICOM Series, edits some metadata and saves a new DICOM Series
        """
        # image_data = image.asnumpy()
        # image_shape = image_data.shape
        #
        # num_images = image_shape[0]
        #
        # for i in range(0, num_images):
        #     input_data = image_data[i, :, :]
        #     pil_image = PILImage.fromarray(input_data)
        #     if pil_image.mode != "RGB":
        #         pil_image = pil_image.convert("RGB")
        #     pil_image.save(join(str(path), join(str(i) + ".png")))
        pass
