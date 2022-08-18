from sacremoses import MosesPunctNormalizer

from hu_nmt.data_augmentator.dependency_parsers.dependency_parser_factory import DependencyParserFactory
from hu_nmt.data_augmentator.preprocessor.language_detector import LanguageDetector
from hu_nmt.data_augmentator.utils.data_helpers import get_config_from_yaml
from hu_nmt.data_augmentator.utils.logger import get_logger

log = get_logger(__name__)


class Preprocessor:
    """
    Receives the entire dataset and returns a preprocessed subsample to augment
    based on predefined criteria
    """

    def __init__(self, source_data_path: str, target_data_path: str, config_path: str, source_output_path: str,
                 target_output_path: str):
        self._source_data_path = source_data_path
        self._target_data_path = target_data_path
        self._config = get_config_from_yaml(config_path)
        self._source_output_path = source_output_path
        self._target_output_path = target_output_path
        self.langdetect = LanguageDetector(self._config.preprocessor.langdetect_model_path)
        self.moses_punct_normalizer_src = MosesPunctNormalizer(lang=self._config.preprocessor.source_language)
        self.moses_punct_normalizer_tgt = MosesPunctNormalizer(lang=self._config.preprocessor.target_language)
        self.source_tokenizer = DependencyParserFactory.get_tokenizer(self._config.preprocessor.source_language)
        self.target_tokenizer = DependencyParserFactory.get_tokenizer(self._config.preprocessor.target_language)

    def preprocess(self):
        log.info('Starting preprocessing...')
        number_of_lines_saved_to_file = 0
        with open(self._source_data_path) as source_file, \
                open(self._target_data_path) as target_file, \
                open(self._source_output_path, 'w') as source_output_file, \
                open(self._target_output_path, 'w') as target_output_file:

            for i, (source_line, target_line) in enumerate(zip(source_file, target_file)):
                source_sentence, target_sentence = source_line.strip(), target_line.strip()
                source_sentence = self.clean_sentence(source_sentence)
                source_sentence = self.moses_punct_normalizer_src.normalize(source_sentence)

                target_sentence = self.clean_sentence(target_sentence)
                target_sentence = self.moses_punct_normalizer_src.normalize(target_sentence)

                if self.is_good_length(source_sentence, target_sentence) and self.is_correct_language(source_sentence,
                                                                                                      target_sentence):
                    source_output_file.write(source_sentence + '\n')
                    target_output_file.write(target_sentence + '\n')

                    number_of_lines_saved_to_file += 1

        log.info(
            f'Finished processing sentences. Number of sentences before and after: {i + 1} -> {number_of_lines_saved_to_file}')

    def is_good_length(self, source_sentence, target_sentence) -> bool:
        source_doc = self.source_tokenizer.tokenize(source_sentence)
        target_doc = self.target_tokenizer.tokenize(target_sentence)
        source_word_count = self.source_tokenizer.count_words(source_doc)
        target_word_count = self.target_tokenizer.count_words(target_doc)

        return self._is_good_word_count(source_word_count) and self._is_good_word_count(target_word_count) and \
            self._is_good_ratio(source_word_count, target_word_count) and self._contains_one_sentence(source_doc,
                                                                                                      target_doc)

    def is_correct_language(self, source_sentence, target_sentence) -> bool:
        return (self.langdetect.predict(source_sentence) == self._config.preprocessor.source_language) and \
               (self.langdetect.predict(target_sentence) == self._config.preprocessor.target_language)

    def _contains_one_sentence(self, source_doc, target_doc) -> bool:
        source_sentence_count = self.source_tokenizer.count_sentences(source_doc)
        target_sentence_count = self.target_tokenizer.count_sentences(target_doc)
        return source_sentence_count == target_sentence_count == 1

    def _is_good_word_count(self, length):
        return (length > self._config.preprocessor.total_wordcount_min) and \
               (length < self._config.preprocessor.total_wordcount_max)

    def _is_good_ratio(self, source_len, target_len):
        return (abs(source_len - target_len) < self._config.preprocessor.wordcount_diff) or \
               (
                       (source_len / target_len < self._config.preprocessor.wordcount_ratio_threshold) and
                       (target_len / source_len < self._config.preprocessor.wordcount_ratio_threshold)
               )

    def clean_sentence(self, sentence):
        sentence = sentence.replace('\xad', '-')  # replace soft hyphens with normal hyphens
        copy = ""
        while copy != sentence:
            copy = sentence
            # lots of sentences start and end with unnecessary double quotes
            if sentence.startswith('"') and sentence.endswith('"'):
                sentence = sentence[1:-1]
            if sentence.startswith("'") and sentence.endswith("'"):
                sentence = sentence[1:-1]
            if sentence.startswith("`") and sentence.endswith("`"):
                sentence = sentence[1:-1]

            if sentence.count("'") == 1 and (sentence.strip().startswith("'") or sentence.strip().endswith("'")):
                sentence = sentence.replace("'", "")
            if sentence.count('"') == 1 and (sentence.strip().startswith('"') or sentence.strip().endswith('"')):
                sentence = sentence.replace('"', "")
            if sentence.count('`') == 1 and (sentence.strip().startswith("`") or sentence.strip().endswith("`")):
                sentence = sentence.replace('`', "")

            if sentence.startswith('-'):
                sentence = sentence[1:]
        return sentence
