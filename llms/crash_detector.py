from ollama import Client
import json
import config_llm as config
import time

client = Client(host='10.129.20.4:9090')


def llm_multiple_runs(
    model: str,
    user_message: str,
    out_name: str, 
    outputfolder: str,
    runs: int = 5,
    MAX_RETRIES: int = 5,
    RETRY_DELAY: int = 10,
):
    predictions = []
    output_file = f"{outputfolder}/crash_detection_results_{out_name}.json"
    for i in range(runs):
        print_head_str = f"Predicting {out_name}: {i}th run..."
        print(print_head_str)

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                print(print_head_str + f"Attempt {attempt}...")
                response = client.chat(
                    model=model, 
                    messages=[
                        {"role": "system", "content": config.prompt_instruct},
                        {"role": "user", "content": user_message} # llms somehow cannot recognize system message after sometime
                    ],
                    options=config.param_options
                )
                content = response['message']['content']
                predictions.append(content.strip())
                print(print_head_str + f"Attempt {attempt} succeed.")
                break
            except Exception as e:
                print(print_head_str + f"Attempt {attempt}: LLM call failed with error: {e}")
                if attempt < MAX_RETRIES:
                    print(f"Retrying in {RETRY_DELAY*attempt} seconds...")
                    time.sleep(RETRY_DELAY*attempt)
                else:
                    # print(f"Max retries reached. Skipping {out_name}.")
                    # return
                    print(print_head_str + f"Max retries reached. Attempt {attempt} written as: [Error-skipping].")
                    predictions.append("[Error-skipping]")

    # Save all outputs
    with open(output_file, "w") as f:
        json.dump(predictions, f, indent=2)

    print(f"Predictions by {model} finished {runs} runs, the results are saved in {output_file}.")

# [for detecting if a target cell crash]
def format_for_prompt(data):
    prompt_text = "Executed Cells:\n"

    if data["executed"]:
        # Sort executed cells by execution count
        executed = sorted(data["executed"], key=lambda cell: cell["execution_count"])
        
        # Extract just the code strings
        executed_cells = [cell["code"] for cell in executed]

        for i, code in enumerate(executed_cells, start=1):
            prompt_text += f"Cell {i}:\n{code}\n\n"

    else:
        prompt_text += "No cell has been executed\n"

    # Get the target cell code
    target_cell = data["target"]["code"]

    prompt_text += "Target Cell:\n"
    prompt_text += target_cell

    return prompt_text
