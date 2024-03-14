import cv2
import os
from random import randint
from PIL import ImageFont, ImageDraw, Image
from pathlib import Path
import numpy as np
import numpy.typing as npt
import random
from scipy import ndimage
from typing import List
from polynomials import polynomialModel, lPolynomial2nlPolynomial, maskFromPolygons, pt


MatLike = npt.NDArray[np.uint8]

TEXTS_SAMPLE = ["Carne", "Pescado", "Verdura", "Fruta", "Pan", "Bebida", "Lacteos", "Higiene", "Limpieza", "Otros"]
TYPES = ["text", "price", "quantity", "percentage"]

FILE_PATH = os.path.dirname(__file__)
IMAGE_PATH = os.path.join(FILE_PATH, 'resources', 'results')

class Text:
    def __init__(self, path:str, max_words:int=10, min_words:int=5, max_length:int=22):
        '''Read a text file and store it in memory

        Args:
        - path: str, the path to the text file
        - max_length: int, the maximum length of the text to be gotten from the file
        - min_length: int, the minimum length of the text to be gotten from the file
        
        '''
        self.max_words = max_words
        self.min_words = min_words
        self.max_length = max_length
        self.path = Path(path)
        with open(self.path, "r") as file:
            self.text = file.read().split(" ")
    
    def get_random_text(self):
        '''Return a random piece of text from the text file'''
        start = randint(0, len(self.text)-self.max_words)
        end = randint(self.min_words, self.max_words)

        text = " ".join(self.text[start:start+end])
        taken = min(self.max_length, len(text))
        return text[:taken]

# TODO IMPROVEMENT: Total and subtotal blocks should be calculated from prices and percentages blocks.

class Block:
    """A block is a rectangle in the image that contains text."""
    def __init__(self, position: tuple, type: str, text_init:Text=None):
        if position.__class__ != tuple and type in TYPES:
            raise TypeError("position must be a tuple or a list")
        elif type not in TYPES and position.__class__ != list:
            raise TypeError("position must be a tuple or a list")
        
        if type.__class__ != str:
            raise TypeError("type must be a string")
        
        self.position = position
        self.type = type
        if type in TYPES:
            self.text, self.value = self.initialize_text(text_init)
        else:
            self.text = self.value = type
    
    def initialize_text(self, text_init:Text=None):
        """Return a random text depending on the type of the block."""
        if self.type == "text":
            if text_init:
                return text_init.get_random_text(), None
            
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

def random_radius(upper_limit: int, lower_limit: int) -> int:
            """Return a random radius"""
            to_return = randint(upper_limit, lower_limit if lower_limit % 2 == 0 else lower_limit - 1) 
            return to_return if to_return % 2 == 0 else to_return + 1

class TicketModifier:
    """This class is used to modify the ticket image."""

    def __init__(self, image_path: str):
        self.image_path = image_path
    
    def modify_image(self, blocks:List[Block], font_path:str, font_size:int=30):
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
    def applyGaussianNoise(image: MatLike):
        """Create a mask and apply gaussian noise to the ticket"""

        polynomials = [] # List of polynomials
        number_of_polynomials = randint(0, 5)
        for i in range(number_of_polynomials):
            center = pt(randint(0, image.shape[0]), randint(0, image.shape[1]))
            radii = [random_radius(50, 200) for i in range(randint(2, 10))]
            linear = polynomialModel(center, radii, 15)
            polynomials.append(lPolynomial2nlPolynomial(linear))
        
        size = (image.shape[0], image.shape[1])
        masks = [maskFromPolygons([np.array(poly, np.int32)],size) for poly in polynomials]
        # extend the mask to 3 channels
        masks = [np.stack([mask,mask,mask], axis=-1) for mask in masks]
        gaussianApplied = image.copy()
        gaussianApplied = cv2.GaussianBlur(gaussianApplied, (9,9), 10)
        for mask in masks:
            image = np.where(mask == 255, gaussianApplied, image)
        
        return image


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

        #print(good_points)

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

class TicketsBackgrounds:
    def __init__(self, path: str):
        path = Path(path)
        self.path = path
        backgrounds = list(self.path.glob('*.jpg'))
        self.backgrounds = [cv2.imread(str(background)) for background in backgrounds]
    
    def applyRandomBackground(self, image:MatLike):
        """Apply a random background to the image"""
        background = self.backgrounds[randint(0, len(self.backgrounds)-1)]
        background = cv2.resize(background, (image.shape[1], image.shape[0]))
        # Apply the background with a random alpha channel
        alpha = randint(70, 98) / 100
        return cv2.addWeighted(image, alpha, background, 1-alpha, 0)


        