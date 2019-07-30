from socialmodels import UserProfile

def save_profile(email, name, preferences):
    p = get_user_profile(email)
    if p:
        p.name = name
        if preferences:
            p.preferences = preferences
        else:
            p.preferences = []
    else:
        p = UserProfile(email=email, name=name, preferences=preferences)
    p.put()

def get_user_profile(email):
    q = UserProfile.query(UserProfile.email==email)
    results = q.fetch(1)
    for profile in results:
        return profile
    return None

def get_profile_by_name(name):
    q = UserProfile.query(UserProfile.name==name)
    results = q.fetch(1)
    for profile in results:
        return profile
    return None

def get_recent_profiles():
    q = UserProfile.query().order(-UserProfile.last_update)
    return q.fetch(50)