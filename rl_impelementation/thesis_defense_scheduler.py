import random
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import math
from rl_impelementation.thesis_defense_environment import ThesisDefenseEnvironment


# Q-Learning model

class ThesisDefenseScheduler:
    def __init__(self, schedule_df, lecturer_expertise):
        self.env = ThesisDefenseEnvironment(schedule_df, lecturer_expertise)
        self.learning_rate = 0.1
        self.discount_factor = 0.9
        self.epsilon = 0.1  # untuk exploration

    def select_action(self, defense_id, valid_actions):
        if np.random.random() < self.epsilon:
            return np.random.choice(valid_actions)
        else:
            action_rewards = {
                lecturer_id: self.env.calculate_assignment_reward(lecturer_id, defense_id)
                for lecturer_id in valid_actions
            }
            return max(action_rewards.items(), key=lambda x: x[1])[0]

    def schedule_defenses(self, schedule_df, lecturer_expertise, max_iterations=1000):
        best_schedule = None
        best_reward = float('-inf')

        for iteration in range(max_iterations):
            self.env = ThesisDefenseEnvironment(schedule_df, lecturer_expertise)
            total_reward = 0
            schedule = []

            # Process each defense
            while len(self.env.current_state['remaining_defenses']) > 0:
                defense_id = self.env.current_state['remaining_defenses'][0]
                valid_actions = self.env.get_valid_actions(defense_id)

                # Select and take action
                selected_lecturer = self.select_action(defense_id, valid_actions)
                new_state, reward, done = self.env.step(defense_id, selected_lecturer)

                total_reward += reward
                schedule.append((defense_id, selected_lecturer))

            # Update best schedule if current is better
            if total_reward > best_reward:
                best_reward = total_reward
                best_schedule = schedule.copy()


        return best_schedule, best_reward

    def analyze_schedule(self, schedule):

        workload = {}
        for defense_id, lecturer_id in schedule:
            workload[lecturer_id] = workload.get(lecturer_id, 0) + 1

        workload_series = pd.Series(workload)

        expertise_matches = 0
        for defense_id, lecturer_id in schedule:
            defense = self.env.schedule.loc[defense_id]
            if defense['bidang'] in self.env.lecturer_expertise[lecturer_id]:
                expertise_matches += 1

        expertise_ratio = expertise_matches / len(schedule)

        return {
            'workload': workload,
            'expertise_ratio': expertise_ratio
        }


