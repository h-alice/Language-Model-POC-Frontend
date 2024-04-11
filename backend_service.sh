screen -S emb-serv -d -m bash -c 'sudo bash ./embedding-service.sh'
screen -S tgi-serv -d -m bash -c 'sudo bash ./text-generation-service.sh'
