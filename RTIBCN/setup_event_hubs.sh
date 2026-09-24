#!/usr/bin/env bash
set -euo pipefail

subscription_id="${AZURE_SUBSCRIPTION_ID:-43552045-b4af-424f-a075-231186cdefe9}"
resource_group="${AZURE_RESOURCE_GROUP:-rg-rtibcn}"
location="${AZURE_LOCATION:-westeurope}"
namespace="${EVENT_HUB_NAMESPACE:-evhns-rtibcn-premium-1976}"
function_app="${FUNCTION_APP_NAME:-func-rtibcn-1976}"

first_hubs=(tmb-ibus-1-65 tmb-metro-1-65)
second_hubs=(tmb-ibus-66-130 tmb-metro-66-130)

az account set --subscription "$subscription_id"

if ! az eventhubs namespace show --resource-group "$resource_group" --name "$namespace" >/dev/null 2>&1; then
  az eventhubs namespace create \
    --resource-group "$resource_group" \
    --name "$namespace" \
    --location "$location" \
    --sku Premium \
    --capacity 1 \
    --output none
fi

for hub in "${first_hubs[@]}" "${second_hubs[@]}"; do
  az eventhubs eventhub create \
    --resource-group "$resource_group" \
    --namespace-name "$namespace" \
    --name "$hub" \
    --partition-count 2 \
    --cleanup-policy Delete \
    --retention-time-in-hours 24 \
    --output none
done

create_consumer_groups() {
  local hub="$1"
  local first_user="$2"
  local last_user="$3"
  local consumer_group
  local -a pending_processes=()

  for user_number in $(seq "$first_user" "$last_user"); do
    consumer_group=$(printf 'user-%03d' "$user_number")
    az eventhubs eventhub consumer-group create \
      --resource-group "$resource_group" \
      --namespace-name "$namespace" \
      --eventhub-name "$hub" \
      --name "$consumer_group" \
      --output none &
    pending_processes+=("$!")

    if (( ${#pending_processes[@]} == 8 )); then
      for process_id in "${pending_processes[@]}"; do
        wait "$process_id"
      done
      pending_processes=()
    fi
  done

  for process_id in "${pending_processes[@]}"; do
    wait "$process_id"
  done
}

for hub in "${first_hubs[@]}"; do
  create_consumer_groups "$hub" 1 65
done

for hub in "${second_hubs[@]}"; do
  create_consumer_groups "$hub" 66 130
done

principal_id=$(az functionapp identity show \
  --resource-group "$resource_group" \
  --name "$function_app" \
  --query principalId \
  --output tsv)
namespace_id=$(az eventhubs namespace show \
  --resource-group "$resource_group" \
  --name "$namespace" \
  --query id \
  --output tsv)

if ! az role assignment list \
  --assignee-object-id "$principal_id" \
  --scope "$namespace_id" \
  --role "Azure Event Hubs Data Sender" \
  --query '[0].id' \
  --output tsv | grep -q .; then
  az role assignment create \
    --assignee-object-id "$principal_id" \
    --assignee-principal-type ServicePrincipal \
    --role "Azure Event Hubs Data Sender" \
    --scope "$namespace_id" \
    --output none
fi

az functionapp config appsettings set \
  --resource-group "$resource_group" \
  --name "$function_app" \
  --settings \
    "EVENT_HUB_CONNECTION__fullyQualifiedNamespace=$namespace.servicebus.windows.net" \
    "EVENT_HUB_CONNECTION__credential=managedidentity" \
    "EVENT_HUB_NAME_IBUS_1_65=tmb-ibus-1-65" \
    "EVENT_HUB_NAME_IBUS_66_130=tmb-ibus-66-130" \
    "EVENT_HUB_NAME_METRO_1_65=tmb-metro-1-65" \
    "EVENT_HUB_NAME_METRO_66_130=tmb-metro-66-130" \
    "TMB_IBUS_STOPS=2689,2259,3347,1090,3477,1878,2700,662,32,2265,1297,956,3878,281,1210,1103,1282,784" \
    "TMB_METRO_STATIONS=416,415,417,422,425,126,130,523,521,518" \
  --output none

printf 'Configured %s with four Event Hubs and 65 workshop consumer groups per hub.\n' "$namespace"