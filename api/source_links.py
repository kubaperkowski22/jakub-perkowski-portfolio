SOURCE_ANCHORS: dict[str, str] = {
    "profile.profile": "about",
    "profile.experience": "experience",
    "profile.education": "education",
    "profile.skills": "skills",
}


def get_source_anchor(
    document_id: str,
) -> str | None:
    return SOURCE_ANCHORS.get(
        document_id
    )