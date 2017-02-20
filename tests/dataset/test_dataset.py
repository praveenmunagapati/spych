import unittest
import tempfile
import shutil
import os

from spych.dataset import dataset


class DatasetTest(unittest.TestCase):
    def setUp(self):
        self.dataset_path = tempfile.mkdtemp()

        self.dataset = dataset.Dataset(self.dataset_path)

        self.wav_1_path = os.path.join(os.path.dirname(__file__), 'spych_ds/wav_1.wav')
        self.wav_2_path = os.path.join(os.path.dirname(__file__), 'spych_ds/wav_2.wav')
        self.wav_3_path = os.path.join(os.path.dirname(__file__), 'spych_ds/wav_3.wav')
        self.wav_4_path = os.path.join(os.path.dirname(__file__), 'spych_ds/wav_4.wav')

        self.file_1 = self.dataset.add_file(self.wav_1_path)
        self.file_2 = self.dataset.add_file(self.wav_2_path)
        self.file_3 = self.dataset.add_file(self.wav_3_path)
        self.file_4 = self.dataset.add_file(self.wav_4_path)

        self.speaker_1 = self.dataset.add_speaker()
        self.speaker_2 = self.dataset.add_speaker()
        self.speaker_3 = self.dataset.add_speaker()

        self.utt_1 = self.dataset.add_utterance(self.file_1.idx, speaker_idx=self.speaker_1.idx)
        self.utt_2 = self.dataset.add_utterance(self.file_2.idx, speaker_idx=self.speaker_1.idx)
        self.utt_3 = self.dataset.add_utterance(self.file_3.idx, speaker_idx=self.speaker_2.idx, start=0, end=15)
        self.utt_4 = self.dataset.add_utterance(self.file_3.idx, speaker_idx=self.speaker_2.idx, start=15, end=25)
        self.utt_5 = self.dataset.add_utterance(self.file_4.idx, speaker_idx=self.speaker_3.idx)

        self.segm_1 = self.dataset.add_segmentation(self.utt_1.idx, segments='who am i')
        self.segm_2 = self.dataset.add_segmentation(self.utt_2.idx, segments='who are you')
        self.segm_3 = self.dataset.add_segmentation(self.utt_3.idx, segments='who is he')
        self.segm_4 = self.dataset.add_segmentation(self.utt_4.idx, segments='who are they')
        self.segm_5 = self.dataset.add_segmentation(self.utt_5.idx, segments='who is she')

    def tearDown(self):
        shutil.rmtree(self.dataset_path, ignore_errors=True)

    def test_name(self):
        self.assertEqual(os.path.basename(self.dataset_path), self.dataset.name)

    #
    #   File
    #

    def test_add_file(self):
        file_obj = self.dataset.add_file(self.wav_1_path)

        self.assertEqual(os.path.relpath(self.wav_1_path, self.dataset_path), file_obj.path)
        self.assertIsNotNone(file_obj.idx)
        self.assertEqual(file_obj, self.dataset.files[file_obj.idx])

    def test_add_file_with_id(self):
        file_obj = self.dataset.add_file(self.wav_1_path, file_idx='file_id_1')

        self.assertEqual(os.path.relpath(self.wav_1_path, self.dataset_path), file_obj.path)
        self.assertEqual('file_id_1', file_obj.idx)
        self.assertEqual(file_obj, self.dataset.files[file_obj.idx])

    def test_add_file_with_copy(self):
        file_obj = self.dataset.add_file(self.wav_1_path, copy_file=True)

        self.assertEqual('wav_1.wav', file_obj.path)
        self.assertIsNotNone(file_obj.idx)
        self.assertEqual(file_obj, self.dataset.files[file_obj.idx])

    def test_remove_files(self):
        self.dataset.remove_files([self.file_1.idx, self.file_3.idx])

        self.assertNotIn(self.file_1.idx, self.dataset.files)
        self.assertNotIn(self.file_3.idx, self.dataset.files)

        self.assertNotIn(self.utt_1.idx, self.dataset.utterances)
        self.assertNotIn(self.utt_3.idx, self.dataset.utterances)
        self.assertNotIn(self.utt_4.idx, self.dataset.utterances)

        self.assertNotIn(self.utt_1.idx, self.dataset.segmentations)
        self.assertNotIn(self.utt_3.idx, self.dataset.segmentations)
        self.assertNotIn(self.utt_4.idx, self.dataset.segmentations)

    #
    #   Utterance
    #

    def test_utterances_in_file(self):
        self.assertSetEqual(set([self.utt_3, self.utt_4]), self.dataset.utterances_in_file(self.file_3.idx))

    def test_utterances_of_speaker(self):
        self.assertEqual(set([self.utt_3, self.utt_4]), self.dataset.utterances_of_speaker(self.speaker_2.idx))

    def test_add_utterance(self):
        utt_obj = self.dataset.add_utterance(self.file_3.idx)

        self.assertEqual(self.file_3.idx, utt_obj.file_idx)
        self.assertEqual(utt_obj, self.dataset.utterances[utt_obj.idx])

    def test_remove_utterances(self):
        self.dataset.remove_utterances([self.utt_2.idx, self.utt_5.idx])

        self.assertNotIn(self.utt_2.idx, self.dataset.utterances)
        self.assertNotIn(self.utt_5.idx, self.dataset.utterances)

        self.assertNotIn(self.utt_2.idx, self.dataset.segmentations)
        self.assertNotIn(self.utt_5.idx, self.dataset.segmentations)

    #
    #   Speaker
    #

    def test_num_speakers(self):
        self.assertEqual(3, self.dataset.num_speakers)

    def test_add_speaker(self):
        spk_obj = self.dataset.add_speaker()

        self.assertIsNotNone(spk_obj.idx)
        self.assertEqual(spk_obj, self.dataset.speakers[spk_obj.idx])

    #
    #   Segmentation
    #

    def test_add_segmentation(self):
        file_path = os.path.join(os.path.dirname(__file__), 'wav_1.wav')
        file_obj = self.dataset.add_file(file_path)

        utt_obj = self.dataset.add_utterance(file_obj.idx)

        seg_obj = self.dataset.add_segmentation(utt_obj.idx, segments='who am i')

        self.assertEqual(utt_obj.idx, seg_obj.utterance_idx)
        self.assertEqual('text', seg_obj.key)
        self.assertEqual(3, len(seg_obj.segments))

        self.assertEqual(seg_obj, self.dataset.segmentations[utt_obj.idx][seg_obj.key])

    #
    #   Div
    #

    def test_import_dataset(self):
        imp_dataset_path = tempfile.mkdtemp()

        imp_dataset = dataset.Dataset(imp_dataset_path)

        imp_wav_1_path = os.path.join(os.path.dirname(__file__), 'spych_ds/wav_1.wav')
        imp_wav_2_path = os.path.join(os.path.dirname(__file__), 'spych_ds/wav_2.wav')
        imp_wav_3_path = os.path.join(os.path.dirname(__file__), 'spych_ds/wav_3.wav')
        imp_wav_4_path = os.path.join(os.path.dirname(__file__), 'spych_ds/wav_4.wav')

        imp_file_1 = imp_dataset.add_file(imp_wav_1_path)
        imp_file_2 = imp_dataset.add_file(imp_wav_2_path)
        imp_file_3 = imp_dataset.add_file(imp_wav_3_path)
        imp_file_4 = imp_dataset.add_file(imp_wav_4_path)

        imp_speaker_1 = imp_dataset.add_speaker()
        imp_speaker_2 = imp_dataset.add_speaker()

        imp_utt_1 = imp_dataset.add_utterance(imp_file_1.idx, speaker_idx=imp_speaker_1.idx)
        imp_utt_2 = imp_dataset.add_utterance(imp_file_2.idx, speaker_idx=imp_speaker_1.idx)
        imp_utt_3 = imp_dataset.add_utterance(imp_file_3.idx, speaker_idx=imp_speaker_2.idx, start=0, end=4)
        imp_utt_4 = imp_dataset.add_utterance(imp_file_3.idx, speaker_idx=imp_speaker_2.idx, start=4, end=17)
        imp_utt_5 = imp_dataset.add_utterance(imp_file_4.idx, speaker_idx=imp_speaker_2.idx)

        imp_segm_1 = imp_dataset.add_segmentation(imp_utt_1.idx, segments='what am i')
        imp_segm_2 = imp_dataset.add_segmentation(imp_utt_2.idx, segments='what are you')
        imp_segm_3 = imp_dataset.add_segmentation(imp_utt_3.idx, segments='what is he')
        imp_segm_4 = imp_dataset.add_segmentation(imp_utt_4.idx, segments='what are they')
        imp_segm_5 = imp_dataset.add_segmentation(imp_utt_5.idx, segments='what is she')

        self.dataset.import_dataset(imp_dataset, copy_files=True)

        self.assertEqual(8, self.dataset.num_files)
        self.assertEqual(5, self.dataset.num_speakers)
        self.assertEqual(10, self.dataset.num_utterances)
        self.assertEqual(10, len(self.dataset.segmentations))

        self.assertEqual(4, len(os.listdir(self.dataset_path)))

        shutil.rmtree(imp_dataset_path, ignore_errors=True)