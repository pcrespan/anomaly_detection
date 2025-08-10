#!/bin/bash

GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

function pause() {
  sleep 1
}

BASE_URL="http://localhost:8080"
EXAMPLE_DIR="./static/example"
mkdir -p "$EXAMPLE_DIR"

echo -e "${BLUE}Starting training tests...${NC}"

sensors=("sensor_01" "sensor_02" "sensor_03" "sensor_04" "sensor_05")
values=("10.0,10.5,11.0" "20.0,20.5,21.0" "30.0,30.5,31.0" "40.0,41.0,39.0" "50.0,49.5,50.5")
timestamps=(1693459200 1693459260 1693459320)

for idx in ${!sensors[@]}; do
  sensor=${sensors[$idx]}
  IFS=',' read -r v1 v2 v3 <<< "${values[$idx]}"

  echo -e "${GREEN}Training ${sensor}${NC}"
  curl -s -X POST ${BASE_URL}/fit/${sensor} \
    -H "Content-Type: application/json" \
    -d "{
      \"timestamps\": [${timestamps[0]}, ${timestamps[1]}, ${timestamps[2]}],
      \"values\": [${v1}, ${v2}, ${v3}]
    }"
  echo -e "\n"
  pause
done

echo -e "${YELLOW}Sending invalid training request (constant data)...${NC}"
curl -s -X POST ${BASE_URL}/fit/sensor_06 \
  -H "Content-Type: application/json" \
  -d '{
    "timestamps": [1693459200, 1693459260, 1693459320],
    "values": [10.0, 10.0, 10.0]
  }'
echo -e "\n"
pause

echo -e "${YELLOW}Sending invalid training request (empty data)...${NC}"
curl -s -X POST ${BASE_URL}/fit/sensor_07 \
  -H "Content-Type: application/json" \
  -d '{
    "timestamps": [],
    "values": []
  }'
echo -e "\n"
pause

echo -e "${BLUE}Retraining sensor_01 to check version increment...${NC}"
curl -s -X POST ${BASE_URL}/fit/sensor_01 \
  -H "Content-Type: application/json" \
  -d "{
    \"timestamps\": [1693460400, 1693460460, 1693460520],
    \"values\": [12.0, 12.5, 13.0]
  }"
echo -e "\n"
pause

echo -e "${BLUE}Starting prediction tests...${NC}"

echo -e "${GREEN}Predicting with normal value for sensor_01${NC}"
curl -s -X POST ${BASE_URL}/predict/sensor_01 \
  -H "Content-Type: application/json" \
  -d '{"timestamp": 1693460000, "value": 10.5}'
echo -e "\n"
pause

echo -e "${GREEN}Predicting with anomalous value for sensor_01${NC}"
curl -s -X POST ${BASE_URL}/predict/sensor_01 \
  -H "Content-Type: application/json" \
  -d '{"timestamp": 1693460060, "value": 22.5}'
echo -e "\n"
pause

echo -e "${YELLOW}Predicting with invalid timestamp (string)...${NC}"
curl -s -X POST ${BASE_URL}/predict/sensor_01 \
  -H "Content-Type: application/json" \
  -d '{"timestamp": "now", "value": 10.5}'
echo -e "\n"
pause

echo -e "${YELLOW}Predicting using an untrained sensor (sensor_999)...${NC}"
curl -s -X POST ${BASE_URL}/predict/sensor_999 \
  -H "Content-Type: application/json" \
  -d '{"timestamp": 1693461000, "value": 10.5}'
echo -e "\n"
pause

echo -e "${BLUE}Fetching plot for sensor_01 version 2...${NC}"
curl -s -G "${BASE_URL}/plot" \
  --data-urlencode "series_id=sensor_01" \
  --data-urlencode "version=v2" \
  --output "${EXAMPLE_DIR}/sensor_01_v2.png"
echo -e "${GREEN}Plot saved to ${EXAMPLE_DIR}/sensor_01_v2.png${NC}"
pause

echo -e "${BLUE}Checking healthcheck endpoint...${NC}"
curl -s ${BASE_URL}/healthcheck
echo -e "\n"

echo -e "${GREEN}Test run completed.${NC}"