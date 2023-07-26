import shutil
import subprocess
import os
import psutil
from datetime import datetime

postgres_container_name = "postgres_uni"
root_user = "test"
root_password = "test"
log_file_path = os.path.join("./postgres_logical_log.txt")

def start_postgres_service(container_name='postgres_uni'):
    process = subprocess.run(["docker", "start", container_name])
    if process.returncode != 0:
        raise Exception('Failed to start PostgreSQL service')

def stop_postgres_service(container_name='postgres_uni'):
    process = subprocess.run(["docker", "stop", container_name])
    if process.returncode != 0:
        raise Exception('Failed to stop PostgreSQL service')

def measure_performance(func):
    start_time = datetime.now()
    start_cpu_percent = psutil.cpu_percent()
    start_ram_percent = psutil.virtual_memory().percent
    func()
    end_cpu_percent = psutil.cpu_percent()
    end_ram_percent = psutil.virtual_memory().percent
    execution_time = datetime.now() - start_time
    average_cpu_percent = (start_cpu_percent + end_cpu_percent) / 2
    average_ram_percent = (start_ram_percent + end_ram_percent) / 2
    return execution_time, average_cpu_percent, average_ram_percent


def perform_logical_backup(backup_directory, root_user):
    if os.path.exists(backup_directory):
        shutil.rmtree(backup_directory)

    os.makedirs(backup_directory, exist_ok=True)

    backup_file = os.path.join(backup_directory, "backup.sql")
    command = f"docker exec {postgres_container_name} pg_dumpall -U {root_user} > {backup_file}"

    try:
        subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        print(f"Logical backup created successfully: {backup_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred during logical backup: {e.output}")


def perform_logical_restore(container_name, backup_directory, root_user):
    backup_file = os.path.join(backup_directory, "backup.sql")
    command = f"docker exec -i {container_name} psql -U {root_user} < {backup_file}"

    try:
        subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        print("Database restored successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred during logical restore: {e.output}")




def main():
    
    log_data = [
        "PostgreSQL Logical Backup Log",
        "-" * 30
    ]

    num_backups = int(input("Enter the number of backups to perform: "))



    log_data.append("-" * 30)

    for i in range(num_backups):
        backup_directory = f"backup_{i+1}"

        execution_time, average_cpu_percent, average_ram_percent = measure_performance(
            lambda: perform_logical_backup(backup_directory, root_user)
        )

        log_data.append(f"Backup {i+1}:")
        log_data.append(f"Backup Time: {execution_time.total_seconds():.2f} seconds")
        log_data.append(f"Average CPU Usage: {average_cpu_percent:.2f}%")
        log_data.append(f"Average RAM Usage: {average_ram_percent:.2f}%")
        

        input(f"Simulate the  error situation and press Enter to continue...")

        
        execution_time, average_cpu_percent, average_ram_percent = measure_performance(
                lambda: perform_logical_restore('postgres_uni_backup', backup_directory, root_user)
            )

        log_data.append("")
        log_data.append(f"Restore {i+1}: ")
        log_data.append(f"Restore Time: {execution_time.total_seconds():.2f} seconds")
        log_data.append(f"Average CPU Usage: {average_cpu_percent:.2f}%")
        log_data.append(f"Average RAM Usage: {average_ram_percent:.2f}%")
        log_data.append("-" * 30)

        input("Check the database and press Enter to continue...")

    with open(log_file_path, "w") as log_file:
        log_file.write("\n".join(log_data))


if __name__ == "__main__":
    main()
