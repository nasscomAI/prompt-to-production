"""
UC-0A — Complaint Classifier
Uses agents.md + skills.md to run a prompt-based classifier over CSV rows.
"""
import argparse
import csv
import json
import logging
import os

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)

AGENTS_SYSTEM_PROMPT = (
    "Expert Civic Data Classifier. Convert unstructured citizen complaints into structured municipal issue records "
    "under strict taxonomy and severity rules. Respond only with a JSON object containing keys: category, priority, reason, flag."
)

DEFAULT_CRAFT_TEMPLATE = (
    "Context: You are a UC-0A Complaint Classifier. Use README rules as the supreme source: categories exactly "
    "Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other. "
    "Priorities are exactly Urgent, Standard, Low. Severity keywords force Urgent.\n"
    "Role: Expert Civic Data Classifier.\n"
    "Action: Analyze {complaint_text} and return structured classification.\n"
    "Format: Produce only raw JSON text with keys category, priority, reason, flag. Do not use markdown code fences or any extra prose.\n"
    "Target: {complaint_text}"
)


def load_craft_prompt_template(skills_path: str = "skills.md") -> str:
    if not os.path.exists(skills_path):
        logging.warning("skills.md not found at %s. Using default CRAFT template.", skills_path)
        return DEFAULT_CRAFT_TEMPLATE

    with open(skills_path, "r", encoding="utf-8") as f:
        content = f.read()

    marker = "craft_prompt_template: |"
    if marker not in content:
        logging.warning("craft_prompt_template block not found in skills.md. Using default template.")
        return DEFAULT_CRAFT_TEMPLATE

    block = content.split(marker, 1)[1]
    lines = block.splitlines()
    extracted_lines = []

    for line in lines:
        if line.startswith("  ") or line.startswith("\t"):
            extracted_lines.append(line.lstrip(" \t"))
        elif line.strip() == "":
            extracted_lines.append("")
        else:
            break

    template = "\n".join(extracted_lines).strip()
    if not template:
        logging.warning("No template content found under craft_prompt_template. Using default template.")
        return DEFAULT_CRAFT_TEMPLATE

    return template


def call_llm_api(prompt_text: str) -> str:
    """Placeholder LLM API call. Replace with actual OpenAI/LiteLLM client code."""
    logging.debug("LLM prompt: %s", prompt_text)

    try:
        from openai import OpenAI
        client = OpenAI()  # Uses OPENAI_API_KEY env var
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": AGENTS_SYSTEM_PROMPT},
                {"role": "user", "content": prompt_text},
            ],
            temperature=0.0,
            max_tokens=300,
        )
        text = response.choices[0].message.content.strip()
        return text
    except ImportError:
        logging.warning("OpenAI package not installed. Using fallback static response.")
        return json.dumps({
            "category": "Other",
            "priority": "Standard",
            "reason": "Fallback response because no LLM SDK is installed.",
            "flag": "NEEDS_REVIEW",
        })
    except Exception as e:
        logging.error("LLM API call failed: %s", e)
        return json.dumps({
            "category": "Other",
            "priority": "Standard",
            "reason": "LLM call failed: %s" % str(e)[:100],
            "flag": "NEEDS_REVIEW",
        })



def parse_llm_response(response_text: str, complaint_text: str) -> dict:
    if not response_text:
        logging.warning("Empty LLM response for complaint: %s", complaint_text)
        return {"category": "Other", "priority": "Standard", "reason": "Empty LLM response", "flag": "NEEDS_REVIEW"}

    try:
        parsed = json.loads(response_text)
        if not isinstance(parsed, dict):
            raise ValueError("Parsed response is not a JSON object")

        category = parsed.get("category", "Other")
        priority = parsed.get("priority", "Standard")
        reason = parsed.get("reason", "No reason provided")
        flag = parsed.get("flag", "")

        return {
            "category": category,
            "priority": priority,
            "reason": reason,
            "flag": flag,
        }
    except json.JSONDecodeError:
        logging.warning("JSON decode error. Response text: %s", response_text)
        return {"category": "Other", "priority": "Standard", "reason": "Invalid JSON response", "flag": "NEEDS_REVIEW"}
    except Exception as e:
        logging.error("Error parsing LLM response: %s", e)
        return {"category": "Other", "priority": "Standard", "reason": "Parse error: %s" % e, "flag": "NEEDS_REVIEW"}


def classify_complaint(row: dict, template: str) -> dict:
    complaint_text = (row.get("description") or row.get("complaint_text") or "").strip()
    if not complaint_text:
        return {"category": "Other", "priority": "Standard", "reason": "Missing complaint text", "flag": "NEEDS_REVIEW"}

    prompt = template.replace("{complaint_text}", complaint_text)
    raw_response = call_llm_api(prompt)
    return parse_llm_response(raw_response, complaint_text)


def batch_classify(input_path: str, output_path: str, skills_path: str = "skills.md"):
    template = load_craft_prompt_template(skills_path)

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    with open(input_path, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)
        original_fields = reader.fieldnames or []

    output_fields = list(original_fields) + ["category", "priority", "reason", "flag"]

    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=output_fields)
        writer.writeheader()

        for idx, row in enumerate(rows, start=1):
            logging.info("Processing row %d/%d", idx, len(rows))
            try:
                result = classify_complaint(row, template)
            except Exception as e:
                logging.error("Error classifying row %d: %s", idx, e)
                result = {"category": "Other", "priority": "Standard", "reason": "Exception during classification", "flag": "NEEDS_REVIEW"}

            output_row = {**row, **result}
            writer.writerow(output_row)

    logging.info("Finished writing output to %s", output_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", default="../data/city-test-files/test_pune.csv", help="Path to input CSV")
    parser.add_argument("--output", default="results_pune.csv", help="Path to output CSV")
    parser.add_argument("--skills", default="skills.md", help="Path to skills.md for craft template")
    args = parser.parse_args()

    logging.info("Starting classifier with input=%s output=%s skills=%s", args.input, args.output, args.skills)
    batch_classify(args.input, args.output, args.skills)
    print(f"Done. Results written to {args.output}")

