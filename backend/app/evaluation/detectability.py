from typing import Any, Dict

from datasets import Dataset

from app.watermarks import WatermarkBase


def evaluation_detectability(watermark: WatermarkBase, dataset: Dataset) -> Dict[
	str, Any]:
	true_positives = 0  # Watermark detected in watermarked text
	false_positives = 0  # Watermark detected in natural text (should be negative)
	true_negatives = 0  # No watermark detected in natural text
	false_negatives = 0  # No watermark detected in watermarked text
	
	total_examples = len(dataset)
	
	for example in dataset:
		prompt = example['prompt']
		natural_text = example['natural_text']
		
		# Generate watermarked text using the prompt
		watermarked_text = watermark.embed(prompt)
		
		# Detect watermark in the watermarked text
		watermarked_detection = watermark.detect(watermarked_text)
		
		# Detect watermark in the natural text (should not have a watermark)
		natural_detection = watermark.detect(natural_text)
		
		# Check watermarked text detection results
		if watermarked_detection['detected']:
			true_positives += 1
		else:
			false_negatives += 1
		
		# Check natural text detection results
		if not natural_detection['detected']:
			true_negatives += 1
		else:
			false_positives += 1
	
	# Calculate standard classification metrics
	accuracy = (true_positives + true_negatives) / (total_examples * 2)
	precision = true_positives / (true_positives + false_positives) if (
				                                                                   true_positives + false_positives) > 0 else 0
	recall = true_positives / (true_positives + false_negatives) if (
				                                                                true_positives + false_negatives) > 0 else 0
	f1_score = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
	
	# Calculate error rates
	fpr = false_positives / (false_positives + true_negatives) if (
				                                                              false_positives + true_negatives) > 0 else 0
	fnr = false_negatives / (false_negatives + true_positives) if (
				                                                              false_negatives + true_positives) > 0 else 0
	
	# Compile all metrics into result dictionary
	results = {
		"accuracy": accuracy,
		"precision": precision,
		"recall": recall,
		"f1_score": f1_score,
		"false_positive_rate": fpr,
		"false_negative_rate": fnr,
		"true_positives": true_positives,
		"false_positives": false_positives,
		"true_negatives": true_negatives,
		"false_negatives": false_negatives,
		"total_examples": total_examples
	}
	
	return results
