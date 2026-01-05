def chapter_to_dict(topic):
    return {
        "title": topic.chapter_title,
        "sequence": topic.sequence,
        "outline": topic.outline,
    }
