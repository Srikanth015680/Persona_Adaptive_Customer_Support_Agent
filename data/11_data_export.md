
# Data Export Guide

CloudSuite allows you to export your account data for reporting, backups, or migration purposes.

## Available Export Types

You can export the following data:

* Tickets and conversation history
* Customer and contact records
* Reports and analytics data
* Account backups with attachments (Enterprise plans only)

Depending on the export type, files may be available in CSV, JSON, PDF, or ZIP format.

## Creating an Export

To generate an export:

1. Open  **Settings** .
2. Select  **Data Export** .
3. Choose the data you want to export.
4. Select a date range if applicable.
5. Click  **Generate Export** .

When the export is ready, CloudSuite sends an email containing a secure download link.

## Download Links

Export files are available for download for 72 hours after they are generated.

If the link expires, simply create a new export request.

## Estimated Processing Time

| Data Volume               | Typical Processing Time |
| ------------------------- | ----------------------- |
| Under 10,000 records      | A few minutes           |
| 10,000 – 100,000 records | 15–30 minutes          |
| More than 100,000 records | Up to 4 hours           |

Large exports may take longer depending on system load.

## Exporting Data Before Cancellation

If you plan to cancel your subscription, export any data you want to keep before the account retention period ends.

Archived accounts are retained for a limited period after cancellation. Once account data is permanently removed, it cannot be recovered.

For more information, see  **Cancelling a Subscription** .

## API Exports

Developers can also create exports through the API.

The `/v2/exports` endpoint supports the same export options available in the CloudSuite dashboard.

Before using the API:

* Generate an API key
* Configure Bearer Token authentication
* Verify the required permissions

See the **API Authentication Guide** for setup instructions.

## Related Articles

* Cancelling a Subscription
* API Authentication Guide
* Subscription Plans and Pricing
