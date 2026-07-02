def level_to_num(gathering_level):
  if gathering_level < 10:
    return 0
  elif gathering_level < 20:
    return 1
  elif gathering_level < 30:
    return 2
  elif gathering_level < 40:
    return 3
  elif gathering_level < 50:
    return 4
  elif gathering_level < 60:
    return 5
  elif gathering_level < 70:
    return 6
  elif gathering_level < 80:
    return 7
  elif gathering_level < 90:
    return 8
  elif gathering_level < 100:
    return 9
  elif gathering_level < 105:
    return 10
  elif gathering_level < 110:
    return 11
  elif gathering_level < 115:
    return 12
  else:
    return 13

def level_to_tiers(n, gathering_level):
  if (gathering_level < 10 or n < 1):
    low, lowmid, mid, highmid, high = 2, 4, 4, 6, 8
  elif (gathering_level < 20 or n < 2):
    low, lowmid, mid, highmid, high = 2, 5, 5, 8, 10
  elif (gathering_level < 30 or n < 3):
    low, lowmid, mid, highmid, high = 3, 5, 6, 9, 12
  elif (gathering_level < 40 or n < 4):
    low, lowmid, mid, highmid, high = 3, 6, 6, 11, 14
  elif (gathering_level < 50 or n < 5):
    low, lowmid, mid, highmid, high = 3, 6, 7, 12, 16
  elif (gathering_level < 60 or n < 6):
    low, lowmid, mid, highmid, high = 4, 7, 8, 14, 18
  elif (gathering_level < 70 or n < 7):
    low, lowmid, mid, highmid, high = 4, 8, 9, 15, 20
  elif (gathering_level < 80 or n < 8):
    low, lowmid, mid, highmid, high = 4, 8, 10, 17, 22
  elif (gathering_level < 90 or n < 9):
    low, lowmid, mid, highmid, high = 4, 9, 10, 18, 24
  elif (gathering_level < 100 or n < 10):
    low, lowmid, mid, highmid, high = 5, 9, 11, 20, 26
  elif (gathering_level < 105 or n < 11):
    low, lowmid, mid, highmid, high = 5, 10, 12, 21, 28
  elif (gathering_level < 110 or n < 12):
    low, lowmid, mid, highmid, high = 5, 10, 12, 22, 29
  elif (gathering_level < 110 or n < 13):
    low, lowmid, mid, highmid, high = 5, 11, 13, 23, 30
  else:
    low, lowmid, mid, highmid, high = 5, 11, 13, 23, 31
  
  return low, lowmid, mid, highmid, high


