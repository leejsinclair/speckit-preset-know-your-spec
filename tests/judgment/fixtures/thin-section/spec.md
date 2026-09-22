# Feature Specification: Bulk Import Partial-Failure Retry

**Feature Branch**: `003-bulk-import-retry`

**Created**: 2026-09-22

**Status**: Draft

**Input**: User description: "When a bulk import of records partially fails, retry only the failed rows automatically instead of making the user re-upload the whole file, but give up after a bounded number of attempts."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Import a file successfully (Priority: P1)

A user uploads a file of records to import. All rows succeed. The user sees a confirmation with
the count of records imported.

**Why this priority**: The baseline happy path every other story builds on.

**Independent Test**: Upload a valid file where every row is well-formed and confirm all rows are
imported and a success confirmation with the correct count is shown.

**Acceptance Scenarios**:

1. **Given** a well-formed import file, **When** the user uploads it, **Then** every row is
   imported and a confirmation shows the total count imported.

---

### User Story 2 - Automatically retry rows that fail on first attempt (Priority: P1)

Some rows in an uploaded file fail on the first import attempt (for reasons like a transient
downstream conflict). Rather than requiring the user to re-upload the entire file, the system
automatically retries only the rows that failed, up to 3 total attempts per row, before giving up
on any row still failing after the third attempt and reporting it to the user as permanently
failed alongside the rows that succeeded.

**Why this priority**: This is the entire point of the feature — without automatic retry of just
the failed subset, this is no different from asking the user to re-upload everything.

**Independent Test**: Upload a file where a known subset of rows fail on their first attempt but
succeed on a later attempt, and confirm only those specific rows are retried (not the whole
file), and that the final report distinguishes rows that succeeded after retry from any that
exhausted all 3 attempts.

**Acceptance Scenarios**:

1. **Given** a file where 2 of 10 rows fail on the first attempt but would succeed if retried,
   **When** the import runs, **Then** those 2 rows are automatically retried without re-running
   the other 8, and the final report shows all 10 rows succeeded (2 of them after retry).
2. **Given** a row that fails on all 3 attempts, **When** the third attempt's failure is
   recorded, **Then** the system stops retrying that specific row, includes it in the final
   report as permanently failed, and still reports the rows that did succeed rather than treating
   the whole import as failed.

---

### Edge Cases

- What happens when something goes wrong during import? The system handles errors gracefully.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST import every row of a well-formed file and report the total count
  imported.
- **FR-002**: System MUST automatically retry only the specific rows that failed on a prior
  attempt, not the entire file.
- **FR-003**: System MUST stop retrying a given row after 3 total attempts and report it as
  permanently failed.
- **FR-004**: System MUST report which rows succeeded (including those that succeeded only after
  a retry) separately from rows that permanently failed, in a single final report per import.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A file with some transiently-failing rows completes with all recoverable rows
  imported successfully, without the user re-uploading anything.
- **SC-002**: No row is retried more than 3 total times.

## Assumptions

- A "transient" failure is one that may succeed on a later attempt; the specific causes of
  transient failure are out of scope for this feature.
