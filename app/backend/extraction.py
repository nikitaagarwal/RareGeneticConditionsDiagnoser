from collections import defaultdict
import os
import nltk
from nltk import word_tokenize,sent_tokenize
from math import isinf
import ssl

from django.conf import settings
from app.backend.preprocess import load_condition_data

nltk_setup()

def get_phenotypes(input):
	"""
	Identify all nouns or noun phrases from the input text.
	"""

	return ([word for (word, pos) in nltk.pos_tag(nltk.word_tokenize(input))
		     if pos[0] in {'N', 'NN', 'NP'}])


def get_probable_diagnoses(input_phenotypes):
	"""
	Given pheonotypes, determine possible conditions and their associated
	probability range given data from OrphaData.
	"""
	data = load_condition_data()
	# We only need to look at symptoms that we have data for.
	relevant_phenotypes = set(data.keys()).intersection(set(input_phenotypes))
	
	results = dict()

	for phenotype in relevant_phenotypes:
		diseases_info = data[phenotype]
		for (disease, (d_min, d_max)) in diseases_info:
			if disease in results:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    				
				((curr_min, curr_max), curr_count, curr_list) = results[disease]
				results[disease] = ((curr_min+d_min, curr_max+d_max),
					curr_count+1, curr_list+[phenotype])
			else:
				results[disease] = ((d_min, d_max), 1, [phenotype])
	return clean_results(results)


def clean_results(probable_diagnoses):
	"""
	Add results to a list for easier Jinja manipulation, calculate averages for
	min/max (remove count of how many relevant phenotypes associated (and make them %),
	remove any -INF (excluded phenotype seen) entries, and sort on probability range).
	"""
	final_results = list()
	for disease,((curr_min, curr_max), curr_count, curr_list) in probable_diagnoses.items():
		if isinf(curr_min):
			continue
		final_results.append((disease, round((curr_min/curr_count)*100.0), round((curr_max/curr_count)*100.0),
			curr_list))
	return sorted(final_results, key=lambda disease_info: disease_info[2],
		reverse=True)


def nltk_setup():
	"""
	Set up NLTK tagger.
	"""
	try:
	    _create_unverified_https_context = ssl._create_unverified_context
	except AttributeError:
	    pass
	else:
	    ssl._create_default_https_context = _create_unverified_https_context
	nltk.data.path.append(os.path.join(settings.DATA_DIR,'punkt'))
	nltk.download('punkt', download_dir=os.path.join(settings.DATA_DIR,'punkt'), 
		raise_on_error=True)
	nltk.download('averaged_perceptron_tagger',
	download_dir=os.path.join(settings.DATA_DIR,'punkt'), raise_on_error=True)
