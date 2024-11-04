#!/bin/bash

set -eu

PORT=${PORT:-8500}
REST_API_PORT=${REST_API_PORT:-8501}
MODEL_NAME=${MODEL_NAME:-"mobilenet_v2"}
MODEL_BASE_PATH=${MODEL_BASE_PATH:-"/sync_async_pattern/saved_model/${MODEL_NAME}"}

tensorflow_model_server \
    --port=${PORT} \
    --rest_api_port=${REST_API_PORT} \
    --model_name=${MODEL_NAME} \
    --model_base_path=${MODEL_BASE_PATH} 