import time

def timer_decorator(func):
    def wrapper(*args, **kwargs):
        # 1. Capture the start time
        start_time = time.time()
        
        # 2. Execute the original function
        result = func(*args, **kwargs)  
        
        # 3. Capture the end time
        end_time = time.time()
        
        # 4. Print the calculation
        print(f"Execution time of {func.__name__}: {end_time - start_time:.4f} seconds")
        
        # 5. Return the original function's result
        return result
    return wrapper

@timer_decorator
def heavy_computation():
    time.sleep(1.5)  # Simulate a long process
    print("Computation complete.")

# Calling the decorated function
heavy_computation()

"""
Computation complete.
Execution time of heavy_computation: 1.5000 seconds
"""

-----------------------------------------

def my_decorator(func):
    def wrapper(*args, **kwargs):
        """I am the wrapper docstring."""
        return func(*args, **kwargs)
    return wrapper

@my_decorator
def say_hello():
    """I am the original docstring."""
    print("Hello!")

print(say_hello.__name__)  # wraper
print(say_hello.__doc__)   # I am the wrapper docstring.

--------------------------------------
# With @Wrap keyword. Note how ye __name__ and __docstring__ are stored
from functools import wraps

def my_decorator(func):
    @wraps(func)  # <--- This is the magic line
    def wrapper(*args, **kwargs):
        """I am the wrapper docstring."""
        return func(*args, **kwargs)
    return wrapper

@my_decorator
def say_hello():
    """I am the original docstring."""
    print("Hello!")

print(say_hello.__name__)   # say_hello
print(say_hello.__doc__)  # I am the original docstring

--------------------------------------------
# class The "Modifying" Approach (Adding functionality)

def add_timestamp(cls):
    # We add a new attribute directly to the class
    cls.created_at = "2026-01-03"
    
    # We add a new method
    def get_info(self):
        return f"Instance of {cls.__name__}, created on {self.created_at}"
    
    cls.get_info = get_info
    return cls

@add_timestamp
class Document:
    def __init__(self, title):
        self.title = title

doc = Document("Project Alpha")
print(doc.get_info())

---------------------------------

def add_branding(cls):
    # We add a class variable
    cls.company = "TechCorp"
    
    # We add a new method using a lambda
    # 'self' is required so it works as an instance method
    cls.get_id = lambda self: f"{self.company}-{self.name.upper()}"
    
    return cls  # Return the modified class

@add_branding
class Employee:
    def __init__(self, name):
        self.name = name

e = Employee("Alice")
print(e.company)    # Output: TechCorp
print(e.get_id())     # Output: TechCorp-ALICE

-------------------------------------------

from functools import wraps

def singleton(cls):
    """Ensures only one instance of a class ever exists."""
    instances = {}

    @wraps(cls)
    def wrapper(*args, **kwargs):
        if cls not in instances:
            # Create the object only if it doesn't exist yet
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    
    return wrapper

@singleton
class DatabaseConnection:
    def __init__(self):
        print("Connecting to Database...")

# Both variables will point to the exact same object
db1 = DatabaseConnection() # Prints: Connecting to Database...
db2 = DatabaseConnection() # Prints nothing!

print(db1 is db2) # Output: True

-------------------------
# How things come together in crew:
"""
YAML file called config.yaml
    
    researcher:
        role: "Senior Researcher"
        goal: "Find the latest AI trends"
"""

import yaml
from functools import wraps
from pydantic import BaseModel, ValidationError

# 1. Define the Schema (Pydantic Model)
class AgentConfig(BaseModel):
    role: str
    goal: str

# 2. The Decorator
def crew_style_linker(config_path):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # A. YAML LINKING: Load the file
            with open(config_path, 'r') as f:
                full_config = yaml.safe_load(f)
            
            # Use the function name as the key in the YAML (like CrewAI does)
            key = func.__name__
            config_data = full_config.get(key)

            # B. PYDANTIC ENFORCEMENT: Validate the data
            try:
                validated_config = AgentConfig(**config_data)
            except ValidationError as e:
                print(f"Validation failed for {key}: {e}")
                raise

            # C. Pass the validated data into the function
            return func(validated_config, *args, **kwargs)
        return wrapper
    return decorator

# 3. Usage
@crew_style_linker("config.yaml")
def researcher(config: AgentConfig):
    print(f"Agent Created! Role: {config.role}, Goal: {config.goal}")

researcher()