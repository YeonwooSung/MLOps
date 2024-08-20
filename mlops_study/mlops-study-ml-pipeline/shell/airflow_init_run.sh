## Run airflow services.
base_name=`basename "${0}"`

# airflow home directory
export AIRFLOW_HOME=~/airflow

# Set the maximum number of attempts
max_attempts=10

function getAirflowProcessIDs() {
  PROCESS_IDS=(`ps -ef | grep "${PROCESS_NANE}" | grep -v 'grep' | grep -v "${base_name}" | awk '{print $2}'`)
}

function getWebserverWorkerProcessIDs() {
  PROCESS_IDS=(`ps -ef | grep "airflow-webserver" | grep "worker" | grep -v 'grep' | grep -v "${base_name}" | awk '{print $2}'`)
}

function checkAirflowProcess() {
  # Check running status
  while [ $success = false ] && [ $attempt_num -le $max_attempts ]; do
    if [ $PROCESS_NANE = "airflow webserver" ]; then
      getWebserverWorkerProcessIDs
    else
      getAirflowProcessIDs
    fi
    if [ ${#PROCESS_IDS[@]} -gt 0 ]; then
      echo "The ${PROCESS_NANE} is running."
      success=true
    else
      echo "The ${PROCESS_NANE} not found.(${attempt_num}/${max_attempts}) Trying again..."
      sleep 2
    fi

    # Increment the attempt counter
    attempt_num=$(( attempt_num + 1 ))
  done
}

function createUsers() {
  airflow users create \
    --username mlops \
    --firstname mlops \
    --lastname study \
    --role Admin \
    --email mlops.study@gmail.com \
    --password study
}

function createVariables() {
  cd ~
  HOME_DIR=(`pwd`)
  airflow variables set AIRFLOW_DAGS_PATH \
    ${HOME_DIR}/Study/mlops-study-ml-pipeline
  cd -
}

function createConnections() {
  airflow connections add 'feature_store' \
    --conn-json '{
        "conn_type": "mysql",
        "login": "root",
        "password": "root",
        "host": "0.0.0.0",
        "port": 3306,
        "schema": "mlops"
    }'
}

function runAirflowComponents() {
  # airflow db clear
  rm -f ${AIRFLOW_HOME}/airflow.db

  # airflow standalone
  nohup airflow standalone >/dev/null 2>&1 &

  # 5 second delay
  sleep 5

  # create Airflow Values
  createUsers
  createVariables
  createConnections
}

function isRunningAirflowComponents() {
    PROCESS_NANE="airflow"
    getAirflowProcessIDs
    if [ ${#PROCESS_IDS[@]} -gt 0 ]; then
      echo "The ${PROCESS_NANE} is running."
      exit 0
    fi
}

function isRunningOfScheduler() {
  # Set a process name
  PROCESS_NANE="airflow scheduler"

  # Set a success
  success=false

  # Set a counter for the number of attempts
  attempt_num=1

  checkAirflowProcess

  if [ $success = false ]; then
    echo "The ${PROCESS_NANE} could not be started."
  fi
}

function isRunningOfTriggerer() {
  # Set a process name
  PROCESS_NANE="airflow triggerer"

  # Set a success
  success=false

  # Set a counter for the number of attempts
  attempt_num=1

  checkAirflowProcess

  if [ $success = false ]; then
    echo "The ${PROCESS_NANE} could not be started."
  fi
}

function isRunningOfWebServer() {
  # Set a process name
  PROCESS_NANE="airflow webserver"

  # Set a success
  success=false

  # Set a counter for the number of attempts
  attempt_num=1

  checkAirflowProcess

  if [ $success = false ]; then
    echo "The ${PROCESS_NANE} could not be started."
  fi
}

isRunningAirflowComponents
runAirflowComponents
isRunningOfTriggerer
isRunningOfScheduler
isRunningOfWebServer
