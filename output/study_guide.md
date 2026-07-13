### Explanation
HTTP (Hypertext Transfer Protocol) status codes are used to communicate the outcome of a server request or response. They indicate whether an operation was successful, what went wrong, and sometimes even provide additional information about the request. HTTP status codes are standardized across all web servers and applications.

### Key concepts
* **Informational responses**: 100-199 (e.g., 101 Switching Protocols)
* **Success codes**: 200-299 (e.g., 200 OK, 201 Created)
* **Redirection codes**: 300-399 (e.g., 301 Moved Permanently)
* **Client error codes**: 400-499 (e.g., 404 Not Found, 401 Unauthorized)
* **Server error codes**: 500-599 (e.g., 500 Internal Server Error)

### Example
```http
HTTP/1.1 200 OK
Content-Type: text/html; charset=UTF-8

Hello World!
```
This example shows a successful HTTP response with status code 200, indicating that the request was fulfilled.