"""Streamlit app for interactive interior design prototyping."""

import sys
import tempfile
from pathlib import Path

import streamlit as st
from PIL import Image
from streamlit_image_coordinates import streamlit_image_coordinates

# Ensure project root is on the path for imports
PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import Config
from src.pipeline import ImageEditingPipeline
from tools.helpers.addRedDotToLayout import add_red_dot
from tools.helpers.describeRedDotLocation import describe_red_dot_location
from src.pipeline.verified_placement import (
    generate_with_verification,
    generate_removal_with_verification,
    PlacementAttempt,
)

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Interior Design Prototyper", layout="wide")
st.title("Interior Design Prototyper")

# ---------------------------------------------------------------------------
# Session state defaults
# ---------------------------------------------------------------------------
_defaults = {
    "room_image_path": None,
    "layout_image_path": None,
    "layout_with_dot_path": None,
    "click_coords": None,
    "result_image_path": None,
}
for key, val in _defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

Config.ensure_directories()

# ===================================================================
# STEP 1 — Upload Room Image
# ===================================================================
st.header("Step 1: Upload Room Image")

room_file = st.file_uploader(
    "Upload a photo of your room",
    type=["png", "jpg", "jpeg"],
    key="room_uploader",
)

if room_file is not None:
    # Save uploaded file to input dir
    room_save_path = Config.INPUT_DIR / room_file.name
    room_save_path.write_bytes(room_file.getvalue())
    st.session_state.room_image_path = str(room_save_path)
    st.image(str(room_save_path), caption="Uploaded room image", use_container_width=True)
else:
    if st.session_state.room_image_path and Path(st.session_state.room_image_path).exists():
        st.image(st.session_state.room_image_path, caption="Uploaded room image", use_container_width=True)

# ===================================================================
# STEP 2 — Generate 2D Top-Down Layout
# ===================================================================
if st.session_state.room_image_path:
    st.divider()
    st.header("Step 2: Generate 2D Layout")

    layout_prompt = st.text_area(
        "Layout generation prompt (edit to customise)",
        value="room layout, floor plan, interior layout, top-down, black white",
        height=80,
    )

    col_gen, col_retry = st.columns([1, 1])
    generate_clicked = col_gen.button("Generate Layout")
    retry_clicked = col_retry.button("Retry Layout")

    if generate_clicked or retry_clicked:
        with st.spinner("Generating layout with Gemini..."):
            try:
                pipeline = ImageEditingPipeline(provider="google")
                output_path = pipeline.process_single(
                    image_path=st.session_state.room_image_path,
                    prompt=layout_prompt,
                )
                st.session_state.layout_image_path = str(output_path)
                # Reset downstream state on new layout
                st.session_state.layout_with_dot_path = None
                st.session_state.click_coords = None
                st.session_state.result_image_path = None
                st.rerun()
            except Exception as e:
                st.error(f"Layout generation failed: {e}")

    if st.session_state.layout_image_path and Path(st.session_state.layout_image_path).exists():
        st.image(st.session_state.layout_image_path, caption="Generated layout", use_container_width=True)

# ===================================================================
# STEP 3 — Select Spot on Layout
# ===================================================================
if st.session_state.layout_image_path and Path(st.session_state.layout_image_path).exists():
    st.divider()
    st.header("Step 3: Select Placement Spot")
    st.write("Click on the layout to mark where you want to place furniture.")

    layout_img = Image.open(st.session_state.layout_image_path)
    orig_w, orig_h = layout_img.size

    # Cap display width so the coordinate component renders at a known size
    display_width = min(orig_w, 700)
    scale = orig_w / display_width

    coords = streamlit_image_coordinates(
        layout_img.resize((display_width, int(orig_h / scale))),
        key="layout_click",
    )

    if coords is not None:
        # Map display coordinates back to original image coordinates
        real_x = int(coords["x"] * scale)
        real_y = int(coords["y"] * scale)

        if (real_x, real_y) != st.session_state.click_coords:
            st.session_state.click_coords = (real_x, real_y)

            # Build a red-dot image
            dot_path = Config.OUTPUT_DIR / f"{Path(st.session_state.layout_image_path).stem}_WithRedDot.png"
            add_red_dot(
                layout_image_path=st.session_state.layout_image_path,
                x=real_x,
                y=real_y,
                output_path=str(dot_path),
            )
            st.session_state.layout_with_dot_path = str(dot_path)
            st.rerun()

    if st.session_state.layout_with_dot_path and Path(st.session_state.layout_with_dot_path).exists():
        st.image(
            st.session_state.layout_with_dot_path,
            caption=f"Placement spot marked at {st.session_state.click_coords}",
            use_container_width=True,
        )

