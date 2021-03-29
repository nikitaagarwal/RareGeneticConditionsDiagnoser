#!/usr/bin/env python
from collections import defaultdict
import json
import math
import os
from pathlib import Path
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import fromstring, ElementTree

from django.conf import settings


DATA = os.path.join(settings.DATA_DIR, 'disorder_data.json')


def load_condition_data():
	"""
	If we've already serialized the data, we can use the existing json data to
	get the condition info dict.
	"""
	if Path(DATA).is_file():
		print("Found file.")
		with open(DATA) as data_file:
			return json.load(data_file)
	
	# Doesn't exist. Need to preprocess data.
	with open(os.path.join(settings.DATA_DIR,'en_product4.xml'), 'r', encoding='utf-8',
             errors='ignore') as f:
		data = f.read()

	freq_dict = {
		# Obligate is 99% instead of 100%, because 100% probability is misleading.
		# Existence of a symtpom does not imply existence of the condition for the
		# use case we are supporting.
		'Obligate (100%)' : (99.0, 99.0),
		'Very frequent (99-80%)' : (0.8, 0.99),
		'Frequent (79-30%)' : (0.3, 0.79),
		'Occasional (29-5%)' : (0.05, 0.29),
		'Very rare (<4-1%)' : (0.01, 0.04),
		'Excluded (0%)' : (-math.inf, -math.inf)
	}

	# Symptom -> [(disease, freq of symp in disease), ...]
	disorder_data_dict = defaultdict(list)

	tree = ElementTree(ET.fromstring(data))
	disorders = tree.find("HPODisorderSetStatusList")
	for e in disorders.findall("HPODisorderSetStatus"):
		disorder = e.find("Disorder")
		disorder_name = disorder.find("Name").text

		all_associations = disorder.find("HPODisorderAssociationList")
		for a in all_associations.findall("HPODisorderAssociation"):
			hpo = a.find("HPO")
			phenotype = hpo.find("HPOTerm").text

			HPOFreq = a.find("HPOFrequency")
			frequency = HPOFreq.find("Name").text
			freq_range = freq_dict[frequency]

			disorder_data_dict[phenotype.lower()].append((disorder_name, freq_range))

	# Serialize to JSON and save for future use.
	with open(DATA, 'w') as fp:
		json.dump(disorder_data_dict, fp)
	return disorder_data_dict
