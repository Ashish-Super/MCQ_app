from flask import Flask, request, jsonify, render_template
from groq_client import ask_groq
import json
import os

app = Flask(__name__)

STORED_QUESTIONS = {}

LEADERBOARD_FILE = "leaderboard.json"

def load_leaderboard():
    if not os.path.exists(LEADERBOARD_FILE):
        return []
    try:
        with open(LEADERBOARD_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_leaderboard(data):
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(data, f)


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate_questions():
    subject = request.json.get("subject")
    class_level = request.json.get("classlevel")
    difficultiy_level = request.json.get("difficultiy_level")

    if not subject:
        return jsonify({"error": "Subject is required"}), 400

    prompt = f"""

Strict rules:
1. Questions must test conceptual understanding.
2. Include multi-step reasoning where possible.
3. Include application-based and situation-based questions.
4.Assume these questions are for scholarship-level practice, not basic revision.

You are a JSON generator.

ABSOLUTE RULES:
- Output ONLY JSON
- No text before JSON
- No text after JSON
- No markdown
- No explanations
- No comments

Generate exactly 10 Class {class_level} {subject.capitalize()} MCQs considering {difficultiy_level} level questions.

JSON FORMAT:
{{
  "questions": [
    {{
      "id": 1,
      "question": "string",
      "options": {{
        "A": "string",
        "B": "string",
        "C": "string",
        "D": "string"
      }},
      "correct_answer": "A"
    }}
  ]
}}
"""
    response = ask_groq(prompt)
    start = response.find("{")
    end = response.rfind("}") + 1

    if start == -1 or end == -1:
        return jsonify({"error": "No JSON found in model output"}), 500

    response = response[start:end]

    try:
        data = json.loads(response)

    except Exception as e:
        print("----- MODEL RAW OUTPUT START -----")
        print(response)
        print("----- MODEL RAW OUTPUT END -----")
        print("JSON ERROR:", e)
        return jsonify({
            "error": "Model did not return valid JSON",
            "raw_output": response
        }), 500

    STORED_QUESTIONS.clear()
    for q in data["questions"]:
        STORED_QUESTIONS[str(q["id"])] = q

    return jsonify(data)

@app.route("/submit", methods=["POST"])
def submit_answers():
    data = request.get_json(force=True)
    class_level = request.json.get("classlevel")
    try:
        data = request.get_json(force=True)
        student_name = data.get("name")
        user_answers = data.get("answers", {})
        if not user_answers:
            return jsonify({"error": "Empty submission ignored"}), 400
        score = 0
        wrong_answers = []

        # Hard validation
        if not student_name or not class_level:
            return jsonify({"error": "Invalid submission"}), 400

        if not isinstance(user_answers, dict) or len(user_answers) == 0:
            return jsonify({"error": "Empty answers rejected"}), 400

        # STORED_QUESTIONS must already exist from /generate
        for qid, question in STORED_QUESTIONS.items():
            correct = question["correct_answer"]
            user_choice = user_answers.get(qid)

            # CASE 1: NOT ATTEMPTED
            if not user_choice:
                wrong_answers.append({
                    "question_id": qid,
                    "question": question["question"],
                    "your_answer": "Not Attempted",
                    "correct_answer": correct,
                    "explanation": json.dumps({
                        "why_your_answer_is_wrong": "You did not attempt this question.",
                        "why_correct_answer_is_right": f"The correct answer is option {correct}.",
                        "key_takeaway": "Always attempt every question in an exam."
                    })
                })
                continue

            # CASE 2: CORRECT
            if user_choice == correct:
                score += 1
                continue

            # CASE 3: WRONG
            explanation_prompt = f"""
You are a Class {class_level} teacher.

Return the explanation STRICTLY in JSON.

JSON format:
{{
  "why_your_answer_is_wrong": "",
  "why_correct_answer_is_right": "",
  "key_takeaway": ""
}}

Question: {question["question"]}
Options: {question["options"]}
Student chose: {user_choice}
Correct answer: {correct}
"""

            explanation = ask_groq(explanation_prompt)

            wrong_answers.append({
                "question_id": qid,
                "question": question["question"],
                "your_answer": user_choice,
                "correct_answer": correct,
                "explanation": explanation
            })

            leaderboard = load_leaderboard()

            updated = False

            for entry in leaderboard:
                if entry["name"] == student_name and entry["class"] == class_level:
                    entry["score"] = score
                    entry["out_of"] = len(STORED_QUESTIONS)
                    updated = True
                    break

            if not updated:
                leaderboard.append({
                    "name": student_name,
                    "class": class_level,
                    "score": score,
                    "out_of": len(STORED_QUESTIONS)
                })

            save_leaderboard(leaderboard)

        # ✅ FINAL RETURN (MANDATORY)
        return jsonify({
            "score": score,
            "out_of": len(STORED_QUESTIONS),
            "wrong_answers": wrong_answers
        })
    
    except Exception as e:
        print("SUBMIT ERROR:", e)
        return jsonify({
            "score": 0,
            "out_of": len(STORED_QUESTIONS) if "STORED_QUESTIONS" in globals() else 0,
            "wrong_answers": [],
            "error": "Submission failed"
        }), 500
    
@app.route("/leaderboard")
def leaderboard():
    data = load_leaderboard()

    class_map = {}

    # Group entries by class
    for entry in data:
        cls = entry["class"]
        if cls not in class_map:
            class_map[cls] = []
        class_map[cls].append(entry)

    result = []

    for cls, entries in class_map.items():
        # Calculate average
        total = sum(e["score"] for e in entries)
        avg = round(total / len(entries), 2)

        # Sort students by score descending
        sorted_students = sorted(entries, key=lambda x: x["score"], reverse=True)

        top_students = []
        for s in sorted_students[:3]:
            top_students.append({
                "name": s["name"],
                "score": s["score"]
            })

        result.append({
            "class": cls,
            "average": avg,
            "top_students": top_students
        })

    # Rank classes by average
    result.sort(key=lambda x: x["average"], reverse=True)

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
