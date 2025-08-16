# Batch Filtering Script - Summary of Changes

## What's New

The updated `run_batch_filtering.py` script now:

1. **Processes 50 emails at a time** - Instead of processing all emails at once, it works in manageable batches

2. **Shows ALL emails in each batch** - You see both:
   - Emails to be DELETED (with reasons)
   - Emails to be KEPT (with reasons)

3. **Asks for confirmation after each batch** - You have full control over each batch before moving on

4. **Automatically continues to next batch** - After you take action on a batch, it automatically loads the next 50 emails

## Example Output

```
================================================================================
BATCH 1 ANALYSIS COMPLETE
================================================================================
Total emails in batch: 50
Emails to DELETE: 9
Emails to KEEP: 41

================================================================================
EMAILS TO BE DELETED:
================================================================================
  1. Call for Offers Next Week 7/29: 245-Site MH Community in Southeastern PA | 100% Occupancy | All Tenant-Owned Homes
     Reason: Wrong state: PA
  2. Now Touring & Call for Offers: 250 LIHTC Units in Austin, TX
     Reason: Wrong state: Texas
  3. JUST SOLD | The Montana | 8 Units | Premier City Park Asset | 1929 YOC | Denver, CO
     Reason: Wrong state: Colorado
  [... more emails ...]

================================================================================
EMAILS TO BE KEPT:
================================================================================
  1. REMINDER - CALL FOR OFFERS: July 29, 2025 :: Capri North and South | 624 Units | Value-Add Multifamily Community in Las Vegas
     Reason: Could not determine - kept for review
  2. Reminder - Now Touring & Call for Offers: 80 LIHTC Units in Sacramento, CA
     Reason: California - meets criteria
  3. New Exclusive Listing: 10200 De Soto Avenue - 86-Unit Value-Add Opportunity in Chatsworth, CA
     Reason: California, 86 units
  [... more emails ...]

================================================================================
OPTIONS:
1. Type 'DELETE' to delete all listed emails
2. Type 'KEEP' followed by numbers to keep specific emails (e.g., 'KEEP 3,5,12')
3. Type 'SKIP' to skip this batch and continue to next
4. Type 'QUIT' to stop processing
================================================================================

Your choice: [User types here]
```

## User Options

- **DELETE** - Deletes all emails in the "TO BE DELETED" list
- **KEEP 1,3,5** - Keeps specific emails from the deletion list (by number)
- **SKIP** - Skips this batch entirely (keeps all emails)
- **QUIT** - Stops processing

## After Each Batch

Once you make a choice:
1. The script executes your decision
2. Automatically loads the next 50 emails
3. Repeats the process until all emails are processed

## To Run

```bash
python3 run_batch_filtering.py
```

## Benefits

1. **Better Control** - Review each batch before any deletions
2. **Full Visibility** - See ALL emails, not just deletions
3. **Manageable Chunks** - 50 emails at a time is easier to review
4. **Continuous Processing** - No need to restart for each batch