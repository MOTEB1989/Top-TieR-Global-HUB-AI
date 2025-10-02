from lexhub import connect_ai, connect_dataset
ai = connect_ai("OpenAI", model="gpt-5")
ds = connect_dataset("huggingface://imdb")
print(ai.infer("Hello LexCode!"))
print(ds.head())
