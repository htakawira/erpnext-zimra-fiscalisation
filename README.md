# ERPNext ZIMRA Fiscalisation Integration

Frappe / ERPNext v15 development scaffold for the ZIMRA Fiscal Device Gateway API v3.0 (2 May 2023).

> **Status: development scaffold only — not production-certified.** The Python application source archive has not yet been committed to this repository. This repository currently contains project documentation only.

## Intended scope

- ERPNext v15
- Online fiscalisation and an offline/recovery workflow
- Multiple fiscal devices per company and branch
- Automatic and manual fiscalisation of Sales Invoices
- Device registration, certificates, fiscal days, receipts, status checks and reconciliation

## API and deployment prerequisites

The supplied ZIMRA API document leaves test and production base URLs as placeholders and refers endpoint paths and request/response examples to separate Swagger/API material. Obtain the current official base URLs, endpoint paths, examples and technical addenda from ZIMRA. Do not guess production URLs or paths.

The v3.0 document describes Online mode as the MVP; Offline mode is outside that MVP scope. An offline implementation must therefore be validated against ZIMRA's current approved offline process before being treated as compliant. In particular, delayed fiscal-day opening and queued receipts must be reconciled in the required order, preserving global receipt numbering.

## Planned installation

Once the complete application source is committed, installation on a Frappe bench will follow this pattern:

```bash
cd ~/frappe-bench
bench get-app https://github.com/htakawira/erpnext-zimra-fiscalisation.git
bench --site your-site install-app erpnext_zimra
bench --site your-site migrate
bench build
bench restart
```

The app module/package name may differ from the Git repository name; use the package name defined by the source.

## Security requirements

- HTTPS only; verify TLS certificates.
- Use mutual TLS for authenticated API operations as required by ZIMRA.
- Keep private keys outside the public web directory and source control.
- Restrict device/settings access to authorised fiscalisation roles.
- Use durable background queues and auditable request/response records.
- Never blindly retry an uncertain receipt with altered payload or sequence data.

## Current implementation caveats

Before production use, the application must be completed and validated for:
- Multiple devices and branch-to-device routing.
- Offline queueing, ordered recovery and reconciliation against ZIMRA's approved offline procedure.
- Global receipt numbering, device hash chain and fiscal counters.
- Certificate lifecycle and signature verification.
- Fiscal-day close submission and asynchronous status polling.
- Credit/debit notes, tax/payment mappings, receipt printing and QR codes.
- Automated tests against ZIMRA test vectors and formal ZIMRA certification/approval.

See [IMPLEMENTATION_CHECKLIST.md](IMPLEMENTATION_CHECKLIST.md) for the remaining work.
