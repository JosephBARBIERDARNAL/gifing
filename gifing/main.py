import numpy as np
import imageio
from PIL import Image, ImageFile
from PIL.Image import Resampling
from typing import Union, Tuple, List
import warnings

from .utils.colors import _strcolor_to_rgb


class Gif:
    def __init__(
        self,
        file_path: List[str],
        frame_duration: int = 1000,
        n_repeat_last_frame: int = 1,
    ):
        """
        Initialize the GIF maker.

        :param file_path: List of file paths to the images to be included in the GIF.
        :param frame_duration: Duration of each frame in milliseconds.
        :param n_repeat_last_frame: The number of additional frames to append with the last image.
        """
        self.file_path = file_path
        self.frame_duration = frame_duration
        self.n_repeat_last_frame = n_repeat_last_frame
        self.size = (1000, 1000)
        self.scale = 1
        self.background_color = (255, 255, 255)

        ImageFile.LOAD_TRUNCATED_IMAGES = True

    def set_size(
        self,
        size: Tuple[int, int],
        scale: int = 1,
    ):
        """
        :param size: The size of the output GIF (width, height) in pixels.
        :param scale: Scaling factor to adjust the size of the images in the GIF.
        """
        self.size = size
        self.scale = scale

    def set_background_color(
        self,
        background_color: Union[str, Tuple[int, int, int]],
    ) -> None:
        """
        :param background_color: The RGB color or string name of the background for each frame.
        Default is (255, 255, 255) (white). Strings can be names of colors such as "white", "black",
        "red", "green", "blue", "yellow", "cyan", "magenta", "gray", "orange", "purple" or "pink".
        :returns: None
        """
        if isinstance(background_color, str):
            background_color = _strcolor_to_rgb(background_color)
        self.background_color = background_color

    def make(
        self,
        output_path: str = "./output.gif",
    ) -> None:
        """
        Creates and saves a GIF.

        :param output_path: Path where the output GIF will be saved. Default is "./output.gif".
        :returns: None
        """
        self.output_path = output_path

        images_for_gif = []

        self.dim = (self.size[0] * self.scale, self.size[1] * self.scale)

        if not self.output_path.endswith(".gif"):
            warnings.warn("The output path does not have a '.gif' extension.")
            self.output_path += ".gif"

        for filename in self.file_path:
            with Image.open(filename) as img:
                img = self._format_image(img)
                img_array = np.array(img)
                images_for_gif.append(img_array)

        last_frame = images_for_gif[-1]
        for _ in range(self.n_repeat_last_frame):
            images_for_gif.append(last_frame)

        self.images_for_gif = images_for_gif

        imageio.mimsave(
            f"{output_path}",
            self.images_for_gif,
            duration=[self.frame_duration] * len(self.images_for_gif),
            format="GIF",
            loop=0,
        )
        print(f"GIF created and saved at {output_path}")

    def get_images(self) -> List:
        return self.images_for_gif

    def _format_image(self, image):
        """
        :param image: The image to be resized and placed on a background.
        """
        img_w, img_h = image.size
        bg_w, bg_h = self.size
        scale = min(bg_w / img_w, bg_h / img_h)
        new_w = int(img_w * scale)
        new_h = int(img_h * scale)
        image = image.resize((new_w, new_h), Resampling.LANCZOS)
        new_image = Image.new("RGB", self.size, self.background_color)
        new_image.paste(image, ((bg_w - new_w) // 2, (bg_h - new_h) // 2))
        return new_image
