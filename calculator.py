def get_mats_of_level(n):
  if n == 0:
    low, lowmid, mid, highmid, high = 2, 4, 4, 6, 8
  elif n == 1:
    low, lowmid, mid, highmid, high = 2, 5, 5, 8, 10
  elif n == 2:
    low, lowmid, mid, highmid, high = 3, 5, 6, 9, 12
  elif n == 3:
    low, lowmid, mid, highmid, high = 3, 6, 6, 11, 14
  elif n == 4:
    low, lowmid, mid, highmid, high = 3, 6, 7, 12, 16
  elif n == 5:
    low, lowmid, mid, highmid, high = 4, 7, 8, 14, 18
  elif n == 6:
    low, lowmid, mid, highmid, high = 4, 8, 9, 15, 20
  elif n == 7:
    low, lowmid, mid, highmid, high = 4, 8, 10, 17, 22
  elif n == 8:
    low, lowmid, mid, highmid, high = 4, 9, 10, 18, 24
  elif n == 9:
    low, lowmid, mid, highmid, high = 5, 9, 11, 20, 26
  elif n == 10:
    low, lowmid, mid, highmid, high = 5, 10, 12, 21, 28
  elif n == 11:
    low, lowmid, mid, highmid, high = 5, 10, 12, 22, 29
  elif n == 12:
    low, lowmid, mid, highmid, high = 5, 11, 13, 23, 30
  elif n == 13:
    low, lowmid, mid, highmid, high = 5, 11, 13, 23, 31
  
  return {
    'ingot': [0, 0, 0, lowmid, 0, high, 0, 0],
    'gem':   [mid, 0, 0, low, 0, 0, 0, highmid],
    'plank': [low, highmid, 0, 0, 0, mid, 0, 0],
    'paper': [0, 0, high, 0, 0, 0, lowmid, 0],
    'string': [0, low, 0, 0, mid, 0, highmid, 0],
    'grains': [high, 0, lowmid, 0, 0, 0, 0, 0],
    'oil':   [0, 0, low, 0, highmid, 0, 0, mid],
    'meat':  [0, lowmid, 0, high, 0, 0, 0, 0]
}




mats_lists = [get_mats_of_level(i) for i in range(14)]

import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds

