#!/bin/bash

exec python init_db.py &
exec python app.py