#!/usr/bin/env bash

set -e

gunicorn config.wsgi -b 0.0.0.0:8000