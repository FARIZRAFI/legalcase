from app.models.timeline_model import TimelineEvent


def create_timeline_event(

    db,

    case_id: int,

    title: str,

    description: str
):

    event = TimelineEvent(

        case_id=case_id,

        title=title,

        description=description
    )

    db.add(event)

    db.commit()

    db.refresh(event)

    return event