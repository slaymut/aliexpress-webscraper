import sys
import os
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class AliExpressStore:
  def __init__(
    self,
    id,
    name,
    isChoiceStore,
    isPlusStore,
    isGoldStore,
    reviewPercentage=None,
    followers=None,
    trustScore=0,
    trustworthiness=None,
  ):
    self.id = id
    self.name = name
    self.reviewPercentage = reviewPercentage
    self.isChoiceStore = isChoiceStore
    self.isPlusStore = isPlusStore
    self.isGoldStore = isGoldStore
    self.followers = followers
    self.trustScore = trustScore
    self.trustworthiness = trustworthiness

  def to_dict(self):
    return {
      'id': self.id,
      'name': self.name,
      'reviewPercentage': self.reviewPercentage,
      'isChoiceStore': self.isChoiceStore,
      'isPlusStore': self.isPlusStore,
      'isGoldStore': self.isGoldStore,
      'followers': self.followers,
      'trustScore': self.trustScore,
      'trustworthiness': self.trustworthiness
    }
    
  