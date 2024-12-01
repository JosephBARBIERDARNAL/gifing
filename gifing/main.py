import numpy as np
import imageio
from PIL import Image, ImageFile, ImageDraw, ImageFont
from PIL.Image import Resampling
from typing import Union, Tuple, List, Optional
import importlib.resources as pkg_resources
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

        Parameters
        - file_path: List of file paths to the images to be included in the GIF.
        - frame_duration: Duration of each frame in milliseconds.
        - n_repeat_last_frame: The number of additional frames to append with the last image.
        """
        self.file_path = file_path
        self.frame_duration = frame_duration
        self.n_repeat_last_frame = n_repeat_last_frame
        self.size = (500, 500)
        self.scale = 1
        self.background_color = (255, 255, 255)
        self.label_loc = None
        self.labels = None
        self.images_for_gif = None
        self.shadow_offset = 10
        self.box_padding = 10
        ImageFile.LOAD_TRUNCATED_IMAGES = True

    def set_size(
        self,
        size: Tuple[int, int],
        scale: int = 1,
    ):
        """
        Set the size (width, height) and scale (default 1) of each image.

        Parameters
        - size: The size of the output GIF (width, height) in pixels.
        - scale: Scaling factor to adjust the size of the images in the GIF.
        """
        self.size = size
        self.scale = scale

    def set_background_color(
        self,
        background_color: Union[str, Tuple[int, int, int]],
    ) -> None:
        """
        Set the background color to use when images have different size.

        Parameters
        - background_color: The RGB color, hex color or string name of the
        background for each frame. Default is (255, 255, 255) (white). Strings
        can be names of colors such as "white", "black", "red", "green",
        "blue", "yellow", "cyan", "magenta", "gray", "orange", "purple" or "pink".
        """
        if isinstance(background_color, str):
            background_color = _strcolor_to_rgb(background_color)
        self.background_color = background_color

    def set_labels(
        self,
        labels: List[str],
        font_size: int = 20,
        loc: str = "top left",
        text_padding: int = 10,
        box_padding: int = 10,
        shadow_offset: int = 10,
    ) -> None:
        """
        Set labels for specific frames in the GIF.

        Parameters
        - labels: a list of strings of the same length as the number of images.
        - font_size: size of the font in pixels.
        - loc: one of "top left", "top right", "bottom left", "bottom right".
        - text_padding: text padding in pixels
        - box_padding: box padding in pixels
        - shadow_offset: offset of the box shadow
        """
        if loc not in ["top left", "top right", "bottom left", "bottom right"]:
            raise ValueError(
                "Invalid loc. Choose from: "
                "'top left', 'top right', 'bottom left', 'bottom right'."
            )
        self.labels = labels
        self.font_size = font_size
        self.label_loc = loc
        self.text_padding = text_padding
        self.box_padding = box_padding
        self.shadow_offset = shadow_offset

    def make(
        self,
        output_path: str = "./output.gif",
    ) -> None:
        """
        Make (and save) a GIF.

        - output_path: path where the output GIF will be saved.
        """
        self.output_path = output_path

        images_for_gif = []

        self.dim = (self.size[0] * self.scale, self.size[1] * self.scale)

        if not self.output_path.endswith(".gif"):
            warnings.warn("The output path does not have a '.gif' extension.")
            self.output_path += ".gif"

        for i, filename in enumerate(self.file_path):
            with Image.open(filename) as img:
                img = self._format_image(img)
                if self.labels is not None:
                    self._draw_label(img, frame_idx=i)
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
        """
        Retrieve a list with all the images
        """
        return self.images_for_gif

    def _format_image(self, image):
        img_w, img_h = image.size
        bg_w, bg_h = self.size
        self.bg_w = bg_w
        self.bg_h = bg_h
        scale = min(bg_w / img_w, bg_h / img_h)
        new_w = int(img_w * scale)
        new_h = int(img_h * scale)
        image = image.resize((new_w, new_h), Resampling.LANCZOS)
        new_image = Image.new("RGB", self.size, self.background_color)
        new_image.paste(image, ((bg_w - new_w) // 2, (bg_h - new_h) // 2))
        return new_image

    def _draw_label(self, img, frame_idx: Optional[int] = None) -> None:
        label_text = self.labels[frame_idx]
        draw = ImageDraw.Draw(img)
        with pkg_resources.path("gifing.fonts", "Urbanist-Bold.ttf") as font_path:
            font = ImageFont.truetype(font_path, self.font_size)

        text_bbox = draw.textbbox(
            (0, 0), label_text, font=font, font_size=self.font_size
        )
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        if self.label_loc == "top left":
            x = self.text_padding
            y = self.text_padding
        elif self.label_loc == "top right":
            x = self.bg_w - text_width - self.text_padding
            y = self.text_padding
        elif self.label_loc == "bottom left":
            x = self.text_padding
            y = self.bg_h - text_height - self.text_padding
        elif self.label_loc == "bottom right":
            x = self.bg_w - text_width - self.text_padding
            y = self.bg_h - text_height - self.text_padding

        baseline_correction = (text_height - (text_bbox[3] - text_bbox[1])) // 2
        y_centered = y + baseline_correction

        box_coords = [
            x - self.box_padding,
            y - self.box_padding,
            x + text_width + self.box_padding,
            y + text_height + self.box_padding,
        ]

        shadow_coords = [coord + self.shadow_offset for coord in box_coords]

        draw.rectangle(shadow_coords, fill=(50, 50, 50, 128))
        draw.rectangle(box_coords, fill=(255, 255, 255))
        draw.text((x, y_centered), label_text, font=font, fill=(0, 0, 0))
