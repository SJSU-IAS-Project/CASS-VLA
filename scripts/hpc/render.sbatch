#!/bin/bash
#SBATCH --job-name=cass_render
#SBATCH --partition=cpuqs
#SBATCH --cpus-per-task=32
#SBATCH --mem=100G
#SBATCH --time=08:00:00
#SBATCH --output=/data/cmpe249-fa26/students/017025164/logs/%x_%j.log
# Render front-camera frames with headless EGL. Usage: sbatch render.sbatch OUT DATA:SPLIT [DATA:SPLIT ...]
# One worker peaked at 5.5 GB in the test job, so 16 workers fit in 100 GB. Reruns resume.
D=/data/cmpe249-fa26/students/017025164
cd $D/CASS-VLA
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 LP_NUM_THREADS=2 MPLCONFIGDIR=$D/cache/mpl
OUT=$1; shift
echo "node $(hostname)  $(date)  out $OUT"
for ds in "$@"; do
  t=$SECONDS
  env -u DISPLAY $D/venv/bin/python scripts/hpc/render_frames_hpc.py --data ${ds%%:*} --split ${ds#*:} --out $OUT --procs 16 --max-msaa 4 2>&1 | grep -v -E "WARNING|AL lib|audio|/dev/input" | awk 'NR==1 || /Error|Traceback/ || NR%50==0'
  echo "== $ds exit ${PIPESTATUS[0]} in $((SECONDS - t)) s, $(wc -l < $OUT/frames.jsonl) frames logged"
done
echo done $(date)
