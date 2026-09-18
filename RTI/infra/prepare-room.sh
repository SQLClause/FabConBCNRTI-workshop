#!/usr/bin/env bash
# prepare-room.sh -- the two things RTIBCN/setup_event_hubs.sh doesn't do: a listen-only SAS policy
# for the room, and a printable seat sheet mapping attendees to consumer groups and hubs.
#
# Run AFTER ../../RTIBCN/setup_event_hubs.sh (which creates the Premium namespace, the four hubs,
# the user-001..user-130 consumer groups, and the Function's Data Sender role).
#
# Usage:
#   ./infra/prepare-room.sh            # uses the same env-var defaults as setup_event_hubs.sh
#   AZURE_RESOURCE_GROUP=... EVENT_HUB_NAMESPACE=... ./infra/prepare-room.sh
set -euo pipefail

subscription_id="${AZURE_SUBSCRIPTION_ID:-43552045-b4af-424f-a075-231186cdefe9}"
resource_group="${AZURE_RESOURCE_GROUP:-rg-rtibcn}"
namespace="${EVENT_HUB_NAMESPACE:-evhns-rtibcn-premium-1976}"

HERE="$(cd "$(dirname "$0")" && pwd)"
OUT_DIR="$HERE/out"
mkdir -p "$OUT_DIR"

az account set --subscription "$subscription_id"

echo "==> Listen-only SAS policy 'attendee-listen' on $namespace (idempotent)"
az eventhubs namespace authorization-rule create --name attendee-listen \
  --namespace-name "$namespace" --resource-group "$resource_group" --rights Listen --output none

echo "==> Send policy 'function-send' for infra/replay_events.py (idempotent; the Function itself uses managed identity)"
az eventhubs namespace authorization-rule create --name function-send \
  --namespace-name "$namespace" --resource-group "$resource_group" --rights Send --output none

LISTEN_KEY=$(az eventhubs namespace authorization-rule keys list --name attendee-listen \
  --namespace-name "$namespace" --resource-group "$resource_group" --query primaryKey -o tsv)
SEND_CS=$(az eventhubs namespace authorization-rule keys list --name function-send \
  --namespace-name "$namespace" --resource-group "$resource_group" --query primaryConnectionString -o tsv)

echo "==> Seat sheet"
SEATS="$OUT_DIR/seat-sheet.csv"
echo "Seat,ConsumerGroup,BusHub,MetroHub" > "$SEATS"
for i in $(seq 1 130); do
  cg=$(printf 'user-%03d' "$i")
  if (( i <= 65 )); then bus="tmb-ibus-1-65"; metro="tmb-metro-1-65"; else bus="tmb-ibus-66-130"; metro="tmb-metro-66-130"; fi
  echo "$i,$cg,$bus,$metro" >> "$SEATS"
done

printf 'EVENTHUB_SEND_CONNECTION_STRING=%s\n' "$SEND_CS" > "$OUT_DIR/replay.env"
chmod 600 "$OUT_DIR/replay.env"

cat <<EOF

Done.

Values for the attendee slide (Module 02):
  Event Hubs namespace  : $namespace
  Shared access key name: attendee-listen
  Shared access key     : $LISTEN_KEY
  Seat sheet            : $SEATS   (seat -> consumer group user-NNN + which hubs; nobody uses \$Default)

Replay connection string written to $OUT_DIR/replay.env (Send; keep private).
EOF
