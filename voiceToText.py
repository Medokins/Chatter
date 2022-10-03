import pyaudio
import wave
import os

def record_data(length):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100

    p = pyaudio.PyAudio()

    stream = p.open(format = FORMAT,
                    channels = CHANNELS,
                    rate = RATE,
                    input = True,
                    frames_per_buffer = CHUNK)

    print("started recording")
    frames = []
    for _ in range(0, int(RATE/CHUNK * length) + 1):
        data = stream.read(CHUNK)
        frames.append(data)

    print("stopped recording")
    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(os.path.join("voice_samples", "sample.wav"), "wb")
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()