import logging

from core import launch

logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)


def run(): 
    logging.info("Launching Bot...") 
    launch() 


if __name__ == "__main__": 
    run() 