# Assumptions for the local demo only

1. Each business account controls jobs tied to its organization ID. The two demo organizations cannot edit each other's jobs. Admin can inspect all demo records.
2. Drafts may be edited, published when required fields are present, or deleted. Published jobs may be edited, paused or closed; paused jobs may reopen or close; closed jobs stay read only.
3. Only published jobs receive new applications or invitations. Closing a job preserves pending requests; their recipients may still respond and see a closed-job notice.
4. Hidden/private profiles leave discovery and new invitations. Historic request snapshots retain name, headline and shared skills, but contact consent is rechecked before disclosure.
5. A sender may cancel only a pending request. Any later request for the same job/profile/type pair is blocked in this demo, including after decline/cancel. Product policy for reapplication is undecided.
6. Email appears only in an accepted connection with current candidate consent; for applications, candidate must also have opted in when sending. Exact address and phone fields are not public. This policy is only a UI simulation.
7. `members` means any signed-in demo account. The demo does not provide a guest mode or real membership verification.
8. CV selection stores only filename, MIME type and size in localStorage. A newly selected local file can be previewed in the current browser session; no file bytes are uploaded or stored, and no OCR is performed.
9. Demo account creation is local and does not assign an Odoo group. Business provisioning remains an operator action in the intended architecture.
10. The selected opportunity taxonomy, pay text and matching weights are sample content, not approved production contracts.
