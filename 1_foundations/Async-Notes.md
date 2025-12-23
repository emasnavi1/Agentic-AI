| Concept             | Code                                  | Meaning                                            |
| :------------------ | :------------------------------------ | :------------------------------------------------- |
| **Define**          | `async def my_func():`                | "This function can be paused."                     |
| **Pause**           | `await my_func()`                     | "Pause here, let others run, come back when done." |
| **Run**             | `asyncio.run(main())`                 | "Start the engine."                                |
| **Parallel**        | `asyncio.gather(task1(), task2())`    | "Run these at the same time and wait for all."     |
| **Wait w/ Timeout** | `asyncio.wait_for(task(), timeout=5)` | "Run this, but cancel if it takes too long."       |

# Simple example

```
mport asyncio
import time

async def say_hello():
    print("Hello...")
    # await passes control back to the loop for 1 second.
    # If other tasks were scheduled, they would run now.
    await asyncio.sleep(1)
    print("...World!")

if __name__ == "__main__":
    asyncio.run(say_hello())
```

# Parallel

```
import asyncio
import time

async def brew_coffee():
    print("Start brewing...")
    await asyncio.sleep(2)
    print("Coffee done!")
    return "Coffee"

async def toast_bread():
    print("Start toasting...")
    await asyncio.sleep(2)
    print("Toast done!")
    return "Toast"

async def main():
    start = time.perf_counter()

    print("Starting breakfast...")

    # Schedule both to run immediately on the event loop
    # gather returns a list of results in the order you passed them
    results = await asyncio.gather(brew_coffee(), toast_bread())

    # Total time: ~2 seconds (because they ran at the same time)
    print(f"Finished in {time.perf_counter() - start:.2f} seconds")
    print(f"Result: {results}")

if __name__ == "__main__":
    asyncio.run(main())

```

# If you absolutely must run blocking code (like using a library that doesn't support async), run it in a separate thread using to_thread.

```
import asyncio
import time

def blocking_io(name:str):
    # This is standard synchronous code
    print(f"Blocking start: {name}")
    time.sleep(2)
    print("Blocking end")

async def main():
    print("Async start")
    # Offload the blocking function to a separate thread
    await asyncio.to_thread(blocking_io, "ehsan")
    print("Async end")

asyncio.run(main())
```
