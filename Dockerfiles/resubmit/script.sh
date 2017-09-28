#!/bin/sh

echo "Running cron-job emailrelay-resubmit at $(date)"

/emailrelay-resubmit /var/spool/emailrelay
