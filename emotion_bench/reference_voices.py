"""Reference voice model IDs for testing."""

import os

from dotenv import load_dotenv

load_dotenv()

# List of voice model IDs to test
# Add your Fish Audio voice model IDs here
REFERENCE_IDS = [
    "802e3bc2b27e49c2995d23ef70e6ac89",  # Energetic Male
    "b545c585f631496c914815291da4e893",  # Friendly Women
    "8ba9b8b845e342da9d511d4e0c2ff733",  # E-girl
]


def get_reference_ids() -> list[str | None]:
    """Get list of reference IDs to test.

    Returns:
        List of reference IDs, or [None] if INCLUDE_NO_REFERENCE is set
    """
    # If INCLUDE_NO_REFERENCE is set, only test with default voice
    if os.getenv("INCLUDE_NO_REFERENCE"):
        return [None]

    # Otherwise, test with configured reference voices
    return list(REFERENCE_IDS)
