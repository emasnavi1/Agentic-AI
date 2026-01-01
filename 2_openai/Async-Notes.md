| Concept             | Code                                  | Meaning                                                                                                                                |
| :------------------ | :------------------------------------ | :------------------------------------------------------------------------------------------------------------------------------------- |
| **Define**          | `async def my_func():`                | "This function can be paused. Using `aysc def` made it a co-routine"                                                                   |
| **Pause**           | `await my_func()`                     | "Execute the co-routine. Pause where it yields, let others run, come back when done."                                                  |
| **Run**             | `asyncio.run(main())`                 | "Start the engine. in Jupyter notebook you can do `await my_fun()`, but in none-jupyter envs, the `asyncio.run()` starter is required" |
| **Parallel**        | `asyncio.gather(task1(), task2())`    | "Run these at the same time and wait for all."                                                                                         |
| **Wait w/ Timeout** | `asyncio.wait_for(task(), timeout=5)` | "Run this, but cancel if it takes too long."                                                                                           |

# Simple example

```
import asyncio
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

# And example of an awaitable object:

```
import asyncio

# 1. A pure Python class (No asyncio inside!)
class ThreeStepPause:
    def __await__(self):
        # Step 1
        print("Step 1: I am pausing...")
        yield  # Passes control back to the Loop (Ping!)

        # Step 2 (Loop calls next() to resume us)
        print("Step 2: I am back! Pausing again...")
        yield  # Passes control back to the Loop (Ping!)

        # Step 3
        print("Step 3: Finishing up!")
        return "Done"

# 2. We use asyncio only to RUN it (The "Loop")
async def main():
    print("Main: Starting")

    # Python sees __await__, so it allows this:
    result = await ThreeStepPause()

    print(f"Main: Received result '{result}'")

asyncio.run(main())
```

# Exmaple of a an Async Genertor and better underestand what Await does inside a functions

```
import asyncio

# --- ACTOR 1: The Background Worker ---
# This simulates a UI loading spinner, a database heartbeat, or another user request.
async def background_worker():
    while True:
        print("  [Background] ⏳ While you wait, I am doing other work...")
        await asyncio.sleep(1) # ticks every 1 second

# --- ACTOR 2: The Slow AI (Your Streamer) ---
# Note hos using the term `yield` is turning this method to an Async Generator
# Async Generator (async def + yield): Yields Data to You (the programmer).
# Custom Awaitable (def __await__ + yield): Yields Control to the Event Loop (the manager).
# This is an example of Async Generator which can be un-wrapped using `async for``
async def fake_ai_streamer(sentence):
    words = sentence.split()

    for word in words:
        # THE PROOF IS HERE:
        # We pause for 3 seconds.
        # Because we use 'await asyncio.sleep', the Event Loop
        # immediately switches to 'background_worker' during this time.
        await asyncio.sleep(3)

        yield "\n" + word + "\n"

# --- THE STAGE (Main) ---
async def main():
    print("--- STARTING DEMO ---")



    # 1. Start the Background Worker
    # create_task schedules it to run on the loop immediately
    # this goes to scheduler right away
    task = asyncio.create_task(background_worker())

    # this will make the main to pause here for 20 seconds. while allowing the prevously scheduled task (background_worker)
    # to run, the line after this line will not be executed until this 20 second sleep is satisfied.
    await asyncio.sleep(20)

    print("🤖 AI is typing: ", end="", flush=True)

    # 2. Run the Streamer
    # The loop will toggle between this streamer and the background task
    async for chunk in fake_ai_streamer("Agentic AI is the future of humanity"):
        print(chunk, end="", flush=True)

    # 3. Cleanup
    print("\n✅ Done!")
    task.cancel() # Stop the background worker

# Run it
await main()
```

# Another example in which I show how time.sleep(3) is used to represent a long running process

```
import asyncio
import time

# A standard, blocking function
def distinct_blocking_read():
    # Imagine this is: with open('big_file.txt') as f: return f.read()
    time.sleep(3)
    return "File Contents"

async def background_worker():
    while True:
        print("  [Background] ⏳ I am alive!")
        await asyncio.sleep(1)

async def main():
    task = asyncio.create_task(background_worker())

    print("Starting threaded read...")

    # MAGIC FIX: Run the blocking function in a thread
    # The Event Loop stays free to run the background worker!
    data = await asyncio.to_thread(distinct_blocking_read)

    print(f"Finished reading: {data}")
    task.cancel()

# Result: The background worker keeps printing the whole time!
await main()
```

# Good examplation for `asyncio.create_task(coro)

```
In Python's asyncio library, asyncio.create_task(coro) is the function used to schedule a coroutine to run concurrently on the event loop.

Think of it like starting a job in the background. If you simply await a coroutine, your code stops and waits for that one job to finish before moving to the next line. With create_task, you submit the job to the "to-do list" of the event loop and immediately move to the next line of code.
```
