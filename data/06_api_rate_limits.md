
# API Rate Limits

CloudSuite applies rate limits to help maintain platform stability and ensure fair usage across all customers.

## Current Limits

| Plan       | Requests per Minute | Burst Allowance |
| ---------- | ------------------- | --------------- |
| Starter    | 60                  | 10              |
| Pro        | 300                 | 50              |
| Enterprise | 2,000               | 200             |

If your application exceeds these limits, requests may be temporarily blocked until the rate limit window resets.

## Rate Limit Headers

Every API response includes rate limit information in the response headers:

* `X-RateLimit-Limit` – Total requests allowed during the current window
* `X-RateLimit-Remaining` – Number of requests remaining
* `X-RateLimit-Reset` – Time when the limit window resets

These headers can be used to monitor usage and avoid hitting rate limits.

## HTTP 429: Too Many Requests

If your application exceeds the allowed limit, the API returns:

```text
HTTP 429 Too Many Requests
```

The response also includes a `Retry-After` header that indicates how long to wait before sending another request.

Recommended approach:

1. Stop sending additional requests.
2. Wait for the time specified in the `Retry-After` header.
3. Retry the request.
4. If the limit is reached again, gradually increase the delay between retries.

This helps prevent repeated throttling and reduces unnecessary API traffic.

## Requesting a Higher Limit

Enterprise customers can request higher API limits if their application regularly exceeds the default allowance.

When contacting support, include:

* Expected request volume
* Peak usage periods
* Business justification for the increase

Most requests are reviewed within 1–2 business days.

## Common Reasons for Rate Limit Errors

Rate limits are most commonly reached when:

* Applications poll endpoints too frequently
* Large batch jobs run at the same time
* Failed requests are retried immediately
* Multiple services share the same API key

Using webhooks instead of frequent polling can significantly reduce API usage.

## Related Articles

* API Authentication
* Webhook Configuration Guide
* Developer Setup Guide
