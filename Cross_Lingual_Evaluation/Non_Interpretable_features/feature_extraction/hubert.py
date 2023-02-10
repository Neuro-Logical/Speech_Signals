hubert_base = '/export/b11/ytsai25/feats/hubert/GITA/'
audio_dir = '/export/b15/afavaro/Frontiers/GITA_NEW_TASKS/All_Recordings_Correct_Naming/'

import os
import numpy as np
import torchaudio

tot = [os.path.join(audio_dir, elem) for elem in os.listdir(audio_dir)]
bundle = torchaudio.pipelines.HUBERT_BASE
model = bundle.get_model()

for audio in tot:
    base = os.path.basename(audio).split(".wav")[0]
    waveform, sample_rate = torchaudio.load(audio)
    waveform = torchaudio.functional.resample(waveform, sample_rate, bundle.sample_rate)
    features, _ = model.extract_features(waveform)

    #save feat from last layer
    numpy_array = features[-1].cpu().detach().numpy()
    output_file = os.path.join(hubert_base, base +".npy")
    print(output_file)
    with open(output_file, 'wb') as f:
        np.save(f, numpy_array)

