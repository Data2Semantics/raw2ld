# Description of `linker.py` output
=author=
	Rinke HOekstra
=date=
	21 November 2012


# Base Indices
## Normalized index
The normalized index is found in files with names similar to e.g. `drug_normalized.pickle` or `diag_normalized.pickle` (depending on the configuration specified in `linker.yaml`)

The index maps **original** URIs of resources to **normalized** URIs. 

The index is a dictionary where an **original** label is the key, and the corresponding **normalized** label is the value.

This index only contains entries for queries that have the `normalize` attribute set to true in the `linker.yaml` configuration file.

The `normalize` method of `linker.py` does the following things:

* Remove substrings of numbers between slashes (e.g. `/123456/`)
* Replace unnecessary characters (e.g. backslashes, circonflex) with spaces
* Add spaces after commas
* Remove trailing commas
* Replace multiple spaces with a single space
* Remove empty brackets
* Remove spaces after/before brackets
* Replace block brackets with normal brackets
* Add spaces between facing brackets (`)(`)
* Add missing brackets
* Remove duplicate words
* Remove partial duplicate words that were cut off at the end of the label
* Remove trailing spaces

## Label index
The label index is found in files with names similar to e.g. `drug_label_index.pickle`.

The index maps **normalized** labels to **original** labels. The **normalized** label can map to *multiple* original labels.

The index is a dictionary where a **normalized** label is the key, and the value is a *set* of corresponding **original** labels.

## Exact index
The exact index is found in files with names similar to e.g. `drug_exact.pickle`.

The index maps **normalized** labels to **normalized URI**s. 

The index is a dictionary that corresponds to the label index, only the value of the dictionary is a *set* of **URI**s that were minted on the basis of the normalized label.

**NOTE**: For queries where the results are not normalized, the **normalized** URI and label will correspond to the **original** label. This means that this index is the trick that allows us to find more matches between resources from multiple repositories. 

## URI index
The URI index is found in files with names similar to e.g. `drug_uri_index.pickle`.

The index maps **normalized URI**s to **normalized** labels.

The index is dictionary where a **normalized** URI is the key, and the value is a *set* of corresponding **normalized** labels.

**NOTE**: For queries where the results are not normalized, the **normalized** URI and label will correspond to the **original** label. Many resources have multiple labels. 

# Extended Indices

## Related index
The related index is found in files with names similar to e.g. `drug_related.pickle`.

The index maps **normalized URI**s to **normalized URI**s based on whether the normalized labels of the URIs are the same (i.e. labels in the *URI index* are compared to labels in the *exact index*, the URIs in the exact index for that label are added to the *related index*). If a match is found, the newly related URI's are again used to retrieve all labels for those URIs (from the *URI index*), and any additional URIs from the *exact index* for those labels are also added to the *related index*.

The index is a dictionary where a **normalized** URI is the key, and the value is a *set* of corresponding **normalized** URIs.

## Broader index
The broader index is found in files with names similar to e.g. `drug_broader.pickle`.

The index maps **normalized URI**s to **normalized URI**s based on whether parts of their normalized labels overlap (on a word-by-word basis). Normalized labels are taken from the *exact index*, split into words, and sequentially concatenated (to a maximum of 4 words) to form new labels, which are tested against the *exact index*. If a match is found, the URIs found for the constructed partial label are added as as values for the original URI in the *broader index*.

The index is a dictionary wher a **normalized** URI is the key, and the value is a *set* of corresponding **normalized** URIs of which the labels overlap, but are shorter than the labels of the key URI.



