from huggingface_hub import InferenceClient

from config.settings import settings


print(
    "HF TOKEN CONFIGURED:",
    bool(settings.hf_token),
)


client = InferenceClient(
    provider="auto",
    api_key=settings.hf_token,
    timeout=180,
)


try:

    image = client.text_to_image(
        prompt=(
            "A simple educational illustration "
            "of the solar system for primary "
            "school children."
        ),
        model="black-forest-labs/FLUX.1-schnell",
    )

    image.save(
        "test_flux.png"
    )

    print(
        "FLUX IMAGE GENERATED SUCCESSFULLY"
    )

except Exception as error:

    print(
        "HUGGING FACE ERROR:",
        repr(error),
    )