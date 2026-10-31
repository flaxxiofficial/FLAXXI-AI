import os
import torch

from PIL import Image
from diffusers import StableDiffusionInpaintPipeline

MODEL_PATH = os.getenv(
    "IMAGE_MODEL_PATH",
    "models/image-inpainting"
)

pipeline = None


def load_model():

    global pipeline

    if pipeline is None:

        if not os.path.exists(MODEL_PATH):
            raise RuntimeError("Image model is not installed")

        pipeline = StableDiffusionInpaintPipeline.from_pretrained(
            MODEL_PATH,
            torch_dtype=torch.float32,
            local_files_only=True
        )

        pipeline.to("cpu")

    return pipeline


def edit_image(image_path,mask_path,prompt,output_path):

    model = load_model()

    image = Image.open(image_path).convert("RGB")

    mask = Image.open(mask_path).convert("RGB")

    mask = mask.resize(image.size)

    result = model(
        prompt=prompt,
        image=image,
        mask_image=mask,
        num_inference_steps=25
    ).images[0]

    result.save(output_path)

    return output_path