class FinalMount():
    def __init__(self, limits, maxs):
        self.limits = limits
        self.maxs = maxs
        self.eaten = []

    def find_feed_plan(self, mats_lists):
        """
        Find the minimum-size multiset of materials (dict name -> list[int])
        needed to bring every skill in self.limits up to self.maxs.
        Returns {material_name: count}, omitting zero counts.
        """
        materials = self.get_current_mats(mats_lists)
        names = list(materials.keys())
        n_skills = len(self.limits)

        needed = np.array(
            [max(0, self.maxs[j] - self.limits[j]) for j in range(n_skills)],
            dtype=float
        )
        if not np.any(needed > 0):
            return {}  # already maxed

        A = np.array([materials[name] for name in names], dtype=float).T
        active_skills = np.where(needed > 0)[0]

        # Drop materials that contribute nothing to any needed skill
        useful_mask = (A[active_skills, :] > 0).any(axis=0)
        useful_idx = np.where(useful_mask)[0]
        if len(useful_idx) == 0:
            return {}  # impossible with this material set

        A_use = A[np.ix_(active_skills, useful_idx)]
        c = np.ones(len(useful_idx))  # minimize total item count

        res = milp(
            c=c,
            constraints=LinearConstraint(A_use, lb=needed[active_skills], ub=np.inf),
            bounds=Bounds(lb=0, ub=np.inf),
            integrality=np.ones(len(useful_idx)),
        )
        if not res.success:
            raise RuntimeError(f"Could not find a feeding plan: {res.message}")

        counts = np.round(res.x).astype(int)
        return {names[useful_idx[i]]: int(counts[i])
                for i in range(len(useful_idx)) if counts[i] > 0}

    def get_food_tier(self, special_limits = None):
      if special_limits == None:
        lims = self.limits
      else:
        lims = special_limits
      max_limit = 0
      for temp_num, max_num in zip(lims, self.maxs):
        if temp_num > max_limit:
          max_limit = min(temp_num, max_num)
      
      if max_limit < 10:
        return 0
      elif max_limit < 20:
        return 1
      elif max_limit < 30:
        return 2
      elif max_limit < 40:
        return 3
      elif max_limit < 50:
        return 4
      elif max_limit < 60:
        return 5
      elif max_limit < 70:
        return 6
      elif max_limit < 80:
        return 7
      elif max_limit < 90:
        return 8
      elif max_limit < 100:
        return 9
      elif max_limit < 105:
        return 10
      elif max_limit < 110:
        return 11
      elif max_limit < 115:
        return 12
      else:
        return 13


    def get_current_mats(self, mats_lists):
      return mats_lists[self.get_food_tier()]
    
    def get_max_food_tier(self):
      max_limit = 0
      for max_num in self.maxs:
        if max_num > max_limit:
          max_limit = max_num
      
      if max_limit < 10:
        return 0
      elif max_limit < 20:
        return 1
      elif max_limit < 30:
        return 2
      elif max_limit < 40:
        return 3
      elif max_limit < 50:
        return 4
      elif max_limit < 60:
        return 5
      elif max_limit < 70:
        return 6
      elif max_limit < 80:
        return 7
      elif max_limit < 90:
        return 8
      elif max_limit < 100:
        return 9
      elif max_limit < 105:
        return 10
      elif max_limit < 110:
        return 11
      elif max_limit < 115:
        return 12
      else:
        return 13
    
    def is_at_max_food_tier(self):
      if self.get_food_tier() == self.get_max_food_tier():
        return True
      return False
    
    def apply_plan_until_new_tier(self, mats_lists, plan):

      current_mats = self.get_current_mats(mats_lists)
      current_tier = self.get_food_tier()
      
      # If there are grains, start with that
      # if not, start with gem

      for name, count in plan.items():
        if name == 'grains':
          vec = current_mats[name]
          for _ in range(count):
            self.eaten.append((name, current_tier))
            for j in range(len(self.limits)):
              self.limits[j] = min(self.maxs[j], self.limits[j] + vec[j])
            
            test_tier = self.get_food_tier()
            if test_tier > current_tier:
              return self.limits

      for name, count in plan.items():
        if name == 'gem':
          vec = current_mats[name]
          for _ in range(count):
            self.eaten.append((name, current_tier))
            for j in range(len(self.limits)):
              self.limits[j] = min(self.maxs[j], self.limits[j] + vec[j])
            
            test_tier = self.get_food_tier()
            if test_tier > current_tier:
              return self.limits

      for name, count in plan.items():
        if name == 'paper':
          vec = current_mats[name]
          for _ in range(count):
            self.eaten.append((name, current_tier))
            for j in range(len(self.limits)):
              self.limits[j] = min(self.maxs[j], self.limits[j] + vec[j])
            
            test_tier = self.get_food_tier()
            if test_tier > current_tier:
              return self.limits

      for name, count in plan.items():
          vec = current_mats[name]
          for _ in range(count):
            self.eaten.append((name, current_tier))
            for j in range(len(self.limits)):
              self.limits[j] = min(self.maxs[j], self.limits[j] + vec[j])
            
            test_tier = self.get_food_tier()
            if test_tier > current_tier:
              return self.limits
    
    def apply_plan(self, materials, plan):
        """Feed the plan to the mount, updating self.limits (clamped to maxs)."""
        tier = self.get_food_tier()
        for name, count in plan.items():
            vec = materials[name]
            for _ in range(count):
                self.eaten.append((name, tier))
                for j in range(len(self.limits)):
                    self.limits[j] = min(self.maxs[j], self.limits[j] + vec[j])
        return self.limits
    
    def fully_eat(self, mats_lists):
      while not self.is_at_max_food_tier():
          plan = self.find_feed_plan(mats_lists)
          self.apply_plan_until_new_tier(mats_lists, plan)
      plan = self.find_feed_plan(mats_lists)
      self.apply_plan(self.get_current_mats(mats_lists), plan)

def tier_to_level(tier):
  if tier == 0:
    return 1
  elif tier == 1:
    return 10
  elif tier == 2:
    return 20
  elif tier == 3:
    return 30
  elif tier == 4:
    return 40
  elif tier == 5:
    return 50
  elif tier == 6:
    return 60
  elif tier == 7:
    return 70
  elif tier == 8:
    return 80
  elif tier == 9:
    return 90
  elif tier == 10:
    return 100
  elif tier == 11:
    return 105
  elif tier == 12:
    return 110
  else:
    return 115

def eaten_to_table(eaten):
    """
    Convert a list of (material_name, tier) to a table for display.
    

    table example:
                |   ingot    |   gem     |   plank   |   paper   |   string  |   grains  |   oil     |   meat    |
    # lvl 1     |
    # lvl 10    |
    # lvl 20    |
    # lvl 30    |
    # lvl 40    |
    # lvl 50    |
    # lvl 60    |
    # lvl 70    |
    # lvl 80    |
    # lvl 90    |
    # lvl 100   |
    # lvl 105   |
    # lvl 110   |
    # lvl 115   |
    """
    table = {}
    for name, tier in eaten:
        if tier not in table:
            table[tier] = {}
        if name not in table[tier]:
            table[tier][name] = 0
        table[tier][name] += 1

    # Convert to a list of rows for display
    rows = [['', 'ingot', 'gem', 'plank', 'paper', 'string', 'grains', 'oil', 'meat']]
    for tier in sorted(table.keys()):
        row = [f"lvl {tier_to_level(tier)}"]
        for name in ['ingot', 'gem', 'plank', 'paper', 'string', 'grains', 'oil', 'meat']:
            row.append(str(table[tier].get(name, 0)))
        rows.append(row)

    return rows

def calculate_feeding(limits, maxes):
    m = FinalMount(limits, maxes)
    m.fully_eat(mats_lists)
    return eaten_to_table(m.eaten)
