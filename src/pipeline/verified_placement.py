"""Multi-agent verified placement pipeline inspired by GenEscape (Shan et al.).

Implements a Generator → Reviewer → Examiner loop:
  1. Generator  – calls insert_item_into_scene to produce a composite image.
  2. Reviewer   – vision model inspects the composite and describes what it sees
                  at the intended location.
  3. Examiner   – compares the review against the placement intent and decides
                  PASS or FAIL with corrective feedback.
  4. On FAIL the feedback is folded into the prompt and we loop back to (1).

The loop runs until the Examiner passes or max_attempts is reached.
"""

from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass, field

from PIL import Image
from google import genai

from ..config import Config

# Re-use the existing item insertion function
import sys
_project_root = str(Path(__file__).parent.parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)
from tempImpl.insertItem import insert_item_into_scene
from tempImpl.removeItem import remove_item_from_scene


@dataclass
class PlacementAttempt:
    """Record of a single generate-verify cycle."""
    attempt: int
    image_path: str
    review: str
    passed: bool
    feedback: str


@dataclass
class VerifiedPlacementResult:
    """Full result returned by the verified placement pipeline."""
    final_image_path: str
    passed: bool
    attempts: List[PlacementAttempt] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Agent prompts
# ---------------------------------------------------------------------------

REVIEWER_PROMPT = """You are an expert interior design reviewer.

You are given:
1. The ORIGINAL room photograph (first image).
2. A COMPOSITE image where a new piece of furniture was supposedly placed into the room (second image).
3. The ITEM image that was meant to be inserted (third image).

INTENDED PLACEMENT: {placement_description}
{additional_instructions_block}
Your task — examine the COMPOSITE image and answer these questions:
- Is a new item clearly visible at or near the intended location?
- Does the item in the composite resemble the provided item image?
- Does the placement look spatially natural (correct perspective, scale, lighting, grounding on the floor/surface)?
- If additional instructions were given above, are they reflected in the result (e.g. orientation, style, finish)?
- Are there any obvious artefacts, distortions, or unrealistic elements?

Respond with a short, factual assessment (3-5 sentences). Do NOT say whether it passes or fails — just describe what you observe."""


EXAMINER_PROMPT = """You are a strict visual quality examiner for an interior design placement system.

You are given four things:
1. The ORIGINAL room photograph (first image).
2. The COMPOSITE image that was generated (second image).
3. The ITEM image that should have been inserted (third image).
4. A reviewer's text observations (below).

INTENDED PLACEMENT: {placement_description}
{additional_instructions_block}
REVIEWER'S OBSERVATIONS (use as a secondary reference, but trust your own eyes first):
{review}

YOUR TASK — look at the composite image yourself and verify:
1. PRESENCE: Is the item from image 3 clearly visible in the composite (image 2)? Does it resemble the original item?
2. LOCATION: Is it placed at the intended location as described above? Compare against the original room (image 1) to judge position.
3. REALISM: Does it look spatially natural — correct scale, perspective, lighting, grounded on a surface?
4. INSTRUCTIONS: If additional instructions were provided above, are they satisfied (e.g. correct orientation, style, material)?

Decision criteria:
- PASS: The item is recognisably present, at roughly the right location, looks plausible, and satisfies any additional instructions. Ensure lighting quality is good.
- FAIL: The item is missing, unrecognisable, placed in the wrong part of the frame, severely distorted, or clearly violates the additional instructions.

Respond in EXACTLY this format (two lines only):
VERDICT: PASS
FEEDBACK: <one-sentence summary of what you see>

or

VERDICT: FAIL
FEEDBACK: <specific, actionable correction describing what went wrong and how to fix it, phrased as an instruction for the image generator>"""


def _call_gemini_text(
    contents: list,
    model: str = "gemini-2.0-flash",
) -> str:
    """Helper: call Gemini and return the text response."""
    Config.validate_api_key("google")
    client = genai.Client(api_key=Config.GOOGLE_API_KEY)
    response = client.models.generate_content(model=model, contents=contents)
    if not response.text:
        raise ValueError("Gemini returned no text.")
    return response.text.strip()


def _format_instructions_block(additional_instructions: str) -> str:
    """Build the additional-instructions block for prompts (empty string if none)."""
    if additional_instructions.strip():
        return f"ADDITIONAL INSTRUCTIONS: {additional_instructions.strip()}\n"
    return ""


def _review(
    original_room_path: str,
    composite_path: str,
    item_path: str,
    placement_description: str,
    additional_instructions: str = "",
) -> str:
    """Reviewer agent: describe what it sees in the composite."""
    prompt = REVIEWER_PROMPT.format(
        placement_description=placement_description,
        additional_instructions_block=_format_instructions_block(additional_instructions),
    )
    room_img = Image.open(original_room_path)
    composite_img = Image.open(composite_path)
    item_img = Image.open(item_path)
    return _call_gemini_text([prompt, room_img, composite_img, item_img])


