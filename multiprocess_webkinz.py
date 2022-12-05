import re
import pyautogui
import multiprocess_imaging
import time
from threading import Thread
from multiprocessing import Pool


class Graph:
    def __init__(self, letters_list):
        self.nodes: list[list[Node], ...] = [[] for _ in range(len(letters_list))]
        # print(self.nodes)
        self.string_nodes = [[] for _ in range(len(letters_list))]
        for idx in range(len(letters_list)):
            for jdx in range(len(letters_list[idx])):
                node = Node(letters_list[idx][jdx])
                self.string_nodes[idx].append(node.to_string())
                self.nodes[idx].append(node)
        # print(self.nodes)
        # print(self.string_nodes)
        for idx in range(len(self.nodes)):
            for jdx in range(len(self.nodes[idx])):
                curr_node = self.nodes[idx][jdx]
                # left column
                if idx != 0:
                    if idx%2 == 0:
                        curr_node.neighbors("up_left", self.nodes[idx-1][jdx])
                        curr_node.neighbors("down_left", self.nodes[idx-1][jdx+1])
                    else:
                        if jdx != 0:
                            curr_node.neighbors("up_left", self.nodes[idx-1][jdx-1])
                        if jdx != len(letters_list[idx])-1:
                            curr_node.neighbors("down_left", self.nodes[idx-1][jdx])

                # same column
                if jdx != 0:
                    curr_node.neighbors("up", self.nodes[idx][jdx-1])
                if jdx != len(letters_list[idx])-1:
                    curr_node.neighbors("down", self.nodes[idx][jdx+1])

                # right column
                if idx != len(letters_list)-1:
                    if idx%2 == 0:
                        curr_node.neighbors("up_right", self.nodes[idx+1][jdx])
                        curr_node.neighbors("down_right", self.nodes[idx+1][jdx+1])
                    else:
                        if jdx != 0:
                            curr_node.neighbors("up_right", self.nodes[idx+1][jdx-1])
                        if jdx != len(letters_list[idx])-1:
                            curr_node.neighbors("down_right", self.nodes[idx+1][jdx])

    def to_string(self):
        return self.string_nodes


class Node:
    def __init__(self, letter: str):
        self.letter = letter
        if letter == 'q':
            self.letter = 'qu'
        self.directions: dict[str: Node] = {
            'up': None,
            'up_left': None,
            'down_left': None,
            'down': None,
            'down_right': None,
            'up_right': None
        }
        self.visited: bool = False

    def neighbors(self, direction: str, node):
        self.directions[direction] = node

    def to_string(self):
        return self.letter

    def visual(self):
        return ("  " + self.check("up") + "  "
                + "\n" + self.check("up_left") + "   " + self.check("up_right")
                + "\n  " + self.letter + "  "
                + "\n" + self.check("down_left") + "   " + self.check("down_right")
                + "\n  " + self.check("down"))

    def check(self, direction):
        if self.directions[direction] is None:
            return " "
        return self.directions[direction].to_string()


def get_input() -> list[str]:
    return [input(f"Type column {str(idx+1)}:") for idx in range(7)]


def get_word_list():
    path = "really_big_wordlist.txt"  # took 7:35 minutes
    path = "webkinz_wordlist.txt"
    with open(path, encoding="utf8") as input_file:
        words = sorted(
            set(line.rstrip("\n").lower() for line in input_file)
        )
    return words


def generate_words(graph) -> list[list[str]]:
    # get all the words and return as list of list
    max_length = 8
    min_length = 3
    all_possible_words = [[] for _ in range(max_length-min_length+1)]
    accepted_words = get_word_list()
    params = []
    for curr_column in graph.nodes:
        for curr_node in curr_column:  # make words from every letter
            curr_string = curr_node.letter
            curr_path = [curr_node]
            pattern = re.compile(fr"^{curr_string}")
            args = (curr_node, curr_string, curr_path, accepted_words, pattern, min_length, max_length)
            params.append(args)

    with Pool() as pool:
        words = pool.starmap(recurse, params)  # words is a list[list[list[str]]] because from each letter's list
    for letter_list in words:
        for word_by_len_idx in range(len(letter_list)):
            all_possible_words[word_by_len_idx].extend(letter_list[word_by_len_idx])
    return all_possible_words


# finds all possible words from each letter
def recurse(curr_node: Node,
            curr_string: str,
            curr_path: list[Node],
            accepted_words: list[str],
            pattern,  # : Pattern[str],
            min_length: int,
            max_length: int
            ):

    possible_words = [[] for _ in range(max_length-min_length+1)]
    # return if len(curr_string) >= max_length
    if len(curr_string) > max_length:
        return possible_words

    # return if there are no matches
    # if it's an exact match, store it in possible words
    # if there's a match but not the end of string, recurse again
    if len(curr_string) >= min_length:
        match = False
        for word in accepted_words:
            if pattern.search(word):
                match = True
                if word == curr_string:
                    # add to possible_words at the length
                    possible_words[len(word)-min_length].append(word)
                    # can I add a break here?
            # returning if there are no possible words with this current string
        if not match:
            return possible_words

    # recurse on all directions if it exists
    for direction in curr_node.directions.values():
        if direction:
            if direction not in curr_path:
                new_string = curr_string + direction.letter
                curr_path.append(direction)
                pattern = re.compile(fr"^{new_string}")
                found_words = recurse(direction, new_string, curr_path, accepted_words, pattern, min_length, max_length)
                for idx in range(len(possible_words)):
                    possible_words[idx].extend(found_words[idx])
                curr_path.remove(direction)
    return possible_words


def editable_input(text):
    time.sleep(0.2)
    pyautogui.click(870, 800)
    time.sleep(0.2)
    Thread(target=write, args=(str(text),)).start()
    modified_input = input("Make any necessary changes:\n")
    modified_input = modified_input[2:-2].split('\', \'')
    return modified_input


def write(text):
    time.sleep(0.3)
    pyautogui.write(text)


def game():
    alt_tab()
    g_input = multiprocess_imaging.get_board()
    alt_tab()
    #g_input = editable_input(g_input)

    # g_input = ['oeotdos', 'edwuuftm', 'mzoylep', 'tlsvwhal', 'euaesbp', 'lkwlldss', 'yoapyre']
    # g_input = ['adikfyc', 'ahfpyvfv', 'oedwlcs', 'gauflaec', 'yupndki', 'osnvabui', 'rdehpgk']
    graph = Graph(g_input)
    word_list = generate_words(graph)
    final_list = []  # [] for _ in range(len(word_list))]
    for idx in range(len(word_list)-1, -1, -1):
        sort = sorted(set(word_list[idx]))
        final_list.append(sort)
    for idx in range(len(final_list)):
        print(f"Words of length {8-idx}:" +
              f"\n{final_list[idx]}")


def alt_tab():
    pyautogui.hotkey('alt', 'tab')


if __name__ == '__main__':
    # ['orancah', 'duokikfl', 'qefqhws', 'npsettce', 'necrtli', 'nmogsehp', 'zeyhsne']
    test_input = ['orangah', 'duokekfl', 'qefqhws', 'npsettce', 'necrtli', 'nmogsehp', 'zeyhsne']

    start_time = time.time()
    game()
    print(f"Time: {time.time() - start_time}")







