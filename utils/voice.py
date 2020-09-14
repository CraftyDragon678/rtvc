import librosa
import soundfile as sf
import numpy as np
from pathlib import Path

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
        data, _ = sf.read(f)
        wav = data.T
        preprocessed_wav = encoder.preprocess_wav(wav)

        return encoder.embed_utterance(preprocessed_wav)
