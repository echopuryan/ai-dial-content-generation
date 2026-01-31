import asyncio
from datetime import datetime

from task._models.custom_content import Attachment
from task._utils.constants import API_KEY, DIAL_URL, DIAL_CHAT_COMPLETIONS_ENDPOINT
from task._utils.bucket_client import DialBucketClient
from task._utils.model_client import DialModelClient
from task._models.message import Message
from task._models.role import Role

class Size:
    """
    The size of the generated image.
    """
    square: str = '1024x1024'
    height_rectangle: str = '1024x1792'
    width_rectangle: str = '1792x1024'


class Style:
    """
    The style of the generated image. Must be one of vivid or natural.
     - Vivid causes the model to lean towards generating hyper-real and dramatic images.
     - Natural causes the model to produce more natural, less hyper-real looking images.
    """
    natural: str = "natural"
    vivid: str = "vivid"


class Quality:
    """
    The quality of the image that will be generated.
     - ‘hd’ creates images with finer details and greater consistency across the image.
    """
    standard: str = "standard"
    hd: str = "hd"

async def _save_images(attachments: list[Attachment]):
    async with DialBucketClient(
            api_key=API_KEY,
            base_url=DIAL_URL
    ) as bucket_client:
        for idx, attachment in enumerate(attachments):
            if attachment.type and attachment.type == 'image/png':

                image_bytes = await bucket_client.get_file(attachment.url)

                file_name = f"generated_image_{idx+1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                with open(file_name, "wb") as image_file:
                    image_file.write(image_bytes)

                print(f"Image saved locally as {file_name}")


def start() -> None:
    client = DialModelClient(
        endpoint=DIAL_CHAT_COMPLETIONS_ENDPOINT,
        deployment_name="dall-e-3",
        api_key=API_KEY
    )
    response = client.get_completion(
        messages=[
            Message(
                role=Role.USER,
                content="Sunny day on Bali",
            )
        ],
        custom_fields={
            "image_generation": {
                "size": Size.square,
                "style": Style.natural,
                "quality": Quality.hd
            }
        }
    )
    attachments = response.custom_content.attachments if response.custom_content else []
    asyncio.run(_save_images(attachments))


start()
