from species_similarity.similarity import difference_mask


def test_mask_length_matches_input() -> None:
    """The bit-mask length must always equal the sequence length."""
    human = "ACGT"
    other = "TCGT"
    mask = difference_mask(human, other)
    assert len(mask) == len(human)
    assert mask == "1000"
