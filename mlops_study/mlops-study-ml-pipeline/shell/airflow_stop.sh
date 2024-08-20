#!/bin/bash

## Stop airflow processes.
base_name=`basename "${0}"`

# Airflow Home
AIRFLOW_HOME=~/airflow

# Set the maximum number of attempts
max_attempts=60

# Set a counter for the number of attempts
attempt_num=1

# Set a flag to indicate whether the command was successful
success=false

# Set a default kill option for the command of kill
kill_option=-15

function getAirflowProcessIDs {
  PROCESS_IDS=$(ps -ef | grep 'airflow' | grep -v 'grep' | grep -v "${base_name}" | awk '{print $2}')
}

function killAirflowProcesses {
  getAirflowProcessIDs
  if [ -z "$PROCESS_IDS" ]; then
    echo "There are no processes running."
  else
    for pid in $PROCESS_IDS; do
      kill ${kill_option} ${pid}
      echo "${pid} process has ended."
    done
  fi
  sleep 2
}

function clearAirflowFiles {
  # Delete *.pid in the directory of ~/airflow.
  PROCESS_ID_FILES=(`ls ${AIRFLOW_HOME} | grep ".pid"`)
  if [ ${#PROCESS_ID_FILES[@]} -gt 0 ]; then
    for file in $PROCESS_ID_FILES; do
      rm -f "${AIRFLOW_HOME}/${file}"
      echo "${file} file has deleted."
      sleep 1
    done
  fi
}

function airflowStop {
  while [ $success = false ] && [ $attempt_num -le $max_attempts ]; do
    # Kill Airflow Processes
    if [ $attempt_num -eq $max_attempts ]; then
      kill_option=-9
    fi
    killAirflowProcesses

    # Check Airflow Processes
    getAirflowProcessIDs
    if [ -z "$PROCESS_IDS" ]; then
      clearAirflowFiles
      success=true
    else
      # The command was not successful
      echo "Attempts to stop Airflow processes failed.(${attempt_num}/${max_attempts}) Trying again..."
    fi

    # Increment the attempt counter
    attempt_num=$(( attempt_num + 1 ))
  done
}

airflowStop
