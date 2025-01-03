import pandas as pd

def load_data(dosen_file_path, jadwal_file_path):
    # Baca data dosen
    dosen_keahlian_df = pd.read_excel(dosen_file_path)
    
    # Baca data jadwal
    jadwal_df = pd.read_excel(jadwal_file_path)
    
    # Buat dictionary expertise dosen
    lecturer_expertise = {}
    for _, row in dosen_keahlian_df.iterrows():
        lecturer_expertise[row['id']] = [field.strip() for field in row['keahlian'].split(',')]
    
    return jadwal_df, lecturer_expertise