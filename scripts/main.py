from base import BASE_PATH
import logging
import os
import pandas as pd
from testapp import build_app
from helper_functions import data_handler

if __name__ == "__main__":
    dh = data_handler()
    app = build_app(dh)
    app.run_server(debug=False)

