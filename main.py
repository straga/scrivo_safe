import asyncio
import machine
import os
import gc
import esp32

import safe
sf = safe.Safe()

storage_dir = "."  # Storage patch

#gc.threshold(1 * 1024)  # Garbage Collector, need test, may not need or some other value or disable
STACK_SIZE = 15 * 1024  # Stack size for ESP32
TREAD = False  # Run in tread if TRUE


def check_memory():
    heaps = esp32.idf_heap_info(0)
    main_heap = heaps[5]  # Main region

    # Check memory status
    if main_heap[2] < 1024:
        print(f"\nCRITICAL! Main heap fragmented! Largest block: {main_heap[2]} bytes")
        import machine
        machine.reset()


async def run_wdt():
    print("WDT: INIT")
    wdt = machine.WDT(timeout=30000)

    print("WDT: WIFI TOUCH")
    asyncio.create_task(wifi_touch())

    print("WDT: WAIT SAFE")
    for i in range(int(sf.wait)):
        await asyncio.sleep(1)
        print(f" Wait SAFE: {i}\r", end="")

    print("WDT: ADD LOADED TASK")
    asyncio.create_task(loader())

    print("WDT: RUN")
    while True:
        wdt.feed()
        gc.collect()
        check_memory()
        await asyncio.sleep(10)


async def wifi_touch():
    while True:
        await sf.touch()
        await asyncio.sleep(5)


# VFS SIZE
def vfs():
    fs_stat = os.statvfs("/")
    fs_size = fs_stat[0] * fs_stat[2]
    fs_free = fs_stat[0] * fs_stat[3]
    print("File System Size {:,} - Free Space {:,}".format(fs_size, fs_free))



# Loader
async def loader():

    print(" ")
    print(" ")

    # Partition name
    part_name = os.getcwd()
    print(f"Part Name: {part_name}")

    # Core
    try:
        from core import Core
        _core = Core(name=part_name)
        asyncio.create_task(_core.run())

    except Exception as e:
        print(f"ERROR: Core Run - {e}")

    print("Ram free: ", gc.mem_free())

def main():
    # VFS info print
    vfs()

    # Create AsyncIO Tasks
    print("Create Event Tasks")
    asyncio.create_task(run_wdt())

    # Run in thread.
    if TREAD:
        import _thread
        print("Start Event Loop in thread: NonBlock Repl")
        loop = asyncio.get_event_loop()
        _ = _thread.stack_size(STACK_SIZE)
        _thread.start_new_thread(loop.run_forever, ())

    # Run without thread.
    else:
        try:
            print("Start Event Loop: Block Repl")
            loop = asyncio.get_event_loop()
            loop.run_forever()
        except KeyboardInterrupt:
            print("\nCtrl+C pressed - stopping asyncio")
            loop = asyncio.get_event_loop()
            loop.stop()
        except Exception as e:
            print(f"Error in main: {e}")
            #machine.reset()

        print("Starting uFTPd...")
        import uftpd
        # Set watchdog for 2 minutes
        machine.WDT(timeout=120000)

    print("Main: Done")


if __name__ == "__main__":
    print("__main__")
    main()
