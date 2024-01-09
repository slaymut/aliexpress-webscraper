import sys
import os
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class AliExpressStore:
  def __init__(
    self,
    name,
    isChoiceStore,
    isPlusStore,
    isGoldStore,
    reviewPercentage=None,
    followers=None,
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

  def to_dict(self):
    return {
      'name': self.name,
      'reviewPercentage': self.reviewPercentage,
      'isChoiceStore': self.isChoiceStore,
      'isPlusStore': self.isPlusStore,
      'isGoldStore': self.isGoldStore,
      'followers': self.followers,
      'id': self.id,
      'trustScore': self.trustScore,
      'trustworthiness': self.trustworthiness
    }
    
  