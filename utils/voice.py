import librosa
import soundfile as sf
import numpy as np

from synthesizer.inference import Synthesizer
from vocoder import inference as vocoder
from encoder import inference as encoder

class TTS():
    def __init__(self):
        encoder.load_model("encoder/saved_models/pretrained.pt")
        self.synthesizer = Synthesizer("synthesizer/saved_models/logs-pretrained/taco_pretrained")
        vocoder.load_model("vocoder/saved_models/pretrained/pretrained.pt")
