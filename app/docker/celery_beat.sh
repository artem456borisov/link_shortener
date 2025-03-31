#!/bin/bash
# pwd
celery -app=tasks.tasks:celery beat --loglevel=info