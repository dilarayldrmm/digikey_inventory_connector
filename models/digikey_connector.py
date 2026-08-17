import requests

from odoo import fields, models
from odoo.exceptions import UserError


class DigiKeyConnector(models.Model):
    _name = "digikey.connector"
    _description = "DigiKey API Connector"

    name = fields.Char(
        string="Name",
        default="DigiKey Integration",
        required=True,
    )

    environment = fields.Selection(
        [
            ("sandbox", "Sandbox"),
            ("production", "Production"),
        ],
        string="Environment",
        required=True,
        default="sandbox",
    )

    client_id = fields.Char(string="Client ID")
    client_secret = fields.Char(string="Client Secret")

    connection_status = fields.Selection(
        [
            ("not_connected", "Not Connected"),
            ("connected", "Connected"),
            ("error", "Connection Error"),
        ],
        string="Connection Status",
        default="not_connected",
        readonly=True,
    )

    last_connection_check = fields.Datetime(
        string="Last Connection Check",
        readonly=True,
    )

    connection_message = fields.Char(
        string="Connection Message",
        readonly=True,
    )

    def _get_api_host(self):
        self.ensure_one()

        if self.environment == "sandbox":
            return "https://sandbox-api.digikey.com"

        return "https://api.digikey.com"

    def _get_access_token(self):
        self.ensure_one()

        client_id = (self.client_id or "").strip()
        client_secret = (self.client_secret or "").strip()

        if not client_id:
            raise UserError("Please enter the DigiKey Client ID.")

        if not client_secret:
            raise UserError("Please enter the DigiKey Client Secret.")

        token_url = f"{self._get_api_host()}/v1/oauth2/token"

        response = requests.post(
            token_url,
            data={
                "client_id": client_id,
                "client_secret": client_secret,
                "grant_type": "client_credentials",
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
            },
            timeout=15,
        )

        if not response.ok:
            raise UserError(
                "DigiKey OAuth failed.\n\n"
                f"Status: {response.status_code}\n"
                f"Response: {response.text}"
            )

        data = response.json()

        access_token = data.get("access_token")

        if not access_token:
            raise UserError(
                "DigiKey authentication response did not contain "
                "an access token."
            )

        return access_token

    def _get_api_headers(self, access_token):
        self.ensure_one()

        client_id = (self.client_id or "").strip()

        if not client_id:
            raise UserError(
                "Client ID is empty. Please save the DigiKey Client ID first."
            )

        return {
            "Authorization": f"Bearer {access_token}",
            "X-DIGIKEY-Client-Id": client_id,
            "X-DIGIKEY-Locale-Site": "US",
            "X-DIGIKEY-Locale-Language": "en",
            "X-DIGIKEY-Locale-Currency": "USD",
            "Accept": "application/json",
        }

    def _fetch_categories(self):
        self.ensure_one()

        access_token = self._get_access_token()

        categories_url = (
            f"{self._get_api_host()}"
            "/products/v4/search/categories"
        )

        headers = self._get_api_headers(access_token)

        response = requests.get(
            categories_url,
            headers=headers,
            timeout=15,
        )

        if not response.ok:
            raise UserError(
                "DigiKey Categories API failed.\n\n"
                f"Status: {response.status_code}\n"
                f"Response: {response.text}"
            )

        data = response.json()

        categories = data.get("Categories", [])

        if not categories:
            raise UserError(
                "DigiKey connection succeeded, "
                "but no categories were returned."
            )

        return categories

    def action_check_connection(self):
        self.ensure_one()

        try:
            categories = self._fetch_categories()

            self.write({
                "connection_status": "connected",
                "last_connection_check": fields.Datetime.now(),
                "connection_message": (
                    "DigiKey Product Information API connected. "
                    f"{len(categories)} top-level categories received."
                ),
            })

            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "DigiKey Connection",
                    "message": (
                        "DigiKey Product Information API connection "
                        "established successfully. "
                        f"{len(categories)} categories received."
                    ),
                    "type": "success",
                    "sticky": False,
                },
            }

        except UserError:
            raise

        except requests.RequestException as error:
            self.write({
                "connection_status": "error",
                "last_connection_check": fields.Datetime.now(),
                "connection_message": (
                    "DigiKey API connection failed."
                ),
            })

            raise UserError(
                f"DigiKey connection error:\n{error}"
            )

    def action_open_product_fetch(self):
        self.ensure_one()
        self.env["digikey.category"].ensure_mock_categories()
        return {
            "type": "ir.actions.act_window",
            "name": "DigiKey Product Fetch",
            "res_model": "digikey.product.fetch.wizard",
            "view_mode": "form",
            "target": "new",
        }