from app.models.timeline_model import (
    TimelineEvent
)



# =========================
# CREATE TIMELINE EVENT
# =========================

def create_timeline_event(

    db,

    case_id: int,

    title: str,

    description: str
):

    try:


        event = TimelineEvent(

            case_id=case_id,

            title=title,

            description=description
        )



        db.add(event)

        db.commit()

        db.refresh(event)



        print(
            f"Timeline event created: {title}"
        )



        return event



    except Exception as e:


        db.rollback()



        print(
            "Timeline creation failed:"
        )

        print(str(e))



        return None



# =========================
# CREATE FORMATTED EVENT
# =========================

def create_formatted_timeline_event(

    db,

    case_id: int,

    title: str,

    lines: list
):

    description = "\n".join(lines)



    return create_timeline_event(

        db=db,

        case_id=case_id,

        title=title,

        description=description
    )



# =========================
# DELETE TIMELINE EVENTS
# =========================

def delete_case_timeline(

    db,

    case_id: int
):

    try:


        db.query(
            TimelineEvent
        ).filter(

            TimelineEvent.case_id == case_id

        ).delete()



        db.commit()



        print(
            f"Timeline deleted for case {case_id}"
        )



        return True



    except Exception as e:


        db.rollback()



        print(
            "Timeline delete failed:"
        )

        print(str(e))



        return False



# =========================
# GET CASE TIMELINE
# =========================

def get_case_timeline(

    db,

    case_id: int
):

    try:


        events = db.query(
            TimelineEvent
        ).filter(

            TimelineEvent.case_id == case_id

        ).order_by(

            TimelineEvent.created_at.desc()

        ).all()



        return events



    except Exception as e:


        print(
            "Timeline fetch failed:"
        )

        print(str(e))



        return []