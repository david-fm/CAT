import os
import asyncio
from random import randint, seed
from basic import TicketModifier, TicketsWrinkleBackgrounds, Text, TicketsBackgrounds
from utils import read_template


PATH = os.path.dirname(__file__)
FONTS = os.path.join(PATH, 'resources', 'fonts')
IMAGES = os.path.join(PATH, 'resources', 'ticketTemplateImages')
TEMPLATES = os.path.join(PATH, 'resources', 'templates.json')
RESULTS = os.path.join(PATH, 'resources', 'results')
BACKGROUND = os.path.join(PATH, 'resources', 'backgrounds')
TICKET_WRINKLE_BACKGROUNDS = os.path.join(PATH, 'resources', 'ticketsBackground')
TEXT = os.path.join(PATH, 'resources', 'text.txt')

MAX_ROTATION = 250


ticket_wrinkle_backgrounds = TicketsWrinkleBackgrounds(TICKET_WRINKLE_BACKGROUNDS)
text = Text(TEXT)
ticket_backgrounds = TicketsBackgrounds(BACKGROUND)

async def create_ticket(filename, blocks, output_image_name):
    image_path = os.path.join(IMAGES, filename)
    ticket = TicketModifier(image_path)
    r = randint(0, len(fonts)-1)
    ticket_image = ticket.modify_image(blocks, os.path.join(FONTS, fonts[r]))

    #Rotation
    cv_ticket = TicketModifier.pil_to_cv2(ticket_image)
    cv_ticket = TicketModifier.applyGaussianNoise(cv_ticket)
    
    cv_ticket = ticket_wrinkle_backgrounds.applyRandomBackground(cv_ticket)

    final_points, rotated_ticket = TicketModifier.rotateTicket(cv_ticket, MAX_ROTATION)
    pil_rotated_ticket = TicketModifier.cv2_to_pil(rotated_ticket)

    backgrounded_image = ticket_backgrounds.addBackground(
        pil_rotated_ticket,
        final_points)
    ticket.save_image(backgrounded_image,output_image_name)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Create tickets')
    parser.add_argument('-e', '--examples', type=int, default=4, help='Number of examples per template')
    parser.add_argument('-r', '--results', type=str, default=RESULTS, help='Path to save the results')
    args = vars(parser.parse_args())

    templates = read_template(
        TEMPLATES, 
        result_path=RESULTS, 
        text_ini=text, 
        example_per_template=args['examples'])
    
    fonts = os.listdir(FONTS)
    seed(3201)
    for filename, blocks, output_image_name in templates:
        asyncio.run(create_ticket(filename, blocks, output_image_name))
