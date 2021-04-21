import os
import unittest

from hu_nmt.data_augmentator.dependency_graph_wrapper import DependencyGraphWrapper
from hu_nmt.data_augmentator.dependency_parsers.english_dependency_parser import EnglishDependencyParser
from hu_nmt.data_augmentator.utils.data_helpers import get_config_from_yaml

dirname = os.path.dirname(__file__)


class DependencyGraphWrapperTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.config = get_config_from_yaml(os.path.join(dirname, 'resources/configs/en_test_config.yaml'))
        sentence = 'Helen took her dog for a walk in the woods.'
        cls.eng_dep_parser = EnglishDependencyParser()
        graph = cls.eng_dep_parser.sentence_to_dep_parse_tree(sentence)
        cls.dep_graph_wrapper = DependencyGraphWrapper(cls.config, graph)

    def test_get_root(self):
        # Should always return the root node
        actual_root = 'root'
        print(self.dep_graph_wrapper.get_root().split('-')[0])
        assert actual_root == self.dep_graph_wrapper.get_root().split('-')[0]  # strip id from node_name

    def test_get_root_token(self):
        actual_root = 'took'
        assert actual_root == self.dep_graph_wrapper.get_root_token().split('-')[0]  # strip id from node_name

    def test_get_distances_from_root(self):
        actual_distances = {
            'root': 0,
            'took': 1,
            'helen': 2,
            'dog': 2,
            'walk': 2,
            '.': 2,
            'her': 3,
            'for': 3,
            'a': 3,
            'woods': 3,
            'in': 4,
            'the': 4
        }
        distances = self.dep_graph_wrapper.get_distances_from_root()
        stripped_distances = {}
        for key, value in distances.items(): # strip id from node_name
            stripped_distances[key.split('-')[0]] = value
        assert stripped_distances == actual_distances

    def test_get_nodes_with_property(self):
        nouns = self.dep_graph_wrapper.get_nodes_with_property('postag', 'NOUN')
        stripped_nouns = [x.split('-')[0] for x in nouns]
        actual_nouns = ['dog', 'walk', 'woods']
        assert stripped_nouns == actual_nouns

        verbs = self.dep_graph_wrapper.get_nodes_with_property('postag', 'VERB')
        stripped_verbs = [x.split('-')[0] for x in verbs]
        actual_verbs = ['took']
        assert stripped_verbs == actual_verbs

        ad_positions = self.dep_graph_wrapper.get_nodes_with_property('postag', 'ADP')
        stripped_adps = [x.split('-')[0] for x in ad_positions]
        actual_adps = ['for', 'in']
        assert stripped_adps == actual_adps

        punct_positions = self.dep_graph_wrapper.get_nodes_with_property('postag', 'PUNCT')
        stripped_puncts = [x.split('-')[0] for x in punct_positions]
        actual_puncts = ['.']
        assert stripped_puncts == actual_puncts

    def test_get_edges_with_property(self):
        edges_with_property = self.dep_graph_wrapper.get_edges_with_property('dep', 'punct')
        source_node, target_node, edge = edges_with_property[0]
        assert 'took' == source_node.split('-')[0]
        assert '.' == target_node.split('-')[0]
