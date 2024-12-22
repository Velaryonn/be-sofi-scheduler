from data_preprocessing import load_data
from thesis_defense_environment import ThesisDefenseEnvironment
from thesis_defense_scheduler import ThesisDefenseScheduler
from thesis_panel_scheduler_final import ThesisPanelSchedulerFinal
from final_thesis_scheduler import FinalThesisScheduler
import pandas as pd


def main():
    # Load data
    dosen_file = "data/dosen_keahlian.xlsx"
    jadwal_file = "data/jadwal_sidang.xlsx"
    jadwal_df, lecturer_expertise = load_data(dosen_file, jadwal_file)

    # 1. Run RL-based Defense Scheduler
    print("\n=== Running RL-based Defense Scheduler ===")

    print("Testing RL Environment:")
    env = ThesisDefenseEnvironment(jadwal_df, lecturer_expertise)

    # Test case: Schedule first defense
    test_defense_id = jadwal_df.index[0]
    print(f"\nTesting assignment for defense {test_defense_id}:")
    print("Defense details:", jadwal_df.loc[test_defense_id])

    valid_actions = env.get_valid_actions(test_defense_id)
    print(f"\nValid lecturers for this defense: {len(valid_actions)}")
    print("Sample of valid lecturers:", valid_actions[:5])

    if valid_actions:
        test_lecturer = valid_actions[0]
        new_state, reward, done = env.step(test_defense_id, test_lecturer)
        print(f"\nAssignment result:")
        print(f"Assigned lecturer: {test_lecturer}")
        print(f"Reward: {reward:.2f}")
        print(f"Done: {done}")
        print(f"Remaining defenses: {len(new_state['remaining_defenses'])}")
    
    rl_scheduler = ThesisDefenseScheduler(jadwal_df, lecturer_expertise)
    best_schedule, best_reward = rl_scheduler.schedule_defenses(max_iterations=500)
    analysis = rl_scheduler.analyze_schedule(best_schedule)
    
    # 2. Run Panel Scheduler
    print("\n=== Running Panel Scheduler ===")
    panel_scheduler = ThesisPanelSchedulerFinal(jadwal_df, lecturer_expertise)
    panel_schedule = panel_scheduler.create_schedule()
    
    # Display panel scheduler results
    print("\nPanel Schedule Results:")
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    print(panel_schedule)
    
    # 3. Run Final Thesis Scheduler
    print("\n=== Running Final Thesis Scheduler ===")
    final_scheduler = FinalThesisScheduler(jadwal_df, lecturer_expertise)
    
    # Schedule all defenses
    complete_schedule = {}
    for defense_id in jadwal_df.index:
        assignments = final_scheduler.schedule_defense(defense_id)
        complete_schedule[defense_id] = assignments
    
    # Analyze and verify final schedule
    final_scheduler.analyze_schedule(complete_schedule)
    is_valid = final_scheduler.verify_schedule(complete_schedule)
    print(f"\nFinal Schedule is valid: {is_valid}")

if __name__ == "__main__":
    main()