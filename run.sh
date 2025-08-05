#!/bin/bash

IS_LAUNCHED=$(docker ps -f name=vllm-server | wc -l)
if [ "$IS_LAUNCHED" == "1" ]
then
	docker run -itd --rm --name vllm-server --device /dev/dri -v /dev/dri/by-path:/dev/dri/by-path --network=host vllm-xpu-env --dtype float16 --enable-auto-tool-choice --tool-call-parser hermes
fi


VLLM_URL=127.0.0.1:8000/health
echo "Waiting for vLLM to become available..."
for i in {1..4}; do
    STATUS=$(curl -o /dev/null -s -w "%{http_code}\n" $VLLM_URL)
    echo "vLLM Status is $STATUS"
    if [ "$STATUS" == "200" ] 
    then
        echo "Is ready."
        break
    else
        sleep 15
    fi
    if [ $i -eq 4 ]; then
        echo "vLLM did not become ready in time. Please check the logs for errors."
        exit 1
    fi
done

source activate-conda.sh
activate_conda
conda activate vllm_env
python3 adk-weather-agent.py
