# CSE310_DNS_Project

## TODO

* Part 2
  * client.py
    * Arguments passed to client.py should be for the manager server.
    * Add ability to remember and contact multiple DNS servers.
    * type command
      * Contacts manager to obtain the address of the DNS server that serves that type.
    * done command
      * Terminates TCP connection with the type DNS server.
  * manager.py (Should manager.py and server.py be in the same file if that's easier?)
    * Reads `manager.in` and starts a DNS server for each type.
    * Receives type requests from client.py and returns the address/port of the appropriate DNS server.
  * server.py
    * Must be able to be started by manager.
    * Must read/write from own records file (separate from other server processes).
* Comments
  * Code must be well-documented.
* Documentation (Must be a `.pdf`)
  * User Documentation
    * Instructions on starting and using the client/server/manager.
  * System Documentation
    * Description of how program works.
    * Protocol description.
    * Important data structures / algorithms.
    * Error conditions.
    * How concurrency is handled.
    * etc.
  * Testing Documentation
    * List of testing scenarios.
      * Why each test case was chosen.
      * Expected output.
      * Actual output.

## Known Issues

* None

## Storage

DNS records are stored in a text file.
Records are stored as follows:

`records.txt`:

``` plaintext
name1 type1 value1\r\n
name2 type2 value2\r\n
```

## Protocol

### Request Format

``` plaintext
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

Requests must be under 1024 bytes in length.

### Response Format

``` plaintext
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