def get_mats_of_levels(n, gathering_levels):

  out = {}

  low, lowmid, mid, highmid, high = level_to_tiers(n, gathering_levels[0])
  out['ingot'] = [0, 0, 0, lowmid, 0, high, 0, 0]
  out['gem']   = [mid, 0, 0, low, 0, 0, 0, highmid]
  
  low, lowmid, mid, highmid, high = level_to_tiers(n, gathering_levels[1])
  out['plank'] = [low, highmid, 0, 0, 0, mid, 0, 0]
  out['paper']   = [0, 0, high, 0, 0, 0, lowmid, 0]

  low, lowmid, mid, highmid, high = level_to_tiers(n, gathering_levels[2])
  out['string'] = [0, low, 0, 0, mid, 0, highmid, 0]
  out['grains']   = [high, 0, lowmid, 0, 0, 0, 0, 0]
  
  low, lowmid, mid, highmid, high = level_to_tiers(n, gathering_levels[3])
  out['oil'] = [0, 0, low, 0, highmid, 0, 0, mid]
  out['meat']   = [0, lowmid, 0, high, 0, 0, 0, 0]
      
  return out



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
        c = np.ones(len(useful_idx)) + (A_use.sum(axis=0) * 0.0001)

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


    def name_to_profession(self, name):
      if name in ["ingot", "gem"]:
            return "Mining"
      elif name in ["plank", "paper"]:
          return "Woodcutting"
      elif name in ["string", "grains"]:
          return "Farming"
      elif name in ["oil", "meat"]:
          return "Fishing"
      else:
          raise ValueError(f"Unknown material name: {name}")

    def get_specific_food_tier(self, name, gathering_levels, special_limits = None):
      profession = self.name_to_profession(name)
      if special_limits == None:
        lims = self.limits
      else:
        lims = special_limits
      
      if profession == "Mining":
        gathering_level = gathering_levels[0]
      
      elif profession == "Woodcutting":
        gathering_level = gathering_levels[1]

      elif profession == "Farming":
        gathering_level = gathering_levels[2]

      elif profession == "Fishing":
        gathering_level = gathering_levels[3]
    
      max_limit = 0
      for temp_num, max_num in zip(lims, self.maxs):
        if temp_num > max_limit:
          max_limit = min(temp_num, max_num)
      
      other_limit = level_to_num(gathering_level)

      max_limit = min(max_limit, other_limit)
      if max_limit == other_limit:
        raise ValueError(f"max_limit: {max_limit}, other_limit: {other_limit}, gathering_level: {gathering_level}, profession: {profession}")
      return max_limit
    

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
    
    def apply_plan_until_new_tier(self, mats_lists, plan, gathering_levels):

      current_mats = self.get_current_mats(mats_lists)
      current_tier = self.get_food_tier()
      
      # If there are grains, start with that
      # if not, start with gem

      for name, count in plan.items():
        if name == 'grains':
          
          named_tier = self.get_specific_food_tier(name, gathering_levels)

          vec = current_mats[name]
          for _ in range(count):
            self.eaten.append((name, named_tier))
            for j in range(len(self.limits)):
              self.limits[j] = min(self.maxs[j], self.limits[j] + vec[j])
            
            test_tier = self.get_food_tier()
            if test_tier > current_tier:
              return self.limits

      for name, count in plan.items():
        if name == 'gem':
          named_tier = self.get_specific_food_tier(name, gathering_levels)

          vec = current_mats[name]
          for _ in range(count):
            self.eaten.append((name, named_tier))
            for j in range(len(self.limits)):
              self.limits[j] = min(self.maxs[j], self.limits[j] + vec[j])
            
            test_tier = self.get_food_tier()
            if test_tier > current_tier:
              return self.limits

      for name, count in plan.items():
        if name == 'paper':
          named_tier = self.get_specific_food_tier(name, gathering_levels)

          vec = current_mats[name]
          for _ in range(count):
            self.eaten.append((name, named_tier))
            for j in range(len(self.limits)):
              self.limits[j] = min(self.maxs[j], self.limits[j] + vec[j])
            
            test_tier = self.get_food_tier()
            if test_tier > current_tier:
              return self.limits

      for name, count in plan.items():
        if name not in ['grains', 'gem', 'paper']:
          named_tier = self.get_specific_food_tier(name, gathering_levels)

          vec = current_mats[name]
          for _ in range(count):
            self.eaten.append((name, named_tier))
            for j in range(len(self.limits)):
              self.limits[j] = min(self.maxs[j], self.limits[j] + vec[j])
                    
              test_tier = self.get_food_tier()
              if test_tier > current_tier:
                  return self.limits

    def apply_plan(self, materials, plan, gathering_levels):
        """Feed the plan to the mount, updating self.limits (clamped to maxs)."""
        tier = self.get_food_tier()
        for name, count in plan.items():
          named_tier = self.get_specific_food_tier(name, gathering_levels)

          vec = materials[name]
          for _ in range(count):
            self.eaten.append((name, named_tier))
            for j in range(len(self.limits)):
              self.limits[j] = min(self.maxs[j], self.limits[j] + vec[j])
        return self.limits
    
    def fully_eat(self, mats_lists, gathering_levels):
      while not self.is_at_max_food_tier():
          plan = self.find_feed_plan(mats_lists)
          self.apply_plan_until_new_tier(mats_lists, plan, gathering_levels)
      plan = self.find_feed_plan(mats_lists)
      self.apply_plan(self.get_current_mats(mats_lists), plan, gathering_levels)

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
            row.append(str(table[tier].get(name, '')))
        rows.append(row)

    return rows

def calculate_feeding2(limits, maxes, gathering_levels):
    mats_lists = [get_mats_of_levels(i, gathering_levels) for i in range(14)]
    m = FinalMount(limits, maxes)
    m.fully_eat(mats_lists, gathering_levels)
    return eaten_to_table(m.eaten)

def calculate_num_needed(limits, maxes, gathering_levels):
    mats_lists = [get_mats_of_levels(i, gathering_levels) for i in range(14)]
    m = FinalMount(limits, maxes)
    m.fully_eat(mats_lists, gathering_levels)
    return len(m.eaten)
