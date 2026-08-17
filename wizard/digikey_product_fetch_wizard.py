from odoo import api, fields, models, _
from odoo.exceptions import UserError

from ..services.digikey_api_service import DigiKeyAPIService


class DigiKeyProductFetchWizard(models.TransientModel):
    _name = "digikey.product.fetch.wizard"
    _description = "DigiKey Product Fetch Wizard"

    category_level_1_id = fields.Many2one(
        "digikey.category",
        string="Main Category",
        required=True,
    )

    category_level_2_id = fields.Many2one(
        "digikey.category",
        string="Subcategory",
    )

    category_level_3_id = fields.Many2one(
        "digikey.category",
        string="Product Category",
    )

    line_ids = fields.One2many(
        "digikey.product.fetch.wizard.line",
        "wizard_id",
        string="Products",
    )

    @api.onchange("category_level_1_id")
    def _onchange_category_level_1_id(self):
        self.category_level_2_id = False
        self.category_level_3_id = False
        self.line_ids = [(5, 0, 0)]

    @api.onchange("category_level_2_id")
    def _onchange_category_level_2_id(self):
        self.category_level_3_id = False
        self.line_ids = [(5, 0, 0)]

    @api.onchange("category_level_3_id")
    def _onchange_category_level_3_id(self):
        self.line_ids = [(5, 0, 0)]

    def action_fetch_products(self):
        self.ensure_one()

        if not self.category_level_3_id:
            raise UserError(
                _("Please select the final product category.")
            )

        products = DigiKeyAPIService.get_products(
            self.category_level_3_id.external_id,
            limit=5,
        )

        if not products:
            raise UserError(
                _("No test products were found for this category.")
            )

        self.line_ids.unlink()

        commands = []

        for product in products:
            commands.append(
                (
                    0,
                    0,
                    {
                        "name": product["name"],
                        "digikey_product_number": product[
                            "digikey_product_number"
                        ],
                        "manufacturer_part_number": product[
                            "manufacturer_part_number"
                        ],
                        "manufacturer": product["manufacturer"],
                        "available_qty": product["available_qty"],
                        "description": product["description"],
                        "datasheet_url": product["datasheet_url"],
                        "product_url": product["product_url"],
                    },
                )
            )

        self.write({
            "line_ids": commands,
        })

        return {
            "type": "ir.actions.act_window",
            "name": _("DigiKey Product Fetch"),
            "res_model": "digikey.product.fetch.wizard",
            "view_mode": "form",
            "res_id": self.id,
            "target": "new",
        }

    def _get_or_create_odoo_category(self):
        self.ensure_one()

        ProductCategory = self.env["product.category"]

        root = ProductCategory.search(
            [
                ("name", "=", "DigiKey Imports"),
                ("parent_id", "=", False),
            ],
            limit=1,
        )

        if not root:
            root = ProductCategory.create({
                "name": "DigiKey Imports",
            })

        parent = root

        for digikey_category in [
            self.category_level_1_id,
            self.category_level_2_id,
            self.category_level_3_id,
        ]:
            if not digikey_category:
                continue

            category = ProductCategory.search(
                [
                    ("name", "=", digikey_category.name),
                    ("parent_id", "=", parent.id),
                ],
                limit=1,
            )

            if not category:
                category = ProductCategory.create({
                    "name": digikey_category.name,
                    "parent_id": parent.id,
                })

            parent = category

        return parent

    def action_import_selected(self):
        self.ensure_one()

        selected_lines = self.line_ids.filtered(
            lambda line: line.selected
        )

        if not selected_lines:
            raise UserError(
                _("Please select a product to import.")
            )

        if len(selected_lines) > 1:
            raise UserError(
                _("Please select only one product.")
            )

        line = selected_lines[0]

        existing_product = self.env["product.template"].search(
            [
                (
                    "digikey_product_number",
                    "=",
                    line.digikey_product_number,
                )
            ],
            limit=1,
        )

        if existing_product:
            raise UserError(
                _(
                    "This DigiKey product already exists in Odoo: %s"
                )
                % existing_product.display_name
            )

        category = self._get_or_create_odoo_category()

        product = self.env["product.template"].create({
            "name": line.name,
            "type": "consu",
            "categ_id": category.id,
            "description": line.description,
            "digikey_product_number": line.digikey_product_number,
            "digikey_manufacturer_part_number":
                line.manufacturer_part_number,
            "digikey_manufacturer": line.manufacturer,
            "digikey_supplier_available_qty": line.available_qty,
            "digikey_datasheet_url": line.datasheet_url,
            "digikey_product_url": line.product_url,
        })

        return {
            "type": "ir.actions.act_window",
            "name": _("Imported Product"),
            "res_model": "product.template",
            "view_mode": "form",
            "res_id": product.id,
            "target": "current",
        }


class DigiKeyProductFetchWizardLine(models.TransientModel):
    _name = "digikey.product.fetch.wizard.line"
    _description = "DigiKey Product Fetch Wizard Line"

    wizard_id = fields.Many2one(
        "digikey.product.fetch.wizard",
        required=True,
        ondelete="cascade",
    )

    selected = fields.Boolean(
        string="Select",
    )

    name = fields.Char(
        string="Product",
        readonly=True,
    )

    digikey_product_number = fields.Char(
        string="DigiKey Product Number",
        readonly=True,
    )

    manufacturer_part_number = fields.Char(
        string="Manufacturer Part Number",
        readonly=True,
    )

    manufacturer = fields.Char(
        string="Manufacturer",
        readonly=True,
    )

    available_qty = fields.Integer(
        string="DigiKey Available",
        readonly=True,
    )

    description = fields.Text(
        string="Description",
        readonly=True,
    )

    datasheet_url = fields.Char(
        string="Datasheet URL",
        readonly=True,
    )

    product_url = fields.Char(
        string="Product URL",
        readonly=True,
    )