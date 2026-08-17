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
    }

    @classmethod
    def get_products(cls, category_external_id, limit=5):
        products = cls.MOCK_PRODUCTS.get(category_external_id, [])

        result = []

        for product in products[:limit]:
            product_data = product.copy()

            product_number = product_data["digikey_product_number"].lower()

            product_data["datasheet_url"] = (
                f"https://example.com/{product_number}-datasheet.pdf"
            )

            product_data["product_url"] = (
                f"https://example.com/{product_number}"
            )

            result.append(product_data)

        return result