# Email Deal Filter - Assistant Contract

## Core Principles

### 1. Always Show ALL Emails Before Delete
- **ALWAYS** display the full list of ALL emails in the batch before any deletion occurs
- Show BOTH emails marked for deletion AND emails marked to keep
- **NEVER** delete emails without explicit user review and confirmation of the complete batch
- Show both the email subject and the reason for deletion/keeping
- Process in batches of 50 emails at a time
- After each batch confirmation, automatically continue to the next batch

### 2. User Control
- The user must explicitly type 'DELETE' to confirm deletion of all emails
- The user can selectively keep emails by typing 'KEEP' followed by email numbers
- The user can skip a batch or quit at any time

### 3. Safety First
- If there's any error processing an email, keep it for safety
- If unable to determine criteria, keep the email for manual review
- Never delete emails with processing errors

## Email Filtering Criteria

### Delete Emails That Are:
1. From wrong states (not CA, AZ, or NM)
2. Have fewer than 50 units (unless it's a land opportunity)
3. Non-deal emails (workshops, newsletters, "just closed", "recently financed", etc.)

### Keep Emails That Are:
1. In target states with 50+ units
2. Land opportunities in target states (regardless of unit count)
3. Unable to be analyzed (kept for safety)

## Script Behavior

### Batch Processing
- Process emails in batches of 50
- Show progress during analysis
- Display summary after each batch
- Automatically continue to next batch after user action

### Display Format
```
BATCH 1 ANALYSIS COMPLETE
================================================================================
Total emails in batch: 50
Emails to DELETE: 13
Emails to KEEP: 37

================================================================================
EMAILS TO BE DELETED:
================================================================================
  1. [Full Email Subject]
     Reason: [Specific reason for deletion]
  2. [Full Email Subject]
     Reason: [Specific reason for deletion]

================================================================================
EMAILS TO BE KEPT:
================================================================================
  1. [Full Email Subject]
     Reason: [Specific reason for keeping]
  2. [Full Email Subject]
     Reason: [Specific reason for keeping]
```

### User Options
1. DELETE - Delete all listed emails
2. KEEP 3,5,12 - Keep specific emails by number
3. SKIP - Skip this batch
4. QUIT - Stop processing

## Commands to Run

When running email filtering:
```bash
python3 run_batch_filtering.py
```

For testing or verification:
```bash
python3 verify_batch.py
```

## Important Notes
- BOTH deletion AND keep lists are ALWAYS shown before any deletion action
- Full subject lines are displayed for ALL emails in the batch
- Each batch of 50 emails requires explicit user action before proceeding
- After user action on a batch, the script automatically continues to the next batch
- Process continues until all emails have been processed