### NOTE: This project is not actively maintained
Please consider using the [Quran.com API](https://quran.api-docs.io/v4/quran/get-uthmani-script-of-ayah) instead.

# quran-tajweed

<img src="http://i.imgur.com/vGYW7ZY.png" width="323"/>


Tajweed annotations for the Qur'an (riwayat hafs). The data is available as a JSON file with exact character indices for each rule, and as individual decision trees for each rule.

You can use this data to display the Qur'an with tajweed highlighting, refine models for Qur'anic speech recognition, or - if you enjoy decision trees - improve your own recitation.

The following tajweed rules are supported:

* Ghunnah (`ghunnah`)
* Idghaam...
  * With Ghunnah (`idghaam_ghunnah`)
  * Without Ghunnah (`idghaam_no_ghunnah`)
  * Mutajaanisain (`idghaam_mutajaanisain`)
  * Mutaqaaribain (`idghaam_mutaqaaribain`)
  * Shafawi (`idghaam_shafawi`)
* Ikhfa...
  * Ikhfa (`ikhfa`)
  * Ikhfa Shafawi (`ikhfa_shafawi`)
* Iqlab (`iqlab`)
* Madd...
  * Regular: 2 harakat (`madd_2`)
  * al-Aarid/al-Leen: 2, 4, 6 harakat (`madd_246`)
  * al-Muttasil: 4, 5 harakat (`madd_muttasil`)
  * al-Munfasil: 4, 5 harakat (`madd_munfasil`)
  * Laazim: 6 harakat (`madd_6`)
* Qalqalah (`qalqalah`)
* Hamzat al-Wasl (`hamzat_wasl`)
* Lam al-Shamsiyyah (`lam_shamsiyyah`)
* Silent (`silent`)

This project was built using information from [ReciteQuran.com](http://recitequran.com), the [Dar al-Maarifah](http://tajweedquran.com) tajweed masaahif, and others.

## Using the tajweed JSON file

All the data you probably need is in `output/tajweed.hafs.uthmani-pause-sajdah.json`. It has the following schema:

    [
        {
            "surah": 1,
            "ayah": 1,
            "annotations": [
                {
                    "rule": "madd_6",
                    "start": 245,
                    "end": 247
                },
                ...
            ]
        },
        ...
    ]

The `start` and `end` indices of each annotation refer to the Unicode codepoint (not byte!) offset within the [Tanzil.net](http://tanzil.net/download) Uthmani Qur'an text. **NOTE:** that the encoding of the files available from Tanzil.net has changed slightly since the annotations were generated, so please use this copy of the Qur'an text file: [quran-uthmani.txt](https://github.com/cpfair/quran-tajweed/files/7281388/quran-uthmani.txt) (downloaded ca. Apr 6, 2017). If you use a different Qur'an text file, you must rebuild the data file from scratch (at your own risk) - refer to the next section.

This data file is licensed under a [Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/), while the original Tanzil.net text file linked above is made available under the [Tanzil.net terms of use](https://tanzil.net/download/).

## Using the decision trees

`tajweed_classifier.py` is a script that takes [Tanzil.net](http://tanzil.net/download) "Text (with aya numbers)"-style input via STDIN, and produces the tajweed JSON file (as described above) via STDOUT. It reads the decision trees from `rule_trees/*.json`. Note that the trees have been built to function best with the Madani text; they rely on the prescence of pronunciation markers (e.g. maddah) that may not be present in other texts.

## Ruleset reference

The following are renderings of the decision trees used to determine where each tajweed annotation starts and stops. Attributes are grouped by the letters they belong to, a letter being defined as a base character (e.g. ل) plus any diacritics that follow (codepoints in the `Mn` category). Superscript/dagger alif is counted as a base character. The numbers prefixing each attribute indicate which letter the attribute belongs to: negative referring to previous letters, positive to future letters. Attributes starting with `0_...` refer to the exact character being considered. Annotations do not always start or stop on letter boundaries. Refer to `tajweed_classifier.py` for the definition of each attribute.

### ghunnah
|Start |End|
|:------------:|:----------------:|
|<img alt="ghunnah start decision tree" src="/output/rule_tree_images/ghunnah.start.png" height="250"/> | <img alt="ghunnah end decision tree" src="/output/rule_tree_images/ghunnah.end.png" height="250"/>|

### hamzat_wasl
|Start |End|
|:------------:|:----------------:|
<img alt="hamzat_wasl start decision tree" src="/output/rule_tree_images/hamzat_wasl.start.png" height="250"/>|<img alt="hamzat_wasl end decision tree" src="/output/rule_tree_images/hamzat_wasl.end.png" height="176"/>

### idghaam_ghunnah
|Start |End|
|:------------:|:----------------:|
<img alt="idghaam_ghunnah start decision tree" src="/output/rule_tree_images/idghaam_ghunnah.start.png" height="250"/>|<img alt="idghaam_ghunnah end decision tree" src="/output/rule_tree_images/idghaam_ghunnah.end.png" height="250"/>

### idghaam_mutajanisayn
|Start |End|
|:------------:|:----------------:|
<img alt="idghaam_mutajanisayn start decision tree" src="/output/rule_tree_images/idghaam_mutajanisayn.start.png" height="250"/>|<img alt="idghaam_mutajanisayn end decision tree" src="/output/rule_tree_images/idghaam_mutajanisayn.end.png" height="176"/>

### idghaam_mutaqaribayn
|Start |End|
|:------------:|:----------------:|
<img alt="idghaam_mutaqaribayn start decision tree" src="/output/rule_tree_images/idghaam_mutaqaribayn.start.png" height="250"/>|<img alt="idghaam_mutaqaribayn end decision tree" src="/output/rule_tree_images/idghaam_mutaqaribayn.end.png" height="176"/>

### idghaam_no_ghunnah
|Start |End|
|:------------:|:----------------:|
<img alt="idghaam_no_ghunnah start decision tree" src="/output/rule_tree_images/idghaam_no_ghunnah.start.png" height="250"/>|<img alt="idghaam_no_ghunnah end decision tree" src="/output/rule_tree_images/idghaam_no_ghunnah.end.png" height="250"/>

### idghaam_shafawi
|Start |End|
|:------------:|:----------------:|
<img alt="idghaam_shafawi start decision tree" src="/output/rule_tree_images/idghaam_shafawi.start.png" height="250"/>|<img alt="idghaam_shafawi end decision tree" src="/output/rule_tree_images/idghaam_shafawi.end.png" height="250"/>

### ikhfa
|Start |End|
|:------------:|:----------------:|
<img alt="ikhfa start decision tree" src="/output/rule_tree_images/ikhfa.start.png" height="250"/>|<img alt="ikhfa end decision tree" src="/output/rule_tree_images/ikhfa.end.png" height="250"/>

### ikhfa_shafawi
|Start |End|
|:------------:|:----------------:|
<img alt="ikhfa_shafawi start decision tree" src="/output/rule_tree_images/ikhfa_shafawi.start.png" height="250"/>|<img alt="ikhfa_shafawi end decision tree" src="/output/rule_tree_images/ikhfa_shafawi.end.png" height="250"/>

### iqlab
|Start |End|
|:------------:|:----------------:|
<img alt="iqlab start decision tree" src="/output/rule_tree_images/iqlab.start.png" height="250"/>|<img alt="iqlab end decision tree" src="/output/rule_tree_images/iqlab.end.png" height="250"/>

### lam_shamsiyyah
|Start |End|
|:------------:|:----------------:|
<img alt="lam_shamsiyyah start decision tree" src="/output/rule_tree_images/lam_shamsiyyah.start.png" height="250"/>|<img alt="lam_shamsiyyah end decision tree" src="/output/rule_tree_images/lam_shamsiyyah.end.png" height="176"/>

### madd_2
|Start |End|
|:------------:|:----------------:|
<img alt="madd_2 start decision tree" src="/output/rule_tree_images/madd_2.start.png" height="250"/>|<img alt="madd_2 end decision tree" src="/output/rule_tree_images/madd_2.end.png" height="176"/>

### madd_246
|Start |End|
|:------------:|:----------------:|
<img alt="madd_246 start decision tree" src="/output/rule_tree_images/madd_246.start.png" height="250"/>|<img alt="madd_246 end decision tree" src="/output/rule_tree_images/madd_246.end.png" height="176"/>

### madd_6
|Start |End|
|:------------:|:----------------:|
<img alt="madd_6 start decision tree" src="/output/rule_tree_images/madd_6.start.png" height="250"/>|<img alt="madd_6 end decision tree" src="/output/rule_tree_images/madd_6.end.png" height="250"/>

### madd_munfasil
|Start |End|
|:------------:|:----------------:|
<img alt="madd_munfasil start decision tree" src="/output/rule_tree_images/madd_munfasil.start.png" height="250"/>|<img alt="madd_munfasil end decision tree" src="/output/rule_tree_images/madd_munfasil.end.png" height="250"/>

### madd_muttasil
|Start |End|
|:------------:|:----------------:|
<img alt="madd_muttasil start decision tree" src="/output/rule_tree_images/madd_muttasil.start.png" height="250"/>|<img alt="madd_muttasil end decision tree" src="/output/rule_tree_images/madd_muttasil.end.png" height="250"/>

### qalqalah
|Start |End|
|:------------:|:----------------:|
<img alt="qalqalah start decision tree" src="/output/rule_tree_images/qalqalah.start.png" height="250"/>|<img alt="qalqalah end decision tree" src="/output/rule_tree_images/qalqalah.end.png" height="250"/>

### silent
|Start |End|
|:------------:|:----------------:|
<img alt="silent start decision tree" src="/output/rule_tree_images/silent.start.png" height="250"/>|<img alt="silent end decision tree" src="/output/rule_tree_images/silent.end.png" height="250"/>


