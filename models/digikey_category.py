from odoo import api, fields, models


class DigiKeyCategory(models.Model):
    _name = "digikey.category"
    _description = "DigiKey Category"
    _order = "name"

    name = fields.Char(
        string="Category Name",
        required=True,
    )

    external_id = fields.Char(
        string="DigiKey Category ID",
        required=True,
        index=True,
    )

    parent_id = fields.Many2one(
        "digikey.category",
        string="Parent Category",
        ondelete="cascade",
    )

    child_ids = fields.One2many(
        "digikey.category",
        "parent_id",
        string="Child Categories",
    )

    active = fields.Boolean(
        default=True,
    )

    _sql_constraints = [
        (
            "digikey_category_external_id_unique",
            "unique(external_id)",
            "DigiKey Category ID must be unique.",
        ),
    ]

    @api.model
    def _get_or_create_mock_category(self, external_id, name, parent=False):
        category = self.search(
            [("external_id", "=", external_id)],
            limit=1,
        )

        values = {
            "name": name,
            "parent_id": parent.id if parent else False,
        }

        if category:
            category.write(values)
        else:
            values["external_id"] = external_id
            category = self.create(values)

        return category

    @api.model
    def ensure_mock_categories(self):
        """
        Temporary category hierarchy.

        This method will later be replaced by
        DigiKey Product Information V4 Categories API.
        """

        electronics = self._get_or_create_mock_category(
            "mock-electronics",
            "Electronic Components",
        )

        sensors = self._get_or_create_mock_category(
            "mock-sensors",
            "Sensors",
            electronics,
        )

        connectors = self._get_or_create_mock_category(
            "mock-connectors",
            "Connectors",
            electronics,
        )

        self._get_or_create_mock_category(
            "mock-temperature-sensors",
            "Temperature Sensors",
            sensors,
        )

        self._get_or_create_mock_category(
            "mock-pressure-sensors",
            "Pressure Sensors",
            sensors,
        )

        self._get_or_create_mock_category(
            "mock-headers",
            "Headers",
            connectors,
        )

        self._get_or_create_mock_category(
            "mock-terminal-blocks",
            "Terminal Blocks",
            connectors,
        )