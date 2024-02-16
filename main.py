import os
import asyncio
from random import randint, seed
from basic import TicketModifier
from utils import read_template

PATH = os.path.dirname(__file__)
FONTS = os.path.join(PATH, 'resources', 'fonts')
IMAGES = os.path.join(PATH, 'resources', 'ticketTemplateImages')
TEMPLATES = os.path.join(PATH, 'resources', 'templates.json')
RESULTS = os.path.join(PATH, 'resources', 'results')
BACKGROUND = os.path.join(PATH, 'resources', 'backgrounds')

MAX_ROTATION = 250


async def create_ticket(filename, blocks, output_image_name):
    image_path = os.path.join(IMAGES, filename)
    ticket = TicketModifier(image_path)
    r = randint(0, len(fonts)-1)
    ticket_image = ticket.modify_image(blocks, os.path.join(FONTS, fonts[r]))

    #Rotation
    cv_ticket = TicketModifier.pil_to_cv2(ticket_image)
    final_points, rotated_ticket = TicketModifier.rotateTicket(cv_ticket, MAX_ROTATION)
    pil_rotated_ticket = TicketModifier.cv2_to_pil(rotated_ticket)

    backgrounded_image = ticket.addBackground(
        pil_rotated_ticket, 
        BACKGROUND,
        final_points)
    ticket.save_image(backgrounded_image,output_image_name)

if __name__ == "__main__":
    templates = read_template(TEMPLATES, result_path=RESULTS)
    fonts = os.listdir(FONTS)
    seed(3201)
    for filename, blocks, output_image_name in templates:
        asyncio.run(create_ticket(filename, blocks, output_image_name))
