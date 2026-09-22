# Feature Specification: Read Receipt Toggle

**Feature Branch**: `004-read-receipt-toggle`

**Created**: 2026-09-22

**Status**: Draft

**Input**: User description: "Let a user turn read receipts on or off. The change should only affect messages read after the change, never messages already read before it."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Turn read receipts on or off (Priority: P1)

A user opens their privacy settings and toggles read receipts off. From that point forward, the
other party in a conversation no longer sees a read receipt when this user reads a message. Any
read receipt already sent for a message read before the toggle was changed is not retracted.

**Why this priority**: This is the entire feature — a single on/off control with one clear
behavioral rule about what it does and doesn't affect retroactively.

**Independent Test**: Toggle read receipts off, read a new message, and confirm no read receipt
is sent for it, while confirming a receipt sent before the toggle was changed remains as it was.

**Acceptance Scenarios**:

1. **Given** read receipts are currently on, **When** the user toggles them off, **Then** reading
   any message afterward does not send a read receipt for it.
2. **Given** read receipts are currently off, **When** the user toggles them back on, **Then**
   reading any message afterward sends a read receipt for it as normal.
3. **Given** a read receipt was already sent for a message before the user toggled the setting,
   **When** the toggle changes, **Then** that already-sent receipt is not retracted or altered.

---

### Edge Cases

- What if something unexpected happens while toggling the setting? The system behaves sensibly.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a single on/off control for read receipts.
- **FR-002**: System MUST default read receipts to on for a new user.
- **FR-003**: System MUST apply a toggle change only to messages read after the change, never
  retroactively to messages already read before it.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A toggle change takes effect for the very next message read afterward, with no
  delay.
- **SC-002**: A read receipt sent before a toggle change is never altered by that later change.

## Assumptions

- This feature covers only the on/off control and its forward-only effect; how read receipts are
  transmitted or displayed to the other party is out of scope.
