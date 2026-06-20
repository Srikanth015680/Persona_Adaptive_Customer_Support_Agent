
# Webhook Configuration Guide

Webhooks allow your application to receive updates from CloudSuite automatically whenever an event occurs. This removes the need to continuously poll the API for changes.

Examples of webhook events include:

* Ticket creation
* Payment failures
* Subscription updates
* User account changes

## Creating a Webhook Endpoint

To add a webhook:

1. Open  **Developer Settings** .
2. Select  **Webhooks** .
3. Click  **Add Endpoint** .
4. Enter a public HTTPS URL.
5. Choose the events you want to receive.
6. Save the configuration.

After saving, CloudSuite sends a test `ping` event to verify that the endpoint can receive requests.

**Note:** Production webhooks require an HTTPS endpoint. HTTP and localhost addresses are not supported.

## Verifying Webhook Requests

Every webhook request includes an `X-CloudSuite-Signature` header.

Before processing a webhook event, verify the signature using your webhook signing secret.

Signature verification helps ensure that requests are coming from CloudSuite and have not been modified during transmission.

## Delivery and Retry Behavior

CloudSuite expects your endpoint to return a successful `2xx` response.

If a successful response is not received within 10 seconds, the event is retried automatically.

Retry schedule:

* 1 minute
* 5 minutes
* 30 minutes
* 2 hours
* 12 hours

After multiple failed delivery attempts, the event is marked as failed and appears in the  **Webhook Delivery Log** .

## Troubleshooting Missing Webhooks

If events are not arriving:

1. Review the  **Webhook Delivery Log** .
2. Check the HTTP response code returned by your endpoint.
3. Confirm the endpoint URL is reachable from the internet.
4. Verify that the required event type is subscribed.
5. Make sure firewalls or authentication settings are not blocking requests.

You can also use the **Resend** option in the delivery log to send a previous event again for testing.

## Common Issues

### Endpoint Not Reachable

The webhook URL cannot be contacted from CloudSuite servers.

Check:

* DNS configuration
* SSL certificate validity
* Firewall settings

### Signature Verification Failed

The signing secret used by your application does not match the secret configured in CloudSuite.

Update the secret and retry the request.

### Receiving Too Many Events

Review the selected event subscriptions and disable events that your application does not need.

## Related Articles

* API Authentication
* API Rate Limits
* Developer Setup Guide
