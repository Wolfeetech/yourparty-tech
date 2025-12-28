---
description: Critical Multi-Point Verification (CMPV) Protocol for Agents
---

# Critical Multi-Point Verification (CMPV) Protocol

To ensure the stability and professional quality of the YourParty.tech systems, all agents must adhere to the following verification protocol before presenting work or declaring a task complete.

## 1. Syntax & Static Analysis
- **PHP**: Perform manual linting if automated tools are unavailable. Check for missing semicolons, correct closure scoping (`use` keyword), and adherence to WordPress coding standards (e.g., `wp_json_encode` instead of `json_encode`).
- **JavaScript**: Ensure all variables are properly scoped. Check for potential `null` or `undefined` pointer exceptions during DOM manipulation.
- **Python**: Verify imports and module paths. Ensure type hints are used for clarity.

## 2. Multi-Angle Logic Review
- **Error Handling**: Never assume an API call or database operation succeeds. Always handle failure cases (404, 500, 429) gracefully with user-facing feedback.
- **Edge Cases**: Consider boundary conditions (e.g., empty strings, oversized payloads, non-JSON responses).
- **Security**: Validate all inputs from the frontend. Never expose internal IPs or sensitive keys. Use existing proxy gateways (`inc/api.php`) instead of direct backend calls.

## 3. Position-Based Testing
- **Frontend Perspective**: Does the UI feel responsive? Is there a loading state? Does the feedback match the server response?
- **Backend Perspective**: Are logs descriptive? Is rate-limiting active? Are database transactions atomic?
- **Network Perspective**: Check CORS headers, HTTPS enforcement, and response times.

## 4. Exclusion of Bugs
- Run manual "stress tests" (e.g., rapid clicks, invalid form data).
- Check for regression: Ensure new features don't break existing ones (e.g., audio playback, visualizers).
- **Double-Check**: Verify file paths and line ranges one last time before committing.

> [!IMPORTANT]
> A feature is only "finished" when it has been verified from at least three different positions (UI, Logic, Infrastructure).
