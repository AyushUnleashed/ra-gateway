from src.config.settings import Settings


pack_type_to_product_id = {
    'test': {
        'BASIC': 'pdt_24EhgTI2a8g8UWLcmmkiG',
        'STANDARD': 'test_prod_002',
    },
    'live': {
        'BASIC': 'prod_001',
        'STANDARD': 'pdt_tn67uip5BYeTkIJzjIDU2',
    },
}

pack_type_to_credit_amount = {
    'BASIC': 20,
    'STANDARD': 40,
}

def get_product_id_from_pack_type(pack_type) -> str:
    if Settings.IS_PRODUCTION:
        environment = 'live'
    else:
        environment = 'test'
        
    pack_type = pack_type.upper()
    return pack_type_to_product_id[environment].get(pack_type, '')

def get_credit_amount_from_pack_type(pack_type) -> int:
    pack_type = pack_type.upper()
    return pack_type_to_credit_amount.get(pack_type, 0)

def get_pack_type_from_product_id(product_id, environment='test') -> str:
    for pack_type, p_id in pack_type_to_product_id[environment].items():
        if p_id == product_id:
            return pack_type
    return ''


def is_payment_test_mode(payment_link: str) -> bool:
    return "test" in payment_link
