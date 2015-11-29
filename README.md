# CSE310_DNS_Project

## Known Issues
* The first response is always interpreted as invalid.

## TODO
* Finish implementing client.py

## Storage

DNS records are stored in a text file.
Records are stored as follows:

`records.txt`:
```
name1 type1 value1\r\n
name2 type2 value2\r\n
```

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
name1 type1 value1\r\n
name2 type2 value2\r\n
...
\r\n
```

Status Code | Status Phrase       | Description
----------- | -------------       | -----------
200         | OK                  | Request succeeded, requested record(s) later in this message.
201         | Created             | Request succeeded, supplied record successfully created.
400         | Bad Request         | Request message not understood by server.
404         | Not Found           | Requested record not found on this server.
503         | Service Unavailable | Server is currently unavailable to handle the request.