def _examine(
    original_room_path: str,
    composite_path: str,
    item_path: str,
    placement_description: str,
    review: str,
    additional_instructions: str = "",
) -> tuple[bool, str]:
    """Examiner agent: visually verify the composite and decide PASS/FAIL."""
    prompt = EXAMINER_PROMPT.format(
        placement_description=placement_description,
        additional_instructions_block=_format_instructions_block(additional_instructions),
        review=review,
    )
    room_img = Image.open(original_room_path)
    composite_img = Image.open(composite_path)
    item_img = Image.open(item_path)
    raw = _call_gemini_text([prompt, room_img, composite_img, item_img])

    # Parse verdict
    passed = "VERDICT: PASS" in raw.upper()
    feedback = ""
    for line in raw.splitlines():
        if line.upper().startswith("FEEDBACK:"):
            feedback = line.split(":", 1)[1].strip()
            break

    return passed, feedback


def generate_with_verification(
    room_image_path: str,
    item_image_path: str,
    placement_description: str,
    additional_instructions: str = "",
    max_attempts: int = 3,
    on_attempt: Optional[callable] = None,
) -> VerifiedPlacementResult:
    """Run the full generate → review → examine loop.

    Args:
        room_image_path: Path to the original room photo.
        item_image_path: Path to the furniture item image.
        placement_description: Natural-language description of where to place
            the item (as produced by describe_red_dot_location).
        additional_instructions: Extra style/orientation hints from the user.
        max_attempts: Maximum generation cycles before giving up.
        on_attempt: Optional callback ``fn(PlacementAttempt)`` called after
            each cycle so the UI can show progress.

    Returns:
        VerifiedPlacementResult with the final image path, pass/fail status,
        and the full history of attempts.
    """
    attempts: list[PlacementAttempt] = []
    accumulated_feedback: list[str] = []

    for i in range(1, max_attempts + 1):
        # ----- BUILD PROMPT -----
        prompt_parts = [placement_description]
        if additional_instructions.strip():
            prompt_parts.append(additional_instructions.strip())
        if accumulated_feedback:
            prompt_parts.append(
                "IMPORTANT corrections from previous attempts: "
                + " ".join(accumulated_feedback)
            )
        full_prompt = ". ".join(prompt_parts)

        # ----- GENERATE (unique path per attempt) -----
        room_stem = Path(room_image_path).stem
        item_stem = Path(item_image_path).stem
        attempt_output = str(
            Config.OUTPUT_DIR / f"{room_stem}_with_{item_stem}_attempt{i}.jpg"
        )
        result_path = insert_item_into_scene(
            room_image_path=room_image_path,
            item_image_path=item_image_path,
            prompt=full_prompt,
            output_path=attempt_output,
        )

        # ----- REVIEW -----
        review = _review(
            original_room_path=room_image_path,
            composite_path=str(result_path),
            item_path=item_image_path,
            placement_description=placement_description,
            additional_instructions=additional_instructions,
        )

        # ----- EXAMINE -----
        passed, feedback = _examine(
            original_room_path=room_image_path,
            composite_path=str(result_path),
            item_path=item_image_path,
            placement_description=placement_description,
            review=review,
            additional_instructions=additional_instructions,
        )

        attempt = PlacementAttempt(
            attempt=i,
            image_path=str(result_path),
            review=review,
            passed=passed,
            feedback=feedback,
        )
        attempts.append(attempt)

        if on_attempt:
            on_attempt(attempt)

        if passed:
            return VerifiedPlacementResult(
                final_image_path=str(result_path),
                passed=True,
                attempts=attempts,
            )

        # Accumulate feedback for next iteration
        accumulated_feedback.append(feedback)

    # Exhausted retries — return best (last) attempt
    return VerifiedPlacementResult(
        final_image_path=str(result_path),
        passed=False,
        attempts=attempts,
    )


# ===================================================================
# REMOVAL verification
# ===================================================================

REMOVAL_REVIEWER_PROMPT = """You are an expert interior design reviewer.

You are given:
1. The ORIGINAL room photograph — before any edits (first image).
2. The EDITED image where an item was supposedly removed (second image).

ITEM LOCATION (what should have been removed): {location_description}
{additional_instructions_block}
Your task — compare the two images and answer these questions:
- Is the item that was at the described location now gone in the edited image?
- Does the area where the item was look natural (matching floor, wall, texture, lighting)?
- Is the rest of the room preserved exactly as before (no unintended changes, no new objects)?
- Are there any obvious artefacts, smudges, or unrealistic patches where the item was?

Respond with a short, factual assessment (3-5 sentences). Do NOT say whether it passes or fails — just describe what you observe."""


