def chapter_to_dict(chapter, outlines):
    return {
        "title": chapter.title,
        "sequence": chapter.sequence,
        "outlines": [outline_to_dict(o) for o in outlines],
    }


def outline_to_dict(outline):
    return {
        "title": outline.title,
        "sequence": outline.sequence,
    }
