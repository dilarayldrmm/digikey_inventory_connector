import base64
import requests
from odoo.exceptions import UserError


class DigiKeyAPIService:
    """
    Service layer for DigiKey product operations.

    Currently uses mock data.
    Real DigiKey Product Information V4 calls
    will be connected here later.
    """

    MOCK_PRODUCTS = {
        "mock-temperature-sensors": [
            {
                "name": "[MOCK] Temperature Sensor A",
                "digikey_product_number": "MOCK-TEMP-001",
                "manufacturer_part_number": "TEMP-A001",
                "manufacturer": "Mock Electronics",
                "available_qty": 1250,
                "description": "Digital temperature sensor for test integration.",
            },
            {
                "name": "[MOCK] Temperature Sensor B",
                "digikey_product_number": "MOCK-TEMP-002",
                "manufacturer_part_number": "TEMP-B002",
                "manufacturer": "Mock Electronics",
                "available_qty": 850,
                "description": "Precision temperature sensor for test integration.",
            },
            {
                "name": "[MOCK] Temperature Sensor C",
                "digikey_product_number": "MOCK-TEMP-003",
                "manufacturer_part_number": "TEMP-C003",
                "manufacturer": "Test Components",
                "available_qty": 640,
                "description": "Low power temperature sensor.",
            },
            {
                "name": "[MOCK] Temperature Sensor D",
                "digikey_product_number": "MOCK-TEMP-004",
                "manufacturer_part_number": "TEMP-D004",
                "manufacturer": "Test Components",
                "available_qty": 420,
                "description": "Industrial temperature sensing component.",
            },
            {
                "name": "[MOCK] Temperature Sensor E",
                "digikey_product_number": "MOCK-TEMP-005",
                "manufacturer_part_number": "TEMP-E005",
                "manufacturer": "Demo Semiconductor",
                "available_qty": 210,
                "description": "Compact digital temperature sensor.",
            },
        ],

        "mock-pressure-sensors": [
            {
                "name": "[MOCK] Pressure Sensor A",
                "digikey_product_number": "MOCK-PRES-001",
                "manufacturer_part_number": "PRES-A001",
                "manufacturer": "Mock Sensors",
                "available_qty": 720,
                "description": "Digital pressure sensor.",
            },
            {
                "name": "[MOCK] Pressure Sensor B",
                "digikey_product_number": "MOCK-PRES-002",
                "manufacturer_part_number": "PRES-B002",
                "manufacturer": "Mock Sensors",
                "available_qty": 510,
                "description": "Low pressure sensing component.",
            },
        ],

        "mock-headers": [
            {
                "name": "[MOCK] Header Connector A",
                "digikey_product_number": "MOCK-HEAD-001",
                "manufacturer_part_number": "HEAD-A001",
                "manufacturer": "Mock Connectors",
                "available_qty": 5000,
                "description": "Two-row header connector.",
            },
            {
                "name": "[MOCK] Header Connector B",
                "digikey_product_number": "MOCK-HEAD-002",
                "manufacturer_part_number": "HEAD-B002",
                "manufacturer": "Mock Connectors",
                "available_qty": 3500,
                "description": "Board header connector.",
            },
        ],

        "mock-terminal-blocks": [
            {
                "name": "[MOCK] Terminal Block A",
                "digikey_product_number": "MOCK-TERM-001",
                "manufacturer_part_number": "TERM-A001",
                "manufacturer": "Mock Connectors",
                "available_qty": 2100,
                "description": "PCB terminal block.",
            },
            {
                "name": "[MOCK] Terminal Block B",
                "digikey_product_number": "MOCK-TERM-002",
                "manufacturer_part_number": "TERM-B002",
                "manufacturer": "Mock Connectors",
                "available_qty": 1750,
                "description": "Two-position terminal block.",
            },
        ],
        "mock-batteries": [
            {
                "name": "BATT LITHIUM 3V 1MAH COIN",
                "digikey_product_number": "728-1053-ND",
                "manufacturer_part_number": "MS412FE-FL26E",
                "manufacturer": "Seiko Instruments",
                "available_qty": 250,
                "description": "Coin lithium battery for test integration.",
                "photo_url": (
                    "https://mm.digikey.com/Volume0/opasdata/d220001/"
                    "derivates/1/002/649/623/"
                    "MS621FE-FL11E%2C%20MS518SE-FL35E%2C%20%20"
                    "MS412FE-FL26E_sml%28200x200%29.jpg"
                ),
            },
        ],
    }

    MOCK_CATEGORIES = [
        {
            "external_id": "mock-electronics",
            "name": "Electronic Components",
            "parent_external_id": False,
        },
        {
            "external_id": "mock-sensors",
            "name": "Sensors",
            "parent_external_id": "mock-electronics",
        },
        {
            "external_id": "mock-connectors",
            "name": "Connectors",
            "parent_external_id": "mock-electronics",
        },
        {
            "external_id": "mock-temperature-sensors",
            "name": "Temperature Sensors",
            "parent_external_id": "mock-sensors",
        },
        {
            "external_id": "mock-pressure-sensors",
            "name": "Pressure Sensors",
            "parent_external_id": "mock-sensors",
        },
        {
            "external_id": "mock-headers",
            "name": "Headers",
            "parent_external_id": "mock-connectors",
        },
        {
            "external_id": "mock-terminal-blocks",
            "name": "Terminal Blocks",
            "parent_external_id": "mock-connectors",
        },
        {
            "external_id": "mock-batteries",
            "name": "Batteries",
            "parent_external_id": "mock-electronics",
        },
    ]

    @classmethod
    def get_categories(cls, connector):
        if connector.data_source == "mock":
            return cls.MOCK_CATEGORIES.copy()
        return cls._get_api_categories(connector)

    @classmethod
    def _get_api_categories(cls, connector):
        access_token = connector._get_access_token()
        url = (
            f"{connector._get_api_host()}"
            "/products/v4/search/categories"
        )
        response = requests.get(
            url,
            headers=connector._get_api_headers(access_token),
            timeout=15,
        )
        if not response.ok:
            raise UserError(
                "DigiKey Categories API failed.\n\n"
                f"Status: {response.status_code}\n"
                f"Response: {response.text}"
            )

        data = response.json()
        result = []

        def flatten_categories(categories, parent_external_id=False):
            for category in categories:
                category_id = category.get("CategoryId")
                if category_id is None:
                    continue

                category_external_id = str(category_id)
                result.append({
                    "external_id": category_external_id,
                    "name": (
                        category.get("Name")
                        or f"Category {category_id}"
                    ),
                    "parent_external_id": parent_external_id,
                })
                children = category.get("Children") or []
                flatten_categories(
                    children,
                    parent_external_id=category_external_id,
                )

        flatten_categories(
            data.get("Categories") or []
        )

        if not result:
            raise UserError(
                "DigiKey API connection succeeded, "
                "but no categories were returned."
            )

        return result

    @classmethod
    def get_products(
        cls,
        category_external_id,
        limit=5,
        connector=None,
    ):
        if connector and connector.data_source == "api":
            return cls._get_api_products(
                connector=connector,
                category_external_id=category_external_id,
                limit=limit,
            )

        products = cls.MOCK_PRODUCTS.get(category_external_id, [])

        result = []

        for product in products[:limit]:
            product_data = product.copy()

            product_number = product_data["digikey_product_number"].lower()

            product_data["datasheet_url"] = (
                product_data.get("datasheet_url")
                or f"https://example.com/{product_number}-datasheet.pdf"
            )

            product_data["product_url"] = (
                product_data.get("product_url")
                or f"https://example.com/{product_number}"
            )

            product_data["photo_url"] = (
                product_data.get("photo_url") or ""
            )

            result.append(product_data)

        return result

    @classmethod
    def _get_api_products(
        cls,
        connector,
        category_external_id,
        limit=5,
    ):
        access_token = connector._get_access_token()
        url = (
            f"{connector._get_api_host()}"
            "/products/v4/search/keyword"
        )
        headers = connector._get_api_headers(access_token).copy()
        headers["Content-Type"] = "application/json"
        payload = {
            "Keywords": "",
            "Limit": min(limit, 5),
            "Offset": 0,
            "FilterOptionsRequest": {
                "CategoryFilter": [
                    {
                        "Id": str(category_external_id),
                    }
                ],
            },
        }
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=20,
        )
        if not response.ok:
            raise UserError(
                "DigiKey Product Search API failed.\n\n"
                f"Status: {response.status_code}\n"
                f"Response: {response.text}"
            )
        data = response.json()
        api_products = data.get("Products") or []
        result = []
        for product in api_products[:5]:
            mapped_product = cls._map_api_product(product)
            if mapped_product:
                result.append(mapped_product)
        if not result:
            raise UserError(
                "DigiKey returned no usable products "
                "for the selected category."
            )
        return result

    @classmethod
    def _map_api_product(cls, product):
        description_data = (product.get("Description") or {})
        manufacturer_data = (product.get("Manufacturer") or {})
        variations = (product.get("ProductVariations") or [])
        digikey_product_number = False

        for variation in variations:
            number = variation.get("DigiKeyProductNumber")
            if number:
                digikey_product_number = number
                break

        if not digikey_product_number:
            return False

        product_name = (
            description_data.get("ProductDescription")
            or product.get("ManufacturerProductNumber")
            or digikey_product_number
        )
        detailed_description = (
            description_data.get("DetailedDescription")
            or description_data.get("ProductDescription")
            or ""
        )

        return {
            "name": product_name,
            "digikey_product_number": digikey_product_number,
            "manufacturer_part_number": product.get(
                "ManufacturerProductNumber"
            ) or "",
            "manufacturer": manufacturer_data.get("Name") or "",
            "available_qty": product.get("QuantityAvailable") or 0,
            "description": detailed_description,
            "datasheet_url": product.get("DatasheetUrl") or "",
            "product_url": product.get("ProductUrl") or "",
            "photo_url": product.get("PhotoUrl") or "",
        }

    MAX_IMAGE_SIZE = 2 * 1024 * 1024  # 2 MB

    @classmethod
    def download_product_image(cls, photo_url):
        """
        Download only the selected product image.
        Returns:
            Base64 encoded image for Odoo image_1920,
            or False if the image cannot be downloaded safely.
        """
        if not photo_url:
            return False

        try:
            response = requests.get(
                photo_url,
                timeout=10,
                stream=True,
                headers={
                    "User-Agent": "Odoo DigiKey Connector/1.0",
                },
            )
            response.raise_for_status()

            content_type = (
                response.headers.get("Content-Type") or ""
            ).lower()
            if not content_type.startswith("image/"):
                return False

            content_length = response.headers.get("Content-Length")
            if content_length:
                try:
                    if int(content_length) > cls.MAX_IMAGE_SIZE:
                        return False
                except ValueError:
                    pass

            chunks = []
            downloaded_size = 0
            for chunk in response.iter_content(chunk_size=64 * 1024):
                if not chunk:
                    continue
                downloaded_size += len(chunk)
                if downloaded_size > cls.MAX_IMAGE_SIZE:
                    return False
                chunks.append(chunk)

            if not chunks:
                return False

            image_data = b"".join(chunks)
            return base64.b64encode(image_data)
        except requests.RequestException:
            return False