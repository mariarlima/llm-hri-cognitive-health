import openai

# Set your OpenAI API key
openai.api_key = 'sk-proj-PMNk7FSF5feoVctz8mpET3BlbkFJdOLU8yIgzpo4nfpPpxtf'

# Function to call OpenAI API with adjustable hyperparameters
def generate_response(prompt, model="gpt-4o", temperature=0.7, max_tokens=150, top_p=1.0, frequency_penalty=0.0, presence_penalty=0.0):
    try:
        response = openai.Completion.create(
            model=model,
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"An error occurred: {e}"

# Example usage
if __name__ == "__main__":
    prompt = "Once upon a time"
    response = generate_response(prompt)
    print(response)