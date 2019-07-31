from socialmodels import UserProfile

def save_profile(email, name, preferences, neighborhood):
    p = get_user_profile(email)
    if p:
        p.name = name
        if preferences:
            p.preferences = preferences
        if neighborhood:
            p.neighborhood = neighborhood
        else:
            p.preferences = []
    else:
        p = UserProfile(email=email, name=name, preferences=preferences, neighborhood= neighborhood)
    p.put()

def get_user_preferences(email): #ask if thisll work
    q = UserProfile.query(UserProfile.email==email)
    results = q.fetch(1)
    for profile in results:
        return profile.preferences
    return None

def get_user_profile(email):
    q = UserProfile.query(UserProfile.email==email)
    results = q.fetch(1)
    for profile in results:
        return profile
    return None

def get_user_matches(email):
    current_profile = get_user_profile(email)
    matching_profiles = UserProfile.query(UserProfile.email != email, UserProfile.preferences.IN(current_profile.preferences), UserProfile.neighborhood == current_profile.neighborhood)
    return matching_profiles

def get_user_compatibilities(email): #returns a list sorted by the level of prefence compatibilities
    compatibilities = {}
    matches = get_user_matches(email)
    for profile in matches: 
        compatibility_score = len ([e for e in profile.preferences if e in current_profile.preferences])
        compatibilities[profile] = compatibility_score 
    list = sorted (compatibilities.items(), key = lambda x: x[1], reverse = True)    


def get_profile_by_name(name):
    q = UserProfile.query(UserProfile.name==name)
    results = q.fetch(1)
    for profile in results:
        return profile
    return None

def get_recent_profiles():
    q = UserProfile.query().order(-UserProfile.last_update)
    return q.fetch(50)