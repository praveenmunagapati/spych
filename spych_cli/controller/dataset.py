from cement.core import controller

from spych.data import dataset
from spych.data import dataset_validation
from spych.data import dataset_fixing
from spych.data.converter import kaldi


class DatasetController(controller.CementBaseController):
    class Meta:
        label = 'dataset'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = "Working with datasets."

        arguments = [
            (['path'],
             dict(action='store', help='path to dataset'))
        ]

    @controller.expose(hide=True)
    def default(self):
        self.app.args.print_help()

    @controller.expose(help="Print information about a given dataset.")
    def info(self):
        dset = dataset.Dataset.load_from_path(self.app.pargs.path)

        info_data = {
            "name": dset.name(),
            "path": dset.path,
            "num_utterances": len(dset.utterances),
            "num_wavs": len(dset.wavs),
            "num_speakers": len(dset.all_speakers())
        }

        self.app.render(info_data, 'dataset_info.mustache')

    @controller.expose(help="Create an empty dataset.")
    def new(self):
        dset = dataset.Dataset(self.app.pargs.path)
        dset.save()


class DatasetMergeController(controller.CementBaseController):
    class Meta:
        label = 'merge'
        stacked_on = 'dataset'
        stacked_type = 'nested'
        description = "Merge two datasets."

        arguments = [
            (['path'], dict(action='store', help='path to target dataset')),
            (['merge_path'], dict(action='store', help='path to dataset to merge into target dataset')),
            (['--copy-wavs'], dict(action='store_true', help='Also copy the audio files to the target dataset folder.'))
        ]

    @controller.expose(hide=True)
    def default(self):
        target = dataset.Dataset.load_from_path(self.app.pargs.path)
        merge = dataset.Dataset.load_from_path(self.app.pargs.merge_path)
        target.merge_dataset(merge, copy_wavs=self.app.pargs.copy_wavs)
        target.save()


class DatasetValidationController(controller.CementBaseController):
    class Meta:
        label = 'validate'
        stacked_on = 'dataset'
        stacked_type = 'nested'
        description = "Validate a dataset and print results."

        arguments = [
            (['path'], dict(action='store', help='path to dataset')),
            (['--details'], dict(action='store_true', help='Show details.'))
        ]

    @controller.expose(hide=True)
    def default(self):
        dset = dataset.Dataset.load_from_path(self.app.pargs.path)

        validator = dataset_validation.DatasetValidation(dset)
        validator.run_all_checks()

        info_data = {
            "name": dset.name(),
            "num_missing_wavs": len(validator.missing_wavs),
            "num_empty_wavs": len(validator.empty_wavs),
            "num_wavs_with_wrong_format": len(validator.wavs_with_wrong_format),
            "num_wavs_without_utterances": len(validator.wavs_without_utterances),
            "num_utterances_with_missing_wav_id": len(validator.utterances_with_missing_wav_id),
            "num_utterances_with_invalid_start_end": len(validator.utterances_with_invalid_start_end),
            "num_missing_empty_transcriptions": len(validator.missing_empty_transcriptions),
            "num_missing_empty_speakers": len(validator.missing_empty_speakers),
            "num_missing_empty_genders": len(validator.missing_empty_genders),
            "num_invalid_utt_ids_in_utt2spk": len(validator.invalid_utt_ids_in_utt2spk)
        }

        if self.app.pargs.details:
            info_data["details"] = True
            info_data["missing_wavs"] = validator.missing_wavs
            info_data["empty_wavs"] = validator.empty_wavs
            info_data["wavs_with_wrong_format"] = validator.wavs_with_wrong_format
            info_data["wavs_without_utterances"] = validator.wavs_without_utterances
            info_data["utterances_with_missing_wav_id"] = validator.utterances_with_missing_wav_id
            info_data["utterances_with_invalid_start_end"] = validator.utterances_with_invalid_start_end
            info_data["missing_empty_transcriptions"] = validator.missing_empty_transcriptions
            info_data["missing_empty_speakers"] = validator.missing_empty_speakers
            info_data["missing_empty_genders"] = validator.missing_empty_genders
            info_data["invalid_utt_ids_in_utt2spk"] = validator.invalid_utt_ids_in_utt2spk

        self.app.render(info_data, 'dataset_validation.mustache')


class DatasetFixController(controller.CementBaseController):
    class Meta:
        label = 'fix'
        stacked_on = 'dataset'
        stacked_type = 'nested'
        description = "Fix a dataset."

        arguments = [
            (['path'], dict(action='store', help='path to dataset'))
        ]

    @controller.expose(hide=True)
    def default(self):
        dset = dataset.Dataset.load_from_path(self.app.pargs.path)
        fixer = dataset_fixing.DatasetFixer(dset)

        fixer.fix()

        print('Done')


class DatasetExportController(controller.CementBaseController):
    class Meta:
        label = 'export'
        stacked_on = 'dataset'
        stacked_type = 'nested'
        description = "Export a dataset to another format."

        arguments = [
            (['path'], dict(action='store', help='path to dataset to export')),
            (['out'], dict(action='store', help='path to export the dataset to.')),
            (['format'], dict(action='store', help='format (kaldi)', choices=['kaldi'])),
            (['--copy-wavs'], dict(action='store_true', help='Also copy the audio files to the out folder.'))
        ]

    @controller.expose(hide=True)
    def default(self):
        dset = dataset.Dataset.load_from_path(self.app.pargs.path)

        target_path = self.app.pargs.out
        target_format = self.app.pargs.format

        if target_format == 'kaldi':
            print('Exporting:')
            print('From: {}'.format(dset.path))
            print('To: {}'.format(target_path))
            print('Format: {}'.format(target_format))

            exporter = kaldi.KaldiExporter(target_path, dset, copy_wavs=self.app.pargs.copy_wavs)
            exporter.run()

        else:
            print('Format {} not supported'.format(target_format))

        print('Done')