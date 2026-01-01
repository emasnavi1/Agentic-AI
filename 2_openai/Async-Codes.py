def count_to_three():
    yield 1
    yield 2
    yield 3

for number in count_to_three():
    print(number)
    
    
    
    ---------------------
    
    

async def fetch_users_async(user_ids):
    for user_id in user_ids:
        # Pause here for the network request
        user_data = await db.get_user(user_id) 
        # Pause here to give the data to the caller
        yield user_data 

# Used like this:
async for user in fetch_users_async([1, 2, 3]):
    print(user.name)
    
    
    
    -------
    
    def greeter():
    while True:
        name = yield  # Execution pauses here and WAITS for a value
        print(f"Hello, {name}!")

g = greeter()
next(g)           # Advance to the first yield
g.send("Alice")   # "Alice" is sent into the function and assigned to 'name'
g.send("Bob")


-----

import asyncio

# This represents our "Pager"
class MyManualFuture:
    def __init__(self):
        self.result = None
        self.done = False

    # This is what the 'await' keyword looks for
    def __await__(self):
        while not self.done:
            # This yields control back to the Event Loop
            yield self 
        return self.result

async def my_async_function(pager):
    print("Step 1: Sending request... (waiting for pager to vibrate)")
    
    # Execution PAUSES here because the __await__ loop yields
    result = await pager 
    
    print(f"Step 3: Pager vibrated! Result: {result}")

async def main():
    pager = MyManualFuture()
    
    # Create the task but don't await it yet so we can trigger the "doorbell"
    task = asyncio.create_task(my_async_function(pager))
    
    # Let the loop run Step 1
    await asyncio.sleep(1) 
    
    print("Step 2: (Meanwhile) The OS/Hardware received the data!")
    pager.result = "Packet Received"
    pager.done = True # The "Doorbell"
    
    await task

asyncio.run(main())
