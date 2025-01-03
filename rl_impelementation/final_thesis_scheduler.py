import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import math

class FinalThesisScheduler:
    def __init__(self, schedule_df, lecturer_expertise):
        self.schedule_df = schedule_df
        self.lecturer_expertise = lecturer_expertise
        self.roles = ['examiner1', 'examiner2', 'supervisor1', 'supervisor2']
        self.lecturer_workload = {lid: 0 for lid in lecturer_expertise.keys()}
        self.target_workload = (len(schedule_df) * 4) / len(lecturer_expertise)

    def calculate_assignment_score(self, lecturer_id, field, current_workload):
        base_score = 0

        if field in self.lecturer_expertise[lecturer_id]:
            expertise_score = 3.0 / len(self.lecturer_expertise[lecturer_id])
            base_score += expertise_score

        workload_diff = abs(current_workload - self.target_workload)
        workload_score = 2.0 * (1.0 / (workload_diff + 1))
        base_score += workload_score

        return base_score

    def schedule_defense(self, defense_id, print_details=True):
        defense = self.schedule_df.loc[defense_id]
        role_assignments = {}
        for role in self.roles:
            valid_lecturers = [
                lid for lid, expertise in self.lecturer_expertise.items()
                if defense['bidang'] in expertise
                and lid not in role_assignments.values()
                and self.lecturer_workload[lid] < max(5, self.target_workload * 1.5)
            ]
            if valid_lecturers:
                scores = {
                    lid: self.calculate_assignment_score(
                        lid,
                        defense['bidang'],
                        self.lecturer_workload[lid]
                    ) for lid in valid_lecturers
                }

                selected = max(scores.items(), key=lambda x: x[1])[0]
                role_assignments[role] = selected
                self.lecturer_workload[selected] += 1
        return role_assignments

    def analyze_schedule(self, complete_schedule):
        workload_series = pd.Series(self.lecturer_workload)
        expertise_matches = 0
        total_assignments = 0
        for defense_id, assignments in complete_schedule.items():
            defense = self.schedule_df.loc[defense_id]
            for role, lecturer_id in assignments.items():
                total_assignments += 1
                if defense['bidang'] in self.lecturer_expertise[lecturer_id]:
                    expertise_matches += 1
        workload_std = workload_series.std()
        balance_score = 1.0 / (1.0 + workload_std)

    def verify_schedule(self, complete_schedule):
        expertise_violations = 0
        time_conflicts = 0
        workload_violations = 0

        for defense_id, assignments in complete_schedule.items():
            defense = self.schedule_df.loc[defense_id]

            # Check each assigned lecturer
            for role, lecturer_id in assignments.items():
                # Expertise check
                if defense['bidang'] not in self.lecturer_expertise[lecturer_id]:
                    expertise_violations += 1

                # Time conflict check
                time_conflict = False
                for other_id, other_assignments in complete_schedule.items():
                    if other_id != defense_id:
                        other_defense = self.schedule_df.loc[other_id]
                        if (other_defense['date'] == defense['date'] and
                            other_defense['time'] == defense['time'] and
                            lecturer_id in other_assignments.values()):
                            time_conflicts += 1
        return expertise_violations == 0 and time_conflicts == 0

