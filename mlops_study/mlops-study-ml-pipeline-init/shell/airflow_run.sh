#!/bin/bash

## Run airflow services.
base_name=`basename "${0}"`

function getAirflowProcessIDs {
  PROCESS_IDS=$(ps -ef | grep "${PROCESS_NANE}" | grep -v 'grep' | grep -v "${base_name}" | awk '{print $2}')
}

function runAirflowCommand() {
  # Check running status
  while [ $success = false ] && [ $attempt_num -le $max_attempts ]; do

    getAirflowProcessIDs
    if [ -z "$PROCESS_IDS" ]; then
      # Run the airflow
      if [ $attempt_num = 1 ]; then
        eval "${AIRFLOW_COMMAND}"
        echo "Run the ${PROCESS_NANE}."
      fi
      echo "The ${PROCESS_NANE} not found.(${attempt_num}/${max_attempts}) Trying again..."
      sleep 2
    else
      echo "The ${PROCESS_NANE} is running."
      success=true
    fi

    # Increment the attempt counter
    attempt_num=$(( attempt_num + 1 ))
  done
}

function startAirflowWebServer() {
  # Set a process name
  PROCESS_NANE="airflow webserver"

  # Set a success
  success=false

  # Set a counter for the number of attempts
  attempt_num=1

  # Set the maximum number of attempts
  max_attempts=10

  # Set a airflow command
  AIRFLOW_COMMAND="airflow webserver --port 8080 -D"

  runAirflowCommand

  if [ $success = false ]; then
    echo "The ${PROCESS_NANE} could not be started. The ${PROCESS_NANE} is forced to start."
    nohup airflow webserver --port 8080 >/dev/null 2>&1 &
  fi
}

function startAirflowScheduler() {
  # Set a process name
  PROCESS_NANE="airflow scheduler"

  # Set a success
  success=false

  # Set a counter for the number of attempts
  attempt_num=1

  # Set the maximum number of attempts
  max_attempts=10

  # Set a airflow command
  AIRFLOW_COMMAND="airflow scheduler -D"

  runAirflowCommand

  if [ $success = false ]; then
    echo "The ${PROCESS_NANE} could not be started. The ${PROCESS_NANE} is forced to start."
    nohup airflow scheduler >/dev/null 2>&1 &
  fi
}

function startAirflowTriggerer() {
  # Set a process name
  PROCESS_NANE="airflow triggerer"

  # Set a success
  success=false

  # Set a counter for the number of attempts
  attempt_num=1

  # Set the maximum number of attempts
  max_attempts=5

  # Set a airflow command
  AIRFLOW_COMMAND="airflow triggerer -D"

  runAirflowCommand

  if [ $success = false ]; then
    echo "The ${PROCESS_NANE} could not be started. The ${PROCESS_NANE} is forced to start."
    nohup airflow triggerer >/dev/null 2>&1 &
  fi
}

startAirflowWebServer
startAirflowScheduler
startAirflowTriggerer
