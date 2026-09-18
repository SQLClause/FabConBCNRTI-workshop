#!/usr/bin/env bash
# create-eventhubs.sh -- provision the shared Event Hubs feed for the RTI half.
#
# Sized for the room: every attendee eventstream needs its own consumer group, and a hub allows
# 100 (Premium) or 20 (Standard) of them, so the script creates as many hubs per feed as needed
# (tmb-ibus-a, tmb-ibus-b, ... and tmb-metro-a, tmb-metro-b, ...) and assigns attendees to hub
# pairs in infra/out/consumer-groups.csv. The Function must publish to every hub of a feed (see
# function-changes/README.md; two output bindings cover up to 200 attendees on Premium).
#
# Also creates: SAS policies `function-send` (Send; used by replay_events.py) and `attendee-listen`
# (Listen; handed to the room), the Data Sender role for the Function's managed identity, and
# infra/out/function-settings.env.
#
# Usage:
#   ./infra/create-eventhubs.sh --prefix fabcon26 --location westeurope --attendees 120 \
#       [--tier Premium|Standard] [--spare 10] [--function-principal-id <objectId>]
set -euo pipefail

PREFIX=""; LOCATION="westeurope"; ATTENDEES=0; TIER="Premium"; SPARE=10; FUNC_PRINCIPAL=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --prefix) PREFIX="$2"; shift 2;;
    --location) LOCATION="$2"; shift 2;;
    --attendees) ATTENDEES="$2"; shift 2;;
    --tier) TIER="$2"; shift 2;;
    --spare) SPARE="$2"; shift 2;;
    --function-principal-id) FUNC_PRINCIPAL="$2"; shift 2;;
    -h|--help) sed -n '2,17p' "$0"; exit 0;;
    *) echo "Unknown argument: $1" >&2; exit 2;;
  esac
done
[[ -z "$PREFIX" || "$ATTENDEES" -le 0 ]] && { echo "--prefix and --attendees are required" >&2; exit 2; }

case "$TIER" in
  Premium) CG_PER_HUB=100;;
  Standard) CG_PER_HUB=20;;
  *) echo "--tier must be Premium or Standard" >&2; exit 2;;
esac

TOTAL_GROUPS=$((ATTENDEES + SPARE))
HUB_PAIRS=$(( (TOTAL_GROUPS + CG_PER_HUB - 1) / CG_PER_HUB ))
if [[ "$HUB_PAIRS" -gt 2 ]]; then
  cat >&2 <<EOF
$TOTAL_GROUPS consumer groups need $HUB_PAIRS hubs per feed on $TIER ($CG_PER_HUB groups per hub).
The Function change in function-changes/README.md wires two output bindings per feed. For more than two,
either add bindings (_C, _D ...) or use --tier Premium (100 groups per hub: two hubs cover 200 attendees).
EOF
  [[ "$TIER" == "Premium" ]] || exit 1
fi

RG="${PREFIX}-fabcon-rg"
NS="${PREFIX}-fabcon-ehns"
HERE="$(cd "$(dirname "$0")" && pwd)"
OUT_DIR="$HERE/out"
SAMPLE_DIR="$HERE/../artifacts/SampleData"
mkdir -p "$OUT_DIR"

echo "==> Resource group $RG in $LOCATION"
az group create --name "$RG" --location "$LOCATION" --output none

echo "==> Namespace $NS ($TIER)"
if [[ "$TIER" == "Premium" ]]; then
  az eventhubs namespace create --name "$NS" --resource-group "$RG" --location "$LOCATION" \
    --sku Premium --capacity 1 --output none
else
  az eventhubs namespace create --name "$NS" --resource-group "$RG" --location "$LOCATION" \
    --sku Standard --capacity 2 --enable-auto-inflate true --maximum-throughput-units 10 --output none
fi

create_hub() {
  local name="$1" partitions="$2"
  echo "==> Event hub $name ($partitions partitions)"
  az eventhubs eventhub create --name "$name" --namespace-name "$NS" --resource-group "$RG" \
    --partition-count "$partitions" --cleanup-policy Delete --retention-time 24 --output none \
  || az eventhubs eventhub create --name "$name" --namespace-name "$NS" --resource-group "$RG" \
       --partition-count "$partitions" --message-retention 1 --output none
}

BUS_HUBS=(); METRO_HUBS=()
for i in $(seq 1 "$HUB_PAIRS"); do
  suffix=$(printf "\\$(printf '%03o' $((96 + i)))")   # a, b, c ...
  BUS_HUBS+=("tmb-ibus-${suffix}"); METRO_HUBS+=("tmb-metro-${suffix}")
done
for hub in "${BUS_HUBS[@]}"; do create_hub "$hub" 4; done
for hub in "${METRO_HUBS[@]}"; do create_hub "$hub" 2; done

