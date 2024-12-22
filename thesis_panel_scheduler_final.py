import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import math

class ThesisPanelSchedulerFinal:
    def __init__(self, schedule_df, lecturer_expertise):
        self.schedule_df = schedule_df.copy()
        self.lecturer_expertise = lecturer_expertise
        self.lecturer_workload = {lid: {'total': 0, 'examiner': 0, 'supervisor': 0,
                                      'daily_assignments': {}}
                                for lid in lecturer_expertise.keys()}
        #self.MAX_WORKLOAD = 3
        self.MIN_TIME_GAP = pd.Timedelta(hours=2)
        self.MAX_WORKLOAD = math.ceil((len(schedule_df) * 4) / len(lecturer_expertise))


    def is_lecturer_available(self, lecturer_id, date, time, assigned_lecturers):
        """Check if lecturer is available for assignment"""
        # Already assigned to this session
        if lecturer_id in assigned_lecturers:
            return False

        # Check daily workload
        daily_count = self.lecturer_workload[lecturer_id]['daily_assignments'].get(date, 0)
        if daily_count >= 2:
            return False

        # Check total workload
        if self.lecturer_workload[lecturer_id]['total'] >= self.MAX_WORKLOAD:
            return False

        return True

    def assign_panel(self, defense):
        """Assign all panel members for a defense"""
        date, time = defense['date'], defense['time']
        field = defense['bidang']
        assigned_lecturers = []
        panel = {}

        # First, find qualified lecturers for this field
        qualified_lecturers = [(lid, expertise) for lid, expertise in self.lecturer_expertise.items()
                             if field in expertise]

        # Sort by current workload (ascending)
        qualified_lecturers.sort(key=lambda x: self.lecturer_workload[x[0]]['total'])

        roles = ['penguji1_id', 'penguji2_id', 'pembimbing1_id', 'pembimbing2_id']
        for role in roles:
            available_lecturers = [
                lid for lid, _ in qualified_lecturers
                if self.is_lecturer_available(lid, date, time, assigned_lecturers)
            ]

            if available_lecturers:
                # Select lecturer with lowest workload
                selected_id = available_lecturers[0]
                panel[role] = selected_id
                assigned_lecturers.append(selected_id)

                # Update workload
                self.lecturer_workload[selected_id]['total'] += 1
                if 'penguji' in role:
                    self.lecturer_workload[selected_id]['examiner'] += 1
                else:
                    self.lecturer_workload[selected_id]['supervisor'] += 1

                if date not in self.lecturer_workload[selected_id]['daily_assignments']:
                    self.lecturer_workload[selected_id]['daily_assignments'][date] = 0
                self.lecturer_workload[selected_id]['daily_assignments'][date] += 1
            else:
                print(f"Warning: No available lecturer for {role} in defense {defense.name}")
                panel[role] = None

        return panel

    def create_schedule(self):
        """Create complete schedule"""
        schedule_data = []

        # Sort defenses by date and time
        sorted_defenses = self.schedule_df.sort_values(['date', 'time'])

        for idx, defense in sorted_defenses.iterrows():
            print(f"\nScheduling defense {idx}")
            print(f"Date: {defense['date']}, Time: {defense['time']}")
            print(f"Field: {defense['bidang']}")

            panel = self.assign_panel(defense)

            schedule_data.append({
                'tanggal': defense['date'],
                'waktu': defense['time'],
                'ruang': defense['ruang'],
                'mahasiswa_id': defense['mahasiswa_id'],
                'judul': defense['judul'],
                'bidang': defense['bidang'],
                **panel
            })

            # Print assignment details
            for role, lid in panel.items():
                if lid:
                    print(f"{role}: Lecturer {lid} "
                          f"(total: {self.lecturer_workload[lid]['total']})")

        return pd.DataFrame(schedule_data)

# Create and run the final scheduler
# print("Creating Final Schedule...")
# final_scheduler = ThesisPanelSchedulerFinal(jadwal_df, lecturer_expertise)
# final_schedule = final_scheduler.create_schedule()

# # Display results
# print("\nFinal Schedule:")
# pd.set_option('display.max_columns', None)
# pd.set_option('display.max_rows', None)
# print(final_schedule)

# print("\nWorkload Statistics:")
# workload_df = pd.DataFrame.from_dict(final_scheduler.lecturer_workload,
#                                     orient='index')
# print(workload_df[['total', 'examiner', 'supervisor']].describe())