REMOVAL_EXAMINER_PROMPT = """You are a strict visual quality examiner for an interior design item-removal system.

You are given:
1. The ORIGINAL room photograph — before any edits (first image).
2. The EDITED image where an item was supposedly removed (second image).
3. A reviewer's text observations (below).

ITEM LOCATION (what should have been removed): {location_description}
{additional_instructions_block}
REVIEWER'S OBSERVATIONS (use as a secondary reference, but trust your own eyes first):
{review}

YOUR TASK — compare original vs. edited yourself and verify:
1. REMOVAL: Is the item at the described location actually gone?
2. INFILL: Does the vacated area look natural — consistent floor/wall/texture with the surroundings?
3. PRESERVATION: Is everything else in the room unchanged (no unintended additions, deletions, or distortions)?

Decision criteria:
- PASS: The item is clearly removed, the infill looks natural, and the rest of the room is preserved.
- FAIL: The item is still present, the infill is obviously artificial, or unintended changes were made elsewhere.

Respond in EXACTLY this format (two lines only):
VERDICT: PASS
FEEDBACK: <one-sentence summary of what you see>

or

VERDICT: FAIL
FEEDBACK: <specific, actionable correction describing what went wrong and how to fix it, phrased as an instruction for the image generator>"""


def _review_removal(
    original_room_path: str,
    edited_path: str,
    location_description: str,
    additional_instructions: str = "",
) -> str:
    """Reviewer agent for removal: compare original vs edited."""
    prompt = REMOVAL_REVIEWER_PROMPT.format(
        location_description=location_description,
        additional_instructions_block=_format_instructions_block(additional_instructions),
    )
    room_img = Image.open(original_room_path)
    edited_img = Image.open(edited_path)
    return _call_gemini_text([prompt, room_img, edited_img])


def _examine_removal(
    original_room_path: str,
    edited_path: str,
    location_description: str,
    review: str,
    additional_instructions: str = "",
) -> tuple[bool, str]:
    """Examiner agent for removal: visually verify and decide PASS/FAIL."""
    prompt = REMOVAL_EXAMINER_PROMPT.format(
        location_description=location_description,
        additional_instructions_block=_format_instructions_block(additional_instructions),
        review=review,
    )
    room_img = Image.open(original_room_path)
    edited_img = Image.open(edited_path)
    raw = _call_gemini_text([prompt, room_img, edited_img])

    passed = "VERDICT: PASS" in raw.upper()
    feedback = ""
    for line in raw.splitlines():
        if line.upper().startswith("FEEDBACK:"):
            feedback = line.split(":", 1)[1].strip()
            break

    return passed, feedback


def generate_removal_with_verification(
    room_image_path: str,
    location_description: str,
    additional_instructions: str = "",
    max_attempts: int = 3,
    on_attempt: Optional[callable] = None,
) -> VerifiedPlacementResult:
    """Run the removal generate → review → examine loop.

    Args:
        room_image_path: Path to the original room photo.
        location_description: Natural-language description of where the item
            to remove is located.
        additional_instructions: Extra hints from the user.
        max_attempts: Maximum generation cycles before giving up.
        on_attempt: Optional callback ``fn(PlacementAttempt)`` for UI progress.

    Returns:
        VerifiedPlacementResult with the final image path, pass/fail status,
        and the full history of attempts.
    """
    attempts: list[PlacementAttempt] = []
    accumulated_feedback: list[str] = []

    for i in range(1, max_attempts + 1):
        # ----- BUILD PROMPT -----
        prompt_parts = [location_description]
        if additional_instructions.strip():
            prompt_parts.append(additional_instructions.strip())
        if accumulated_feedback:
            prompt_parts.append(
                "IMPORTANT corrections from previous attempts: "
                + " ".join(accumulated_feedback)
            )
        full_location = ". ".join(prompt_parts)

        # ----- GENERATE (unique path per attempt) -----
        room_stem = Path(room_image_path).stem
        attempt_output = str(
            Config.OUTPUT_DIR / f"{room_stem}_removed_attempt{i}.jpg"
        )
        result_path = remove_item_from_scene(
            room_image_path=room_image_path,
            location_description=full_location,
            output_path=attempt_output,
        )

        # ----- REVIEW -----
        review = _review_removal(
            original_room_path=room_image_path,
            edited_path=str(result_path),
            location_description=location_description,
            additional_instructions=additional_instructions,
        )

        # ----- EXAMINE -----
        passed, feedback = _examine_removal(
            original_room_path=room_image_path,
            edited_path=str(result_path),
            location_description=location_description,
            review=review,
            additional_instructions=additional_instructions,
        )

        attempt = PlacementAttempt(
            attempt=i,
            image_path=str(result_path),
            review=review,
            passed=passed,
            feedback=feedback,
        )
        attempts.append(attempt)

        if on_attempt:
            on_attempt(attempt)

        if passed:
            return VerifiedPlacementResult(
                final_image_path=str(result_path),
                passed=True,
                attempts=attempts,
            )

        accumulated_feedback.append(feedback)

    return VerifiedPlacementResult(
        final_image_path=str(result_path),
        passed=False,
        attempts=attempts,
    )
