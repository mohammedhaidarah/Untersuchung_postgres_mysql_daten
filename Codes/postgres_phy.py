import shutil
import subprocess
import time
import psutil
import os
from datetime import datetime


postgres_container_name = "postgres_uni"
log_file_path = os.path.join("./postgres_phy_log.txt")

def start_postgres_service(container_name='postgres_uni'):
    process = subprocess.run(["docker", "start", container_name])
    if process.returncode != 0:
        raise Exception('Failed to start PostgreSQL service')

def stop_postgres_service(container_name='postgres_uni'):
    process = subprocess.run(["docker", "stop", container_name])
    if process.returncode != 0:
        raise Exception('Failed to stop PostgreSQL service')

def copy_data_directory(backup_directory):
    process = subprocess.run(["docker", "cp", f"{postgres_container_name}:/var/lib/postgresql/data", backup_directory])
    if process.returncode != 0:
        raise Exception('Failed to copy data directory')

def restore_data_directory(backup_directory, container_name='postgres_uni'):
    stop_postgres_service(container_name)

    renamed_directory = os.path.join(os.path.dirname(backup_directory), "data")
    os.rename(backup_directory, renamed_directory)

    process = subprocess.run(["docker", "cp", f"{renamed_directory}", f"{container_name}:/var/lib/postgresql"])
    if process.returncode != 0:
        raise Exception('Failed to restore data directory')
    os.rename(renamed_directory, backup_directory)
    start_postgres_service(container_name)

def measure_performance(func):
    start_time = time.time()
    start_cpu_percent = psutil.cpu_percent()
    start_ram_percent = psutil.virtual_memory().percent
    func()
    end_cpu_percent = psutil.cpu_percent()
    end_ram_percent = psutil.virtual_memory().percent
    execution_time = time.time() - start_time
    average_cpu_percent = (start_cpu_percent + end_cpu_percent) / 2
    average_ram_percent = (start_ram_percent + end_ram_percent) / 2
    return execution_time, average_cpu_percent, average_ram_percent

def save_to_file(file_path, data):
    with open(file_path, "a") as file:
        file.write(data)
        file.write("\n")

def perform_backup(backup_directory):
    stop_postgres_service()

    if os.path.exists(backup_directory):
        shutil.rmtree(backup_directory)

    execution_time, average_cpu_percent, average_ram_percent = measure_performance(lambda: copy_data_directory(backup_directory))
    start_postgres_service()

    time_data = f"Backup Time: {execution_time:.2f} seconds"
    performance_cpu_percent = f"Average CPU Usage: {average_cpu_percent}% "
    performance_ram_percent = f"Average RAM Usage: {average_ram_percent}%"

    save_to_file(log_file_path, backup_directory + " :")
    save_to_file(log_file_path, time_data)
    save_to_file(log_file_path, performance_cpu_percent)
    save_to_file(log_file_path, performance_ram_percent)

def perform_recovery(container_name,backup_directory):
    subprocess.run(["docker", "exec", container_name, "sh", "-c", "rm -rf /var/lib/postgresql/data/*"])
    stop_postgres_service(container_name)
    execution_time, average_cpu_percent, average_ram_percent = measure_performance(lambda: restore_data_directory(backup_directory,container_name))
    start_postgres_service(container_name)

    time_data = f"Restore Time: {execution_time:.2f} seconds"
    performance_cpu_percent = f"Average CPU Usage: {average_cpu_percent}% "
    performance_ram_percent = f"Average RAM Usage: {average_ram_percent}%"
    
    save_to_file(log_file_path, "")
    save_to_file(log_file_path, "Restore " + backup_directory + " :")
    save_to_file(log_file_path, time_data)
    save_to_file(log_file_path, performance_cpu_percent)
    save_to_file(log_file_path, performance_ram_percent)
    save_to_file(log_file_path, "-" * 30)
    

def main():
    
    save_to_file(log_file_path, "PostgreSQL Physical Backup Log")
    save_to_file(log_file_path, "-" * 30)

    num_backups = int(input("Enter the number of backups to perform: "))


    save_to_file(log_file_path, "-" * 30)
    for i in range(num_backups):
        backup_directory = f"backup_{i+1}"
        perform_backup(backup_directory)
        input(f"Simulate the error situation and press Enter to continue...")
        perform_recovery('postgres_uni_backup',backup_directory)
        input("Check the database and press Enter to continue...")

if __name__ == "__main__":
    main()
