from datetime import date, time

def serialize(meet):
    serialized = {}
    for key, value in meet.items():
        if isinstance(value, date) or isinstance(value, time):
            serialized[key] = value.isoformat()
        else:
            serialized[key] = value
            
    return serialized