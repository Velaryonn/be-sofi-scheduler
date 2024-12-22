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
        """Calculate score for potential assignment"""
        base_score = 0

        # Expertise matching (0-3 points)
        if field in self.lecturer_expertise[lecturer_id]:
            expertise_score = 3.0 / len(self.lecturer_expertise[lecturer_id])
            base_score += expertise_score

        # Workload balancing (-2 to 2 points)
        workload_diff = abs(current_workload - self.target_workload)
        workload_score = 2.0 * (1.0 / (workload_diff + 1))
        base_score += workload_score

        return base_score

    def schedule_defense(self, defense_id, print_details=True):
        """Schedule a single defense with improved workload balancing"""
        defense = self.schedule_df.loc[defense_id]
        role_assignments = {}

        if print_details:
            print(f"\nScheduling Defense {defense_id}:")
            print(f"Field: {defense['bidang']}")
            print(f"Target workload per lecturer: {self.target_workload:.2f}")

        for role in self.roles:
            valid_lecturers = [
                lid for lid, expertise in self.lecturer_expertise.items()
                if defense['bidang'] in expertise
                and lid not in role_assignments.values()
                and self.lecturer_workload[lid] < max(5, self.target_workload * 1.5)
            ]

            if valid_lecturers:
                # Score candidates
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

                if print_details:
                    print(f"\n{role}: Lecturer {selected}")
                    print(f"  Expertise: {self.lecturer_expertise[selected]}")
                    print(f"  New workload: {self.lecturer_workload[selected]}")
                    print(f"  Assignment score: {scores[selected]:.2f}")

        return role_assignments

    def analyze_schedule(self, complete_schedule):
        """Analyze schedule quality"""
        print("\nSchedule Analysis:")

        # Workload statistics
        workload_series = pd.Series(self.lecturer_workload)
        print("\nWorkload Distribution:")
        print(workload_series.describe())

        # Expertise matching
        expertise_matches = 0
        total_assignments = 0
        for defense_id, assignments in complete_schedule.items():
            defense = self.schedule_df.loc[defense_id]
            for role, lecturer_id in assignments.items():
                total_assignments += 1
                if defense['bidang'] in self.lecturer_expertise[lecturer_id]:
                    expertise_matches += 1

        print(f"\nExpertise Matching: {expertise_matches}/{total_assignments} ({expertise_matches/total_assignments*100:.1f}%)")

        # Workload balance score
        workload_std = workload_series.std()
        balance_score = 1.0 / (1.0 + workload_std)
        print(f"Workload Balance Score: {balance_score:.3f} (higher is better)")

    def verify_schedule(self, complete_schedule):
        """Verify the complete schedule for constraints"""
        print("\nVerifying Schedule Constraints:")

        # Check expertise matching
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
                    print(f"Expertise mismatch: Defense {defense_id}, {role}")

                # Time conflict check
                time_conflict = False
                for other_id, other_assignments in complete_schedule.items():
                    if other_id != defense_id:
                        other_defense = self.schedule_df.loc[other_id]
                        if (other_defense['date'] == defense['date'] and
                            other_defense['time'] == defense['time'] and
                            lecturer_id in other_assignments.values()):
                            time_conflicts += 1
                            print(f"Time conflict: Lecturer {lecturer_id} in defenses {defense_id} and {other_id}")

        print(f"\nConstraint Violations:")
        print(f"Expertise mismatches: {expertise_violations}")
        print(f"Time conflicts: {time_conflicts}")

        return expertise_violations == 0 and time_conflicts == 0

# Test the final scheduler
# print("Testing Final Scheduler Implementation:")
# final_scheduler = FinalThesisScheduler(jadwal_df, lecturer_expertise)

# # Schedule all defenses
# complete_schedule = {}
# for defense_id in jadwal_df.index:
#     assignments = final_scheduler.schedule_defense(defense_id)
#     complete_schedule[defense_id] = assignments

# # Analyze final schedule
# final_scheduler.analyze_schedule(complete_schedule)

# # Verify the schedule
# is_valid = final_scheduler.verify_schedule(complete_schedule)
# print(f"\nSchedule is valid: {is_valid}")