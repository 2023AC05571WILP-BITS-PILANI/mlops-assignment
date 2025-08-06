#!/bin/bash

# File to store PIDs
PID_FILE="service_pids.txt"

start_services() {
    echo "Starting services..."
    COMMAND="/Users/sanjaykumarc/anaconda/anaconda3/bin/python /Users/sanjaykumarc/mlops-assignment/mlops-assignment/main.py"
    $COMMAND

    # Start each script in the background and save its PID
    ./docker_run.sh &
    echo $! > "$PID_FILE"

    ./start_ml_flow_ui.sh &
    echo $! >> "$PID_FILE"

    ./start_monitoring.sh &
    echo $! >> "$PID_FILE"

    ./trigger_training_on_data_change.sh &
    echo $! >> "$PID_FILE"

    echo "All services started and PIDs saved to $PID_FILE."
}

stop_services() {
    echo "Stopping services..."

    if [ ! -f "$PID_FILE" ]; then
        echo "No PID file found. Are the services running?"
        exit 1
    fi

    while read -r pid; do
        if kill "$pid" > /dev/null 2>&1; then
            echo "Stopped process $pid"
        else
            echo "Failed to stop process $pid or it may not be running."
        fi
    done < "$PID_FILE"

    rm -f "$PID_FILE"
    echo "All services stopped and PID file removed."
}

# Main logic
case "$1" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    *)
        echo "Usage: $0 {start|stop}"
        exit 1
        ;;
esac
