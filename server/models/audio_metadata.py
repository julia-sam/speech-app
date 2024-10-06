from database import db

class AudioMetadata(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text, nullable=True)  # Text for text-to-speech, can be nullable
    recording_path = db.Column(db.Text, nullable=True)  # Audio URL
    waveform_plot_path = db.Column(db.Text, nullable=True)  # URL for waveform image
    pitch_plot_path = db.Column(db.Text, nullable=True)  # URL for pitch plot image
    waveform_data = db.Column(db.Text, nullable=True)  # Base64-encoded waveform data
    pitch_data = db.Column(db.Text, nullable=True)  # Base64-encoded pitch data
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self):
        return f'<AudioMetadata {self.id}>'

