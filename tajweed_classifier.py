from collections import deque, namedtuple
from tree import Exemplar, json2tree
import glob
import json
import multiprocessing
import os
import sys
import unicodedata

RangeAttributes = namedtuple("Attributes", "start end attributes")


def attributes_for(rule, txt, i, include_this=True, auxiliary_stream=None):
    # Determine bounds of this letter.
    start_i = i
    while start_i and unicodedata.category(txt[start_i]) == "Mn" and (txt[start_i] != "ٰ" or txt[start_i - 1] == "ـ"):
        start_i -= 1
    end_i = start_i + 1
    while end_i < len(txt) and unicodedata.category(txt[end_i]) == "Mn" and txt[end_i] != "ٰ":
        end_i += 1

    c = txt[i]
    c_ext = txt[start_i:end_i]
    c_base = txt[start_i]

    # Build attributes dict.
    res = {}
    if auxiliary_stream:
        res.update(auxiliary_stream[i])

    if rule == "ghunnah":
        if not include_this:
            res.update({
                "base_is_heavy": c_base in "هءحعخغ",
                "base_is_noon_or_meem": c_base == "ن" or c_base == "م",
                "has_shaddah": "ّ" in c_ext,
                "has_tanween": any(s in c_ext for s in "ًٌٍ"),
            })
        if include_this:
            res.update({
                "is_noon_or_meem": c == "ن" or c == "م",
                "is_initial": i - 1 < 0 or txt[i - 1] == " ",
            })
    elif rule == "hamzat_wasl":
        if include_this:
            res.update({
                "is_alif_waslah": c == "ٱ",
            })
    elif rule == "idghaam_ghunnah":
        if not include_this:
            res.update({
                "base_is_idghaam_ghunna_set": c_base in "يمون",
                "has_implicit_sukoon": not any(s in c_ext for s in "ًٌٍَُِْ"),
            })
        if include_this:
            res.update({
                "is_noon": c == "ن",
                "is_tanween": any(s == c for s in "ًٌٍ"),
                "is_final": end_i >= len(txt) or txt[end_i] == " ",
            })
    elif rule == "idghaam_mutajanisayn":
        if not include_this:
            res.update({
                "base_is_nateeyah_a": c_base in "تط",
                "base_is_nateeyah_b": c_base in "تد",
                "base_is_lathaweeyah_a": c_base in "ثذ",
                "base_is_lathaweeyah_b": c_base in "ظذ",
                "base_is_meem": c_base == "م",
                "base_is_noon": c_base == "ب",
                "has_implicit_sukoon": not any(s in c_ext for s in "ًٌٍَُِْ"),
            })
    elif rule == "idghaam_mutaqaribayn":
        if not include_this:
            res.update({
                "has_implicit_sukoon": not any(s in c_ext for s in "ًٌٍَُِْ"),
                "base_is_qaf_kaf": c_base in "كق",
                "base_is_lam": c_base == "ل",
                "base_is_rah": c_base == "ر",
            })
    elif rule == "idghaam_no_ghunnah":
        if not include_this:
            res.update({
                "has_implicit_sukoon": not any(s in c_ext for s in "ًٌٍَُِْ"),
                "base_is_noon_rah": c_base in "لر",
            })
        if include_this:
            res.update({
                "is_noon": c == "ن",
                "is_tanween": any(s == c for s in "ًٌٍ"),
                "is_final": end_i >= len(txt) or txt[end_i] == " ",
            })
    elif rule == "idghaam_shafawi":
        if not include_this:
            res.update({
                "has_implicit_sukoon": not any(s in c_ext for s in "ًٌٍَُِْ"),
                "base_is_meem": c_base == "م",
            })
    elif rule == "ikhfa":
        if not include_this:
            res.update({
                "has_implicit_sukoon": not any(s in c_ext for s in "ًٌٍَُِْ"),
                "base_is_ikhfa_set": c_base in "تثجدذزسشصضطظفقك",
            })
        if include_this:
            res.update({
                "is_noon": c == "ن",
                "is_high_noon": c == "ۨ",
                "is_tanween": any(s == c for s in "ًٌٍ"),
                "is_final": end_i >= len(txt) or txt[end_i] == " ",
            })
    elif rule == "ikhfa_shafawi":
        if not include_this:
            res.update({
                "has_implicit_sukoon": not any(s in c_ext for s in "ًٌٍَُِْ"),
                "base_is_meem": c_base == "م",
            })
    elif rule == "iqlab":
        if not include_this:
            res.update({
                "has_tanween": any(s in c_ext for s in "ًٌٍ"),
                "has_small_meem": "ۢ" in c_ext or "ۭ" in c_ext,
            })
        if include_this:
            res.update({
                "is_tanween": c in "ًٌٍ",
                "is_base": (unicodedata.category(c) != "Mn" and c != "ـ") or c == "ٰ",
            })
    elif rule == "lam_shamsiyyah":
        if not include_this:
            res.update({
                "has_vowel_incl_tanween": any(s in c_ext for s in "ًٌٍَُِْ"),
                "has_shaddah": "ّ" in c_ext,
            })
        if include_this:
            res.update({
                "is_alif_waslah": c == "ٱ",
                "is_lam": c == "ل",
                "is_allah_word_start": txt[start_i:start_i + 7] in ("للَّهِ ", "للَّهُ ", "للَّهَ "),
            })
    elif rule == "madd_2":
        if not include_this:
            res.update({
                "has_maddah": "ٓ" in c_ext,
                "has_hamza": any(s in c_ext for s in "ؤئٕإأٔ"),
                "has_vowel_incl_tanween": any(s in c_ext for s in "ًٌٍَُِْ"),
                "has_proc_sukoon": "۟" in c_ext or "ْ" in c_ext or not any(s in c_ext for s in "ًٌٍَُِْ"),
                "is_final_letter_in_ayah": end_i >= len(txt),
            })
        if include_this:
            res.update({
                "is_dagger_alif": c == "ٰ",
                "is_small_yeh": c == "ۦ",
                "is_small_waw": c == "ۥ",
                "is_final": end_i >= len(txt) or txt[end_i] == " ",
                })
    elif rule == "madd_246":
        if not include_this:
            res.update({
                "has_maddah": "ٓ" in c_ext,
                "has_fathah": "َ" in c_ext,
                "has_dammah": "ُ" in c_ext,
                "has_kasrah": "ِ" in c_ext,
                "has_vowel_no_tanween": any(s in c_ext for s in "َُِْ"),
                "has_tanween": any(s in c_ext for s in "ًٌٍ"),
            })
        if include_this:
            res.update({
                "is_alif": c == "ا",
                "is_yeh": c == "ي",
                "is_waw": c == "و",
            })
    elif rule == "madd_6":
        if not include_this:
            res.update({
                "has_maddah": "ٓ" in c_ext,
                "has_explicit_sukoon": "۟" in c_ext or "ْ" in c_ext,
                "has_vowel_incl_tanween": any(s in c_ext for s in "ًٌٍَُِْ"),
                "has_shaddah": "ّ" in c_ext,
                "has_hamza": any(s in c_ext for s in "ؤئٕإأٔ"),
                "base_is_alif_maksura": c_base == "ى",
            })
        if include_this:
            res.update({
                "is_hamza": c == "ء",
                "is_base": (unicodedata.category(c) != "Mn" and c != "ـ") or c == "ٰ",
                "is_final": end_i >= len(txt) or txt[end_i] == " ",
            })

    elif rule in ("madd_munfasil", "madd_muttasil"):
        if not include_this:
            res.update({
                "has_maddah": "ٓ" in c_ext,
                "has_explicit_sukoon": "۟" in c_ext or "ْ" in c_ext,
                "has_non_initial_hamza": any(s in c_ext for s in "ؤئٕٔ"),
                "base_is_isolated_hamza": c_base == "ء",
                "has_initial_hamza": any(s in c_ext for s in "ٕإأ"),
                # The following attributes permit this to work without inspecting for maddah(?):
                # "has_implicit_sukoon": not any(s in c_ext for s in "ًٌٍَُِْ"),
                # "has_explicit_sukoon_mod": "۟" in c_ext or "ْ" in c_ext or "۠" in c_ext,
                # "has_fathah": "َ" in c_ext,
                # "has_dammah": "ُ" in c_ext,
                # "has_kasrah": "ِ" in c_ext,
            })
        if include_this:
            res.update({
                "is_base": (unicodedata.category(c) != "Mn" and c != "ـ") or c == "ٰ",
                "is_alif": c == "ا",
                "is_dagger_alif": c == "ٰ",
                "is_alif_maksura": c == "ى",
                "is_final": end_i >= len(txt) or txt[end_i] == " ",
                "is_space": c == " ",
            })
    elif rule == "qalqalah":
        if not include_this:
            res.update({
                "has_explicit_sukoon": "۟" in c_ext or "ْ" in c_ext,
                "has_maddah": "ٓ" in c_ext,
            })
        if include_this:
            res.update({
                "is_muqalqalah": c in "بدجطق",
            })
    elif rule == "silent":
        if not include_this:
            res.update({
                "has_silent_circle": "۟" in c_ext,
                "has_vowel_incl_tanween": any(s in c_ext for s in "ًٌٍَُِْ"),
                "base_is_dagger_alif": c_base == "ٰ",
            })
        if include_this:
            res.update({
                "precedes_high_seen": i + 1 < len(txt) and txt[i + 1] == "ۜ",
                "is_alif": c == "ا",
                "is_alif_maksura": c == "ى",
                "is_waw": c == "و",
                "is_yeh": c == "ي",
            })
    elif rule == "END":
        if not include_this:
            res.update({
                "base_is_space": c_base == " ",
                "has_no_diacritics": start_i + 1 == end_i,
                "has_high_noon": "ۨ" in c_ext,
                "has_explicit_sukoon": "۟" in c_ext or "ْ" in c_ext,
            })
        if include_this:
            res.update({
                "is_base": (unicodedata.category(c) != "Mn" and c != "ـ") or c == "ٰ",
                "is_final_codepoint_in_letter": i + 1 == end_i,
                "is_final_letter_in_ayah": end_i >= len(txt),
            })
    else:
        raise RuntimeError("Unknown rule %s" % rule)

    return RangeAttributes(start_i, end_i, res)


