# CSE310_DNS_Project

## Protocol
### Request Format

```
DNS/1.0 METHOD name type value
```

_name_, _type_, and _value_ are optional depending on the method.

Valid Methods:
* PUT
 * Requires _name_, _type_, and _value_.
* GET
 * Requires _name_ and _type_.
* DELETE
 * Requires _name_ and _type_.
* BROWSE
 * Does not require any other fields.

### Response Format

```
DNS/1.0 StatusCode StatusPhrase\r\n
\r\n
name1 type1 value1\r\n
name2 type2 value2\r\n
...
```

Status Code | Status Phrase | Description
----------- | ------------- | -----------
200         | OK            | Request succeeded, requested record(s) later in this message.
201         | Created       | Request succeeded, supplied record successfully created.
400         | Bad Request   | Request message not understood by server.
404         | Not Found     | Requested record not found on this server.