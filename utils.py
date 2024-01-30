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
        final_blocks = []
        for block in blocks:
            block_type = block.get('type')
            block_pos = block.get('pos')
            if block_type == 'total':
                block_pos = [tuple(pos) for pos in block_pos]
                subtotal_pos = block.get('subtotal')
                subtotal_block = Block(tuple(subtotal_pos), 'price')
                final_blocks.append(subtotal_block)
                

                tax_pos = block.get('tax')
                tax_block = Block(tuple(tax_pos), 'price')
                final_blocks.append(tax_block)

                
                
                total_str = "%.2f" % (subtotal_block.value + tax_block.value)
                total_str = total_str.replace('.', ',')
                total_block = Block(block_pos, total_str)
                final_blocks.append(total_block)


            else:
                block_pos = tuple(block_pos)
                final_blocks.append(Block(block_pos, block_type))
        templates.append((image_path, final_blocks))
    return templates