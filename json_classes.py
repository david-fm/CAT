'''Auxiliary classes for json parsing to create the ground truth'''

from basic import Block

class GroundTruth:
    def __init__(self, menu, subtotal, total):
        self.menu = menu
        self.subtotal = subtotal
        self.total = total
    
    def __init__(self):
        self.menu = []
        self.subtotal = None
        self.total = None

    def add_item(self, nm, cnt, price):
        self.menu.append(
            {
                "nm": nm,
                "cnt": cnt,
                "price": price
            }
        )


class Sub_total:
    def __init__(self, subtotal_price:str, service_price:str, tax_price:str, etc:str):
        self.subtotal_price = subtotal_price
        self.service_price = service_price
        self.tax_price = tax_price
        self.etc = etc


class Total:
    def __init__(self, total_price):
        self.total_price = total_price