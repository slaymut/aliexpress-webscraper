def calculate_trust_score(follower_nbr, reviews_percentage):
  followersWeight=0.33
  reviewsWeight=0.67
  
  normalizedFollowers = follower_nbr / 100000
  normalizedGoodReviews = reviews_percentage / 100
  trust_score = (normalizedFollowers * followersWeight) + (normalizedGoodReviews * reviewsWeight)

  return trust_score * 100

def calculate_trust_score(rating, reviews_nbr, number_of_sells, price):
  ratingWeight=0.1
  reviewsWeight=0.2
  sellsWeight=0.3
  priceWeight=0.4
  
  normalizedRating = rating / 5
  normalizedReviews = reviews_nbr / 100
  normalizedSells = number_of_sells / 100000
  normalizedPrice = price / 1000
  
  trust_score = (normalizedRating * ratingWeight) + (normalizedReviews * reviewsWeight) + (normalizedSells * sellsWeight) + (normalizedPrice * priceWeight)

  return trust_score * 100

def format_follower_count(follower_count):
  if follower_count[-1] == 'K':
    return float(follower_count[:-1]) * 1000
  elif follower_count[-1] == 'M':
    return float(follower_count[:-1]) * 1000000
  else:
    return int(follower_count)
  
def classify_trustworthiness(trust_score):
  if trust_score >= 90:
    return 'Highly Trustworthy'
  elif trust_score >= 80:
    return 'Very Trustworthy'
  elif trust_score >= 70:
    return 'Trustworthy'
  elif trust_score >= 60:
    return 'Somewhat Trustworthy'
  elif trust_score >= 50:
    return 'Neutral Trustworthiness'
  elif trust_score >= 40:
    return 'Questionable Trustworthiness'
  elif trust_score >= 30:
    return 'Low Trustworthiness'
  elif trust_score >= 20:
    return 'Very Low Trustworthiness'
  elif trust_score >= 10:
    return 'Untrustworthy'
  else:
    return 'Highly Untrustworthy'
