import ollama

modelname = "phi3"


# Pull the model if it doesn't exist
def on_import():
    try:
        ollama.list(modelname)
    except:
        ollama.pull(modelname)


on_import()


def nl_to_regex(nat_lang_str: str):
    message = f"You generate python compatible regular expressions that are directly used from within python. Your responses are 100% a python regex. Do not output anything that is not a regex string. Do not use code blocks or '`'. The expression to match is: {nat_lang_str}"
    response = ollama.chat(
        model=modelname,
        messages=[
            {
                "role": "user",
                "content": message,
            },
        ],
    )
    return response["message"]["content"].strip()


def regex_to_nl(regex_str: str):
    message = f"You generate a natural language description of a regular expression. Your input is a python regex string. Do not output anything that is not a natural language string. Do not use code blocks or '`'. The regex to describe is: {regex_str}"
    response = ollama.chat(
        model=modelname,
        messages=[
            {
                "role": "user",
                "content": message,
            },
        ],
    )
    return response["message"]["content"].strip()


if __name__ == "__main__":
    natural_language = input("Describe what you would like to match: ")
    print(nl_to_regex(natural_language))
    input()
    regex = input("Enter a regex to describe: ")
    print(regex_to_nl(regex))
    input()
