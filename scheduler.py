import psutil
import subprocess
import time

# List of process names that trigger the main script
# Caution: Must be the full name, i.e., chrome.exe not just chrome
processes_that_trigger_script = ["chrome.exe", "msedge.exe"]

# Path to the script that should be executed
script_path = "C:\\Users\\PC\\OneDrive\\Documents\\Python stuff\\LogU\\test.py"

# Time delay between checking if the process(s) that trigger the script are running
wait_time = 2

# Executes the specified script
def run_script(running_processes: dict, script_path: str):
    return subprocess.Popen(['python', script_path])

# Terminates the script instance
def terminate_script(script_instance: subprocess.Popen):
    script_instance.terminate()

# Monitors processes and triggers the script
def monitor_processes(trigger_processes: list[str], script_path: str):
    trigger_processes = [process.lower() for process in trigger_processes]
    script_is_running = False
    running_processes = {} # The name of the currently running process(s) that triggered the script
    accessed_keys = {}
    process_is_running = False
    found_terminated_process = False
    script_instance = None

    while True:
        process_is_running = False
        accessed_keys = {}
        terminated_processes = []

        # Iterate over all running processes
        for process in psutil.process_iter():
            process = process.name().lower()
            
            # Check if the process matches the trigger processes
            if process in trigger_processes:
                # If the script is already running but the process wasn't included in it's execution context, update the running_processes and restart the script
                if len(running_processes) > 0 and process not in running_processes:
                    terminate_script(script_instance)
                    running_processes[process] = True
                    script_instance = run_script(running_processes, script_path)
                
                # If the script is not running, set script_is_running to True, start the script, and update running_processes
                if not script_is_running:
                    script_is_running = True
                    process_is_running = True
                    running_processes[process] = True
                    script_instance = run_script(running_processes, script_path)

            # If the script is running and the process is in running_processes, mark it as accessed
            if script_is_running and process in running_processes:
                process_is_running = True
                accessed_keys[process] = True

        # If no trigger processes are running and the script is running, stop the script
        if not process_is_running and script_is_running:
            script_is_running = False
            running_processes = {}
            accessed_keys = {}
            terminate_script(script_instance)

        # Check for terminated processes in running_processes
        for key in running_processes:
            if key not in accessed_keys:
                found_terminated_process = True
                terminated_processes.append(key)

        # Remove the terminated processes from running_processes
        for key in terminated_processes:
            del running_processes[key]

        if found_terminated_process:
            found_terminated_process = False

            # Terminate the script if a terminated process was found
            terminate_script(script_instance)

            # If there are still running processes, restart the script
            if len(running_processes) > 0:
                run_script(running_processes, script_path)

        time.sleep(wait_time)

# Call the monitor_processes function with the provided trigger processes and script path
monitor_processes(processes_that_trigger_script, script_path)
