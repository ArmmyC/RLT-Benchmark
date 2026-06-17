from rtlbench.adapters.verilogeval import VerilogEvalAdapter
from rtlbench.adapters.rtllm2 import RTLLM2Adapter
from rtlbench.adapters.protocollm import ProtocolLLMAdapter
from rtlbench.adapters.rfid_apbench import RFIDAPBenchAdapter
from rtlbench.adapters.rtlopt import RTLOPTAdapter

ADAPTERS = {
    "verilogeval": VerilogEvalAdapter,
    "rtllm2": RTLLM2Adapter,
    "protocollm": ProtocolLLMAdapter,
    "rtlopt": RTLOPTAdapter,
    "rfid_apbench": RFIDAPBenchAdapter,
}
