from database import db

class AudioMetadata(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text, nullable=True)  
    recording_path = db.Column(db.Text, nullable=True)  
    waveform_plot_path = db.Column(db.Text, nullable=True)  
    pitch_plot_path = db.Column(db.Text, nullable=True)  
    waveform_data = db.Column(db.Text, nullable=True)  
    pitch_data = db.Column(db.Text, nullable=True)  
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self):
        return f'<AudioMetadata {self.id}>'

