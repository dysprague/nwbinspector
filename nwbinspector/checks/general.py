"""Check functions that examine any general neurodata_type with the available attrbutes."""
from ..register_checks import register_check, InspectorMessage, Importance

COMMON_DESCRIPTION_PLACEHOLDERS = ["no description", "no desc", "none"]


@register_check(importance=Importance.CRITICAL, neurodata_type=None)
def check_name_slashes(obj):
    """Check if there  has been added for the session."""
    if hasattr(obj, "name") and any((x in obj.name for x in ["/", "\\"])):
        return InspectorMessage(message="Object name contains slashes, .")


@register_check(importance=Importance.BEST_PRACTICE_SUGGESTION, neurodata_type=None)
def check_description(obj):
    """Check if the description is a not missing or a placeholder."""
    common_description_placeholders = ["no description", "no desc", "none"]
    if not hasattr(obj, "description"):
        return
    if obj.description is None or obj.description.strip(" ") == "":
        return InspectorMessage(message="Description is missing.")
    if obj.description.lower().strip(".") in common_description_placeholders:
        return InspectorMessage(message=f"Description ({obj.description}) is a placeholder.")
