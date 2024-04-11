EMBEDDING_URL="127.0.0.1:15820"
LLM_URL="127.0.0.1:15810"
MAX_RETRIES=100
RETRY_INTERVAL=5

retries=0

printf "[+] Starting backend embedding service.\n"

screen -S emb-serv -d -m bash -c 'sudo bash ./embedding-service.sh'

printf "[.] Checking if backend embedding service is up.\n"
while [ $retries -lt $MAX_RETRIES ]; do
    response=$(curl -s -o /dev/null -w "%{http_code}" $EMBEDDING_URL/embed -X POST -d '{"inputs":"Rose are red violets are blue"}' -H 'Content-Type: application/json')
    if [ $response -eq 200 ]; then
        printf "[+] Embedding service is up.\n"
        break
    else
        printf "[.] Embedding service unreachable, retrying in $RETRY_INTERVAL seconds.\n"
        sleep $RETRY_INTERVAL
        retries=$((retries+1))
    fi
done

if [ $retries -ge $MAX_RETRIES ]; then
    echo "[x] Max retries reached. Embedding service failed to start."
    exit 1
fi


retries=0

printf "[+] Starting backend LLM service.\n"

screen -S tgi-serv -d -m bash -c 'sudo bash ./text-generation-service.sh'

printf "[.] Checking if backend LLM service is up.\n"
while [ $retries -lt $MAX_RETRIES ]; do
    response=$(curl -s -o /dev/null -w "%{http_code}" $EMBEDDING_URL/embed -X POST -d '{"inputs":"Rose are red violets are blue"}' -H 'Content-Type: application/json')
    if [ $response -eq 200 ]; then
        printf "[+] LLM service is up.\n"
        break
    else
        printf "[.] LLM service unreachable, retrying in $RETRY_INTERVAL seconds.\n"
        sleep $RETRY_INTERVAL
        retries=$((retries+1))
    fi
done

if [ $retries -ge $MAX_RETRIES ]; then
    echo "[x] Max retries reached. LLM service failed to start."
    exit 1
fi

printf "[+] All services are green!\n"