import os
import subprocess
import uuid
import sys
import re
from pathlib import Path
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import google.generativeai as genai

from .models import Problem, CodeSubmission  # 🔹 ADDED CodeSubmission


# Configure Gemini API
genai.configure(api_key=settings.GEMINI_API_KEY)


@csrf_exempt
def ask_ai_for_boilerplate(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            problem_desc = data.get("problem_description", "")
            language = data.get("language", "Python")

            if not problem_desc:
                return JsonResponse({"error": "No problem description provided."}, status=400)

            model = genai.GenerativeModel("models/gemini-1.5-flash")
            prompt = f"Write a {language} boilerplate code template for the following problem:\n\n{problem_desc}\n\nOnly return the code without explanation."
            response = model.generate_content(prompt)
            ai_response = getattr(response, "text", "") or str(response)
            return JsonResponse({"ai_response": ai_response})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method."}, status=405)


@csrf_exempt
def gemini_ai(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            code = data.get('code', '')

            prompt = f"Fix any bugs and improve the following code:\n\n{code}"
            model = genai.GenerativeModel("models/gemini-1.5-flash")
            response = model.generate_content(prompt)

            return JsonResponse({'response': response.text})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Only POST method allowed'}, status=405)


def deeplogic_page(request):
    return render(request, 'DeepLogic.html')

# ----------------------------- Standalone Compiler with Submission Saving
@login_required
def submit(request):
    if request.method == "POST":
        language = request.POST.get("language")
        code = request.POST.get("code")
        input_data = request.POST.get("input_data", "")

        if not language or not code:
            return render(request, "index.html", {
                "error": "Language and code are required.",
                "language": language,
                "code": code,
                "input_data": input_data
            })

        output, errors = run_code(language, code, input_data)

        # 🔹 Save submission
        submission = CodeSubmission.objects.create(
            user=request.user,
            language=language,
            code=code,
            input_data=input_data,
            output=output,
            errors=errors
        )

        return render(request, "index.html", {
            "language": language,
            "code": code,
            "input_data": input_data,
            "output": output,
            "errors": errors,
            "submission": submission
        })

    return render(request, "index.html")


# ----------------------------- Profile View: Show Submission History
@login_required
def profile_view(request):
    submissions = CodeSubmission.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'profile.html', {'submissions': submissions})

@login_required
def update_profile(request):
    if request.method == 'POST':
        user = request.user
        user.username = request.POST.get('username', user.username)
        user.email = request.POST.get('email', user.email)
        user.save()
    return redirect('profile')
# ----------------------------- Problem List View
@login_required
def problem_list(request):
    query = request.GET.get('q', '')
    difficulty = request.GET.get('difficulty', '')
    topic = request.GET.get('topic', '')
    problems = Problem.objects.all()

    if query:
        problems = problems.filter(description__icontains=query)
    if difficulty:
        problems = problems.filter(difficulty=difficulty)
    if topic:
        problems = problems.filter(topic=topic)

    return render(request, 'problem_list.html', {
        'problems': problems,
        'query': query,
        'selected_difficulty': difficulty,
        'selected_topic': topic,
    })


# ----------------------------- Problem Detail View with Submission Saving
@login_required
def problem_detail(request, problem_id):
    problem = get_object_or_404(Problem, id=problem_id)
    test_results, raw_output, raw_errors, error = None, None, None, None

    if request.method == 'POST':
        language = request.POST.get("language")
        code = request.POST.get("code")
        action = request.POST.get("action")
        custom_input = request.POST.get("custom_input", "")

        if not language or not code:
            error = "Please select a language and write your code."
        else:
            if action == "run":
                raw_output, raw_errors = run_code(language, code, custom_input)

            elif action == "submit":
                test_results = []
                for test_case in problem.test_cases.all():
                    input_data = test_case.input_data
                    expected_output = test_case.expected_output.strip()
                    actual_output, errors = run_code(language, code, input_data)
                    passed = (actual_output.strip() == expected_output) and (not errors)
                    test_results.append({
                        'input': input_data,
                        'expected': expected_output,
                        'output': actual_output.strip(),
                        'errors': errors,
                        'status': "Passed" if passed else "Failed"
                    })

                # 🔹 Save submission with all test results
                CodeSubmission.objects.create(
                    user=request.user,
                    problem=problem,
                    language=language,
                    code=code,
                    input_data="Multiple test cases",
                    output="\n".join([r['output'] for r in test_results]),
                    errors="\n".join([r['errors'] for r in test_results if r['errors']])
                )

    return render(request, 'problem_detail.html', {
        'problem': problem,
        'test_results': test_results,
        'raw_output': raw_output,
        'raw_errors': raw_errors,
        'error': error,
        'posted_language': request.POST.get('language', ''),
        'posted_code': request.POST.get('code', ''),
        'custom_input': request.POST.get('custom_input', ''),
    })


# ----------------------------- Logout
def logout_user(request):
    logout(request)
    messages.info(request, "Logout successful.")
    return redirect('/auth/login/')


# ----------------------------- Core Code Execution Logic
def run_code(language, code, input_data):
    base_path = Path(settings.BASE_DIR)
    codes_dir = base_path / "codes"
    inputs_dir = base_path / "inputs"
    outputs_dir = base_path / "outputs"

    for folder in [codes_dir, inputs_dir, outputs_dir]:
        folder.mkdir(parents=True, exist_ok=True)

    unique_id = str(uuid.uuid4())
    input_file = inputs_dir / f"{unique_id}.txt"
    output_file = outputs_dir / f"{unique_id}.txt"
    input_file.write_text(input_data)

    output, errors = "", ""
    exec_file = code_file = None
    class_name = None
    ext = ".exe" if sys.platform.startswith("win") else ""

    try:
        if language == "cpp":
            code_file = codes_dir / f"{unique_id}.cpp"
            exec_file = codes_dir / f"{unique_id}{ext}"
            code_file.write_text(code)
            compile = subprocess.run(["g++", str(code_file), "-o", str(exec_file)],
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=10)
            if compile.returncode != 0:
                errors = compile.stderr.strip()
                return "", errors
            with open(input_file, 'r') as infile:
                run = subprocess.run([str(exec_file)], stdin=infile, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5)
            output, errors = run.stdout.strip(), run.stderr.strip()

        elif language == "c":
            code_file = codes_dir / f"{unique_id}.c"
            exec_file = codes_dir / f"{unique_id}{ext}"
            code_file.write_text(code)
            compile = subprocess.run(["gcc", str(code_file), "-o", str(exec_file)],
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=10)
            if compile.returncode != 0:
                errors = compile.stderr.strip()
                return "", errors
            with open(input_file, 'r') as infile:
                run = subprocess.run([str(exec_file)], stdin=infile, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5)
            output, errors = run.stdout.strip(), run.stderr.strip()

        elif language == "py":
            code_file = codes_dir / f"{unique_id}.py"
            code_file.write_text(code)
            run = subprocess.run(["python3", str(code_file)], input=input_data, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5)
            output, errors = run.stdout.strip(), run.stderr.strip()

        elif language == "java":
            class_name = f"Main_{unique_id.replace('-', '_')}"
            if not re.search(r"public\s+class\s+Main\b", code):
                errors = "Java code must contain 'public class Main'."
                return "", errors
            code = re.sub(r"public\s+class\s+Main\b", f"public class {class_name}", code)
            code_file = codes_dir / f"{class_name}.java"
            code_file.write_text(code)
            compile = subprocess.run(["javac", str(code_file)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=10)
            if compile.returncode != 0:
                errors = compile.stderr.strip()
                return "", errors
            with open(input_file, 'r') as infile:
                run = subprocess.run(["java", "-cp", str(codes_dir), class_name], stdin=infile, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5)
            output, errors = run.stdout.strip(), run.stderr.strip()

        else:
            errors = "Unsupported language."

    except subprocess.TimeoutExpired:
        errors = "Execution timed out."
    except Exception as e:
        errors = f"Error during code execution: {str(e)}"
    finally:
        for f in [code_file, exec_file, input_file, output_file]:
            if f and f.exists():
                try:
                    f.unlink()
                except Exception:
                    pass

    return output, errors
