def select_verified_protocol(con, zone_id):
    return con.execute("""
        SELECT * FROM protocols
        WHERE verified=1 AND (zone_id=? OR zone_id IS NULL)
        ORDER BY CASE WHEN zone_id=? THEN 0 ELSE 1 END, id DESC LIMIT 1
    """, (zone_id, zone_id)).fetchone()

def response_message(con, zone_id, predicted_class, triggered_events):
    protocol = select_verified_protocol(con, zone_id)
    triggered = predicted_class == "HIGH" or bool(triggered_events)
    if not triggered:
        return {
            "state":"MONITOR", "headline":"No response trigger",
            "message":"Continue scheduled monitoring and follow the site's approved routine inspection plan.",
            "protocol":protocol
        }
    if protocol:
        return {
            "state":"PROTOCOL AVAILABLE", "headline":"Escalation review required",
            "message":"A model high-risk classification or independent sensor trigger was recorded. Review the verified site protocol and notify the designated safety authority. Human authorization is required for any operational action.",
            "protocol":protocol
        }
    return {
        "state":"NO VERIFIED PROTOCOL", "headline":"Official instructions required",
        "message":"No verified protocol is available for this zone. Do not infer evacuation routes or assembly points. Follow official site/emergency instructions and contact the responsible safety authority.",
        "protocol":None
    }
