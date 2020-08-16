schema = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["address", "owner", "floors"],
        "properties": {
            "owner": {
                "bsonType": "string",
                "description": "must be a string and is required"
            },
            "floors": {
                "bsonType": "int",
                "minimum": 1,
                "description": "must be an integer with minimum of 1 and is required"
            },
            "address": {
                "bsonType": "object",
                "required": ["city", "houseNumber", "street"],
                "properties": {
                    "street": {
                        "bsonType": "string",
                        "description": "must be a string and is required"
                    },
                    "city": {
                        "bsonType": "string",
                        "description": "must be a string and is required"
                    },
                    "houseNumber": {
                        "bsonType": "int",
                        "minimum": 1,
                        "description": "must be an integer with minimum of 1 and is required"
                    },
                    "houseNumberAdd": {
                        "bsonType": "string",
                        "description": "must be a string if present and have a length of exactly 1"
                    }
                }
            }
        }
    }
}
