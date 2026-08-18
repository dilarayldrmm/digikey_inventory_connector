from odoo import api, fields, models

from ..services.digikey_api_service import DigiKeyAPIService


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
    def sync_categories_from_service(self, connector):
        """
        Synchronize categories from the selected data source.
        Mock mode:
            DigiKeyAPIService -> mock categories
        API mode:
            DigiKeyAPIService -> real DigiKey Categories API
        """
        categories = DigiKeyAPIService.get_categories(connector)
        if not categories:
            return True

        Category = self.with_context(active_test=False)

        # Önce eski kaynağın kategorilerini gizle.
        # API çağrısı hata verirse bu noktaya gelmediğimiz için
        # mevcut çalışan kategoriler kaybolmaz.
        Category.search([]).write({
            "active": False,
        })

        # 1. geçiş: bütün kategorileri oluştur/güncelle.
        for category_data in categories:
            external_id = category_data["external_id"]
            category = Category.search(
                [("external_id", "=", external_id)],
                limit=1,
            )
            values = {
                "name": category_data["name"],
                "active": True,
            }
            if category:
                category.write(values)
            else:
                values["external_id"] = external_id
                Category.create(values)

        # 2. geçiş: parent-child ilişkilerini oluştur.
        for category_data in categories:
            category = Category.search(
                [
                    (
                        "external_id",
                        "=",
                        category_data["external_id"],
                    )
                ],
                limit=1,
            )
            parent_external_id = category_data.get("parent_external_id")
            parent = False
            if parent_external_id:
                parent = Category.search(
                    [
                        (
                            "external_id",
                            "=",
                            parent_external_id,
                        )
                    ],
                    limit=1,
                )
            category.write({
                "parent_id": parent.id if parent else False,
            })

        return True