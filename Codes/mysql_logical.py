import shutil
import subprocess
import os
import psutil
from datetime import datetime

mysql_container_name = "mysql_uni"
root_user = "root"
root_password = "test"
log_file_path = os.path.join("./mysql_logical_log.txt")

def start_mysql_service(container_name='mysql_uni'):
    process = subprocess.run(["docker", "start", container_name])
    if process.returncode != 0:
        raise Exception('Failed to start MySQL service')

def stop_mysql_service(container_name='mysql_uni'):
    process = subprocess.run(["docker", "stop", container_name])
    if process.returncode != 0:
        raise Exception('Failed to stop MySQL service')

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


def perform_logical_backup(backup_directory, root_user, root_password):
    if os.path.exists(backup_directory):
        shutil.rmtree(backup_directory)

    os.makedirs(backup_directory, exist_ok=True)


    backup_file = os.path.join(backup_directory, "backup.sql")
    command = f"docker exec {mysql_container_name} mysqldump --all-databases -u {root_user} -p{root_password} > {backup_file}"


    try:
        subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        print(f"Logical backup created successfully: {backup_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred during logical backup: {e.output}")


def perform_logical_restore(container_name,backup_directory, root_user, root_password):

    backup_file = os.path.join(backup_directory, "backup.sql")
    command = f"docker exec -i {container_name} mysql -u {root_user} -p{root_password} < {backup_file}"
    try:
        subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        print("Database restored successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred during logical restore: {e.output}")


def main():
    
    log_data = [
        "MySQL Logical Backup Log",
        "-" * 30
    ]

    num_backups = int(input("Enter the number of backups to perform: "))



    log_data.append("-" * 30)

    for i in range(num_backups):
        backup_directory = f"backup_{i+1}"

        execution_time, average_cpu_percent, average_ram_percent = measure_performance(
            lambda: perform_logical_backup(backup_directory, root_user, root_password)
        )

        log_data.append(f"Backup {i+1}:")
        log_data.append(f"Backup Time: {execution_time.total_seconds():.2f} seconds")
        log_data.append(f"Average CPU Usage: {average_cpu_percent:.2f}%")
        log_data.append(f"Average RAM Usage: {average_ram_percent:.2f}%")
        
        

        execution_time, average_cpu_percent, average_ram_percent = measure_performance(
            lambda: perform_logical_restore('mysql_uni_backup',backup_directory, root_user, root_password))
        
        log_data.append("")
        log_data.append(f"Restore {i+1}:")
        log_data.append(f"Restore Time: {execution_time.total_seconds():.2f} seconds")
        log_data.append(f"Average CPU Usage: {average_cpu_percent:.2f}%")
        log_data.append(f"Average RAM Usage: {average_ram_percent:.2f}%")
        log_data.append("-" * 30)

        input("Check the database and press Enter to continue...")

    with open(log_file_path, "w") as log_file:
        log_file.write("\n".join(log_data))


if __name__ == "__main__":
    main()
