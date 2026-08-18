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

    connector_id = fields.Many2one(
        "digikey.connector",
        string="DigiKey Connector",
        readonly=True,
    )

    line_ids = fields.One2many(
        "digikey.product.fetch.wizard.line",
        "wizard_id",
        string="Products",
    )

    @api.onchange("category_level_1_id")
    def _onchange_category_level_1_id(self):
        """
        Main Category kullanıcı tarafından değiştirilirse,
        artık ona ait olmayan alt seçimleri temizle.
        """
        if not self.category_level_1_id:
            self.category_level_2_id = False
            self.category_level_3_id = False
            self.line_ids = [(5, 0, 0)]
            return

        if self.category_level_3_id:
            leaf = self.category_level_3_id
            parent = leaf.parent_id
            grandparent = parent.parent_id if parent else False
            expected_main = grandparent if grandparent else parent

            if self.category_level_1_id == expected_main:
                return

        self.category_level_2_id = False
        self.category_level_3_id = False
        self.line_ids = [(5, 0, 0)]

    @api.onchange("category_level_2_id")
    def _onchange_category_level_2_id(self):
        """
        Subcategory elle seçilirse gerekiyorsa Main Category'yi doldur.
        Product Category tarafından otomatik doldurulduysa
        mevcut hiyerarşiyi bozma.
        """
        if self.category_level_3_id:
            leaf = self.category_level_3_id
            parent = leaf.parent_id
            grandparent = parent.parent_id if parent else False
            expected_subcategory = parent if grandparent else False
            if self.category_level_2_id == expected_subcategory:
                return

        if self.category_level_2_id:
            parent = self.category_level_2_id.parent_id
            if parent:
                self.category_level_1_id = parent

        self.category_level_3_id = False
        self.line_ids = [(5, 0, 0)]

    @api.onchange("category_level_3_id")
    def _onchange_category_level_3_id(self):
        """
        Product Category doğrudan seçildiğinde DigiKey'in
        gerçek parent zincirini kullanarak üst alanları doldur.
        2 seviyeli yapı:
            Main -> Product
        3 seviyeli yapı:
            Main -> Subcategory -> Product
        """
        self.line_ids = [(5, 0, 0)]
        if not self.category_level_3_id:
            self.category_level_1_id = False
            self.category_level_2_id = False
            return

        leaf = self.category_level_3_id
        parent = leaf.parent_id
        if not parent:
            self.category_level_1_id = False
            self.category_level_2_id = False
            return

        grandparent = parent.parent_id
        if grandparent:
            self.category_level_1_id = grandparent
            self.category_level_2_id = parent
        else:
            self.category_level_1_id = parent
            self.category_level_2_id = False

    def _get_selected_category(self):
        self.ensure_one()

        if self.category_level_3_id:
            return self.category_level_3_id
        if self.category_level_2_id:
            return self.category_level_2_id
        if self.category_level_1_id:
            return self.category_level_1_id

        raise UserError(
            _("Please select a DigiKey category first.")
        )

    def action_fetch_products(self):
        self.ensure_one()

        selected_category = self._get_selected_category()

        products = DigiKeyAPIService.get_products(
            selected_category.external_id,
            limit=5,
            connector=self.connector_id,
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
                        "photo_url": product.get("photo_url") or "",
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

    def action_select_all(self):
        self.ensure_one()
        self.line_ids.write({
            "selected": True,
        })
        return {
            "type": "ir.actions.act_window",
            "name": "DigiKey Product Fetch",
            "res_model": "digikey.product.fetch.wizard",
            "view_mode": "form",
            "res_id": self.id,
            "target": "new",
        }

    def action_clear_selection(self):
        self.ensure_one()
        self.line_ids.write({
            "selected": False,
        })
        return {
            "type": "ir.actions.act_window",
            "name": "DigiKey Product Fetch",
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
                _("Please select at least one product to import.")
            )

        category = self._get_or_create_odoo_category()

        created_product_ids = []

        for line in selected_lines:
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
                continue

            product_values = {
                "name": line.name,
                "type": "consu",
                "is_storable": True,
                "tracking": "none",
                "categ_id": category.id,
                "description": line.description,
                "digikey_product_number": line.digikey_product_number,
                "digikey_manufacturer_part_number":
                    line.manufacturer_part_number,
                "digikey_manufacturer": line.manufacturer,
                "digikey_supplier_available_qty": line.available_qty,
                "digikey_datasheet_url": line.datasheet_url,
                "digikey_product_url": line.product_url,
            }

            image_data = DigiKeyAPIService.download_product_image(
                line.photo_url
            )
            if image_data:
                product_values["image_1920"] = image_data

            product = self.env["product.template"].create(product_values)
            created_product_ids.append(product.id)

        if not created_product_ids:
            raise UserError(
                _("Selected products already exist in Odoo.")
            )

        created_products = self.env["product.template"].browse(
            created_product_ids
        )

        return {
            "type": "ir.actions.act_window",
            "name": _("Imported Products"),
            "res_model": "product.template",
            "view_mode": "list,form",
            "domain": [("id", "in", created_product_ids)],
            "res_id": created_products[0].id,
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

    photo_url = fields.Char(
        string="Photo URL",
        readonly=True,
    )