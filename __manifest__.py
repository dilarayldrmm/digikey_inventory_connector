{
    "name": "DigiKey Inventory Connector",
    "version": "18.0.1.0.0",
    "summary": "Integrate DigiKey product information with Odoo Inventory",
    "description": """
        DigiKey API integration for Odoo Inventory.

        Features:
        - DigiKey connection test
        - Category-based product search
        - Import DigiKey products into Odoo Inventory
    """,
    "author": "Dilara",
    "category": "Inventory/Inventory",
    "license": "LGPL-3",

    "depends": [
        "base",
        "product",
        "stock",
    ],

    "data": [
        "security/ir.model.access.csv",
        "views/digikey_connector_views.xml",
        "views/digikey_product_fetch_wizard_views.xml",
        "views/product_template_views.xml",
    ],

    "installable": True,
    "application": True,
}