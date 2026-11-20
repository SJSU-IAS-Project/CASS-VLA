#!/bin/bash
#SBATCH --job-name=cass_render_test
#SBATCH --partition=cpuqs
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=00:30:00
#SBATCH --output=/data/cmpe249-fa26/students/017025164/logs/%x_%j.log
# Renders 9 frames of one seed with headless EGL (no Xvfb on the compute nodes) and reports time and memory.
D=/data/cmpe249-fa26/students/017025164
cd $D/CASS-VLA
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MPLCONFIGDIR=$D/cache/mpl
echo "node $(hostname)  $(date)"
rm -rf out/hpc_test_frames_egl
t=$(date +%s); env -u DISPLAY /usr/bin/time -v $D/venv/bin/python scripts/hpc/render_frames_hpc.py --data out/hpc_test_ds --split final --out out/hpc_test_frames_egl --procs 1 --max-msaa 4 2>&1 | grep -E "frames|Error|error:|Maximum resident|Elapsed" | grep -v WARNING | tail -8
echo "egl exit in $(( $(date +%s)-t )) s"; ls out/hpc_test_frames_egl/ambiguous_light | wc -l; echo done $(date)
