import json
from basic import Block

def read_template(template_path):
    """Read a .json templates file and return a list of tuples (image ,[blocks...])"""
    with open(template_path) as f:
        template = json.load(f)
    templates = []
    for item in template:
        image_path = item.get('fileName')
        blocks = item.get('blocks')
        blocks = [Block((block['pos'][0],block['pos'][1]), block['type']) for block in blocks]
        templates.append((image_path, blocks))
    return templates