import json
import os
from collections import defaultdict
from enum import Enum

from hu_nmt.data_augmentator.preprocessor.preprocessor import Preprocessor
from hu_nmt.data_augmentator.utils.logger import get_logger

log = get_logger(__name__)


class DropOutType(Enum):
    WRONG_SRC_LANGUAGE = 'WRONG_SRC_LANGUAGE'
    WRONG_TGT_LANGUAGE = 'WRONG_TGT_LANGUAGE'
    EMPTY_SRC_SENT = 'EMPTY_SRC_SENT'
    EMPTY_TGT_SENT = 'EMPTY_TGT_SENT'
    WRONG_RATIO = 'WRONG_RATIO'
    LONG_SRC_SENT = 'LONG_SRC_SENT'
    LONG_TGT_SENT = 'LONG_TGT_SENT'


class PreprocessorWithDropoutStat(Preprocessor):

    def __init__(self, source_data_path: str, target_data_path: str, config_path: str, source_output_path: str,
                 target_output_path: str, dep_tree_output_path: str = None):
        self.drop_out_stats = defaultdict(lambda: 0)
        super().__init__(source_data_path, target_data_path, config_path, source_output_path, target_output_path,
                         dep_tree_output_path)

    def preprocess_and_precompute(self):
        log.info('Starting preprocessing...')

        self.skip_batches = self._find_num_of_preprocessed_batches()
        if self.skip_batches > 0:
            log.info(f'Found previous run, skipping {self.skip_batches} batches and continuing preprocessing.')

        number_of_lines_saved_to_file = 0
        all_lines = 0
        file_idx = self.skip_batches + 1

        preprocess_output_path = os.path.dirname(self._source_output_path)
        if not os.path.exists(preprocess_output_path):
            os.makedirs(preprocess_output_path)

        line_batch_generator = self._get_file_line_batch_generator(self._source_data_path, self._target_data_path,
                                                                   self._config.preprocessor.batch_size)

        self._init_models()
        for line_batch in line_batch_generator:
            result_batch = self._filter_batch(line_batch)

            self.write_preprocessed_sentences_to_files(result_batch, file_idx)
            file_idx += 1
            number_of_lines_saved_to_file += len(result_batch.src_sents)
            all_lines += len(line_batch)

        log.info(
            f'Finished processing sentences. Number of sentences before and after: {all_lines} -> {number_of_lines_saved_to_file}')

        with open('drop_out_stat.json', 'w') as f:
            json.dump(dict(self.drop_out_stats), f)

    def is_correct_language(self, source_sentence, target_sentence) -> bool:
        correct_src = self.langdetect.predict(source_sentence) == self._config.preprocessor.source_language
        correct_tgt = self.langdetect.predict(target_sentence) == self._config.preprocessor.target_language
        if not correct_src:
            self.drop_out_stats[str(DropOutType.WRONG_SRC_LANGUAGE)] += 1
            return False
        elif not correct_tgt:
            self.drop_out_stats[str(DropOutType.WRONG_TGT_LANGUAGE)] += 1
            return False
        return True

    def is_good_length(self, source_word_count, target_word_count) -> bool:
        src_good_word_count = self._is_good_word_count(source_word_count)
        tgt_good_word_count = self._is_good_word_count(target_word_count)
        good_ratio = self._is_good_ratio(source_word_count, target_word_count)

        if not src_good_word_count:
            self.drop_out_stats[str(DropOutType.LONG_SRC_SENT)] += 1
            return False
        elif not tgt_good_word_count:
            self.drop_out_stats[str(DropOutType.LONG_TGT_SENT)] += 1
            return False
        elif not good_ratio:
            self.drop_out_stats[str(DropOutType.WRONG_RATIO)] += 1
            return False
