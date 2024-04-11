EMBEDDING_URL="127.0.0.1:15820"
LLM_URL="127.0.0.1:15810"
MAX_RETRIES=100
RETRY_INTERVAL=5

## Starting embedding service.

retries=0 # Reset retry counter.

printf "[+] Starting backend embedding service.\n"

# Start the embedding service in a detached screen session.
screen -S emb-serv -d -m bash -c 'sudo bash ./embedding-service.sh'

printf "[.] Checking if backend embedding service is up.\n"

# Check if the embedding service is up by sending a request to the /embed endpoint.
while [ $retries -lt $MAX_RETRIES ]; do # Loop until the max retries is reached.
    response=$(curl -s -o /dev/null -w "%{http_code}" $EMBEDDING_URL/embed -X POST -d '{"inputs":"Rose are red violets are blue"}' -H 'Content-Type: application/json')
    if [ $response -eq 200 ]; then
        printf "[+] Embedding service is up.\n"
        break # Exit the loop if the service is up.
    else
        printf "[.] Embedding service unreachable, retrying in $RETRY_INTERVAL seconds.\n"
        sleep $RETRY_INTERVAL  # Wait for a few momnents before retrying.
        retries=$((retries+1)) # Increment the retry counter.
    fi
done

# If the max retries is reached, exit the script.
if [ $retries -ge $MAX_RETRIES ]; then
    echo "[x] Max retries reached. Embedding service failed to start."
    exit 1
fi

## Starting LLM service.

retries=0 # Reset retry counter.

printf "[+] Starting backend LLM service.\n"

# Start the LLM service in a detached screen session.
screen -S tgi-serv -d -m bash -c 'sudo bash ./text-generation-service.sh'

printf "[.] Checking if backend LLM service is up.\n"

# Check if the LLM service is up.
while [ $retries -lt $MAX_RETRIES ]; do
    response=$(curl -s -o /dev/null -w "%{http_code}" $LLM_URL/generate -X POST -d '{"inputs":"Why is the sky blue?","parameters":{"max_new_tokens":20}}' -H 'Content-Type: application/json')
    if [ $response -eq 200 ]; then
        printf "[+] LLM service is up.\n"
        break
    else
        printf "[.] LLM service unreachable, retrying in $RETRY_INTERVAL seconds.\n"
        sleep $RETRY_INTERVAL  # Wait for a few momnents before retrying.
        retries=$((retries+1)) # Increment the retry counter.
    fi
done

# If the max retries is reached, exit the script.
if [ $retries -ge $MAX_RETRIES ]; then
    echo "[x] Max retries reached. LLM service failed to start."
    exit 1
fi

printf "[+] All services are green!\n"