echo "==> SAS policies (namespace level)"
az eventhubs namespace authorization-rule create --name function-send --namespace-name "$NS" --resource-group "$RG" --rights Send --output none
az eventhubs namespace authorization-rule create --name attendee-listen --namespace-name "$NS" --resource-group "$RG" --rights Listen --output none

if [[ -n "$FUNC_PRINCIPAL" ]]; then
  echo "==> Role 'Azure Event Hubs Data Sender' for principal $FUNC_PRINCIPAL"
  NS_ID=$(az eventhubs namespace show --name "$NS" --resource-group "$RG" --query id -o tsv)
  az role assignment create --assignee-object-id "$FUNC_PRINCIPAL" --assignee-principal-type ServicePrincipal \
    --role "Azure Event Hubs Data Sender" --scope "$NS_ID" --output none
fi

echo "==> $TOTAL_GROUPS consumer groups across $HUB_PAIRS hub pair(s)"
SEATS="$OUT_DIR/consumer-groups.csv"
echo "Seat,ConsumerGroup,BusHub,MetroHub" > "$SEATS"
PER_PAIR=$(( (TOTAL_GROUPS + HUB_PAIRS - 1) / HUB_PAIRS ))   # spread evenly, e.g. 130 -> 65 + 65
for i in $(seq 1 "$TOTAL_GROUPS"); do
  cg=$(printf "attendee-%03d" "$i")
  idx=$(( (i - 1) / PER_PAIR ))
  bus_hub="${BUS_HUBS[$idx]}"; metro_hub="${METRO_HUBS[$idx]}"
  for hub in "$bus_hub" "$metro_hub"; do
    az eventhubs eventhub consumer-group create --name "$cg" --eventhub-name "$hub" \
      --namespace-name "$NS" --resource-group "$RG" --output none
  done
  echo "$i,$cg,$bus_hub,$metro_hub" >> "$SEATS"
done

echo "==> Keys and Function settings"
SEND_CS=$(az eventhubs namespace authorization-rule keys list --name function-send --namespace-name "$NS" --resource-group "$RG" --query primaryConnectionString -o tsv)
LISTEN_KEY=$(az eventhubs namespace authorization-rule keys list --name attendee-listen --namespace-name "$NS" --resource-group "$RG" --query primaryKey -o tsv)

IBUS_STOPS=""; METRO_STATIONS=""
[[ -f "$SAMPLE_DIR/stops.csv" ]] && IBUS_STOPS=$(tail -n +2 "$SAMPLE_DIR/stops.csv" | cut -d, -f1 | paste -sd, -)
[[ -f "$SAMPLE_DIR/metro_stations.csv" ]] && METRO_STATIONS=$(tail -n +2 "$SAMPLE_DIR/metro_stations.csv" | cut -d, -f1 | paste -sd, -)

{
  echo "# Azure Function app settings (RTIBCN). Do not commit. Generated $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "EVENT_HUB_CONNECTION__fullyQualifiedNamespace=${NS}.servicebus.windows.net"
  echo "EVENT_HUB_NAME_IBUS_A=${BUS_HUBS[0]}"
  echo "EVENT_HUB_NAME_IBUS_B=${BUS_HUBS[1]:-${BUS_HUBS[0]}}"
  echo "EVENT_HUB_NAME_METRO_A=${METRO_HUBS[0]}"
  echo "EVENT_HUB_NAME_METRO_B=${METRO_HUBS[1]:-${METRO_HUBS[0]}}"
  echo "IBUS_SCHEDULE=*/30 * * * * *"
  echo "METRO_SCHEDULE=0 */1 * * * *"
  echo "TMB_MAX_CONCURRENCY=5"
  echo "TMB_IBUS_STOPS=${IBUS_STOPS:-<run infra/resolve_stops.py first>}"
  echo "TMB_METRO_STATIONS=${METRO_STATIONS:-<run infra/resolve_stops.py first>}"
  echo "# Used only by infra/replay_events.py (SAS, Send):"
  echo "EVENTHUB_SEND_CONNECTION_STRING=$SEND_CS"
} > "$OUT_DIR/function-settings.env"
chmod 600 "$OUT_DIR/function-settings.env"

cat <<EOF

Done.

Values for the attendee slide (Module 02):
  Event Hubs namespace  : $NS
  Bus hubs              : ${BUS_HUBS[*]}     (each attendee's hub is on the seat sheet)
  Metro hubs            : ${METRO_HUBS[*]}
  Shared access key name: attendee-listen
  Shared access key     : $LISTEN_KEY
  Consumer groups       : $SEATS  (one per attendee -- nobody uses \$Default)

Function settings written to $OUT_DIR/function-settings.env (keep private).
$( [[ -z "$FUNC_PRINCIPAL" ]] && echo "Remember to grant the Function App identity 'Azure Event Hubs Data Sender' on $NS (re-run with --function-principal-id)." )
Tear down after the event:  az group delete --name $RG --yes --no-wait
EOF
