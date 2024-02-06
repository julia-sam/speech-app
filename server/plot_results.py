import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt
import numpy as np
from transcribe_and_analyze import transcribe_audio, analyze_pitch

def plot_results(audio_segment, waveform_plot_path, pitch_plot_path):
    print("Plotting results...")

    # Attempt to transcribe the audio
    try:
        transcription, _ = transcribe_audio(audio_segment)
    except Exception as e:
        print(f"Error in transcription: {e}")
        transcription = "Transcription Unavailable"

    # Extract data from the audio segment for waveform plot
    samples = np.array(audio_segment.get_array_of_samples())
    duration = len(samples) / audio_segment.frame_rate
    time = np.linspace(0., duration, len(samples))
    
    # Plot the audio waveform
    plt.figure()
    plt.plot(time, samples)
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.title("Waveform for: " + transcription)
    plt.savefig(waveform_plot_path)
    plt.close()
    print("Waveform plot saved.")

    # Plot the pitch data
    try:
        time_values, pitch_values = analyze_pitch(audio_segment)
        plt.figure()
        plt.plot(time_values, pitch_values, 'o', markersize=5, color='blue')
        plt.title("Pitch Over Time for: " + transcription)
        plt.xlabel("Time (s)")
        plt.ylabel("Pitch (Hz)")
        plt.grid(True)
        plt.savefig(pitch_plot_path)
        plt.close()
        print("Pitch plot saved.")
    except Exception as e:
        print(f"Error in pitch analysis: {e}")

    return {
        'waveform_plot_path': waveform_plot_path,
        'pitch_plot_path': pitch_plot_path,
        'transcription': transcription
    }