def exemplars_for(rule, txt, auxiliary_stream=None):
    context_size_map = {
        "ghunnah": (3, 1),
        "hamzat_wasl": (1, 0),
        "idghaam_ghunnah": (1, 3),
        "idghaam_mutajanisayn": (0, 2),
        "idghaam_mutaqaribayn": (1, 2),
        "idghaam_no_ghunnah": (0, 3),
        "idghaam_shafawi": (0, 2),
        "ikhfa": (0, 3),
        "ikhfa_shafawi": (0, 2),
        "iqlab": (0, 2),
        "lam_shamsiyyah": (1, 1),
        "madd_2": (0, 1),
        "madd_246": (1, 2),
        "madd_6": (1, 1),
        "madd_munfasil": (1, 2),
        "madd_muttasil": (0, 3),
        "qalqalah": (1, 1),
        "silent": (0, 1),
        "END": (1, 0)
    }
    lookbehind, lookahead = context_size_map[rule]

    # Use a circular buffer to store the letter attributes.
    # We calculate the codepoint attributes - which are slightly different - within the main loop.

    # Pre-fill the buffer with empty data representing the initial lookbehind.
    letter_attr_buffer = deque([RangeAttributes(-1, 0, None) for x in range(lookbehind)],
                               maxlen=lookbehind + 1 + lookahead)
    # Prime with real present-letter & lookahead data.
    for x in range(lookahead + 1):
        start_idx = letter_attr_buffer[-1].end if letter_attr_buffer else 0
        range_attrs = attributes_for(rule,
                                     txt,
                                     start_idx,
                                     include_this=False,
                                     auxiliary_stream=auxiliary_stream)
        letter_attr_buffer.append(range_attrs)
        if range_attrs.end == len(txt):
            break

    # If we ran out of letters before filling the lookahead, top it off.
    for x in range(lookbehind + 1 + lookahead - len(letter_attr_buffer)):
        letter_attr_buffer.append(RangeAttributes(len(txt), len(txt), None))

    for i in range(len(txt)):
        # Advance letter buffer if required.
        if i >= letter_attr_buffer[lookbehind].end:
            if letter_attr_buffer[-1].end == len(txt):
                letter_attr_buffer.append(RangeAttributes(len(txt), len(txt), None))
            else:
                letter_attr_buffer.append(attributes_for(rule,
                                                         txt,
                                                         letter_attr_buffer[-1].end,
                                                         include_this=False,
                                                         auxiliary_stream=auxiliary_stream))
            assert i < letter_attr_buffer[lookbehind].end, "Next letter did not advance"

        # Build final attribute dictionary.
        attr_full = {}
        for off in range(lookbehind + 1 + lookahead):
            if letter_attr_buffer[off].attributes is None:
                attr_full.update({"%d_exists" % (off - lookbehind): False})
            else:
                attr_full.update({"%d_%s" % (off - lookbehind, k): v
                                  for k, v in letter_attr_buffer[off].attributes.items()})
                attr_full.update({"%d_exists" % (off - lookbehind): True})
        attr_full.update({"0_%s" % k: v
                          for k, v in attributes_for(rule,
                                                     txt,
                                                     i,
                                                     include_this=True,
                                                     auxiliary_stream=auxiliary_stream).attributes.items()})

        yield Exemplar(None, attr_full, 1)


