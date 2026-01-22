#!/bin/bash

set -a

if [ -f /opt/elasticbeanstalk/deployment/env ]; then
    source /opt/elasticbeanstalk/deployment/env
fi

set +a

