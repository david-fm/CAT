import json
import os
from basic import Block
from json_classes import *
from PIL import Image

FILE_PATH = os.path.dirname(__file__)
IMAGES = os.path.join(FILE_PATH, 'resources', 'results', 'images')

def read_template(template_path, example_per_template=1000, result_path=IMAGES):
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

                name_block = Block(item_name, 'text')
                quantity_block = Block(item_quantity, 'quantity')
                price_block = Block(item_price, 'price')
                
                gt.add_item(name_block.text, quantity_block.text, price_block.text)
                final_blocks.append(name_block)
                final_blocks.append(quantity_block)
                final_blocks.append(price_block)
            
            subtotal = template.get('sub_total')

            subtotal_pos = subtotal.get('subtotal')
            subtotal_block = Block(tuple(subtotal_pos), 'price')
            final_blocks.append(subtotal_block)
                    

            tax_pos = subtotal.get('tax')
            tax_block = Block(tuple(tax_pos), 'price')
            final_blocks.append(tax_block)
            
            gt_subtotal = Sub_total(subtotal_block.text, '0', tax_block.text, '0')

            total = template.get('total')
            total_block_pos = [tuple(pos) for pos in total]  
            total_str = "%.2f" % (subtotal_block.value + tax_block.value)
            total_str = total_str.replace('.', ',')
            total_block = Block(total_block_pos, total_str)
            final_blocks.append(total_block)

            gt_total = Total(total_block.text)

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
