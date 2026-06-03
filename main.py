from alarm.scheduler import AlarmScheduler
from alarm.store import AlarmStore
from alarm.repl import AlarmRepl


def main() -> None:
    store     = AlarmStore()
    scheduler = AlarmScheduler(store)
    repl      = AlarmRepl(store)

    scheduler.start()
    try:
        repl.run()
    finally:
        scheduler.stop()
        print("\nGoodbye.")


if __name__ == "__main__":
    main()
