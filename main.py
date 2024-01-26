import os
from random import randint, seed
from basic import TicketModifier
from utils import read_template

PATH = os.path.dirname(__file__)
FONTS = os.path.join(PATH, 'resources', 'fonts')
IMAGES = os.path.join(PATH, 'resources', 'ticketTemplateImages')
TEMPLATES = os.path.join(PATH, 'resources', 'templates.json')


if __name__ == "__main__":
    templates = read_template(TEMPLATES)
    fonts = os.listdir(FONTS)
    seed(3201)
    for filename, blocks in templates:
        image_path = os.path.join(IMAGES, filename)
        ticket = TicketModifier(image_path)
        r = randint(0, len(fonts)-1)
        ticket_image = ticket.modify_image(blocks, os.path.join(FONTS, fonts[r]))
        ticket.show_image(ticket_image)