from langfuse import Langfuse
from langfuse.model import CreateScore
from langfuse.model import CreateScoreRequest


# Trace langchain run via the Langfuse CallbackHandler as shown above

# Get id of created trace
traceId = handler.get_trace_id()

# Add score, e.g. via the Python SDK
langfuse = Langfuse(ENV_PUBLIC_KEY, ENV_SECRET_KEY, ENV_HOST)
trace = langfuse.score(
    CreateScoreRequest(
        traceId=traceId,
        name="user-explicit-feedback",
        value=1,
        comment="I like how personalized the response is"
    )
)
