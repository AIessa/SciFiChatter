class Phrase:

    def __init__(self, i, text, speaker):
        self.i = i  # defines sentence order in original transcript
        self.text = text  # a sentence from the original transcript
        self.speaker = speaker  # original speaker

        # additional:
        self.template = None  # after all normalization
        self.type_vector = None  # binary vector
        self.type_nums = None  # type choices readable
        self.speaker_change_bool = None  # [is_starter, is_ending]

    # BASIC SET-UP ------------------------------------------------
    def setup(self, temp, types, type_nums, speaker_change):
        self.template = temp
        self.type_vector = types
        self.type_nums = type_nums
        self.speaker_change_bool = speaker_change

    # GET COMPONENTS ----------------------------------------------
    def get_i(self):
        return self.i

    def get_text(self):
        return self.text

    def get_speaker(self):
        return self.speaker

    def get_template(self):
        return self.template

    def get_types(self):
        return self.type_vector

    def get_type_nums(self):
        return self.type_nums

    def is_starter(self):
        return self.speaker_change_bool[0]

    def is_ending(self):
        return self.speaker_change_bool[1]
