import cv2
import os
from random import randint
from PIL import ImageFont, ImageDraw, Image

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
    
    def show_image(self, image: Image):
        """Show the image created by modify_image."""
        import matplotlib.pyplot as plt

        plt.imshow(image)
        plt.axis("off")
        plt.show()

    def save_image(self, image: Image, image_name:str):
        """Save an image to the ground truth folder"""
        path = os.path.join(IMAGE_PATH, image_name+".jpg")
        image.save(path)