import cv2
from random import randint
from PIL import ImageFont, ImageDraw, Image

TEXTS_SAMPLE = ["Carne", "Pescado", "Verdura", "Fruta", "Pan", "Bebida", "Lacteos", "Higiene", "Limpieza", "Otros"]

# TODO : Search for a database of products for the text samples
# TODO IMPROVEMENT: Total and subtotal blocks should be calculated from prices and percentages blocks.

class Block:
    """A block is a rectangle in the image that contains text."""
    def __init__(self, position, type):
        if position.__class__ != tuple:
            raise TypeError("position must be a tuple")
        self.position = position
        self.type = type
    
    @property
    def text(self):
        """Return a random text depending on the type of the block."""
        if self.type == "text":
            return TEXTS_SAMPLE[randint(0, len(TEXTS_SAMPLE)-1)]
        elif self.type == "price":
            # Return a random price between 00,00 and 99,99
            return str(randint(0, 99)) + "," + str(randint(0, 99))
        elif self.type == "quantity":
            return str(randint(1, 10))
        elif self.type == "percentage":
            return str(randint(0, 100)) + "%"
        return self.type

    def __repr__(self):
        return f"Block({self.position}, {self.type})"


def add_text_to_image( image, text, position, font_path, font_size=30):
        
        font = ImageFont.truetype(font_path, font_size)
        img = ImageDraw.Draw(image)
        img.text(position, text, (0,0,0), font=font)


class TicketModifier:
    """This class is used to modify the ticket image."""

    def __init__(self, image_path):
        self.image_path = image_path
    
    def modify_image(self, blocks, font_path, font_size=30):
        """Modify the image with the given blocks.
        
        Keyword arguments:
        blocks -- a list of Block objects
        
        Returns:
        A PIL image."""
        image = cv2.imread(self.image_path)
        modified_image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(modified_image_rgb)
        for block in blocks:
            add_text_to_image(pil_image, block.text, block.position, font_path, font_size)
        return pil_image
    
    def show_image(self, image):
        """Show the image created by modify_image."""
        import matplotlib.pyplot as plt

        plt.imshow(image)
        plt.axis("off")
        plt.show()

    