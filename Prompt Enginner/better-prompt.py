import spacy
from transformers import TFT5ForConditionalGeneration, T5Tokenizer
import language_tool_python
import tensorflow as tf
import time

# Load tools
nlp = spacy.load("en_core_web_sm")  # English spaCy model
tool = language_tool_python.LanguageTool('en-US')  # English LanguageTool model

# Load TensorFlow models instead of PyTorch
model = TFT5ForConditionalGeneration.from_pretrained('t5-small')
tokenizer = T5Tokenizer.from_pretrained('t5-small', legacy=False)

def refine_prompt(prompt_text, enhancement_type="general"):
    """
    Refines a prompt text to make it more effective for LLM processing.
    
    Parameters:
    - prompt_text: The original user prompt
    - enhancement_type: Type of enhancement to apply (general, creative, technical, academic)
    
    Returns:
    - refined_prompt: The improved prompt
    """
    # Step 1: Fix grammatical errors
    try:
        matches = tool.check(prompt_text)
        corrected_text = language_tool_python.utils.correct(prompt_text, matches)
    except:
        corrected_text = prompt_text  # Fallback if grammar check fails
        print("Grammar check skipped due to an error")
    
    # Step 2: Analyze the text with spaCy for structure improvements
    doc = nlp(corrected_text)
    
    # Check if the prompt is a question and add a question mark if needed
    is_question = any(token.tag_ == "WP" or token.tag_ == "WRB" for token in doc) or doc[0].tag_ == "VB"
    if is_question and not corrected_text.strip().endswith("?"):
        corrected_text = corrected_text.strip() + "?"
    
    # Step 3: Create a task-specific prompt for T5
    if enhancement_type == "creative":
        task_prefix = "Convert to creative writing prompt:"
    elif enhancement_type == "technical":
        task_prefix = "Improve technical clarity of question:"
    elif enhancement_type == "academic":
        task_prefix = "Refine for academic context:"
    else:  # general enhancement
        task_prefix = "Improve this prompt for an AI:"
    
    input_text = f"{task_prefix} {corrected_text}"
    
    # Step 4: Generate enhanced prompt using T5 with TensorFlow
    input_ids = tokenizer(input_text, return_tensors="tf", padding=True, truncation=True, max_length=512).input_ids
    
    # Generate with TensorFlow
    outputs = model.generate(
        input_ids,
        max_length=150,
        num_beams=5,
        temperature=0.7,
        top_k=50,
        top_p=0.95,
        repetition_penalty=1.2,
        early_stopping=True
    )
    
    refined_prompt = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Step 5: Sanity check - ensure we didn't lose the original intent
    if len(refined_prompt) < len(prompt_text) * 0.5:
        print("Warning: Refined prompt seems too short, using corrected original instead")
        return corrected_text
    
    return refined_prompt

def enhance_prompt_structure(prompt_text):
    """
    Adds structural elements to make prompts more effective for LLMs.
    """
    doc = nlp(prompt_text)
    
    # Check if prompt already has clear instructions
    has_instruction = any(token.lemma_ in ["explain", "describe", "analyze", "compare", "create", "write"] 
                         for token in doc)
    
    # If no clear instruction, add structure based on content
    if not has_instruction:
        if any(token.pos_ == "NOUN" for token in doc):
            # Extract key nouns for context
            key_nouns = [token.text for token in doc if token.pos_ == "NOUN"][:3]
            context = ", ".join(key_nouns)
            
            # Determine appropriate verb based on content
            if any(token.lemma_ in ["how", "why", "what"] for token in doc):
                prompt_text = f"Explain in detail about {prompt_text}"
            else:
                prompt_text = f"Provide comprehensive information about {prompt_text}"
    
    return prompt_text

def process_prompt(prompt_text, enhancement_style="general"):
    """
    Complete prompt engineering pipeline.
    """
    print(f"Original prompt: {prompt_text}")
    
    # First apply structural enhancement
    structured_prompt = enhance_prompt_structure(prompt_text)
    print(f"Structurally enhanced: {structured_prompt}")
    
    # Then apply semantic refinement with T5
    final_prompt = refine_prompt(structured_prompt, enhancement_style)
    print(f"Final refined prompt: {final_prompt}")
    
    return final_prompt

# Simpler version focused just on fixing grammar and basic enhancement
def simple_refine_question(question):
    """
    A simpler version that just focuses on grammatical fixes and basic enhancement.
    Use this if the full pipeline is too resource-intensive.
    """
    # Fix grammar
    try:
        matches = tool.check(question)
        corrected = language_tool_python.utils.correct(question, matches)
    except:
        corrected = question
    
    # Basic prefix for T5
    input_text = f"Improve this question: {corrected}"
    
    # Generate with TensorFlow
    input_ids = tokenizer(input_text, return_tensors="tf", padding=True, truncation=True).input_ids
    outputs = model.generate(input_ids, max_length=100)
    refined = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    return refined

# Example usage
if __name__ == "__main__":
    # Test with your example
    test_prompt = "how temperate climate influence agriculture"
    
    # Try the simple version first
    print("Testing simple refinement...")
    simple_refined = simple_refine_question(test_prompt)
    print(f"Simple refinement result: {simple_refined}")
    
    print("\nTesting full refinement pipeline...")
    try:
        full_refined = process_prompt(test_prompt)
        print(f"Full refinement result: {full_refined}")
    except Exception as e:
        print(f"Full pipeline error: {e}")
        print("Consider using the simple_refine_question function instead.")