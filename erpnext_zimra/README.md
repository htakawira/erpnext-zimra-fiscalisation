# ERPNext ZIMRA Fiscalisation (v0.1.0)

Frappe app source targeting ERPNext v15. Implements a configurable REST/mTLS gateway client, per-device routing, fiscal-day state, manual and automatic Sales Invoice enqueueing, durable local queue records, and ordered online recovery.

## Important compliance boundary
Based on ZIMRA Fiscal Device Gateway API Specification v3.0 (2023-05-02): online mode is the MVP; offline mode is explicitly out of MVP scope. In the online scenario, if connectivity is lost after opening a fiscal day or issuing a receipt, the delayed openDay message must be sent before receipts and before fiscal-day close. Offline mode in the document describes file submission (Self-Service or a future API). This app's offline queue is a local store-and-forward/recovery mechanism; it does not claim to implement or certify ZIMRA's separate file-based offline mode.

The specification omits production/test base URLs and says endpoint examples are in a separate document. Configure paths and URLs from ZIMRA's current official Swagger/examples. Do not guess them.

## Install
Copy this app folder into a bench's apps directory, then run:
```bash
bench --site SITE install-app erpnext_zimra
bench --site SITE migrate
bench build
bench restart
```

Create DocTypes through the Frappe UI or add the DocType JSON definitions from the next release. Configure ZIMRA Settings and Fiscal Devices, then enable the Sales Invoice integration only after staging validation.

## Status
This repository is an early functional integration core, not a production-ready fiscal device or ZIMRA-certified implementation. Remaining work is listed in IMPLEMENTATION_CHECKLIST.md. The supplied specification's missing endpoint examples/test vectors prevent asserting full protocol conformance.
