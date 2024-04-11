streamlit run webui.py --browser.gatherUsageStats False \
                       --server.address "0.0.0.0" \
                       --server.port "443" \
                       --server.sslCertFile .cert/webapp-selfsigned.crt \
                       --server.sslKeyFile .cert/webapp-selfsigned.key