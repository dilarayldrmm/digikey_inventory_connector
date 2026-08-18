from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    digikey_product_number = fields.Char(
        string="DigiKey Product Number",
        copy=False,
        index=True,
    )

    digikey_manufacturer_part_number = fields.Char(
        string="Manufacturer Part Number",
        copy=False,
    )

    digikey_manufacturer = fields.Char(
        string="Manufacturer",
        copy=False,
    )

    digikey_supplier_available_qty = fields.Integer(
        string="DigiKey Available Quantity",
        copy=False,
    )

    digikey_datasheet_url = fields.Char(
        string="DigiKey Datasheet URL",
        copy=False,
    )

    digikey_product_url = fields.Char(
        string="DigiKey Product URL",
        copy=False, 
    )