import subprocess
import uuid
from pathlib import Path
from django.conf import settings
from django.shortcuts import render
from submit.models import CodeSubmission
import os

def submit(request):
    if request.method == "POST":
        language = request.POST.get("language")
        code = request.POST.get("code")
        input_data = request.POST.get("input_data", "")

        if not language or not code:
            error = "Language and code are required."
            return render(request, "index.html", {"error": error, "language": language, "code": code, "input_data": input_data})

        output, errors = run_code(language, code, input_data or "")

        submission = CodeSubmission.objects.create(
            language=language,
            code=code,
            input_data=input_data,
            output_data=(output if output else "") + ("\n\nErrors:\n" + errors if errors else "")
        )

        return render(request, "result.html", {"submission": submission})

    return render(request, "index.html")


def run_code(language, code, input_data):
    project_path = Path(settings.BASE_DIR)
    codes_dir = project_path / "codes"
    inputs_dir = project_path / "inputs"
    outputs_dir = project_path / "outputs"
    for d in [codes_dir, inputs_dir, outputs_dir]:
        d.mkdir(parents=True, exist_ok=True)

    unique = str(uuid.uuid4())

    input_file_path = inputs_dir / f"{unique}.txt"
    with open(input_file_path, "w") as f:
        f.write(input_data)

    output = ""
    errors = ""

    try:
        if language == "cpp":
            code_file_path = codes_dir / f"{unique}.cpp"
            executable_path = codes_dir / unique
            with open(code_file_path, "w") as f:
                f.write(code)
            compile_proc = subprocess.run(["clang++", str(code_file_path), "-o", str(executable_path)],
                                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=10)
            if compile_proc.returncode != 0:
                return "", compile_proc.stderr

            run_proc = subprocess.run([str(executable_path)],
                                      stdin=open(input_file_path), stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE, text=True, timeout=5)
            output = run_proc.stdout
            errors = run_proc.stderr
            os.remove(executable_path)
            os.remove(code_file_path)

        elif language == "c":
            code_file_path = codes_dir / f"{unique}.c"
            executable_path = codes_dir / unique
            with open(code_file_path, "w") as f:
                f.write(code)
            compile_proc = subprocess.run(["clang", str(code_file_path), "-o", str(executable_path)],
                                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=10)
            if compile_proc.returncode != 0:
                return "", compile_proc.stderr

            run_proc = subprocess.run([str(executable_path)],
                                      stdin=open(input_file_path), stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE, text=True, timeout=5)
            output = run_proc.stdout
            errors = run_proc.stderr
            os.remove(executable_path)
            os.remove(code_file_path)

        elif language == "py":
            code_file_path = codes_dir / f"{unique}.py"
            with open(code_file_path, "w") as f:
                f.write(code)
            normalized_input = input_data.replace('\r\n', '\n').rstrip() + '\n'
            run_proc = subprocess.run(["python3", str(code_file_path)],
                                      input=normalized_input, stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE, text=True, timeout=5)
            output = run_proc.stdout
            errors = run_proc.stderr
            os.remove(code_file_path)

        elif language == "java":
            code_class_name = f"Main_{unique.replace('-', '_')}"
            code_file_path = codes_dir / f"{code_class_name}.java"
            code = code.replace("public class Main", f"public class {code_class_name}")
            with open(code_file_path, "w") as f:
                f.write(code)

            compile_proc = subprocess.run(["javac", str(code_file_path)],
                                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=10)
            if compile_proc.returncode != 0:
                return "", compile_proc.stderr

            run_proc = subprocess.run(["java", "-cp", str(codes_dir), code_class_name],
                                      stdin=open(input_file_path), stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE, text=True, timeout=5)
            output = run_proc.stdout
            errors = run_proc.stderr

            class_file = codes_dir / f"{code_class_name}.class"
            if class_file.exists():
                os.remove(class_file)
            os.remove(code_file_path)

        else:
            errors = "Unsupported language"

    except subprocess.TimeoutExpired:
        errors = "Error: Execution timed out."

    except Exception as e:
        errors = f"Error: {str(e)}"

    if input_file_path.exists():
        os.remove(input_file_path)

    return output, errors
