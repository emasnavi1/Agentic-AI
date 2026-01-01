from redmail import gmail
from agents import Agent, function_tool

INSTRUCTIONS = """You are able to send an emial."""

@function_tool
def send_html_email(subject: str, message_body: str):
    """ Send out an HTML email with an embedded image to all sales prospects """

    html_template = f"""
    <div style="font-family: Jost, sans-serif; padding: 20px;">
        <h2>{subject}</h2>
        <p>{message_body}</p>
        <br>
        <hr>
        <img src="{{{{ my_logo.src }}}}" style="width: 150px;">
    </div>
    """

    gmail.username = "emasnavi1@gmail.com"
    gmail.password = os.environ.get('GMAIL_APP_PASSWORD')
    gmail.send(
        subject=subject,
        receivers=["ehsan.masnavi@gmail.com"],
        # 1. Define the HTML with the special syntax
        html=html_template,
        # 2. Tell Redmail where the file is
        body_images={
            "my_logo": "./me/emasnavi.png" 
        }
    )
    return {"status": "success"}

email_agent = Agent(
    name="Emailer agent",
    instructions=INSTRUCTIONS,
    tools=[send_html_email],
    model="gpt-4o-mini"
)
