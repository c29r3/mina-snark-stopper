import logging
import yaml
import time
import sys
import datetime
from CodaClient import Client


def write_to_log(log_str: str, print_mode: str = "info"):
    now = datetime.datetime.now()
    if print_mode == "warning":
        logger.warning(log_str)
    else:
        logger.info(log_str)
    
    with open("snark_stopper.log", "a") as log_f:
        log_f.write(f'{now.strftime("%Y-%m-%d %H:%M:%S")} | {log_str}\n')


def worker_manager(mode: str):
    data = None
    if mode == "on":
        # Reread WORKER_FEE every time
        c = yaml.load(open('config.yml', encoding='utf8'), Loader=yaml.SafeLoader)
        WORKER_FEE        = float(c["WORKER_FEE"])
        WORKER_FEE        = int(WORKER_FEE * 1e9)
        daemon_status     = coda.get_daemon_status()
        status_worker_pub = daemon_status["daemonStatus"]["snarkWorker"]
        status_worker_fee = daemon_status["daemonStatus"]["snarkWorkFee"]

        if status_worker_pub is None or int(status_worker_fee) != WORKER_FEE:
            write_to_log(f'Start worker: FEE {WORKER_FEE / 1e9} MINA')
            worker_address = coda.get_daemon_status()["daemonStatus"]["snarkWorker"]
            write_to_log(f'Worker status check. worker_pub_key = {worker_address}')
            data = coda.set_current_snark_worker(WORKER_PUB_KEY, WORKER_FEE)

    elif mode == "off":
        write_to_log("Turn off worker")
        data = coda.set_current_snark_worker(None, 0)
        worker_address = coda.get_daemon_status()["daemonStatus"]["snarkWorker"]
        write_to_log(f'Worker status check. worker_pub_key = {worker_address}')
    return data


def parse_next_proposal_time():
    try:
        daemon_status  = coda.get_daemon_status()
        sync_status    = daemon_status["daemonStatus"]["syncStatus"]
        current_height = daemon_status["daemonStatus"]["blockchainLength"] or 1
        max_height     = daemon_status["daemonStatus"]["highestBlockLengthReceived"] or 1

        if sync_status.lower() != "synced" or int(current_height) < int(max_height)-3:
            logger.fatal(f'😿 Node is not synced yet. STATUS: {sync_status} | Height: {current_height}\\{max_height}')

        if "startTime" not in str(daemon_status["daemonStatus"]["nextBlockProduction"]):
            worker_manager(mode="on")
            next_propos = "🙀 No proposal in this epoch"
        else:
            next_propos = int(daemon_status["daemonStatus"]["nextBlockProduction"]["times"][0]["startTime"]) / 1000
        return next_propos

    except Exception as parseProposalErr:
        write_to_log(f'😱 parse_next_proposal_time Exception: {parseProposalErr}', print_mode="warning")
        return f'parse_next_proposal_time() Exception: {parseProposalErr}'


def parse_worker_pubkey():
    daemon_status        = coda.get_daemon_status()
    status_worker_pub    = daemon_status["daemonStatus"]["snarkWorker"]

    if len(WORKER_PUB_KEY) == 55:
        return WORKER_PUB_KEY
    
    elif status_worker_pub is not None and len(status_worker_pub) == 55:
        return status_worker_pub

    elif status_worker_pub is None:
        logger.info(f'Worker public key is None')
        
        BLOCK_PROD_KEY = daemon_status["daemonStatus"]["blockProductionKeys"][0]
        return BLOCK_PROD_KEY

    else:
        write_to_log('😡 Enter the worker public key in config.yml', print_mode="warning")
        exit(1)
    

# Configure Logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='|%(asctime)s| %(message)s')
logger = logging.getLogger(__name__)
c = yaml.load(open('config.yml', encoding='utf8'), Loader=yaml.SafeLoader)
print("version 1.2.5")

WORKER_PUB_KEY          = str(c["WORKER_PUB_KEY"])
WORKER_FEE              = float(c["WORKER_FEE"])
CHECK_PERIOD_SEC        = int(c["CHECK_PERIOD_SEC"])
STOP_WORKER_FOR_MIN     = int(c["STOP_WORKER_FOR_MIN"])
STOP_WORKER_BEFORE_MIN  = int(c["STOP_WORKER_BEFORE_MIN"])
GRAPHQL_HOST            = str(c["GRAPHQL_HOST"])
GRAPHQL_PORT            = int(c["GRAPHQL_PORT"])
# MINA --> nanomina
WORKER_FEE              = int(WORKER_FEE * 1e9)

try:
    coda = Client(graphql_host=GRAPHQL_HOST, graphql_port=GRAPHQL_PORT)
    WORKER_PUB_KEY = parse_worker_pubkey()
    write_to_log("Snark-stopper launched")

except:
    write_to_log(f'😿 Can\'t connect to graphql {GRAPHQL_HOST}:{GRAPHQL_PORT}. '
                 f'Check troubleshooting manual - https://github.com/c29r3/mina-snark-stopper#troubleshooting', print_mode="warning")
    exit(1)

print(f'Worker public key:  {WORKER_PUB_KEY}\n'
      f'Worker fee:         {WORKER_FEE}\n'
      f'Check period(sec):  {CHECK_PERIOD_SEC}\n'
      f'Stop before(min):   {STOP_WORKER_BEFORE_MIN}\n'
      f'https://github.com/c29r3/mina-snark-stopper\n'
      f'http://staketab.com/\n')

while True:
    try:
        next_proposal = parse_next_proposal_time()
        while type(next_proposal) is str:
            write_to_log(next_proposal)
            time.sleep(CHECK_PERIOD_SEC)
            next_proposal = parse_next_proposal_time()

        time_to_wait = str(datetime.timedelta(seconds=int(next_proposal - time.time())))
        write_to_log(f'🕐 Next proposal via {time_to_wait}')
        if next_proposal-time.time() <= STOP_WORKER_BEFORE_MIN*60:
            worker_manager(mode="off")
            logger.info(f'⏰ Waiting {STOP_WORKER_FOR_MIN} minutes')
            time.sleep(60 * STOP_WORKER_FOR_MIN)
            worker_manager(mode="on")

        else:
            worker_manager(mode="on")

        time.sleep(CHECK_PERIOD_SEC)

    except (TypeError, Exception) as parseErr:
        write_to_log(f'🤷‍♂️ Parse error: {parseErr}', print_mode="warning")
        time.sleep(10)
