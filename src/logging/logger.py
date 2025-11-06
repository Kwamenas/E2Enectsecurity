import logging
import os
from datetime import datetime

###how should the logfile look like
timestamp=datetime.now().strftime('%d_%m_%Y_%H_%M_%S')

##this create cwd/logs/time_stamp
log_dir=os.path.join(os.getcwd(),'logs',timestamp)
os.makedirs(log_dir,exist_ok=True)

#this will creaste timestamp.log
#then will put timestamp.log into the cwd/logs/time_stamp
log_file=f"{timestamp}.log"
LOG_FILE_PATH=os.path.join(log_dir,log_file)


logging.basicConfig(
    filename=LOG_FILE_PATH,
    format="[ %(asctime)s ] %(lineno)d %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# 🧪 Test the logger
#logging.info("Logger initialized successfully.")
#logging.warning("This is a sample warning.")
#print(f"✅ Log file created at: {LOG_FILE_PATH}")