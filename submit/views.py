import subprocess
import uuid
from pathlib import Path
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from submit.models import CodeSubmission
from .models import Problem
import os

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


@login_required
def problem_detail(request, problem_id):
    problem = get_object_or_404(Problem, id=problem_id)
    test_results = None
    raw_output = None
    raw_errors = None
    error = None

    if request.method == 'POST':
        language = request.POST.get("language")
        code = request.POST.get("code")
        action = request.POST.get("action")  # either 'run' or 'submit'
        custom_input = request.POST.get("custom_input", "")

        if not language or not code:
            error = "Please select a language and write your code."
        else:
            if action == "run":
                # Just run the code with custom input
                raw_output, raw_errors = run_code(language, code, custom_input)

            elif action == "submit":
                # Validate against test cases
                test_results = []
                for test_case in problem.test_cases.all():
                    input_data = test_case.input_data
                    expected_output = test_case.expected_output.strip()

                    actual_output, errors = run_code(language, code, input_data)

                    passed = actual_output.strip() == expected_output and not errors
                    test_results.append({
                        'input': input_data,
                        'expected': expected_output,
                        'output': actual_output.strip(),
                        'errors': errors,
                        'status': "Passed" if passed else "Failed"
                    })

                # Save submission for the problem
                CodeSubmission.objects.create(
                    user=request.user,
                    problem=problem,
                    language=language,
                    code=code,
                    input_data="Multiple test cases",
                    output="\n".join([r['output'] for r in test_results]),
                    errors="\n".join([r['errors'] for r in test_results if r['errors']])
                )

    context = {
        'problem': problem,
        'test_results': test_results,
        'raw_output': raw_output,
        'raw_errors': raw_errors,
        'error': error,
        'posted_language': request.POST.get('language', ''),
        'posted_code': request.POST.get('code', ''),
        'custom_input': request.POST.get('custom_input', ''),
    }

    return render(request, 'problem_detail.html', context)


@login_required
def profile_view(request):
    submissions = CodeSubmission.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'profile.html', {'submissions': submissions})

@login_required
def submit(request):
    if request.method == "POST":
        language = request.POST.get("language")
        code = request.POST.get("code")
        input_data = request.POST.get("input_data", "")

        if not language or not code:
            error = "Language and code are required."
            return render(request, "index.html", {
                "error": error,
                "language": language,
                "code": code,
                "input_data": input_data
            })

        output, errors = run_code(language, code, input_data)

        submission = CodeSubmission.objects.create(
            user=request.user,
            language=language,
            code=code,
            input_data=input_data,
            output=output,
            errors=errors
        )

        return render(request, "index.html", {
            "submission": submission,
            "language": language,
            "code": code,
            "input_data": input_data,
            "output": output,
            "errors": errors,
        })

    return render(request, "index.html")

def logout_user(request):
    logout(request)
    messages.info(request, "Logout successful.")
    return redirect('/auth/login/')

def run_code(language, code, input_data):
    project_path = Path(settings.BASE_DIR)
    codes_dir = project_path / "codes"
    inputs_dir = project_path / "inputs"
    for d in [codes_dir, inputs_dir]:
        d.mkdir(parents=True, exist_ok=True)

    unique = str(uuid.uuid4())
    input_file_path = inputs_dir / f"{unique}.txt"
    input_file_path.write_text(input_data)

    output = ""
    errors = ""

    try:
        if language == "cpp":
            code_file = codes_dir / f"{unique}.cpp"
            exec_file = codes_dir / unique
            code_file.write_text(code)

            compile_proc = subprocess.run(
                ["clang++", str(code_file), "-o", str(exec_file)],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, timeout=10
            )
            if compile_proc.returncode != 0:
                return "", compile_proc.stderr.strip()

            with open(input_file_path, "r") as input_file:
                run_proc = subprocess.run(
                    [str(exec_file)],
                    stdin=input_file,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=5
                )
            output = run_proc.stdout.strip()
            errors = run_proc.stderr.strip()
            os.remove(exec_file)
            os.remove(code_file)

        elif language == "c":
            code_file = codes_dir / f"{unique}.c"
            exec_file = codes_dir / unique
            code_file.write_text(code)

            compile_proc = subprocess.run(
                ["clang", str(code_file), "-o", str(exec_file)],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, timeout=10
            )
            if compile_proc.returncode != 0:
                return "", compile_proc.stderr.strip()

            with open(input_file_path, "r") as input_file:
                run_proc = subprocess.run(
                    [str(exec_file)],
                    stdin=input_file,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=5
                )
            output = run_proc.stdout.strip()
            errors = run_proc.stderr.strip()
            os.remove(exec_file)
            os.remove(code_file)

        elif language == "py":
            code_file = codes_dir / f"{unique}.py"
            code_file.write_text(code)

            normalized_input = input_data.replace('\r\n', '\n').rstrip() + '\n'
            run_proc = subprocess.run(
                ["python3", str(code_file)],
                input=normalized_input,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=5
            )
            output = run_proc.stdout.strip()
            errors = run_proc.stderr.strip()
            os.remove(code_file)

        elif language == "java":
            class_name = f"Main_{unique.replace('-', '_')}"
            code_file = codes_dir / f"{class_name}.java"
            code = code.replace("public class Main", f"public class {class_name}")
            code_file.write_text(code)

            compile_proc = subprocess.run(
                ["javac", str(code_file)],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, timeout=10
            )
            if compile_proc.returncode != 0:
                return "", compile_proc.stderr.strip()

            with open(input_file_path, "r") as input_file:
                run_proc = subprocess.run(
                    ["java", "-cp", str(codes_dir), class_name],
                    stdin=input_file,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=5
                )
            output = run_proc.stdout.strip()
            errors = run_proc.stderr.strip()

            class_file = codes_dir / f"{class_name}.class"
            if class_file.exists():
                os.remove(class_file)
            os.remove(code_file)

        else:
            errors = "Unsupported language"

    except subprocess.TimeoutExpired:
        errors = "Error: Execution timed out."
    except Exception as e:
        errors = f"Error: {str(e)}"

    if input_file_path.exists():
        os.remove(input_file_path)

    return output, errors
