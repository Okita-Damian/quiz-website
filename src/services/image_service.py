import asyncio
import io

import cloudinary
import cloudinary.uploader

from huggingface_hub import InferenceClient
from errorHandlers.exceptions import NotFoundError

import config.cloudinary

from config.settings import settings


# -------------------------
# Hugging Face Configuration
# -------------------------

IMAGE_MODEL = (
    "black-forest-labs/FLUX.1-schnell"
)


# -------------------------
# Hugging Face Client
# -------------------------

client = InferenceClient(
    provider="auto",
    api_key=settings.hf_token,
)


# -------------------------
# Generate Image
# -------------------------

async def generate_image(
    image_prompt: str,
) -> str:

    if not image_prompt:
        raise NotFoundError(
            "An image prompt is required."
        )

    # -------------------------
    # Generate Image
    # -------------------------

    try:

        image = await asyncio.to_thread(
            client.text_to_image,
            prompt=image_prompt,
            model=IMAGE_MODEL,
        )

    except Exception as error:

        print(
            "HUGGING FACE ERROR:",
            repr(error),
        )

        raise NotFoundError(
            "Hugging Face image generation "
            "failed."
        ) from error

    if image is None:

        raise NotFoundError(
            "Hugging Face did not return "
            "an image."
        )

    # -------------------------
    # Convert Image To Bytes
    # -------------------------

    image_file = io.BytesIO()

    try:

        image.save(
            image_file,
            format="PNG",
        )

        image_file.seek(0)

    except Exception as error:

        print(
            "IMAGE CONVERSION ERROR:",
            repr(error),
        )

        raise NotFoundError(
            "The generated image could "
            "not be converted."
        ) from error

    # -------------------------
    # Upload To Cloudinary
    # -------------------------

    try:

        upload_result = (
            cloudinary.uploader.upload(
                image_file,
                folder="education/questions",
                resource_type="image",
            )
        )

    except Exception as error:

        print(
            "CLOUDINARY ERROR:",
            repr(error),
        )

        raise NotFoundError(
            "The generated image could "
            "not be uploaded to Cloudinary."
        ) from error

    # -------------------------
    # Get Cloudinary URL
    # -------------------------

    cloudinary_url = (
        upload_result.get(
            "secure_url"
        )
    )

    if not cloudinary_url:

        raise NotFoundError(
            "Cloudinary did not return "
            "an image URL."
        )

    return cloudinary_url




    