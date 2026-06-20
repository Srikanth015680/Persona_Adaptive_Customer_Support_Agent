
# Salesforce Integration Guide

CloudSuite can connect with Salesforce to keep customer information, tickets, and account records synchronized between both platforms.

The integration is available on Pro and Enterprise plans.

## Connecting Salesforce

To set up the integration:

1. Open  **Integrations** .
2. Select  **Salesforce** .
3. Click  **Connect** .
4. Sign in with your Salesforce account.
5. Review the requested permissions.
6. Configure your field mappings.
7. Click  **Activate Sync** .

CloudSuite uses Salesforce OAuth for authentication and does not store your Salesforce password.

## Field Mapping

Field mapping determines how information is shared between CloudSuite and Salesforce.

Examples:

* Ticket Priority → Salesforce Case Priority
* Customer Name → Contact Name
* Account Owner → Account Owner

Default mappings are provided, but you can modify them if needed.

## Sync Options

You can choose how data is synchronized:

* CloudSuite → Salesforce
* Salesforce → CloudSuite
* Two-way synchronization

Choose the option that best fits your workflow.

## Sync Timing

New records are usually synchronized automatically within a few moments.

CloudSuite also performs periodic checks to make sure records remain consistent across both systems.

Large accounts with significant amounts of data may require additional time during the initial setup.

## Common Sync Issues

### Duplicate Records

Duplicate records can occur if the same customer or ticket is created in both systems before synchronization begins.

Use the **Merge Duplicates** tool to combine duplicate records.

### Permission Errors

If records are not updating correctly, verify that the connected Salesforce user has the required permissions.

In some cases, reconnecting the integration with an administrator account may resolve the issue.

### Missing Updates

If expected updates are not appearing:

1. Check the integration status page.
2. Review recent sync activity.
3. Confirm field mappings are configured correctly.
4. Reconnect the integration if necessary.

## Disconnecting Salesforce

Disconnecting the integration stops future synchronization.

Existing records that were already synced remain available in both CloudSuite and Salesforce.

No previously synced data is automatically removed.

## Related Articles

* API Authentication Guide
* Webhook Configuration Guide
* Data Export Guide
