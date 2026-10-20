"""Fresh CPU/CUDA calibration replay in an isolated Docker research workspace.

Uses the rebuilt iKalibr binary directly, never the installed CPU binary or a
previously solved parameter file. The output is benchmark evidence, not an
importable/validated phone profile. Notebook orchestration owns the container.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import threading
import time

import yaml


def digest(path):
    with Path(path).open("rb") as source:
        value = hashlib.sha256()
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def run(prepared=False):
    # Source ROS within Linux, avoiding shell interpolation through Windows/WSL.
    ros_environment = subprocess.check_output([
        "bash", "-c", "source /opt/ros/noetic/setup.bash && env -0"])
    os.environ.update(dict(item.decode().split("=", 1) for item in ros_environment.split(b"\0") if item))
    os.environ["LD_LIBRARY_PATH"] = (
        "/opt/ceres-cuda/lib:/opt/ikalibr-cuda-devel/lib:"
        "/home/iKalibr/src/ikalibr/thirdparty/ctraj-install/lib:"
        "/home/iKalibr/install/lib:/usr/local/cuda-12.9/lib64:"
        + os.environ.get("LD_LIBRARY_PATH", ""))
    source, target, evidence = Path("/source"), Path("/data"), Path("/evidence")
    engine = Path("/opt/ikalibr-cuda-devel/lib/ikalibr/ikalibr_prog")
    mode = os.environ["BENCHMARK_MODE"]
    if mode not in ("cpu", "cuda") or (not prepared and any(target.iterdir())):
        raise ValueError("Use a fresh research volume and an explicit backend")
    linkage = subprocess.check_output(["ldd", str(engine)], text=True)
    if "/opt/ceres-cuda/lib/libceres.so" not in linkage:
        raise ValueError("Rebuilt executable is not linked to the CUDA-capable Ceres library")
    source_diff = subprocess.check_output([
        "git", "-C", "/home/iKalibr/src/ikalibr", "diff", "HEAD"], text=True)
    changed_lines = [line for line in source_diff.splitlines()
                     if line.startswith(("+", "-")) and not line.startswith(("+++", "---"))]
    linkage_changes = {
        sign + "    " + declaration for sign, declarations in (
            ("-", ("inline Eigen::Vector2f Raw() const;", "inline Eigen::Vector2f Undistorted() const;")),
            ("+", ("Eigen::Vector2f Raw() const;", "Eigen::Vector2f Undistorted() const;")))
        for declaration in declarations}
    if not all(line.startswith("+#include ") or line in linkage_changes for line in changed_lines):
        raise ValueError("Experimental source edits extend beyond build declarations")
    evidence.mkdir(exist_ok=True)
    if not prepared:
        for name in ("capture.bag", "camera.json", "imu.json", "provenance.json", "sfm-complete.json"):
            shutil.copyfile(source / name, target / name)
    sfm_parent = Path("output/images/gaittrace/camera")
    if not prepared:
        shutil.copytree(source / sfm_parent, target / sfm_parent)
    config = yaml.safe_load(((target if prepared else source) / "config.yaml").read_text())
    config["Configor"]["Preference"]["ThreadsToUse"] = 2
    config["Configor"]["Preference"]["UseCudaInSolving"] = mode == "cuda"
    (target / "config.yaml").write_text(yaml.safe_dump(config, sort_keys=False))
    stop = threading.Event()
    samples = []

    def monitor():
        while not stop.is_set():
            try:
                reading = subprocess.check_output([
                    "nvidia-smi", "--query-gpu=timestamp,utilization.gpu,memory.used",
                    "--format=csv,noheader,nounits"], text=True, timeout=3)
                processes = subprocess.check_output([
                    "nvidia-smi", "--query-compute-apps=pid,process_name,used_gpu_memory",
                    "--format=csv,noheader,nounits"], text=True, timeout=3)
                samples.append({"gpu": reading.strip(), "processes": processes.strip()})
            except (subprocess.SubprocessError, OSError) as error:
                samples.append({"error": str(error)})
            stop.wait(1)

    master = subprocess.Popen(["roscore"], stdout=(target / "roscore.log").open("w"),
                              stderr=subprocess.STDOUT, start_new_session=True)
    process = None
    thread = threading.Thread(target=monitor, daemon=True)
    stamp = None
    success = False
    failure = None
    try:
        for _ in range(30):
            ready = subprocess.run(["rosparam", "set", "/ikalibr_prog/config_path", "/data/config.yaml"],
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if ready.returncode == 0:
                break
            time.sleep(1)
        else:
            raise RuntimeError("ROS master did not start")
        thread.start()
        stamp = time.perf_counter()
        log = target / "reference-final.log"
        with log.open("w") as stream:
            process = subprocess.Popen([
                "xvfb-run", "-a", "-s", "-screen 0 1280x720x24 +extension GLX",
                str(engine), "__name:=ikalibr_prog"], stdout=stream,
                stderr=subprocess.STDOUT, start_new_session=True)
            while True:
                contents = log.read_text(errors="replace")
                if "solving and outputting finished" in contents:
                    success = True
                    break
                if process.poll() is not None:
                    raise RuntimeError("Reference solver exited without completion marker")
                if time.perf_counter() - stamp > 900:
                    raise TimeoutError("Reference solver exceeded 900 seconds")
                time.sleep(0.5)
        if not (target / "output/ikalibr_param.json").is_file():
            raise RuntimeError("No upstream parameters written")
        reports = re.findall(r"Ceres Solver Report:.*", contents)
        if len(reports) < 7 or not all("CONVERGENCE" in report for report in reports):
            success = False
            raise RuntimeError("Reference convergence gate failed")
    except Exception as error:
        success = False
        failure = str(error)
    finally:
        elapsed = None if stamp is None else time.perf_counter() - stamp
        stop.set()
        if thread.is_alive():
            thread.join(timeout=8)
        for child in (process, master):
            if child is not None and child.poll() is None:
                os.killpg(child.pid, signal.SIGTERM)
                try:
                    child.wait(timeout=20)
                except subprocess.TimeoutExpired:
                    os.killpg(child.pid, signal.SIGKILL)
                    child.wait(timeout=10)
        for name in ("reference-final.log", "config.yaml"):
            if (target / name).is_file():
                shutil.copyfile(target / name, evidence / name)
        if (target / "output/ikalibr_param.json").is_file():
            shutil.copyfile(target / "output/ikalibr_param.json", evidence / "ikalibr_param.json")
        record = {
            "kind": "experimental-calibration-backend-benchmark-v1",
            "mode": mode, "converged": success, "error": failure,
            "finalSolverWallSeconds": elapsed,
            "imageId": os.environ["BENCHMARK_IMAGE_ID"],
            "executableSha256": digest(engine),
            "ceresLibrarySha256": digest("/opt/ceres-cuda/lib/libceres.so.2.2.0"),
            "sourceProvenance": json.loads(Path("/opt/source-provenance.json").read_text()),
            "upstreamSourceDiff": source_diff,
            "buildOnlyDeclarationsVerified": True,
            "ceresSourceCommit": subprocess.check_output([
                "git", "-C", "/home/software/ceres-solver", "rev-parse", "HEAD"], text=True).strip(),
            "configurationSha256": digest(target / "config.yaml"),
            "calibrationInputsSha256": {name: digest(target / name) for name in (
                "camera.json", "imu.json", "provenance.json", "sfm-complete.json")},
            "captureBagSha256": digest(target / "capture.bag"),
            "sourceCaptureSha256": json.loads((target / "provenance.json").read_text())["sourceSha256"],
            "fixedSfmPointsSha256": digest(target / sfm_parent / "sfm_ws/points3D.txt"),
            "threads": 2, "dynamicLinkage": linkage,
            "freshPipelineInputs": prepared,
            "gpuSamples": samples, "distanceReady": False,
            "independentDistanceValidation": False,
        }
        (evidence / "benchmark.json").write_text(json.dumps(record, indent=2))
        print(json.dumps({key: value for key, value in record.items()
                          if key not in ("gpuSamples", "dynamicLinkage")}), flush=True)
    if failure:
        raise RuntimeError(failure)


if __name__ == "__main__":
    run()
