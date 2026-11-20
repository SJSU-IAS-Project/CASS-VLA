"""Selector inputs from the cached VLM pass (Phase 5), joined onto dataset rows by frame key.

    from cassvla.perception.vlm import load_cache
    from cassvla.perception.vlm_features import VLMFeatures
    vf = VLMFeatures(load_cache("out/vlm"), n_pca=32).fit(train_rows)   # PCA fitted on train rows only
    X = vf.transform(test_rows)               # (N, n_pca + len(PROMPTED_NAMES))
    vf.prompted_tool(test_rows)               # the VLM's own query choice: tool index, or -1 for none

Rows without a cached frame cannot be featurised; ``covered(rows)`` says which rows are usable, and the
evaluation restricts every method to the covered rows so all of them see the same decisions.
"""
import numpy as np

from cassvla.perception.frames import frame_key
from cassvla.perception.vlm import LIGHTS, QUERIES
from cassvla.planning.tools import TOOLS

PROMPTED_NAMES = (*[f"vlm_query_{q}" for q in QUERIES], "vlm_occlusion", *[f"vlm_light_{lt}" for lt in LIGHTS],
                  "vlm_n_hazards", "vlm_parse_error")


def row_key(row):
    return frame_key(row["family"], row["seed"], row["t_dec"])


def prompted_vector(answer):
    v = [float(answer["query"] == q) for q in QUERIES]
    v.append(float(answer["occlusion"]))
    v += [float(answer["light"] == lt) for lt in LIGHTS]
    hazards = [h for h in answer["hazards"] if h.strip().lower() not in ("none", "no hazards", "")]
    v += [min(len(hazards), 5) / 5.0, float(answer["parse_error"])]
    return v


class VLMFeatures:
    def __init__(self, cache, n_pca=32):
        self.n_pca = n_pca
        self.index = {k: i for i, k in enumerate(cache["keys"])}
        self.emb = cache["emb"]
        self.prompted = cache["prompted"]
        self.mean = self.components = None

    def covered(self, rows):
        return np.array([row_key(r) in self.index and row_key(r) in self.prompted for r in rows], bool)

    def _emb(self, rows):
        return self.emb[[self.index[row_key(r)] for r in rows]].astype(np.float64)

    def fit(self, train_rows):
        E = self._emb(train_rows)
        self.mean = E.mean(axis=0)
        _, s, vt = np.linalg.svd(E - self.mean, full_matrices=False)
        k = min(self.n_pca, vt.shape[0])
        self.components = vt[:k]
        self.explained = float((s[:k] ** 2).sum() / max((s ** 2).sum(), 1e-12))
        return self

    def names(self):
        return [f"vlm_pc{i}" for i in range(len(self.components))] + list(PROMPTED_NAMES)

    def transform(self, rows):
        if self.components is None:
            raise RuntimeError("call fit() on the train rows first")
        pcs = (self._emb(rows) - self.mean) @ self.components.T
        prompted = np.array([prompted_vector(self.prompted[row_key(r)]) for r in rows], float).reshape(len(rows), len(PROMPTED_NAMES))
        return np.hstack([pcs, prompted])

    def prompted_tool(self, rows):
        """The tool the VLM itself asked for: index into TOOLS, or -1 when it said none."""
        return np.array([TOOLS.index(q) if (q := self.prompted[row_key(r)]["query"]) in TOOLS else -1 for r in rows], int)
