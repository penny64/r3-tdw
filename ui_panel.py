from framework import display, entities

import constants
import ui_menu

ACTIVE_MENU = None


def show_inventory(entity):
    global ACTIVE_MENU
    
    _holder_menu = ui_menu.create(1, 1, title='Inventory', surface='ui_inventory')
    
    for holder_name in entity['inventory']['holders']:
        _holder = entity['inventory']['holders'][holder_name]
        
        ui_menu.add_selectable(_holder_menu, holder_name.title(), lambda _: 1==1)
    
    ACTIVE_MENU = _holder_menu