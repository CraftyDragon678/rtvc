import librosa
import soundfile as sf
from pydub import AudioSegment
import numpy as np
from pathlib import Path
import io

from synthesizer.inference import Synthesizer
from vocoder import inference as vocoder
from encoder import inference as encoder
from werkzeug.datastructures import FileStorage

class TTS():
    def __init__(self):
        encoder.load_model(Path("encoder/saved_models/pretrained.pt"))
        self.synthesizer = Synthesizer(Path("synthesizer/saved_models/logs-pretrained/taco_pretrained"))
        vocoder.load_model(Path("vocoder/saved_models/pretrained/pretrained.pt"))

    def encode(self, f: FileStorage):
        from pydub import AudioSegment
        sound = AudioSegment.from_wav(f)
        sound = sound.set_channels(1)
        sound.export('files.wav', format="wav")
        data, _ = sf.read('files.wav')
        wav = data.T
        preprocessed_wav = encoder.preprocess_wav(wav)

        return encoder.embed_utterance(preprocessed_wav)
    
    def vocode(self, embed, texts, array=False):
        embeds = np.stack([embed] * len(texts))
        specs = self.synthesizer.synthesize_spectrograms(texts, embeds)
        breaks = [spec.shape[1] for spec in specs]
        spec = np.concatenate(specs, axis=1)

        wav = vocoder.infer_waveform(spec)

        b_ends = np.cumsum(np.array(breaks) * Synthesizer.hparams.hop_size)
        b_starts = np.concatenate(([0], b_ends[:-1]))

        wavs = [wav[start:end] for start, end in zip(b_starts, b_ends)]
        breaks = [np.zeros(int(0.15 * Synthesizer.sample_rate))] * len(breaks)

        wav = np.concatenate([i for w, b in zip(wavs, breaks) for i in (w, b)])

        wav = encoder.preprocess_wav(wav)
        if array:
            return wav
        file = io.BytesIO()

        sf.write(file, wav, 16000, format='wav')
        file.seek(0)
        wav = AudioSegment.from_file(file, 'wav')
        file.close()

        file = io.BytesIO()
        wav.export(file)
        file.seek(0)
        return file
