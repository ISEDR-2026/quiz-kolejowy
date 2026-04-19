#!/bin/sh
cd /volume1/home/Demokris/quiz_app
/usr/local/AppCentral/python3/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true
