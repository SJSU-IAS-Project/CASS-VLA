#!/bin/bash
#SBATCH --job-name=cass_vlm
#SBATCH --partition=gpuqs
#SBATCH --gres=gpu:a100:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=01:00:00
#SBATCH --output=/data/cmpe249-fa26/students/017025164/logs/%x_%j.log
# Phase 5 VLM pass inside the ctxeval vLLM image, read-only. Usage: sbatch [--time=H:MM:SS] vlm.sbatch FRAMES OUT LIMIT DATA SPLIT[,SPLIT]
# The model snapshot and the image are read in place from cmpe295-suresh, bound read-only; every cache is ours.
set -u
D=/data/cmpe249-fa26/students/017025164
R=/data/cmpe295-suresh/017025164
SIF=$R/sif/vllm-openai-v0.30.0.sif
MODEL=$R/hf/hub/models--Qwen--Qwen3.5-9B/snapshots/c202236235762e1c871ad0ccb60c8ee5ba337b9a
FRAMES=$1 OUT=$2 LIMIT=${3:-0} DATA=${4:-} SPLIT=${5:-val}
SC=/scratch/cmpe249-fa26/017025164; mkdir -p $SC 2>/dev/null && [ -w $SC ] || SC=${TMPDIR:-/tmp}/017025164-scratch
T=$SC/tmp/$SLURM_JOB_ID; C=$SC/cache; mkdir -p $T $C/apptainer/cache $C/apptainer/tmp $D/cache/hf
export APPTAINER_CACHEDIR=$C/apptainer/cache APPTAINER_TMPDIR=$C/apptainer/tmp
export APPTAINERENV_HF_HOME=$D/cache/hf APPTAINERENV_HF_HUB_OFFLINE=1 APPTAINERENV_TRANSFORMERS_OFFLINE=1
export APPTAINERENV_HF_HUB_DISABLE_TELEMETRY=1 APPTAINERENV_VLLM_NO_USAGE_STATS=1 APPTAINERENV_DO_NOT_TRACK=1
export APPTAINERENV_VLLM_CACHE_ROOT=$C/vllm APPTAINERENV_XDG_CACHE_HOME=$C/xdg APPTAINERENV_TRITON_CACHE_DIR=$C/triton
export APPTAINERENV_TORCHINDUCTOR_CACHE_DIR=$C/inductor APPTAINERENV_TMPDIR=$T APPTAINERENV_PYTHONNOUSERSITE=1
[ -n "${CUDA_VISIBLE_DEVICES:-}" ] && export APPTAINERENV_CUDA_VISIBLE_DEVICES=$CUDA_VISIBLE_DEVICES
echo "node $(hostname) gpu ${CUDA_VISIBLE_DEVICES:-unset} $(date)"
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader ${CUDA_VISIBLE_DEVICES:+-i $CUDA_VISIBLE_DEVICES}
run() { apptainer exec --nv --cleanenv -B $D,$SC -B $R/hf:$R/hf:ro -B $R/sif:$R/sif:ro $SIF python3 $D/CASS-VLA/scripts/vlm_encode.py "$@"; }
cd $D/CASS-VLA
for stage in embed describe prompt; do
  t=$SECONDS
  if [ $stage = prompt ]; then
    [ -n "$DATA" ] || continue
    for sp in ${SPLIT//,/ }; do
      run prompt --frames $FRAMES --model $MODEL --out $OUT --limit $LIMIT --data $DATA --split $sp 2>&1 | grep -v -i -E "warn|it/s\]|INFO" | tail -6
    done
  else
    run $stage --frames $FRAMES --model $MODEL --out $OUT --limit $LIMIT 2>&1 | grep -v -i -E "warn|it/s\]|INFO" | tail -10
  fi
  echo "== $stage exit ${PIPESTATUS[0]} in $((SECONDS - t)) s"
done
rm -rf $T; echo done $(date)
