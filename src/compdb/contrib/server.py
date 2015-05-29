import logging
logger = logging.getLogger(__name__)

DESCR_SERVER = "Start a compDB job queue execution server."

def start_with_args(args):
    return start(
        timeout = args.timeout,
        reload = not args.no_reload,
        combine = args.combine,
        logtodb = not args.no_logging)

def start(timeout = 300, reload = False, combine = False, logtodb = True):
    from compdb.contrib import get_project
    from compdb.core.mongodb_queue import Empty

    project = get_project()
    if logtodb:
        project.start_logging()

    # Catch SIGTERM logic
    import signal, sys
    def signal_term_handler(signal, frame):
        project.job_queue.stop_event.set()
        sys.exit(0)
    signal.signal(signal.SIGTERM, signal_term_handler)
    try:
        msg = "Entering execution loop for project '{}', timeout={}s."
        print(msg.format(project, timeout))
        if combine:
            project.job_queue.enter_loop_mpi(
                timeout = timeout,
                reload = reload)
        else:
            project.job_queue.enter_loop(
                timeout = timeout,
                reload = reload)
    except Empty:
        print("Queue empty, timed out.")
    except (KeyboardInterrupt, SystemExit):
        print("Interrupted, exiting.")
    else:
        print("Exiting.")

def setup_parser(parser):
    parser.add_argument(
        '-t', '--timeout',
        type = int,
        default = 300,
        help = "Seconds to wait for new jobs in execution loop.")
    parser.add_argument(
        '--no-reload',
        action = 'store_true',
        help = "Do not reload modules before execution.")
    parser.add_argument(
        '-c', '--combine',
        action = 'store_true',
        help = "Do not fork the queue execution into multiple processes.")
    parser.add_argument(
        '--no-logging',
        action = 'store_true',
        help = "Do not log to project database.")
    parser.set_defaults(func = start_with_args)

def main(arguments = None):
    from argparse import ArgumentParser
    parser = ArgumentParser(description = DESCR_SERVER)
    setup_parser(parser)
    args = parser.parse_args(arguments)
    return start_with_args(args)

if __name__ == '__main__':
    logging.basicConfig(level = logging.INFO)
    main()