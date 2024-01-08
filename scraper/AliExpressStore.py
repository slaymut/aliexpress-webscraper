import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class AliExpressStore:
  def __init__(
    self,
    name,
    reviewPercentage,
    isChoiceStore,
    isPlusStore,
    isGoldStore,
    followers,
    id=None,
    trustScore=0,
    trustworthiness=None,
  ):
    self.name = name
    self.reviewPercentage = reviewPercentage
    self.isChoiceStore = isChoiceStore
    self.isPlusStore = isPlusStore
    self.isGoldStore = isGoldStore
    self.followers = followers
    self.id = id
    self.trustScore = trustScore
    self.trustworthiness = trustworthiness