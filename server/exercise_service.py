def fetch_exercises_for_category(category_name):
    exercises = [
        {'category': 'The R Sound', 'word_or_phrase': 'red', 'audio_file_path': 'audio/samples/red.mp3'},
        {'category': 'Short I Sound', 'word_or_phrase': 'sit', 'audio_file_path': 'audio/samples/sit.mp3'},
        {'category': 'Long I Sound', 'word_or_phrase': 'seat', 'audio_file_path': 'audio/samples/seat.mp3'},
        {'category': 'Phrase', 'word_or_phrase': 'What kind of car do you want to drive Mr. Foreigner?', 'audio_file_path': 'audio/samples/r_phrase.mp3'},
    ]

    filtered_exercises = [exercise for exercise in exercises if exercise['category'] == category_name]
    return filtered_exercises