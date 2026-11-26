"""Structured output demo: turn a free-text support message into a typed ticket.

The Pydantic model below is passed to the agent as `output_schema`. ADK sends
it to the model as a response schema, so the reply is always JSON that matches
it, and ADK validates the reply against the model. With `output_key` set, the
validated result is also saved to session state under that key, where other
agents or code can read it.
"""

from typing import Literal

from google.adk.agents.llm_agent import Agent
from pydantic import BaseModel, Field


class ActionItem(BaseModel):
    """One concrete thing the support team should do."""

    task: str = Field(description="What needs to be done, as a short imperative sentence.")
    owner: Literal["support", "billing", "engineering"] = Field(
        description="Which team should do it."
    )


class SupportTicket(BaseModel):
    """A support ticket extracted from a customer's message."""

    customer_name: str | None = Field(
        description="The customer's name if they gave it, otherwise null."
    )
    category: Literal["billing", "bug", "feature_request", "account", "other"] = Field(
        description="The main topic of the message."
    )
    priority: Literal["low", "medium", "high", "urgent"] = Field(
        description=(
            "urgent: service down or money lost now; high: blocks the customer; "
            "medium: workaround exists; low: question or suggestion."
        )
    )
    sentiment: Literal["positive", "neutral", "negative"] = Field(
        description="The customer's overall tone."
    )
    summary: str = Field(description="One sentence describing the problem.")
    action_items: list[ActionItem] = Field(
        description="Next steps for the support team, most important first."
    )


root_agent = Agent(
    model='gemini-3.5-flash',
    name='structured_output_agent',
    description="Turns a customer support message into a structured ticket.",
    instruction=(
        "You are a support triage assistant. The user pastes a message from a "
        "customer. Read it and fill in every field of the ticket. Only use facts "
        "stated in the message; do not invent names, order numbers or details."
    ),
    output_schema=SupportTicket,
    output_key="ticket",
)
