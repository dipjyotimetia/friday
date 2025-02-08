# API Test Results
        Generated on: 2025-02-08 17:02:34

        ## Summary
        - Total Tests: 19
        - Passed: 0
        - Failed: 19
        - Errors: 0

        ## Detailed Results

### Basic post /pet test
Status: FAIL
Response Code: 415
Response: ```json
{
  "raw": "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?><apiResponse><type>unknown</type></apiResponse>"
}
```

### Basic put /pet test
Status: FAIL
Response Code: 405
Response: ```json
{
  "raw": "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?><apiResponse><type>unknown</type></apiResponse>"
}
```

### Basic get /pet/findByStatus test
Status: FAIL
Response Code: 404
Response: ```json
{
  "raw": "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?><apiResponse><message>null for uri: http://petstore.swagger.io/v2/pet/pet/findByStatus</message><type>unknown</type></apiResponse>"
}
```

### Basic get /pet/findByTags test
Status: FAIL
Response Code: 404
Response: ```json
{
  "raw": "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?><apiResponse><message>null for uri: http://petstore.swagger.io/v2/pet/pet/findByTags</message><type>unknown</type></apiResponse>"
}
```

### Basic get /pet/{petId} test
Status: FAIL
Response Code: 404
Response: ```json
{
  "raw": "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?><apiResponse><message>null for uri: http://petstore.swagger.io/v2/pet/pet/%7BpetId%7D</message><type>unknown</type></apiResponse>"
}
```

### Basic post /pet/{petId} test
Status: FAIL
Response Code: 404
Response: ```json
{
  "raw": "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?><apiResponse><message>null for uri: http://petstore.swagger.io/v2/pet/pet/%7BpetId%7D</message><type>unknown</type></apiResponse>"
}
```

### Basic delete /pet/{petId} test
Status: FAIL
Response Code: 404
Response: ```json
{
  "raw": "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?><apiResponse><message>null for uri: http://petstore.swagger.io/v2/pet/pet/%7BpetId%7D</message><type>unknown</type></apiResponse>"
}
```

### Basic post /pet/{petId}/uploadImage test
Status: FAIL
Response Code: 404
Response: ```json
{
  "raw": "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?><apiResponse><message>null for uri: http://petstore.swagger.io/v2/pet/pet/%7BpetId%7D/uploadImage</message><type>unknown</type></apiResponse>"
}
```

### Basic get /store/inventory test
Status: FAIL
Response Code: 404
Response: ```json
{
  "raw": "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?><apiResponse><message>null for uri: http://petstore.swagger.io/v2/pet/store/inventory</message><type>unknown</type></apiResponse>"
}
```

### Basic post /store/order test
Status: FAIL
Response Code: 404
Response: ```json
{
  "raw": "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?><apiResponse><message>null for uri: http://petstore.swagger.io/v2/pet/store/order</message><type>unknown</type></apiResponse>"
}
```

### Basic get /store/order/{orderId} test
Status: FAIL
Response Code: 404
Response: ```json
{
  "raw": "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?><apiResponse><message>null for uri: http://petstore.swagger.io/v2/pet/store/order/%7BorderId%7D</message><type>unknown</type></apiResponse>"
}
```

### Basic delete /store/order/{orderId} test
Status: FAIL
Response Code: 404
Response: ```json
{
  "raw": "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?><apiResponse><message>null for uri: http://petstore.swagger.io/v2/pet/store/order/%7BorderId%7D</message><type>unknown</type></apiResponse>"
}
```

### Basic post /user test
Status: FAIL
Response Code: 415
Response: ```json
{
  "raw": "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?><apiResponse><type>unknown</type></apiResponse>"
}
```

### Basic post /user/createWithList test
Status: FAIL
Response Code: 404
Response: ```json
{
  "raw": "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?><apiResponse><message>null for uri: http://petstore.swagger.io/v2/pet/user/createWithList</message><type>unknown</type></apiResponse>"
}
```

### Basic get /user/login test
Status: FAIL
Response Code: 404
Response: ```json
{
  "raw": "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?><apiResponse><message>null for uri: http://petstore.swagger.io/v2/pet/user/login</message><type>unknown</type></apiResponse>"
}
```

### Basic get /user/logout test
Status: FAIL
Response Code: 404
Response: ```json
{
  "raw": "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?><apiResponse><message>null for uri: http://petstore.swagger.io/v2/pet/user/logout</message><type>unknown</type></apiResponse>"
}
```

### Basic get /user/{username} test
Status: FAIL
Response Code: 404
Response: ```json
{
  "raw": "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?><apiResponse><message>null for uri: http://petstore.swagger.io/v2/pet/user/%7Busername%7D</message><type>unknown</type></apiResponse>"
}
```

### Basic put /user/{username} test
Status: FAIL
Response Code: 404
Response: ```json
{
  "raw": "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?><apiResponse><message>null for uri: http://petstore.swagger.io/v2/pet/user/%7Busername%7D</message><type>unknown</type></apiResponse>"
}
```

### Basic delete /user/{username} test
Status: FAIL
Response Code: 404
Response: ```json
{
  "raw": "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?><apiResponse><message>null for uri: http://petstore.swagger.io/v2/pet/user/%7Busername%7D</message><type>unknown</type></apiResponse>"
}
```
