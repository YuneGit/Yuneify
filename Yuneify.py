import subprocess
import sys
import signal

# Function to handle termination signals
def terminate_processes(processes):
    for process in processes:
        process.terminate()
    sys.exit(0)

def main():
    # List to keep track of subprocesses
    processes = []

    try:
        # Launch the UI process
        ui_process = subprocess.Popen([sys.executable, 'Yuneify_UI.py'])
        processes.append(ui_process)

        # Launch the ContextWheel process
        context_wheel_process = subprocess.Popen([sys.executable, 'Yuneify_ContextWheel.py'])
        processes.append(context_wheel_process)

        # Wait for processes to complete
        for process in processes:
            process.wait()

    except KeyboardInterrupt:
        print("Terminating processes...")
        terminate_processes(processes)

    except Exception as e:
        print(f"An error occurred: {e}")
        terminate_processes(processes)

if __name__ == "__main__":
    # Register signal handlers for graceful termination
    signal.signal(signal.SIGINT, lambda sig, frame: terminate_processes([]))
    signal.signal(signal.SIGTERM, lambda sig, frame: terminate_processes([]))
    main()
