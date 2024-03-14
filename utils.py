import json
import os
from basic import Block, Text
from json_classes import *
from random import uniform
from typing import List

FILE_PATH = os.path.dirname(__file__)
IMAGES = os.path.join(FILE_PATH, 'resources', 'results')

def total_subtotal(template, final_blocks):
    """Calculate the total from subtotal if subtotal is given"""
    subtotal = template.get('sub_total')
    subtotal_pos:None|List = subtotal.get('subtotal')

    
    if subtotal_pos:
        subtotal_block = Block(tuple(subtotal_pos), 'price')
        final_blocks.append(subtotal_block)
    
    tax_pos = subtotal.get('tax')
    if tax_pos:
        tax_block = Block(tuple(tax_pos), 'price')
        final_blocks.append(tax_block)
    
    construct_total:bool = tax_pos and subtotal_pos

    subtotal_str = subtotal_block.text if subtotal_pos else '0'
    tax_str = tax_block.text if tax_pos else '0'
    gt_subtotal = Sub_total(subtotal_str, '0', tax_str, '0')

    total = template.get('total')
    total_block_pos = [tuple(pos) for pos in total]
    if construct_total:
        total_str = "%.2f" % (subtotal_block.value + tax_block.value)
        total_str = total_str.replace('.', ',')
    else:
        total_str = "%.2f" % (uniform(-100, 1000))
        total_str = total_str.replace('.', ',')
    total_block = Block(total_block_pos, total_str)
    final_blocks.append(total_block)

    gt_total = Total(total_block.text)

    return gt_total, gt_subtotal


def read_template(template_path, example_per_template=1000, result_path=IMAGES, text_ini:Text=None):
    """Read a .json templates file and return a list of tuples (image ,[blocks...])
    
    Template file indicates info about the tickets image templates to
    generate. 
    
    Args:
    - template_path: str, path to the .json file with the templates
    - example_per_template: int, number of examples to generate per template
    - result_path: str, path to save the metadata.jsonl file with the ground truth"""

    with open(template_path) as f:
        templates = json.load(f)
    to_return = []
    for template in templates:
        for i in range(example_per_template):
            gt_total = None # Total object for the ground truth
            gt_subtotal = None # Subtotal object for the ground truth
            gt = GroundTruth()

            image_path = template.get('fileName')
            menu = template.get('menu')
            final_blocks = []
            for item in menu:
                item_name = tuple(item.get('nm'))
                item_quantity = tuple(item.get('cnt'))
                item_price = tuple(item.get('price'))
                item_pvp = tuple(item.get('pvp')) if item.get('pvp') else None

                name_block = Block(item_name, 'text', text_ini)
                quantity_block = Block(item_quantity, 'quantity')
                price_block = Block(item_price, 'price')
                pvp_block = Block(item_pvp, 'price') if item_pvp else None
                
                gt.add_item(name_block.text, quantity_block.text, price_block.text)
                final_blocks.append(name_block)
                final_blocks.append(quantity_block)
                final_blocks.append(price_block)
                if pvp_block:
                    final_blocks.append(pvp_block)
            
            gt_total, gt_subtotal = total_subtotal(template, final_blocks)

            gt.total = gt_total
            gt.subtotal = gt_subtotal

            json_gt = json.dumps(gt, default=lambda o: o.__dict__, indent=4)
            # save ground truth to file
            template_name = template.get('name')
            image_file_name = template_name+str(i)+'.jpg'
            text = json.loads(json_gt)
            metadata = json.dumps({'text': text, 'file_name': image_file_name})
            with open(os.path.join(result_path,'metadata.jsonl'), 'a') as f:
                f.write(metadata+'\n')

            extra = template.get('extra')
            for item in extra:
                extra_type = item.get('type')
                extra_pos = item.get('pos')
                extra_block = Block(tuple(extra_pos), extra_type)
                final_blocks.append(extra_block)


            to_return.append((image_path, final_blocks, template_name+str(i)))

    return to_return

