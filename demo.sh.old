#!/bin/bash

GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

function pause() {
  sleep 1
}

echo -e "${BLUE}Starting training tests...${NC}"

sensors=("sensor_01" "sensor_02" "sensor_03" "sensor_04" "sensor_05")
values=("10.0,10.5,11.0" "20.0,20.5,21.0" "30.0,30.5,31.0" "40.0,41.0,39.0" "50.0,49.5,50.5")

for idx in ${!sensors[@]}; do
  sensor=${sensors[$idx]}
  IFS=',' read -r v1 v2 v3 <<< "${values[$idx]}"
  
  echo -e "${GREEN}Training ${sensor}${NC}"
  curl -s -X POST http://localhost:8000/fit/${sensor} \
    -H "Content-Type: application/json" \
    -d "{\"data\": [
      {\"timestamp\": 1693459200, \"value\": ${v1}},
      {\"timestamp\": 1693459260, \"value\": ${v2}},
      {\"timestamp\": 1693459320, \"value\": ${v3}}
    ]}"
  echo -e "\n"
  pause
done

echo -e "${YELLOW}Sending invalid training request (constant data)...${NC}"
curl -s -X POST http://localhost:8000/fit/sensor_06 \
  -H "Content-Type: application/json" \
  -d '{"data": [{"timestamp": 1693459200, "value": 10.0},{"timestamp": 1693459260, "value": 10.0},{"timestamp": 1693459320, "value": 10.0}]}'
echo -e "\n"
pause

echo -e "${YELLOW}Sending invalid training request (empty data)...${NC}"
curl -s -X POST http://localhost:8000/fit/sensor_07 \
  -H "Content-Type: application/json" \
  -d '{"data": []}'
echo -e "\n"
pause

echo -e "${BLUE}Starting prediction tests...${NC}"

echo -e "${GREEN}Predicting with normal value for sensor_01${NC}"
curl -s -X POST http://localhost:8000/predict/sensor_01 \
  -H "Content-Type: application/json" \
  -d '{"timestamp": 1693460000, "value": 10.5}'
echo -e "\n"
pause

echo -e "${GREEN}Predicting with anomalous value for sensor_01${NC}"
curl -s -X POST http://localhost:8000/predict/sensor_01 \
  -H "Content-Type: application/json" \
  -d '{"timestamp": 1693460060, "value": 22.5}'
echo -e "\n"
pause

echo -e "${YELLOW}Predicting with invalid timestamp (string)...${NC}"
curl -s -X POST http://localhost:8000/predict/sensor_01 \
  -H "Content-Type: application/json" \
  -d '{"timestamp": "now", "value": 10.5}'
echo -e "\n"
pause

echo -e "${YELLOW}Predicting using an untrained sensor (sensor_999)...${NC}"
curl -s -X POST http://localhost:8000/predict/sensor_999 \
  -H "Content-Type: application/json" \
  -d '{"timestamp": 1693461000, "value": 10.5}'
echo -e "\n"
pause

echo -e "${BLUE}Checking healthcheck endpoint...${NC}"
curl -s http://localhost:8000/healthcheck
echo -e "\n"

echo -e "${GREEN}Test run completed.${NC}"
