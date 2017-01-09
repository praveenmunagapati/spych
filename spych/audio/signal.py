import numpy as np
import scipy.io.wavfile


def calculate_energy_of_samples(samples):
    values = np.abs(samples).astype(np.int)

    if type(values) == list:
        values = np.array(values)

    return np.sum(np.power(values, 2)) / values.size


def add_noise_to_signal(signal, noise, snr=None):
    added_noise = np.copy(noise)

    if snr is not None:
        signal_energy = calculate_energy_of_samples(signal)
        noise_energy = calculate_energy_of_samples(noise)

        current_ratio = signal_energy / noise_energy
        target_ratio = np.power(10, (snr / 10.0))

        noise_scaler = np.sqrt(current_ratio / target_ratio)
        added_noise = added_noise * noise_scaler

    return (signal * 0.5 + added_noise * 0.5).astype(signal.dtype)


def add_random_noise_to_signal(signal, snr=None):
    noise = np.random.normal(0, 1, signal.size)
    max_amp = np.iinfo(signal.dtype).max
    noise = (noise / np.max(np.abs(noise))) * max_amp
    noise = noise.astype(signal.dtype)

    return add_noise_to_signal(signal, noise, snr=snr)


def add_noise_to_wav(signal_path, noise_path, output_path, snr=None):
    signal_sampling_rate, signal_samples = scipy.io.wavfile.read(signal_path)
    noise_sampling_rate, noise_samples = scipy.io.wavfile.read(noise_path)

    if signal_sampling_rate != noise_sampling_rate:
        raise ValueError("Signal and noise have different sampling rates. ({} - {})".format(signal_sampling_rate, noise_sampling_rate))

    if noise_samples.size > signal_samples.size:
        max_start_index = noise_samples.size - signal_samples.size
        start_index = np.random.randint(max_start_index + 1)
        noise_samples = noise_samples[start_index:start_index + signal_samples.size]

    if noise_samples.size < signal_samples.size:
        noise_samples_extended = noise_samples.copy()

        while noise_samples_extended.size < signal_samples.size:
            max_to_add = signal_samples.size - noise_samples_extended.size

            noise_samples_extended = np.concatenate([noise_samples_extended, noise_samples[:max_to_add]])

        noise_samples = noise_samples_extended

    output_samples = add_noise_to_signal(signal_samples, noise_samples, snr=snr)
    scipy.io.wavfile.write(output_path, signal_sampling_rate, output_samples)


def add_random_noise_to_wav(wav_path, output_path, snr=None):
    sampling_rate, samples = scipy.io.wavfile.read(wav_path)
    new_samples = add_random_noise_to_signal(samples, snr=snr)
    scipy.io.wavfile.write(output_path, sampling_rate, new_samples)
