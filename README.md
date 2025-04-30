# QUBIKOS – QUantum Benchmark wIth Known-Optimal SWAP Counts

QUBIKOS is a benchmarking tool designed to evaluate quantum layout synthesis tools by generating quantum circuits with a known optimal number of SWAP operations.

## 📌 Overview

QUBIKOS generates benchmark circuits that respect a given hardware topology and ensures the minimal number of SWAP gates is known. This allows for accurate assessment of SWAP insertion efficiency in quantum compilers and layout synthesis tools.

## ⚙️ How to Use

### Generate QUBIKOS Benchmark with `QUBIKOS.py`

To generate a benchmark circuit, provide a **device coupling graph** — a list of tuples like `[(0, 1), (1, 2)]`, where each number is a physical qubit and each tuple denotes a connection between them. Physical qubits should be labeled from `0` to `n-1`.

### Example

```python
from QUBIKOS import *

benchmark_circuit, compiled_circuit = generate_qubikos_circuit(
    "benchmark.qasm",         # Output QASM file for the benchmark circuit
    "compiled.qasm",          # Output QASM file for the compiled circuit with SWAPs
    [(0, 1), (1, 2)],          # Coupling graph
    2,                         # Known optimal number of SWAPs (minimum is 1)
    50,                        # Number of two-qubit gates
    10                         # Number of single-qubit gates
)
```

- `benchmark.qasm`: File where the benchmark circuit will be written.
- `compiled.qasm`: File for the compiled circuit with inserted SWAP gates.
- Coupling graph: Describes the hardware connectivity.
- The function returns two `QuantumCircuit` objects (`benchmark_circuit` and `compiled_circuit`).

> ⚠️ **Note:** If the number of two-qubit gates is too small to satisfy the construction constraints, the output circuit may contain more gates than specified.

## 📄 Citation

If you use QUBIKOS in your research, please cite the following paper:

```bibtex
@misc{ping2025assessingquantumlayoutsynthesis,
      title={Assessing Quantum Layout Synthesis Tools via Known Optimal-SWAP Cost Benchmarks}, 
      author={Shuohao Ping and Wan-Hsuan Lin and Daniel Bochen Tan and Jason Cong},
      year={2025},
      eprint={2502.08839},
      archivePrefix={arXiv},
      primaryClass={quant-ph},
      url={https://arxiv.org/abs/2502.08839}, 
}
```

## 🔗 Resources

- [arXiv:2502.08839](https://arxiv.org/abs/2502.08839) – Full paper on the QUBIKOS methodology and benchmark analysis.
