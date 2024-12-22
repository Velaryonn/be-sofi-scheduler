import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import math

class ThesisDefenseEnvironment:
    def __init__(self, schedule_df, lecturer_expertise):
        self.schedule = schedule_df.copy()
        self.lecturer_expertise = lecturer_expertise

        total_roles = len(self.schedule) * 4  # 4 roles per sidang
        num_lecturers = len(self.lecturer_expertise)
        avg_roles_per_lecturer = total_roles / num_lecturers

        self.target_workload = round(avg_roles_per_lecturer, 2)
        self.assignments = {}  # {(date, time_slot): [lecturer_ids]}
        self.current_state = self.get_initial_state()

        # Constants from our analysis
        self.MAX_ASSIGNMENTS_PER_SLOT = 4  # 2 penguji + 2 pembimbing
        self.MIN_TIME_GAP = 7200  # 2 jam

    def get_initial_state(self): # STATE
        """Create initial state representation"""
        return {
            'scheduled_defenses': [],
            'lecturer_loads': {lid: 0 for lid in self.lecturer_expertise.keys()},
            'remaining_defenses': self.schedule.index.tolist()
        }

    def get_valid_actions(self, defense_id): # ACTION
        """Menentukan action dalam penugasan sidang"""
        defense = self.schedule.loc[defense_id]
        valid_actions = []

        for lecturer_id in self.lecturer_expertise.keys():
            # Check expertise match
            if defense['bidang'] in self.lecturer_expertise[lecturer_id]:
                # Check time conflicts
                has_conflict = False
                if (defense['date'], defense['time']) in self.assignments:
                    if lecturer_id in self.assignments[(defense['date'], defense['time'])]:
                        has_conflict = True

                if not has_conflict:
                    valid_actions.append(lecturer_id)

        return valid_actions

    def calculate_assignment_reward(self, lecturer_id, defense_id): # REWARD
        """Menentukan reward dalam penugasan sidang"""
        defense = self.schedule.loc[defense_id]

        # 1. Expertise Matching (0 to 3.0)
        expertise_score = 0
        if defense['bidang'] in self.lecturer_expertise.get(lecturer_id, []):
            expertise_score = 3.0 * (1.0 / len(self.lecturer_expertise[lecturer_id]))

        # 2. Workload Balance (0 to 2)
        current_load = self.current_state['lecturer_loads'].get(lecturer_id, 0)
        workload_diff = abs(current_load - self.target_workload)
        workload_penalty = 2.0 * (1.0 / (workload_diff + 1))

        # 3. Time Conflict Check (-2.0 or 0)
        conflict_penalty = 0
        if (defense['date'], defense['time']) in self.assignments:
            if lecturer_id in self.assignments[(defense['date'], defense['time'])]:
                conflict_penalty = -2.0

        return expertise_score + workload_penalty + conflict_penalty

    def step(self, defense_id, lecturer_id): # memperbarui status environment
        """mengambil tindakan, menghitung reward, memperbarui status jadwal, dan mengembalikan status baru"""
        defense = self.schedule.loc[defense_id]
        reward = self.calculate_assignment_reward(lecturer_id, defense_id)

        # Update state
        key = (defense['date'], defense['time'])
        if key not in self.assignments:
            self.assignments[key] = []
        self.assignments[key].append(lecturer_id)

        self.current_state['lecturer_loads'][lecturer_id] = self.current_state['lecturer_loads'].get(lecturer_id, 0) + 1

        if defense_id in self.current_state['remaining_defenses']:
            self.current_state['remaining_defenses'].remove(defense_id)
            self.current_state['scheduled_defenses'].append(defense_id)

        done = len(self.current_state['remaining_defenses']) == 0
        return self.current_state, reward, done


## Test the environment
# print("Testing RL Environment:")
# jadwal_df = pd.read_excel(jadwal_file_path)
# env = ThesisDefenseEnvironment(jadwal_df, lecturer_expertise)

# # Test case: Schedule first defense
# test_defense_id = jadwal_df.index[0]
# print(f"\nTesting assignment for defense {test_defense_id}:")
# print("Defense details:", jadwal_df.loc[test_defense_id])

# valid_actions = env.get_valid_actions(test_defense_id)
# print(f"\nValid lecturers for this defense: {len(valid_actions)}")
# print("Sample of valid lecturers:", valid_actions[:5])

# if valid_actions:
#     test_lecturer = valid_actions[0]
#     new_state, reward, done = env.step(test_defense_id, test_lecturer)
#     print(f"\nAssignment result:")
#     print(f"Assigned lecturer: {test_lecturer}")
#     print(f"Reward: {reward:.2f}")
#     print(f"Done: {done}")
#     print(f"Remaining defenses: {len(new_state['remaining_defenses'])}")