# ===================================================================
# STEP 4 — Insert or Remove Furniture
# ===================================================================
if st.session_state.layout_with_dot_path and Path(st.session_state.layout_with_dot_path).exists():
    st.divider()
    st.header("Step 4: Edit Furniture")

    mode = st.radio("Action", ["Insert Item", "Remove Item"], horizontal=True)

    additional_instructions = st.text_input(
        "Additional instructions (optional)",
        placeholder="e.g. facing forward, modern style"
            if mode == "Insert Item"
            else "e.g. fill with hardwood floor, match surrounding wall colour",
    )

    max_attempts = st.slider("Max verification attempts", min_value=1, max_value=5, value=3)

    # --- shared helpers ---
    def _show_attempt(attempt: PlacementAttempt):
        with _attempt_ph.container():
            st.markdown(f"**Attempt {attempt.attempt}**")
            st.image(attempt.image_path, width=400)
            st.markdown(f"**Reviewer:** {attempt.review}")
            verdict = "PASS" if attempt.passed else "FAIL"
            st.markdown(f"**Examiner verdict:** {verdict} — {attempt.feedback}")

    # ---- INSERT mode ----
    if mode == "Insert Item":
        item_file = st.file_uploader(
            "Upload the furniture / item image to insert",
            type=["png", "jpg", "jpeg"],
            key="item_uploader",
        )

        if item_file is not None:
            item_save_path = Config.INPUT_DIR / item_file.name
            item_save_path.write_bytes(item_file.getvalue())
            st.image(str(item_save_path), caption="Item to insert", width=300)

            if st.button("Insert Item", key="btn_insert"):
                with st.spinner("Analysing placement location..."):
                    try:
                        location_description = describe_red_dot_location(
                            original_room_path=st.session_state.room_image_path,
                            layout_with_dot_path=st.session_state.layout_with_dot_path,
                        )
                        st.info(f"**Detected location:** {location_description}")
                    except Exception as e:
                        st.error(f"Location analysis failed: {e}")
                        st.stop()

                _progress = st.container()
                _attempt_ph = _progress.empty()

                with st.spinner("Generating and verifying placement (multi-agent loop)..."):
                    try:
                        result = generate_with_verification(
                            room_image_path=st.session_state.room_image_path,
                            item_image_path=str(item_save_path),
                            placement_description=location_description,
                            additional_instructions=additional_instructions,
                            max_attempts=max_attempts,
                            on_attempt=_show_attempt,
                        )
                        st.session_state.result_image_path = result.final_image_path
                        st.session_state.verification_result = result
                    except Exception as e:
                        st.error(f"Item insertion failed: {e}")
                        st.stop()

    # ---- REMOVE mode ----
    else:
        st.write("The item at the selected spot will be removed from the room photo.")

        if st.button("Remove Item", key="btn_remove"):
            with st.spinner("Analysing location of item to remove..."):
                try:
                    location_description = describe_red_dot_location(
                        original_room_path=st.session_state.room_image_path,
                        layout_with_dot_path=st.session_state.layout_with_dot_path,
                    )
                    st.info(f"**Item location:** {location_description}")
                except Exception as e:
                    st.error(f"Location analysis failed: {e}")
                    st.stop()

            _progress = st.container()
            _attempt_ph = _progress.empty()

            with st.spinner("Removing item and verifying (multi-agent loop)..."):
                try:
                    result = generate_removal_with_verification(
                        room_image_path=st.session_state.room_image_path,
                        location_description=location_description,
                        additional_instructions=additional_instructions,
                        max_attempts=max_attempts,
                        on_attempt=_show_attempt,
                    )
                    st.session_state.result_image_path = result.final_image_path
                    st.session_state.verification_result = result
                except Exception as e:
                    st.error(f"Item removal failed: {e}")
                    st.stop()

    # ---- RESULTS (shared) ----
    if st.session_state.get("result_image_path") and Path(st.session_state.result_image_path).exists():
        result = st.session_state.get("verification_result")
        if result:
            status = "Verified" if result.passed else f"Best of {len(result.attempts)} attempts (not verified)"
            st.subheader(f"Result — {status}")

            with st.expander(f"View all {len(result.attempts)} attempt(s)", expanded=False):
                for a in result.attempts:
                    verdict = "PASS" if a.passed else "FAIL"
                    st.markdown(f"---\n**Attempt {a.attempt}** — {verdict}")
                    st.image(a.image_path, width=350)
                    st.caption(f"Reviewer: {a.review}")
                    st.caption(f"Feedback: {a.feedback}")
        else:
            st.subheader("Result")

        st.image(st.session_state.result_image_path, caption="Final result", use_container_width=True)

        with open(st.session_state.result_image_path, "rb") as f:
            st.download_button(
                label="Download Result",
                data=f,
                file_name=Path(st.session_state.result_image_path).name,
                mime="image/jpeg",
            )