def run_tree(tree, exemplar):
    while not hasattr(tree, "label"):
        if exemplar.attributes.get(tree.attribute, -1) >= tree.value:
            tree = tree.gt
        else:
            tree = tree.lt
    return tree.label


def label_ayah(params):
    surah, ayah, text, rule_trees = params  # Multiprocessing...
    # We have to cut out the basmala since it is, in effect, a separate verse.
    # Rules that depend on ayah start/end stop working if it's kept in place.
    # But we remember the offset so we can put everything back where we found it.
    offset = 0
    if surah not in (1, 9) and ayah == 1:
        old_text = text
        text = " ".join(text.split(" ")[4:])
        offset = len(old_text) - len(text)

    # Initialize exemplar generators.
    rules_start_exemplars = {
        k: exemplars_for(k, text) for k in rule_trees
    }
    # All the rules use the same exemplars for making end decisions.
    end_exemplars = exemplars_for("END", text)

    annotations = []
    annotations_run = {k: deque() for k in rule_trees}
    letter_start = 0
    last_letter_start = 0
    for i in range(len(text)):
        end_e = next(end_exemplars)
        # We need some bookkeeping in here for the end-rule trees.
        # I made a one-size-fits-all solution in exemplars_for's auxiliary stream
        # that fits exactly one case - and it's not this one.
        # Also, note that "-1_in_rule" refers to the first character in the letter group.
        # If the rule starts with some harakat in the letter, it will still be false!
        # There is 1 case where this happens: ikhfa on 21:88
        if unicodedata.category(text[i]) != "Mn" or text[i] == "ٰ":
            last_letter_start = letter_start
            letter_start = i
        for k, trees in rule_trees.items():
            e = next(rules_start_exemplars[k])
            if run_tree(trees["start"], e):
                annotations_run[k].append(i)

            # Hax - the exemplars_for auxiliary stream parameter must be random access.
            # So just paste the value we need in here.
            end_e.attributes.update({
                "0_in_rule": len(annotations_run[k]) > 0,
                "-1_in_rule": any(x <= last_letter_start for x in annotations_run[k])
            })

            if run_tree(trees["end"], end_e):
                annotations.append({
                    "rule": k,
                    "start": annotations_run[k].popleft() + offset,
                    "end": i + 1 + offset
                })

    assert all(len(q) == 0 for q in annotations_run.values()), \
        "Some rules left hanging at end of ayah @ %d: %s (%d:%d) %s" % \
        (len(text), annotations_run, surah, ayah, annotations)
    return {
        "surah": surah,
        "ayah": ayah,
        "annotations": sorted(annotations, key=lambda x: x["start"])
    }


if __name__ == "__main__":
    # Load rules from incredibly high-tech datastore.
    rule_trees = {}
    rule_start_files = glob.glob("output/rule_trees/*.start.json")
    for start_file in rule_start_files:
        rule_name = os.path.basename(start_file).partition(".")[0]
        end_file = start_file.replace(".start.", ".end.")
        rule_trees[rule_name] = {
            "start": json2tree(json.load(open(start_file))),
            "end": json2tree(json.load(open(end_file))),
        }

    # Read in text to classify
    tasks = []
    for line in sys.stdin:
        line = line.split("|")
        if len(line) != 3:
            continue
        tasks.append((int(line[0]), int(line[1]), line[2].strip(), rule_trees))

    # Perform classification.
    with multiprocessing.Pool() as p:
        results = p.map(label_ayah, tasks)

    # Pretty-print output because disk space is cheap.
    json.dump(results, sys.stdout, indent=2, sort_keys=True)
    print("")
