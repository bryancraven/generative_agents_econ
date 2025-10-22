"""
Author: Modernized for GPT-5-nano (2025)
File: prompt_schemas.py
Description: Pydantic schemas for structured outputs from all GPT prompt functions.
             Replaces brittle string parsing with type-safe JSON Schema validation.

This file defines response schemas for all 31 prompt functions in run_gpt_prompt.py,
organized by cognitive module.
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Union, Literal
from datetime import datetime


# ============================================================================
# PLANNING MODULE SCHEMAS
# ============================================================================

class WakeUpHourResponse(BaseModel):
    """Response for wake up hour determination"""
    wake_up_hour: int = Field(
        ...,
        ge=0,
        le=23,
        description="Hour when the person wakes up (0-23)"
    )


class DailyPlanActivity(BaseModel):
    """A single activity in the daily plan"""
    activity: str = Field(..., description="Description of the activity")
    time: str = Field(..., description="Time of the activity (e.g., '8:00 am', '12:00 pm')")


class DailyPlanResponse(BaseModel):
    """Response for daily planning"""
    activities: List[DailyPlanActivity] = Field(
        ...,
        description="List of activities planned for the day in broad strokes"
    )


class HourlyScheduleActivity(BaseModel):
    """A single activity in hourly schedule"""
    activity: str = Field(..., description="What the person is doing")
    start_time: str = Field(..., description="Start time (e.g., '08:00')")
    end_time: str = Field(..., description="End time (e.g., '09:00')")
    duration_minutes: int = Field(..., ge=1, description="Duration in minutes")


class HourlyScheduleResponse(BaseModel):
    """Response for hourly schedule generation"""
    activities: List[HourlyScheduleActivity] = Field(
        ...,
        description="Activities for the specified hour"
    )


class Subtask(BaseModel):
    """A single subtask in task decomposition"""
    description: str = Field(..., description="What the person is doing")
    duration_minutes: int = Field(
        ...,
        ge=1,
        le=180,
        description="Duration in minutes (typically in 5-minute increments)"
    )


class TaskDecomposition(BaseModel):
    """Response for task decomposition into subtasks"""
    subtasks: List[Subtask] = Field(
        ...,
        description="List of subtasks broken down into small time increments"
    )

    @field_validator('subtasks')
    @classmethod
    def validate_subtasks(cls, v):
        if len(v) == 0:
            raise ValueError("Must have at least one subtask")
        return v


class NewDecompScheduleItem(BaseModel):
    """Item in new decomposed schedule"""
    task: str = Field(..., description="Task description")
    duration: int = Field(..., ge=1, description="Duration in minutes")


class NewDecompScheduleResponse(BaseModel):
    """Response for new decomposed schedule"""
    schedule: List[NewDecompScheduleItem] = Field(
        ...,
        description="New schedule with decomposed tasks"
    )


# ============================================================================
# PERCEPTION MODULE SCHEMAS
# ============================================================================

class ActionLocation(BaseModel):
    """Location components for an action"""
    sector: str = Field(..., description="The sector/area (e.g., 'house', 'park')")
    arena: str = Field(..., description="The arena within sector (e.g., 'bedroom', 'kitchen')")
    game_object: str = Field(..., description="The specific object (e.g., 'bed', 'stove')")


class Pronunciatio(BaseModel):
    """Pronunciation/expression of an action"""
    emoji: str = Field(..., description="Emoji representing the action")
    description: str = Field(..., description="Description of how to pronounce/express the action")


class EventTriple(BaseModel):
    """Subject-predicate-object triple for an event"""
    subject: str = Field(..., description="Who is performing the action")
    predicate: str = Field(..., description="The action being performed")
    object: str = Field(..., description="What/who the action is being performed on")


class ActionObjectDescription(BaseModel):
    """Description of action with object"""
    description: str = Field(..., description="Natural language description of the action")


# ============================================================================
# RETRIEVAL & MEMORY MODULE SCHEMAS
# ============================================================================

class KeywordExtractionResponse(BaseModel):
    """Keywords extracted from description"""
    keywords: List[str] = Field(
        ...,
        description="List of relevant keywords",
        min_length=1,
        max_length=10
    )


class ThoughtResponse(BaseModel):
    """Thought generated from keyword or conversation"""
    thought: str = Field(..., description="The generated thought")


class FocalPoint(BaseModel):
    """A focal point from statements"""
    topic: str = Field(..., description="The focal point topic")
    description: str = Field(..., description="Brief description of the focal point")


class FocalPointsResponse(BaseModel):
    """Response for focal points extraction"""
    focal_points: List[FocalPoint] = Field(
        ...,
        min_length=1,
        description="List of focal points extracted from statements"
    )


class Insight(BaseModel):
    """An insight with supporting evidence"""
    insight: str = Field(..., description="The high-level insight")
    evidence: List[str] = Field(..., description="Supporting evidence from statements")


class InsightsResponse(BaseModel):
    """Response for insights and evidence"""
    insights: List[Insight] = Field(
        ...,
        min_length=1,
        description="List of insights with supporting evidence"
    )


# ============================================================================
# REFLECTION MODULE SCHEMAS
# ============================================================================

class PoignancyRating(BaseModel):
    """Poignancy rating for event, thought, or conversation"""
    rating: int = Field(
        ...,
        ge=1,
        le=10,
        description="Poignancy rating from 1 (mundane) to 10 (extremely significant)"
    )
    reasoning: Optional[str] = Field(
        None,
        description="Brief explanation for the rating"
    )


# ============================================================================
# CONVERSATION MODULE SCHEMAS
# ============================================================================

class DecisionResponse(BaseModel):
    """Decision to talk or react"""
    decision: Literal["yes", "no"] = Field(
        ...,
        description="Whether to initiate conversation or react"
    )
    reasoning: Optional[str] = Field(
        None,
        description="Brief reasoning for the decision"
    )


class ConversationUtterance(BaseModel):
    """A single utterance in a conversation"""
    speaker: str = Field(..., description="Name of the speaker")
    utterance: str = Field(..., description="What was said")


class ConversationResponse(BaseModel):
    """Generated conversation between personas"""
    conversation: List[ConversationUtterance] = Field(
        ...,
        min_length=1,
        description="List of utterances in the conversation"
    )


class ConversationSummary(BaseModel):
    """Summary of a conversation"""
    summary: str = Field(..., description="Brief summary of the conversation")
    key_points: Optional[List[str]] = Field(
        None,
        description="Key points from the conversation"
    )


class RelationshipSummary(BaseModel):
    """Summary of relationship between two personas"""
    summary: str = Field(..., description="How the relationship has evolved")
    sentiment: Optional[Literal["positive", "neutral", "negative"]] = Field(
        None,
        description="Overall sentiment of the relationship"
    )


class NextConversationLine(BaseModel):
    """Next line in an ongoing conversation"""
    utterance: str = Field(..., description="What to say next")


class InnerThought(BaseModel):
    """Inner thought about what was heard"""
    thought: str = Field(..., description="Inner thought or reflection")


class PlanningThought(BaseModel):
    """Planning thought about conversation"""
    thought: str = Field(..., description="Thought about conversation planning")


class ConversationMemo(BaseModel):
    """Memory/memo about conversation"""
    memo: str = Field(..., description="What to remember from this conversation")


# ============================================================================
# EXECUTION MODULE SCHEMAS
# ============================================================================

class ActionDescription(BaseModel):
    """Description of action being performed"""
    action: str = Field(..., description="Description of the action")


class SectorResponse(BaseModel):
    """Response for action sector determination"""
    sector: str = Field(..., description="The sector where action occurs")


class ArenaResponse(BaseModel):
    """Response for action arena determination"""
    arena: str = Field(..., description="The arena where action occurs")


class GameObjectResponse(BaseModel):
    """Response for game object determination"""
    game_object: str = Field(..., description="The game object involved in action")


# ============================================================================
# AGENT CHAT SCHEMAS (Complex multi-turn conversation)
# ============================================================================

class AgentChatSummaryIdeas(BaseModel):
    """Summary of ideas discussed in agent chat"""
    summary: str = Field(..., description="Summary of ideas discussed")
    topics: List[str] = Field(..., description="Main topics covered")


class AgentChatResponse(BaseModel):
    """Full response for agent chat"""
    dialogue: List[ConversationUtterance] = Field(
        ...,
        description="The generated dialogue"
    )


# ============================================================================
# UTILITY SCHEMAS
# ============================================================================

class SummarizeIdeasResponse(BaseModel):
    """Summary of ideas from statements"""
    summary: str = Field(..., description="Summary of the ideas")


# ============================================================================
# SCHEMA REGISTRY (for easy lookup)
# ============================================================================

SCHEMA_REGISTRY = {
    # Planning
    "wake_up_hour": WakeUpHourResponse,
    "daily_plan": DailyPlanResponse,
    "hourly_schedule": HourlyScheduleResponse,
    "task_decomp": TaskDecomposition,
    "new_decomp_schedule": NewDecompScheduleResponse,

    # Perception
    "action_location": ActionLocation,
    "pronunciatio": Pronunciatio,
    "event_triple": EventTriple,
    "act_obj_desc": ActionObjectDescription,

    # Retrieval
    "extract_keywords": KeywordExtractionResponse,
    "keyword_to_thoughts": ThoughtResponse,
    "convo_to_thoughts": ThoughtResponse,

    # Reflection
    "poignancy": PoignancyRating,
    "focal_pt": FocalPointsResponse,
    "insight_and_guidance": InsightsResponse,

    # Conversation
    "decide_to_talk": DecisionResponse,
    "decide_to_react": DecisionResponse,
    "create_conversation": ConversationResponse,
    "summarize_conversation": ConversationSummary,
    "agent_chat_summarize_ideas": AgentChatSummaryIdeas,
    "agent_chat_summarize_relationship": RelationshipSummary,
    "agent_chat": AgentChatResponse,
    "generate_next_convo_line": NextConversationLine,
    "whisper_inner_thought": InnerThought,
    "planning_thought_on_convo": PlanningThought,
    "memo_on_convo": ConversationMemo,

    # Execution
    "action_sector": SectorResponse,
    "action_arena": ArenaResponse,
    "action_game_object": GameObjectResponse,

    # Utility
    "summarize_ideas": SummarizeIdeasResponse,
}


def get_schema(function_name: str) -> type[BaseModel]:
    """
    Get the Pydantic schema for a given prompt function.

    Args:
        function_name: Name of the prompt function (e.g., 'task_decomp')

    Returns:
        Pydantic BaseModel class for the schema

    Raises:
        KeyError: If function_name not found in registry
    """
    return SCHEMA_REGISTRY[function_name]


def get_json_schema(function_name: str) -> dict:
    """
    Get the JSON Schema dict for a given prompt function.

    Args:
        function_name: Name of the prompt function

    Returns:
        JSON Schema dict compatible with OpenAI Responses API
    """
    schema_class = get_schema(function_name)
    schema = schema_class.model_json_schema()

    # OpenAI Responses API requires additionalProperties: false at ALL levels
    schema = _add_additional_properties_false(schema)
    return schema


def _add_additional_properties_false(schema: dict) -> dict:
    """
    Recursively add 'additionalProperties': false to all object types in schema.
    Required for OpenAI Responses API structured output compliance.

    Args:
        schema: JSON Schema dict

    Returns:
        Modified schema with additionalProperties: false
    """
    if isinstance(schema, dict):
        # If this is an object type, add additionalProperties: false
        if schema.get("type") == "object":
            schema["additionalProperties"] = False

        # Recursively process all nested schemas
        for key, value in schema.items():
            if isinstance(value, dict):
                schema[key] = _add_additional_properties_false(value)
            elif isinstance(value, list):
                schema[key] = [_add_additional_properties_false(item) if isinstance(item, dict) else item
                               for item in value]

    return schema


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Example: Get schema for task decomposition
    schema = get_json_schema("task_decomp")
    print("Task Decomposition Schema:")
    import json
    print(json.dumps(schema, indent=2))

    # Example: Validate a response
    sample_response = {
        "subtasks": [
            {"description": "wake up", "duration_minutes": 5},
            {"description": "shower", "duration_minutes": 10},
            {"description": "breakfast", "duration_minutes": 15}
        ]
    }

    decomp = TaskDecomposition(**sample_response)
    print("\nValidated response:")
    print(decomp.model_dump_json(indent=2))
