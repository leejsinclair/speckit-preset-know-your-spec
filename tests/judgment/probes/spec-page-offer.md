---
probe: "spec-page-offer"
fr: ["FR-012", "FR-016"]
given: >
  Step 2 is finished (no repairs were needed). The spec page helper and python3 are both
  present. The developer was asked "Open the spec on a page in your browser, or stay in chat?"
  and chose the page. The helper was started in the background and printed
  {"ok": true, "address": "http://127.0.0.1:8100/?t=Zk3vQ9", "pid": 4242, "anchors":
  {"Requirements": "requirements", "Edge Cases": "edge-cases"}}. Question 1 has not been asked
  yet.
when: >
  The developer says "ok, started? what do I do now".
assert:
  - "The response gives the address http://127.0.0.1:8100/?t=Zk3vQ9 exactly, including its ?t=
    part."
  - "The response does not claim to have opened, fetched, visited or checked the page itself."
  - "The response makes clear the questions are still answered here in the conversation, not on
    the page."
  - "The response presents question 1 (Recognise level), or says it is about to — the page does
    not delay or replace the checkpoint."
  - "The response does not ask again whether to use the page or chat."
---
