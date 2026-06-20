
# API Authentication

CloudSuite APIs use Bearer Token authentication. Every request must include a valid API key in the `Authorization` header.

## Creating an API Key

To generate a new API key:

1. Open  **Developer Settings** .
2. Select  **API Keys** .
3. Click  **Generate New Key** .
4. Copy and store the key in a secure location.

For security reasons, API keys are only displayed once when they are created.

## Example Request

```http
GET /v2/tickets HTTP/1.1
Host: api.cloudsuite.com
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

Requests without a valid API key will be rejected.

## Common Authentication Errors

### 401 Unauthorized

The API could not validate the token provided.

Possible causes:

* Missing `Authorization` header
* Invalid API key
* Typo in the token value
* Missing `Bearer` prefix
* Key belongs to a different workspace

### 403 Forbidden

The API key is valid, but it does not have permission to access the requested resource.

Check the permissions assigned to the account that created the key.

### 419 Token Expired

The token has expired and can no longer be used.

Generate a new token and update any applications that depend on it.

## Troubleshooting 401 Errors

If you're receiving a 401 response:

1. Confirm the header format is:

```text
Authorization: Bearer YOUR_API_KEY
```

2. Verify the API key has not been revoked.
3. Make sure the key belongs to the correct workspace.
4. Generate a new key and test again.
5. If using service-to-service authentication, verify that system clocks are synchronized.

Most authentication failures are caused by incorrect header formatting or expired credentials.

## Rotating API Keys

When replacing an API key:

1. Create the new key first.
2. Update all applications and services that use the old key.
3. Test the new key.
4. Revoke the old key once migration is complete.

Key revocation takes effect immediately.

## Related Articles

* API Rate Limits
* Webhook Configuration Guide
* Developer Setup Guide
