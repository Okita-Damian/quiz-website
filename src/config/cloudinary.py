import cloudinary

from config.settings import settings


print("SETTINGS CLOUD NAME:", settings.cloudinary_cloud_name)
print("SETTINGS API KEY:", settings.cloudinary_api_key)
print(
    "SETTINGS API SECRET:",
    bool(settings.cloudinary_api_secret),
)


cloudinary.config(
    cloud_name=settings.cloudinary_cloud_name,
    api_key=settings.cloudinary_api_key,
    api_secret=settings.cloudinary_api_secret,
    secure=True,
)