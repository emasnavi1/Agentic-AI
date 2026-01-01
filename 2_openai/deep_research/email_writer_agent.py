from pydantic import BaseModel, Field
from agents import Agent

email_writer_instructions = """ 
You are able to come up with a good engaging subject, and body of an email based on a detailed report you receive.
Include the entire report in the email. The body of the email will be inserted into a <body> segment of an html temlpate. so 
ensure the body of the email is html compatible.
"""

class EmailContent(BaseModel):
    subject: str= Field(description="A proper subject for the email to be sent based on a detail report received.")
    message_body: str  = Field(description="A proper body for the email to be sent based on a detail report received. include the entire detailed report.")
    
email_writer_agent = Agent(name="Email Writer", instructions=email_writer_instructions, model="gpt-4o-mini", output_type=EmailContent)