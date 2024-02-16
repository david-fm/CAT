import cv2
import os
from random import randint
from PIL import ImageFont, ImageDraw, Image
from pathlib import Path
import numpy as np
import numpy.typing as npt
import random
from scipy import ndimage

MatLike = npt.NDArray[np.uint8]

TEXTS_SAMPLE = ["Carne", "Pescado", "Verdura", "Fruta", "Pan", "Bebida", "Lacteos", "Higiene", "Limpieza", "Otros"]
TYPES = ["text", "price", "quantity", "percentage"]

FILE_PATH = os.path.dirname(__file__)
IMAGE_PATH = os.path.join(FILE_PATH, 'resources', 'results')


# TODO : Search for a database of products for the text samples
# TODO IMPROVEMENT: Total and subtotal blocks should be calculated from prices and percentages blocks.

class Block:
    """A block is a rectangle in the image that contains text."""
    def __init__(self, position: tuple, type: str):
        if position.__class__ != tuple and type in TYPES:
            raise TypeError("position must be a tuple or a list")
        elif type not in TYPES and position.__class__ != list:
            raise TypeError("position must be a tuple or a list")
        
        if type.__class__ != str:
            raise TypeError("type must be a string")
        
        self.position = position
        self.type = type
        if type in TYPES:
            self.text, self.value = self.initialize_text()
        else:
            self.text = self.value = type
    
    def initialize_text(self):
        """Return a random text depending on the type of the block."""
        if self.type == "text":
            return TEXTS_SAMPLE[randint(0, len(TEXTS_SAMPLE)-1)], None
        elif self.type == "price":
            # Return a random price between 00,00 and 99,99
            integerpart = randint(0, 99)
            decimalpart = randint(0, 99)
            value = float(str(integerpart) + "." + str(decimalpart))
            return str(integerpart) + "," + str(decimalpart), value
        elif self.type == "quantity":
            value = randint(1, 10)
            return str(value), value
        elif self.type == "percentage":
            value = randint(0, 100)
            return str(value) + "%", value
        else:
            raise ValueError("Invalid type")

    def __repr__(self):
        return f"Block({self.position}, {self.type})"


def add_text_to_image( image: Image, text: str, position: tuple, font_path: str, font_size: int=30):
        
        font = ImageFont.truetype(font_path, font_size)
        img = ImageDraw.Draw(image)
        img.text(position, text, (0,0,0), font=font)


class TicketModifier:
    """This class is used to modify the ticket image."""

    def __init__(self, image_path: str):
        self.image_path = image_path
    
    def modify_image(self, blocks:[Block], font_path:str, font_size:int=30):
        """Modify the image with the given blocks.
        
        Keyword arguments:
        blocks -- a list of Block objects
        
        Returns:
        A PIL image."""
        image = cv2.imread(self.image_path)
        modified_image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(modified_image_rgb)

        for block in blocks:
            if block.type not in TYPES:
                for i in range(len(block.position)):
                    position = block.position[i]
                    add_text_to_image(pil_image, block.text, position, font_path, font_size)
            else:
                add_text_to_image(pil_image, block.text, block.position, font_path, font_size)
        return pil_image
    @staticmethod
    def show_image( image: Image):
        """Show the image created by modify_image."""
        import matplotlib.pyplot as plt

        plt.imshow(image)
        plt.axis("off")
        plt.show()

    @staticmethod
    def cv2_to_pil(image):
        """Convert a cv2 image to a PIL image."""
        return Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    
    @staticmethod
    def pil_to_cv2(image):
        """Convert a PIL image to a cv2 image."""
        return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    @staticmethod
    def rotateTicket(image:MatLike, pixels_max_movement:int=50):
        """Rotate an image perspective """
        initial_points = np.array(
            [
                [0, 0], 
                [0, image.shape[0]], 
                [image.shape[1], 0], 
                [image.shape[1], image.shape[0]]

                ], dtype=np.float32)
        
        movement_matrix = np.array(
            [
                [randint(0, pixels_max_movement), randint(0, pixels_max_movement)],
                [randint(0, pixels_max_movement), randint(-pixels_max_movement, 0)],
                [randint(-pixels_max_movement, 0), randint(0, pixels_max_movement)],
                [randint(-pixels_max_movement, 0), randint(-pixels_max_movement, 0)]
            ], dtype=np.float32)
        
        final_points = initial_points + movement_matrix

        perspective_matrix = cv2.getPerspectiveTransform(initial_points, final_points)
        return (final_points, cv2.warpPerspective(
            image, 
            perspective_matrix, 
            (image.shape[1], image.shape[0])))


    @staticmethod
    def createMask(image: Image, final_points: npt.NDArray[np.float32]):
        """Create a mask for the rotated image"""
        mask = np.zeros_like(image)

        good_points = np.array(
            [
                final_points[0],
                final_points[1],
                final_points[3],
                final_points[2]
            ]
        )

        print(good_points)

        mask = cv2.fillPoly(mask, [good_points.astype(np.int32)], (255, 255, 255))
        
        mask = Image.fromarray(mask).convert("L")

        return mask

    @staticmethod
    def positionTicketOnBackground(background, ticket):
        """Return the center position to place a ticket on a background image without overflows"""

        x = (background.width - ticket.width) // 2
        y = (background.height - ticket.height) // 2
        return x, y

    @staticmethod
    def addTicketToBackground(background: Image, ticket: Image, final_points, x, y):
        """Add a ticket to a background image
        
        Args:
        - background: PIL.Image, the background image
        - ticket: PIL.Image, the ticket image
        - final_points: npt.NDArray[np.float32], the final points of the ticket,
        if rotated with TicketModifier.rotateTicket
        - x: int, x position to place the ticket
        - y: int, y position to place the ticket
        """
        background_copy = background.copy()
        mask = TicketModifier.createMask(
            ticket, 
            final_points)
        

        background_copy.paste(im=ticket, box=(x, y), mask=mask)
        return background_copy
    
    def addBackground(self, pil_image: Image, backgrounds_path: Path, final_points: npt.NDArray[np.float32]):
        """Add a random background to the image."""

        # First we pick a random background from the backgrounds folder

        path = Path(backgrounds_path)
        backgrounds = list(path.glob('*.png'))
        selected = str(backgrounds[randint(0, len(backgrounds)-1)])

        background = cv2.imread(selected)
        background_rgb = cv2.cvtColor(
            background, 
            cv2.COLOR_BGR2RGB)
        
        background = Image.fromarray(background_rgb)

        # Now resize the ticket to a random size between 0.5 and 1

        width, height = pil_image.size
        factor = randint(4, 8) / 10
        pil_image = pil_image.resize((int(width*factor), int(height*factor)))

        # Resize the final points
        final_points = final_points * factor

        position = TicketModifier.positionTicketOnBackground(
            background, 
            pil_image)
        
        background = TicketModifier.addTicketToBackground(
            background, 
            pil_image,
            final_points, 
            *position)
        
        return background

    def save_image(self, image: Image, image_name:str):
        """Save an image to the ground truth folder"""
        path = os.path.join(IMAGE_PATH, image_name+".jpg")
        image.save(path)