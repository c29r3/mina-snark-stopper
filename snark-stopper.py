#!/usr/bin/python3
# Python 3.6+
import logging
import yaml
from time import sleep
from CodaClient import Client


def worker_manager(mode: str) -> str:
    if mode == "on":
        print("Start worker")
        data = coda.set_current_snark_worker(WORKER_PUB_KEY, WORKER_FEE)

    elif mode == "off":
        print("Turn off worker")
        data = coda.set_current_snark_worker(None, 99999999)
    return data


def parse_next_proposal_time():
    try:
        daemon_status = coda.get_daemon_status()
        next_propos = str(daemon_status["daemonStatus"]["nextProposal"]).split()[-1]

        # minutes
        if str(next_propos).endswith("m"):
            next_propos = float(next_propos.replace("m", ""))
            return next_propos

        # hours
        elif str(next_propos).endswith("h"):
            next_propos = float(next_propos.replace("h", "")) * 60
            return next_propos

        # seconds
        elif str(next_propos).endswith("s"):
            next_propos = float(next_propos.replace("s", "")) / 60
            return next_propos

        else:
            logger.error(f'Can\'t parse next proposal time {next_propos}')
            return "err"

    except Exception as parseProposalErr:
        logger.exception(parseProposalErr)
        return "err"


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
c = yaml.load(open('config.yml', encoding='utf8'), Loader=yaml.SafeLoader)

WORKER_PUB_KEY          = c["WORKER_PUB_KEY"]
WORKER_FEE              = c["WORKER_FEE"]
CHECK_PERIOD_SEC        = c["CHECK_PERIOD_SEC"]
STOP_WORKER_FOR_MIN     = c["STOP_WORKER_FOR_MIN"]
GRAPHQL_HOST            = c["GRAPHQL_HOST"]
GRAPHQL_PORT            = c["GRAPHQL_PORT"]

coda = Client(graphql_host=GRAPHQL_HOST, graphql_port=GRAPHQL_PORT)
daemon_status = coda.get_daemon_status()

if type(WORKER_PUB_KEY) is not str or len(WORKER_PUB_KEY) != 144:
    try:
        WORKER_PUB_KEY = daemon_status["daemonStatus"]["snarkWorker"]

    except Exception as workerAddrErr:
        logger.exception(f'Can\'t get worker public key. Is it running?')
        exit(1)

print(f'Current worker public key is: {WORKER_PUB_KEY}')

while True:
    try:
        next_proposal = round(parse_next_proposal_time(), 1)
        while next_proposal == "err":
            sleep(5)
            next_proposal = parse_next_proposal_time()

        print(f'Next proposal in {next_proposal} min.')
        if next_proposal < 3.0:
            worker_on = worker_manager(mode="off")
            logger.info(worker_on)

            print(f'Waiting {STOP_WORKER_FOR_MIN} minutes')
            sleep(60 * STOP_WORKER_FOR_MIN)

            worker_off = worker_manager(mode="on")
            logger.info(worker_off)
        sleep(CHECK_PERIOD_SEC)

    except (TypeError, Exception) as parseErr:
        logger.exception(f'Parse error: {parseErr}')
        sleep(5)
