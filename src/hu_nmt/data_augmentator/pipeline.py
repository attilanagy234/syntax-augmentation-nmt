from hu_nmt.data_augmentator.dependency_graph_wrapper import DependencyGraphWrapper
from hu_nmt.data_augmentator.dependency_parsers.english_dependency_parser import EnglishDependencyParser
from hu_nmt.data_augmentator.dependency_parsers.hungarian_dependency_parser import HungarianDependencyParser
from hu_nmt.data_augmentator.utils.data_helpers import get_config_from_yaml

if __name__ == '__main__':
    # Test English dependency parser
  #   config = get_config_from_yaml('./configs/example_en_config.yaml')
  #   sentence = 'This is a very colorful rainbow.'
  #   eng_dep_parser = EnglishDependencyParser()
  #   dep_graph = eng_dep_parser.sentence_to_dep_parse_tree(sentence)
  #   eng_dep_graph_wrapper = DependencyGraphWrapper(config, dep_graph)
  #   eng_dep_graph_wrapper.display_graph()

    # Test Hungarian dependency parser
    config = get_config_from_yaml('./configs/example_en_config.yaml')
    sentence = 'Ez egy nagyon színes szivárvány.'
    emtsv_output_file_path = '/Users/attilanagy/Personal/hu-nmt/src/hu_nmt/test/resources/emtsv/hun_output.txt'
    hun_dep_parser = HungarianDependencyParser(emtsv_output_file_path)
    dep_graphs = hun_dep_parser.sentence_batch_to_dep_parse_trees()
    for dep_graph in dep_graphs:
        hun_dep_graph_wrapper = DependencyGraphWrapper(config, dep_graph)
        hun_dep_graph_wrapper.display_graph()
