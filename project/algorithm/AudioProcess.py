from transformers import WhisperProcessor, WhisperForConditionalGeneration
import torch
import librosa
import noisereduce as nr
from pydub import AudioSegment
import numpy as np
from scipy.signal import resample

class AudioProcessor:
    def __init__(self):
        self.processor = WhisperProcessor.from_pretrained(r"F:\a\apaper\project\project\algorithm\model\whisper-small")
        self.trans_model = WhisperForConditionalGeneration.from_pretrained(r"F:\a\apaper\project\project\algorithm\model\whisper-small")

    # 降噪处理
    def denoise_audio(self, audio, sr):
        # 提取前 1 秒音频作为噪声样本
        noise_sample = audio[:int(sr * 1)]
        denoised_audio = nr.reduce_noise(y=audio, sr=sr, y_noise=noise_sample)
        return denoised_audio

    # 去除静音片段
    def remove_silence(self, audio, sr, threshold=0.01):
        energy = librosa.feature.rms(y=audio)
        non_silent_indices = np.where(energy > threshold)[1]
        start = non_silent_indices.min()
        end = non_silent_indices.max()
        return audio[start:end]

    # 音频增强
    def enhance_audio(self, audio, sr):
        audio_segment = AudioSegment(
            audio.tobytes(),
            frame_rate=sr,
            sample_width=audio.dtype.itemsize,
            channels=1
        )
        # 增加 5dB 音量
        audio_segment = audio_segment + 5
        # 提高音调 20%
        new_frame_rate = int(audio_segment.frame_rate * 1.2)
        audio_segment = audio_segment._spawn(audio_segment.raw_data, overrides={
            "frame_rate": new_frame_rate
        })
        audio_segment = audio_segment.set_frame_rate(sr)
        enhanced_audio = np.array(audio_segment.get_array_of_samples())
        return enhanced_audio

    # 重采样，统一采样率
    def resample_audio(self, audio, sr, target_sr=16000):
        if sr != target_sr:
            duration = len(audio) / sr
            num_samples = int(duration * target_sr)
            resampled_audio = resample(audio, num_samples)
            return resampled_audio
        return audio

    # 音频预处理
    def preprocess_audio(self, audio_path):
        # 加载音频
        audio, sr = librosa.load(audio_path)
        # 降噪
        # audio = self.denoise_audio(audio, sr)
        # 去除静音
        # audio = self.remove_silence(audio, sr)
        # 音频增强
        # audio = self.enhance_audio(audio, sr)
        # 重采样
        audio = self.resample_audio(audio, sr)

        return audio

    # 语音识别
    def transcribe_speech(self, audio_input):
        inputs = self.processor(audio_input, sampling_rate=16000, return_tensors="pt").input_features
        # 将模型和输入数据移动到 GPU（如果可用）
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.trans_model.to(device)
        inputs = inputs.to(device)

        # 生成转录结果
        with torch.no_grad():
            forced_decoder_ids = self.processor.get_decoder_prompt_ids(language="zh", task="transcribe")
            predicted_ids = self.trans_model.generate(inputs, forced_decoder_ids=forced_decoder_ids)

        # 解码输出
        transcription = self.processor.batch_decode(predicted_ids, skip_special_tokens=True)
        print("语音识别结果: ", transcription[0])
        return transcription[0]

    # 提取声学特征
    def analyze_acoustic_features(self, audio, sr):
        # 提取 MFCC 特征
        mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
        # 提取频谱中心频率
        spectral_centroids = librosa.feature.spectral_centroid(y=audio, sr=sr)
        # 提取频谱带宽
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio, sr=sr)
        # 提取频谱平坦度
        spectral_flatness = librosa.feature.spectral_flatness(y=audio)

        return mfccs, spectral_centroids, spectral_bandwidth, spectral_flatness


if __name__ == "__main__":
    
    audio_processor = AudioProcessor()

    # 读取音频文件
    audio_path = r"F:\a\apaper\project\project\algorithm\test_media\common_voice_zh-CN_40975066.mp3"
    pre_audio = audio_processor.preprocess_audio(audio_path)
    trans_result = audio_processor.transcribe_speech(pre_audio)
    print(f"音频数据类型: {pre_audio.dtype}")
    print(f"音频形状: {pre_audio.shape}")
    print(f"音频时长: {len(pre_audio)/16000:.2f} 秒")
    # 特征提取
    audio_input, sampling_rate = librosa.load(audio_path, sr=16000)
    mfccs, spectral_centroids, spectral_bandwidth, spectral_flatness = audio_processor.analyze_acoustic_features(pre_audio, sr=16000)
    # print(mfccs, spectral_centroids, spectral_bandwidth, spectral_flatness)