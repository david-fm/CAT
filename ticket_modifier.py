import cv2
from PIL import ImageFont, ImageDraw, Image
import os
PATH = os.path.dirname(__file__)
FONT = os.path.join(PATH, 'TimesRegular.ttf')
IMAGE = os.path.join(PATH, 'Mercadona.png')


def add_text_to_image(image, text, position):
    
    font = ImageFont.truetype(FONT, 30)
    img = ImageDraw.Draw(image)
    img.text(position, text, (0,0,0), font=font)




if __name__ == "__main__":
    import matplotlib.pyplot as plt

    image = cv2.imread(IMAGE)
    first_item_name_str = "PATATAS"
    first_item_price_str = "1,50"
    first_item_amount_str = "1"

    second_item_name_str = "COLACAO"
    second_item_price_str = "2,50"
    second_item_amount_str = "1"

    subtotal_str = "4,00"
    iva_str = "10%"
    tax_str = "0,40"

    subtotalB_str = "1,00"
    ivaB_str = "0%"
    taxB_str = "0,00"

    subtotalFinal_str = "5,00"
    taxFinal_str = "0,40"

    totalFinal_str = "5,40"
    
    
    # measured with online tool
    first_item_amount = (57, 584)
    first_item_name = (117, 584) 
    first_item_price = (770, 584)
    
    second_item_amount = (57, 622)
    second_item_name = (117, 622)
    second_item_price = (770, 622)

    iva = (145, 807)
    subtotal = (413, 807)
    tax = (682, 807)

    ivaB = (145, 845)
    subtotalB = (413, 845)
    taxB = (682, 845)

    subtotalFinal = (413, 876)
    taxFinal = (682, 883)
    total = (770, 669)


    # Convert from cv2 BGR to RGB
    modified_image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(modified_image_rgb)
    # Add text to the image
    add_text_to_image(pil_image, first_item_name_str, first_item_name)
    add_text_to_image(pil_image, second_item_name_str, second_item_name)
    add_text_to_image(pil_image, first_item_price_str, first_item_price)
    add_text_to_image(pil_image, second_item_price_str, second_item_price)
    add_text_to_image(pil_image, first_item_amount_str, first_item_amount)
    add_text_to_image(pil_image, second_item_amount_str, second_item_amount)
    add_text_to_image(pil_image, subtotal_str, subtotal)
    add_text_to_image(pil_image, iva_str, iva)
    add_text_to_image(pil_image, tax_str, tax)
    add_text_to_image(pil_image, subtotalB_str, subtotalB)
    add_text_to_image(pil_image, ivaB_str, ivaB)
    add_text_to_image(pil_image, taxB_str, taxB)
    add_text_to_image(pil_image, subtotalFinal_str, subtotalFinal)
    add_text_to_image(pil_image, taxFinal_str, taxFinal)
    add_text_to_image(pil_image, totalFinal_str, total)

    

    # Plot the modified image
    plt.imshow(pil_image)
    plt.axis("off")
    plt.show()