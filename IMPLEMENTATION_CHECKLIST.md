# Implementation and go-live checklist

This checklist distinguishes the intended project scope from items that must be completed and verified before production.

## ZIMRA integration prerequisites
- [ ] Obtain current ZIMRA testing and production base URLs.
- [ ] Obtain current Swagger/API endpoint paths, request/response examples and technical addenda.
- [ ] Confirm registered device model name/version, serial number, device ID and activation credentials.
- [ ] Validate all payloads and response handling against the ZIMRA test environment.

## Device and certificate lifecycle
- [ ] Implement device registration and certificate issuance/renewal.
- [ ] Validate CSR subject distinguished name exactly as required by ZIMRA.
- [ ] Store private keys securely outside source control and public/www.
- [ ] Implement certificate expiry monitoring and server-signature verification.
- [ ] Support multiple fiscal devices per company and branch with explicit routing.

## Receipt fiscalisation
- [ ] Implement manual and automatic Sales Invoice fiscalisation controls.
- [ ] Map tax templates, tax IDs, exempt treatment, discounts and inclusive pricing.
- [ ] Map payment types, currencies, buyer details and receipt document types.
- [ ] Enforce receiptGlobalNo sequencing and durable idempotency.
- [ ] Implement previous-receipt hash chaining exactly against ZIMRA test vectors.
- [ ] Persist receipt ID, server date, server signature and complete audit trail.
- [ ] Implement credit/debit note references and validation.
- [ ] Add receipt print format and QR code to the ERPNext invoice.

## Fiscal day and counters
- [ ] Implement fiscal-day open and close payloads.
- [ ] Implement counter ledger by currency, tax ID and payment type.
- [ ] Implement close-day status polling and reconciliation.
- [ ] Handle FiscalDayClosed and FiscalDayCloseFailed states.
- [ ] Implement Z/X reports as required by the current ZIMRA specification.

## Offline and recovery
- [ ] Confirm the currently approved ZIMRA offline procedure and submission channel.
- [ ] Implement durable offline queueing with strict global receipt ordering.
- [ ] Ensure delayed fiscal-day opening is submitted before queued receipts when required.
- [ ] Reconcile every queued receipt with ZIMRA before advancing the queue.
- [ ] Prevent sequence gaps, duplicate submissions and altered retries.

## Operations and quality
- [ ] Add role permissions and secure configuration management.
- [ ] Add API logs with secrets and private key material redacted.
- [ ] Add automated unit/integration tests and retry/recovery tests.
- [ ] Test multi-company, multi-branch and multi-device scenarios.
- [ ] Complete staging validation and obtain ZIMRA approval before production.

## Current repository state

At the time of this commit, this repository contains project documentation only. The earlier generated ZIP is a preliminary development scaffold and is not included here because its source contents could not be verified and safely transferred into the repository in this session. Do not treat this repository as an installable or production-ready Frappe application yet.
