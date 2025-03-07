import numpy as np
import pytest

from spikeinterface.extractors import MEArecRecordingExtractor
from spikeinterface import download_dataset


from spikeinterface.sortingcomponents.peak_pipeline import run_node_pipeline, PeakRetriever, ExtractDenseWaveforms
from spikeinterface.sortingcomponents.waveforms.neural_network_denoiser import SingleChannelToyDenoiser


def test_single_channel_toy_denoiser_in_peak_pipeline(mearec_recording, detected_peaks, chunk_executor_kwargs):
    recording = mearec_recording
    peaks = detected_peaks

    ms_before = 2.0
    ms_after = 2.0
    waveform_extraction = ExtractDenseWaveforms(recording, ms_before=ms_before, ms_after=ms_after, return_output=True)

    # Build nodes for computation
    peak_retriever = PeakRetriever(recording, peaks)
    waveform_extraction = ExtractDenseWaveforms(
        recording, parents=[peak_retriever], ms_before=ms_before, ms_after=ms_after, return_output=True
    )
    toy_denoiser = SingleChannelToyDenoiser(recording, parents=[peak_retriever, waveform_extraction])

    nodes = [peak_retriever, waveform_extraction, toy_denoiser]
    waveforms, denoised_waveforms = run_node_pipeline(recording, nodes=nodes, job_kwargs=chunk_executor_kwargs)

    assert waveforms.shape == denoised_waveforms.shape
