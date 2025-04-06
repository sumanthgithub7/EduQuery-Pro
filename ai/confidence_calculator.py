from typing import List, Dict, Tuple
import numpy as np
from transformers import AutoTokenizer, AutoModel
import torch
import torch.nn.functional as F

class ConfidenceCalculator:
    def __init__(self):
        # Initialize the model and tokenizer for semantic similarity
        self.model_name = "sentence-transformers/all-MiniLM-L6-v2"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModel.from_pretrained(self.model_name)
        
    def _mean_pooling(self, model_output: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
        """Calculate mean pooling of token embeddings"""
        token_embeddings = model_output[0]
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)
    
    def _get_embeddings(self, texts: List[str]) -> torch.Tensor:
        """Get embeddings for a list of texts"""
        encoded_input = self.tokenizer(texts, padding=True, truncation=True, return_tensors='pt')
        with torch.no_grad():
            model_output = self.model(**encoded_input)
        sentence_embeddings = self._mean_pooling(model_output, encoded_input['attention_mask'])
        return F.normalize(sentence_embeddings, p=2, dim=1)
    
    def calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts"""
        embeddings = self._get_embeddings([text1, text2])
        return float(torch.cosine_similarity(embeddings[0], embeddings[1], dim=0))
    
    def calculate_option_distinctiveness(self, options: List[str]) -> List[float]:
        """Calculate how distinct each option is from others"""
        embeddings = self._get_embeddings(options)
        n_options = len(options)
        distinctiveness_scores = []
        
        for i in range(n_options):
            other_similarities = []
            for j in range(n_options):
                if i != j:
                    similarity = float(torch.cosine_similarity(embeddings[i], embeddings[j], dim=0))
                    other_similarities.append(similarity)
            # Higher score means more distinct (less similar to others)
            distinctiveness = 1 - np.mean(other_similarities)
            distinctiveness_scores.append(distinctiveness)
            
        return distinctiveness_scores
    
    def calculate_relevance_to_question(self, question: str, option: str) -> float:
        """Calculate how relevant an option is to the question"""
        similarity = self.calculate_semantic_similarity(question, option)
        # We want some similarity to question but not too much
        # Score peaks at 0.5 similarity and decreases towards 0 and 1
        relevance = 1 - abs(0.5 - similarity)
        return relevance
    
    def calculate_confidence_scores(self, 
                                  question: str,
                                  options: List[str],
                                  correct_answer: str) -> Dict[str, float]:
        """Calculate confidence scores for all options"""
        # Calculate distinctiveness for all options
        distinctiveness_scores = self.calculate_option_distinctiveness(options)
        
        # Calculate confidence scores for each option
        confidence_scores = {}
        for i, option in enumerate(options):
            # Semantic similarity with correct answer (lower is better for distractors)
            semantic_similarity = self.calculate_semantic_similarity(option, correct_answer)
            semantic_score = 1 - semantic_similarity if option != correct_answer else semantic_similarity
            
            # Relevance to question
            relevance_score = self.calculate_relevance_to_question(question, option)
            
            # Distinctiveness from other options
            distinctiveness_score = distinctiveness_scores[i]
            
            # Combine scores with weights
            if option == correct_answer:
                # For correct answer, we want high similarity and relevance
                confidence = 0.4 * semantic_score + 0.4 * relevance_score + 0.2 * distinctiveness_score
            else:
                # For distractors, we want low similarity but high relevance and distinctiveness
                confidence = 0.3 * semantic_score + 0.4 * relevance_score + 0.3 * distinctiveness_score
            
            confidence_scores[option] = float(confidence)
        
        return confidence_scores